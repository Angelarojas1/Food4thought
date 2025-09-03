#!/usr/bin/env python
# coding: utf-8

# #### Data Cleaning of Costo Rica

# In[1]:


# import packages
get_ipython().run_line_magic('matplotlib', 'inline')
import ast
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re
from deep_translator import GoogleTranslator
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

from nltk import word_tokenize,Text,pos_tag 
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

from word2number import w2n


# In[2]:


# import dataset
data = pd.read_csv("/Users/xixi/Dropbox/food4thought/data/intermediate/CostaRica.csv")
data.drop(['Unnamed: 0'],axis=1,inplace=True)

data.head()


# In[3]:


data.shape


# ##### Drop recipes with missing values in ingredients or instructions

# In[4]:


# convert string repretention of list to a list
data['List of ingredients'] = data['List of ingredients'].apply(lambda x:ast.literal_eval(x))
data['List of instructions'] = data['List of instructions'].apply(lambda x:ast.literal_eval(x))

# drop thoes with missing values
data = data[data['List of ingredients'].map(lambda d: len(d)) > 0]
data = data[data['List of instructions'].map(lambda d: len(d)) > 0]
data.shape


# #### Category

# In[5]:


# convert category to the category in English
data['Category'].replace({'Bebidas': 'Drinks','Entradas': 'Appetizers', 'Plato Principal': 'Main dish', 'Repostería': 'Dessert', 'Sopas': 'Soup','Reposteria':"Dessert", "Cake": "Dessert"},inplace=True)
data.head()


# In[6]:


# construct new variables called Dessert and Drinks
data['Dessert'] = data['Category'].apply(lambda x: x=='Dessert')
data['Drinks'] = data['Category'].apply(lambda x: x=='Drinks')


# In[7]:


data.head()


# ### Translate ingredients to English

# In[ ]:


# translate ingredients to English
def transIngredient(content):
    """
    input: ingredient list of one recipe
    output: ingredient list of one recipe in English
    
    """
    
    ingredientEng = [GoogleTranslator(source='auto', target='english').translate(i) for i in content]
    return ingredientEng

data['List of ingredients_Eng'] = data['List of ingredients'].apply(lambda x:transIngredient(x))
data.head()


# ### Generate indicators for ingredients that appears in the dessert

# In[5]:


# convert string repretention of list to a list
data['List of ingredients_Eng'] = data['List of ingredients_Eng'].apply(lambda x:ast.literal_eval(x))


# In[8]:


# generate indicators that if ingredients contain sugar, egg, flour, baking powder, milk, butter
for key in ['sugar','egg','yolk','flour','baking powder','milk','butter']:
    data[key] = data['List of ingredients_Eng'].apply(lambda x: True if sum([key in i.lower() for i in x])>=1 else False)


# In[9]:


data.head()


# ### Ingredient tagger

# In[6]:


def num_there(s):
    return any(i.isdigit() for i in s)

import unicodedata

def fraction_finder(s):
    """
    find if there is a unicode fraction in the string s
    """
    for c in s:
        try:
            name = unicodedata.name(c)
        except ValueError:
            continue
        if name.startswith('VULGAR FRACTION'):
            normalized = unicodedata.normalize('NFKC', c)
            numerator, _slash, denominator = normalized.partition('⁄')
            return str(int(numerator)/int(denominator))
        
def fraction_replace(s):
    """
    replace the unicode fraction to normal fraction   
    
    """
    for c in s:
        try:
            name = unicodedata.name(c)
        except ValueError:
            continue
        if name.startswith('VULGAR FRACTION'):
            normalized = unicodedata.normalize('NFKC', c)
            numerator, _slash, denominator = normalized.partition('⁄')
            s = s.replace(c,str(int(numerator))+'/'+str(int(denominator)))
            
    return s

def fractionToFloat(fraction):

    """
    input: fraction in string
    output: float
    
    """
    num = 0
    mult = 1

    if fraction[:1] == "-":
        fraction = fraction[1:]     
        mult = -1

    if " " in fraction:
        a = fraction.split(" ")
        num = float(a[0])
        toSplit = a[1]
    else:
        toSplit = fraction

    frac = toSplit.split("/")
    num += float(frac[0]) / float(frac[1])

    return num * mult


# In[7]:


def ifUnit(ingredientStr):
    
    """
    input: ingredient string in English
    output: return a list [True/False, index]
    the first item indicates whether we have a unit in the ingredient
    the second item indicates the index of the unit in the ingredientStr
    
    we apply fuzzy match to determine if there contains a unit
    
    """
    # initialize the output
    result = [False]
    
    # import unit data
    unitData = pd.ExcelFile("/Users/xixi/Dropbox/food4thought/material/unit_data/roster_unit.xlsx")
    unit = pd.read_excel(unitData)

    # add unit to list
    unitLst = []
    for i in range(len(unit)):
        unitLst.append(unit.loc[i,'unit'])
    
    # initialize the output list
    fuzzScore = []
    
    for i in ingredientStr.split():
        fullScore = []
        for ele in unitLst:
            fullScore.append(fuzz.ratio(i.lower(),ele))
            
        fuzzScore.append(max(fullScore))
                
    for i in fuzzScore:
        if i >= 90:
            result[0] = True
        
        
    for i in range(len(fuzzScore)):
        if fuzzScore[i] >=90:
            result.append(i)
            
    return result
    


# In[8]:


def ingredientTagger(ingredientStr):
    
    """
    input: ingredient string in English, like "1 pound carrots, young ones if possible"
    output: dictionary like
    
    {
    
        "qty": "1",
        "unit":"pound",
        "item":"carrots",
        "preparation":"young ones if possible",
        "input":"1 pound carrots, young ones if possible"
    }
    
    """
    
    # initialize output dictionary
    result = {
        "qty":"",
        "unit":"",
        "item":"",
        "preparation":"",
        "input":""
    }
    
    result["input"] = ingredientStr
    
    # step 0: transfer ingredient to lower case
    ingredientStr = ingredientStr.lower()
    
    # step 0: if we have () in the end of the ingredient, split by () and get optional preparation method
    if ")" == ingredientStr[-1] and "(" in ingredientStr:
        result["preparation"] = ingredientStr.split("(")[1].replace(")","")
        ingredientStr = ingredientStr.split("(")[0]
        
    # step 1: if we have comma in the ingredient, split by ","
    if "," in ingredientStr:
        
        # step 1.1: if the second part contains digit, then replace "," with ""
        if num_there(ingredientStr.split(",")[1]):
            ingredientStr = ingredientStr.replace(",","")
            
        # step 1.2: if the second part doesn't contain digit, then get the optional preparation method
        else:
            result["preparation"] = ingredientStr.split(",")[1]
            ingredientStr = ingredientStr.split(",")[0]
            
    # step 2: transfer unicode literals to fractions
    if fraction_finder(ingredientStr) != None:
        
        # step 2.1: if there is no other digit, transfer unicode directly
        if num_there(ingredientStr) == False:
            ingredientStr = fraction_replace(ingredientStr)
        
        # step 2.2: if there is other digit
        else:
            
            # case 1.½
            if "." in ingredientStr:
                ingredientStr = ingredientStr.replace("."," ")
                
                
            # case 1 and ½ or 1 ½ 
            if len([int(s) for s in ingredientStr.split() if s.isdigit()]) > 0:
                
                newFraction = [int(s) for s in ingredientStr.split() if s.isdigit()][0] + float(fraction_finder(ingredientStr))

                for c in ingredientStr:
                    if c.isdigit():
                        ingredientStr = ingredientStr.replace(c,"")
                        
                for c in ingredientStr:
                    try:
                        name = unicodedata.name(c)
                    except ValueError:
                        continue
                    if name.startswith('VULGAR FRACTION'):
                        ingredientStr = ingredientStr.replace(c,str(newFraction))
                           
                        
            # case 1½
            else:
                
                newFraction = float(fraction_finder(ingredientStr))
             
                for c in ingredientStr:
                    try:
                        name = unicodedata.name(c)
                    except ValueError:
                        continue
                    if name.startswith('VULGAR FRACTION'):
                        newFraction += [int(s) for s in ingredientStr.split(c)[0].split() if s.isdigit()][0]
                        ingredientStr = ingredientStr.replace(c,"")
                        
                for c in ingredientStr:
                    if c.isdigit():
                        ingredientStr = ingredientStr.replace(c,str(newFraction))
                        
    if "/" in ingredientStr:
        temp = ingredientStr.split()
        for i in range(len(temp)):
            if "/" in temp[i]:
                try:
                    temp[i] = str(fractionToFloat(temp[i]))
                    
                except:
                    temp[i] = ''
                
        ingredientStr = " ".join(temp)
                
                     
    # step 3: if a digit isn’t in the ingredient:
    if num_there(ingredientStr) == False:
        
        # step 3.1. We split by “ “. If we have a unit in the ingredient,
        if ifUnit(ingredientStr)[0] == True:
            
            # if the word before the unit is “a” and the word before the “a” is “half”, then the qty = 0.5
            if ingredientStr.split()[ifUnit(ingredientStr)[1]-1] == "a" and ingredientStr.split()[ifUnit(ingredientStr)[1]-2] == "half":
                result["qty"] = "0.5"
                result["unit"] = ingredientStr.split()[ifUnit(ingredientStr)[1]]
                result["item"] = ' '.join(ingredientStr.split()[ifUnit(ingredientStr)[1]+1:]) 
            
            # if the word before the unit is “a” and the word before the “a” isn’t “half”, then the qty = 1
            elif ingredientStr.split()[ifUnit(ingredientStr)[1]-1] == "a" and ingredientStr.split()[ifUnit(ingredientStr)[1]-2] != "half":
                result["qty"] = "1"
                result["unit"] = ingredientStr.split()[ifUnit(ingredientStr)[1]]
                result["item"] = ' '.join(ingredientStr.split()[ifUnit(ingredientStr)[1]+1:])
                
            else:
                result["qty"] = "1"
                result["unit"] = ingredientStr.split()[ifUnit(ingredientStr)[1]]
                result["item"] = ' '.join(ingredientStr.split()[ifUnit(ingredientStr)[1]+1:])
                
        # step 3.2.  If we don’t have a unit in the ingredient,  then we can only get ingredients, the qty = missing  
        else:
            result["item"] = ingredientStr
            
    # step 4: if a digit is in the ingredient 
    else:
        
        # step 4: and if “of” is in the ingredient 
        if "of" in ingredientStr.split():
            
            if num_there(ingredientStr.split("of")[0]):
                result["item"] = ingredientStr.split("of")[1]
                ingredientStr = ingredientStr.split("of")[0]
            
                # step 4.1: if we have a unit in the ingredient
                if ifUnit(ingredientStr)[0] == True:
                    result["unit"] = ingredientStr.split()[ifUnit(ingredientStr)[1]]
                
                    if ingredientStr.split()[ifUnit(ingredientStr)[1]-1].isdigit():
                        result["qty"] = ingredientStr.split()[ifUnit(ingredientStr)[1]-1]
                    
                    else:
                        result["qty"] = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", ingredientStr)[0]
                    
                # step 4.2: if we don't have a unit in the ingredient
                else:
                    result["qty"] = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", ingredientStr)[0]
                
            else:
                ingredientStr = ingredientStr.split("of")[1]
                
                if ifUnit(ingredientStr)[0] == True:
                    result["unit"] = ingredientStr.split()[ifUnit(ingredientStr)[1]]
                    result["item"] = ' '.join(ingredientStr.split()[ifUnit(ingredientStr)[1]+1:])
                
                    if ingredientStr.split()[ifUnit(ingredientStr)[1]-1].isdigit():
                        result["qty"] = ingredientStr.split()[ifUnit(ingredientStr)[1]-1]
                    
                    else:
                        result["qty"] = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", ingredientStr)[0]
                    
                else:
                    result["qty"] = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", ingredientStr)[0]
                    result["item"] = re.sub(r"[-+]?(?:\d*\.\d+|\d+)", '', ingredientStr)
                
        
        # step 5: and if “of” isn't in the ingredient     
        else:
            
            # step 5.1: if we have a unit in the ingredient
            if ifUnit(ingredientStr)[0] == True:
                result["item"] = ' '.join(ingredientStr.split()[ifUnit(ingredientStr)[1]+1:])
                
                # If the word before the unit is “half” and the word before the “half” is “a”
                if ingredientStr.split()[ifUnit(ingredientStr)[1]-1] == "half" and ingredientStr.split()[ifUnit(ingredientStr)[1]-2] == "a":
                    result["qty"] = str([int(s) for s in ingredientStr.split() if s.isdigit()][0]+0.5)
                    result["unit"] = ingredientStr.split()[ifUnit(ingredientStr)[1]]
                    
                else:
                    if len([int(s) for s in ingredientStr.split()[:ifUnit(ingredientStr)[1]] if s.isdigit()]) > 0:
                        result["qty"] =  re.findall(r"[-+]?(?:\d*\.\d+|\d+)", ingredientStr)[0]
                        result["unit"] = ingredientStr.split()[ifUnit(ingredientStr)[1]]
                        
                    else:
                        result["qty"] = re.findall(r"[-+]?(?:\d*\.\d+|\d+)"," ".join(ingredientStr.split()[:ifUnit(ingredientStr)[1]]))[0]
                        result["unit"] = re.sub(r"[-+]?(?:\d*\.\d+|\d+)", '',ingredientStr.split()[ifUnit(ingredientStr)[1]])
                        
            # step 5.2: if we don't have a unit in the ingredient
            else:
                result["qty"] = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", ingredientStr)[0]
                result["item"] = re.sub(r"[-+]?(?:\d*\.\d+|\d+)", '', ingredientStr)

    return result


# In[9]:


def ingredientLstTagger(ingredientLst):
    
    """
    input: ingredient in list
    output: ingredient tagger in list
    
    """
    result = []
    
    for i in ingredientLst:
        try:
            result.append(ingredientTagger(i))
            
        except:
            result.append({
        "qty":"",
        "unit":"",
        "item":i,
        "preparation":"",
        "input":i
    })
        
    return result

data['Ingredient list tagger'] = data["List of ingredients_Eng"].apply(lambda x: ingredientLstTagger(x))


# ### Get the amount of sugar

# In[15]:


def unitInLst(unitTagger):
    """
    input: unit from ingredient tagger
    
    output: unit from the unit list that is most similar to the unit
    
    """
    
    # import unit data
    unitData = pd.ExcelFile("/Users/xixi/Dropbox/food4thought/material/unit_data/roster_unit.xlsx")
    unit = pd.read_excel(unitData)

    # add unit to list
    unitLst = []
    for i in range(len(unit)):
        unitLst.append(unit.loc[i,'unit'])
        
    
    scoreLst = []
    for ele in unitLst:
        scoreLst.append(fuzz.ratio(unitTagger,ele))
        
        
    return unitLst[scoreLst.index(max(scoreLst))]
    
    
def sugarAmount(ingredientLstTagger):
    """
    input: ingredient list tagger
    
    output: sugar amount in tsp
     
    """
    
    # initialize the sugar amount
    sugarAmount = 0
    
    # import unit measure data
    unitMeasure = pd.ExcelFile("/Users/xixi/Dropbox/food4thought/material/unit_data/Unit standard.xlsx")
    unitMeasureDic = pd.read_excel(unitMeasure, index_col=0).to_dict()['teaspoon']
    
    for dic in ingredientLstTagger:
        if "sugar" in dic["item"] and dic["unit"] != "":
            sugarAmount += unitMeasureDic[unitInLst(dic["unit"])]*float(dic["qty"])
            
    for dic in ingredientLstTagger:
        if "sugar" in dic["item"] and sugarAmount == 0:
            sugarAmount = np.nan
            
    return sugarAmount 

data["sugarAmount in tsp(ingredient tagger)"] = data['Ingredient list tagger'].apply(lambda x: sugarAmount(x))


# In[16]:


data['sugarAmount in tsp(ingredient tagger)'].describe()


# In[17]:


data['sugarAmount in tsp'].describe()


# ### Get proportion of fruit, yogurt, and milk

# In[13]:


def calProportion(ingredientLstTagger):
    """
    input: ingredient list tagger
    
    output: the proportion of fruits, yogurt, and milk
    
    """
    
    # import fruit list
    import json
    with open("/Users/xixi/Dropbox/food4thought/material/fruit_data/fruits.json") as read_file:
        fruit = json.load(read_file)
        
    # add milk and yogurt to the fruit list
    fruit.append("milk")
    fruit.append("yogurt")
    
    # count the total number of ingredients
    total = len(ingredientLstTagger)
    
    if total == 0:
        return 0
    
    # count the number of fruit, milk, and yogurt
    count = 0
    
    for dic in ingredientLstTagger:
        scoreLst = []
        for ele in fruit:
            scoreLst.append(fuzz.partial_ratio(dic["item"],ele))
            
        if max(scoreLst) >= 90:
            count += 1
            
            
    return count/total  

data["Proportion of fruit"] = data['Ingredient list tagger'].apply(lambda x: calProportion(x))


# ### Recipe Tagger

# In[4]:


data['Ingredient list tagger'] = data['Ingredient list tagger'].apply(lambda x:ast.literal_eval(x))


# In[5]:


from recipe_tagger import recipe_tagger


def recipeTagger(ingredientTagger):
    """
    input: ingredient list tagger
    output: recipe tagger list
    
    """
    
    ingredientClass = []
    for dic in ingredientTagger:
        if dic['item'] != '':
            try:
                ingredientClass.append(recipe_tagger.get_ingredient_class(dic['item']))
                
            except:
                ingredientClass.append('')
                
        else:
            try:
                ingredientClass.append(recipe_tagger.get_ingredient_class(dic['input']))
                
            except:
                ingredientClass.append('')
            
    return ingredientClass

data['recipe tagger'] = data['Ingredient list tagger'].apply(lambda x: recipeTagger(x))


# In[6]:


def proportionClass(recipeTagger):
    """
    input: recipe tagger list
    output: proportion of each class
    
    """
    
    # initialize the output dictionary
    dic = {
        "Vegetable":0,
        "Fruit":0,
        "Legume":0,
        "Meat":0,
        "Diary":0,
        "Staple":0,
        "Condiment":0,
        "Nut":0,
        "Seafood":0,
        "Snack":0,
        "Mushroom":0,
        "Dessert":0,
        "Beverage":0
    }
    
    # count the total number of ingredients
    total = len(recipeTagger)
    
    if total == 0:
        return dic
    
    
    for category in ["Vegetable","Fruit","Legume","Meat","Diary","Staple","Condiment","Nut","Seafood","Snack","Mushroom","Dessert","Beverage"]:
        count = 0
        for i in recipeTagger:
            if i == category.lower():
                count += 1
                
        dic[category] = count/total

    return dic

data['recipe tagger proportion'] = data['recipe tagger'].apply(lambda x: proportionClass(x))
            


# #### Save the data

# In[8]:


data.to_csv("/Users/xixi/Dropbox/food4thought/data/intermediate/CostaRica.csv")


# In[ ]:




