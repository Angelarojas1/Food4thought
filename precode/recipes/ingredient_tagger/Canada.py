#!/usr/bin/env python
# coding: utf-8

# #### Ingredient Tagger of Canada

# In[1]:


# import packages
get_ipython().system('pip install deep_translator')
get_ipython().system('pip install fuzzywuzzy')
get_ipython().system('pip install word2number')
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


from google.colab import drive
drive.mount('/content/drive')


# In[3]:


# import dataset
data = pd.read_csv("/content/drive/MyDrive/DATA/Canada.csv")
data.shape


# In[4]:


#drop those with missing values 
data.dropna(subset=['List of ingredients'], inplace= True)
data.shape


# In[5]:


data.head()


# In[6]:


# convert string repretention of list to a list

data['List of ingredients'] = data['List of ingredients'].apply(lambda x: ast.literal_eval(str(x)))
data['List of ingredients']


# In[8]:


data['List of ingredients'].head(100)[19]


# ### Ingredient tagger

# In[9]:


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


# In[10]:


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
    unitData = pd.ExcelFile("/content/drive/MyDrive/DATA/roster_unit.xlsx")
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
    


# In[11]:


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
    if ")" != ingredientStr[-1] and "(" in ingredientStr:
        ingredientStr = ingredientStr.split("(")[1].replace(")","")
            
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
        # Case 1: e.g 1 2/3 g
        if len(list(ingredientStr.split()[0]))==1:
          temp =  int(list(ingredientStr.split('/')[0])[0]) + (int(list(ingredientStr.split('/')[0])[2])/int(list(ingredientStr.split('/')[1])[0]))
          ingredientStr = ingredientStr.replace(' '.join(ingredientStr.split()[:2]), str(temp) + '' )
        # Case 2: e.g 15/3 g or 2/3 g
        else:
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
                result["unit"] = (re.sub(r"[-+]?(?:\d*\.\d+|\d+)", '', ingredientStr)).split()[0]
                result["item"] = ' '.join((re.sub(r"[-+]?(?:\d*\.\d+|\d+)", '', ingredientStr)).split()[1:])

    return result


# In[12]:


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

data['Ingredient list tagger'] = data["List of ingredients"].apply(lambda x: ingredientLstTagger(x))


# In[13]:


data['Ingredient list tagger'].head(30)[10]


# ### Save the data

# In[14]:


data.to_csv("/content/drive/MyDrive/DATA/INTERMEDIATE/Canada.csv")


# In[ ]:




