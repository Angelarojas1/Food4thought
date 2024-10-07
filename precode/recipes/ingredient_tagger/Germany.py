#!/usr/bin/env python
# coding: utf-8

# #### Ingredient Tagger of Germany
# 

# In[2]:


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


# In[3]:


# import dataset
data = pd.read_csv("/Users/stell/Dropbox/food4thought/analysis23/data/precoded/recipes/intermediate/Germany.csv")
data.drop(['Unnamed: 0'],axis=1,inplace=True)
data.head()

# In[4]:


data.shape


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


# ### Ingredient tagger

# In[5]:


# convert string repretention of list to a list
data['List of ingredients_Eng'] = data['List of ingredients_Eng'].apply(lambda x:ast.literal_eval(x))


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
            s = s.replace(c,str(int(numerator)/int(denominator)))
            
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
    unitData = pd.ExcelFile("/Users/stell/Dropbox/food4thought/analysis23/data/raw/unit_data/roster_unit.xlsx")
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


def EuropeanIngredientTagger(ingredientStr):
    """
    
    input: ingredient string in English from European data, like "1 pound carrots, young ones if possible"
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

    # step 1: transfer all unicode literals to fractions
    if fraction_finder(ingredientStr) != None:
        
        # step 1.1: if there is no other digit, transfer unicode directly
        if num_there(ingredientStr) == False:
            ingredientStr = fraction_replace(ingredientStr)
            
        # step 1.2: if there is other digit,
        else:
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
                        
    # step 2: Count the number of comma in the ingredient phrase
    numComma = ingredientStr.count(",")
    
    
    # step 2.1 if there is no comma in the ingredient phrase
    def noCommaTagger(ingredientStr):
        """
        fill in the output dictionary if there is no comma in the ingredient phrase
        
        """
        # initialize the output dictionary
        noComma = {     
            "qty":"",
            "unit":"",
            "item":""
        }
        
        # if there is digit
        if num_there(ingredientStr) == True:
            
            # the digit part is quantity
            noComma["qty"] =  re.findall(r"[-+]?(?:\d*\.\d+|\d+)", ingredientStr)[0]
            
            # remove the digit part
            ingredientStr = re.sub(r"[-+]?(?:\d*\.\d+|\d+)", '', ingredientStr).lstrip()
            
            # detect if there is a unit
            if ifUnit(ingredientStr)[0] == True:
                noComma["unit"] = ingredientStr.split()[ifUnit(ingredientStr)[1]].replace(" ","")
                noComma["item"] = ' '.join(ingredientStr.split()[ifUnit(ingredientStr)[1]+1:]).replace("of","")
            
            # if there is no unit:
            else:
                noComma["item"] = ingredientStr.replace("of","")
                
        # if there is no digit
        else:
            noComma["item"] = ingredientStr.replace("of","")
            
        return noComma
    
    if numComma == 0:
        result["qty"] = noCommaTagger(ingredientStr)["qty"]
        result["unit"] = noCommaTagger(ingredientStr)["unit"]
        result["item"] = noCommaTagger(ingredientStr)["item"]
        
        
    # step 2.2 if there is 1 comma in the inredient phrase
    if numComma == 1:
        # if there is no digit in the part after the comma
        if num_there(ingredientStr.split(",")[1]) == False:
            result["preparation"] = ingredientStr.split(",")[1]
            # for the part before the comma, go back to step 2.1
            ingredientStr = ingredientStr.split(",")[0]
            result["qty"] = noCommaTagger(ingredientStr)["qty"]
            result["unit"] = noCommaTagger(ingredientStr)["unit"]
            result["item"] = noCommaTagger(ingredientStr)["item"]
            if result["item"] == "":
                result["item"] = result["preparation"]
                result["preparation"] = ""
            
        # if there is digit
        else:
            # if there is no digit in the first part
            if num_there(ingredientStr.split(",")[0]) == False:
                result["item"] = ingredientStr.split(",")[0]
                ingredientStr = ingredientStr.split(",")[1]
                result["qty"] = noCommaTagger(ingredientStr)["qty"]
                result["unit"] = noCommaTagger(ingredientStr)["unit"]
               
            # if there is a digit in the first part
            else:
                ingredientStr = ingredientStr.replace(",","")
                result["qty"] = noCommaTagger(ingredientStr)["qty"]
                result["unit"] = noCommaTagger(ingredientStr)["unit"]
                result["item"] = noCommaTagger(ingredientStr)["item"]
         
    # step 2.3 if there are 2 commas in the ingredient phrase
    if numComma == 2:
        
        # if there is no digit in the part after the second comma
        if num_there(ingredientStr.split(",")[2]) == False:
            result["preparation"] = ingredientStr.split(",")[2]
            
            if num_there(ingredientStr.split(",")[1]) == True and num_there(ingredientStr.split(",")[0]) == True:
                ingredientStr = ingredientStr.replace(",","").replace(result["preparation"],"")
                result["qty"] = noCommaTagger(ingredientStr)["qty"]
                result["unit"] = noCommaTagger(ingredientStr)["unit"]
                result["item"] = noCommaTagger(ingredientStr)["item"]
                
            else:
                result["preparation"] = "".join(ingredientStr.split(",")[1:])
                ingredientStr = ingredientStr.split(",")[0]
                result["qty"] = noCommaTagger(ingredientStr)["qty"]
                result["unit"] = noCommaTagger(ingredientStr)["unit"]
                result["item"] = noCommaTagger(ingredientStr)["item"]
                
        # if there is digit in the part after the second comma:
        else:
            result["item"] = "".join(ingredientStr.split(",")[:2])
            ingredientStr = ingredientStr.split(",")[2]
            result["qty"] = noCommaTagger(ingredientStr)["qty"]
            result["unit"] = noCommaTagger(ingredientStr)["unit"]
            
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
            result.append(EuropeanIngredientTagger(i))
            
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

# In[10]:


def unitInLst(unitTagger):
    """
    input: unit from ingredient tagger
    
    output: unit from the unit list that is most similar to the unit
    
    """
    
    # import unit data
    unitData = pd.ExcelFile("/Users/stell/Dropbox/food4thought/analysis23/data/raw/unit_data/roster_unit.xlsx")
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
    unitMeasure = pd.ExcelFile("/Users/stell/Dropbox/food4thought/analysis23/data/raw/unit_data/Unit standard.xlsx")
    unitMeasureDic = pd.read_excel(unitMeasure, index_col=0).to_dict()['teaspoon']
    
    for dic in ingredientLstTagger:
        if "sugar" in dic["item"] and dic["unit"] != "":
            sugarAmount += unitMeasureDic[unitInLst(dic["unit"])]*float(dic["qty"])
            
    for dic in ingredientLstTagger:
        if "sugar" in dic["item"] and sugarAmount == 0:
            sugarAmount = np.nan
            
    return sugarAmount 

data["sugarAmount in tsp(ingredient tagger)"] = data['Ingredient list tagger'].apply(lambda x: sugarAmount(x))


# In[11]:


data['sugarAmount in tsp(ingredient tagger)'].describe()


# ### Save the data

# In[12]:


data.to_csv("/Users/stell/Dropbox/food4thought/analysis23/data/precoded/recipes/final/Germany.csv")


# In[ ]:




