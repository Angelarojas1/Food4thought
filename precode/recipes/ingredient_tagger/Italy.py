#!/usr/bin/env python
# coding: utf-8

# #### Ingredient Tagger of Italy
# 

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
data = pd.read_csv("/Users/xixi/Dropbox/food4thought/data/intermediate/Italy.csv")
data.drop(['Unnamed: 0'],axis=1,inplace=True)
data.head()


# In[3]:


data.shape


# ### Ingredient tagger

# In[5]:


# convert string repretention of list to a list
data['List of ingredients'] = data['List of ingredients'].apply(lambda x:ast.literal_eval(x))


# In[40]:


def num_there(s):
    return any(i.isdigit() for i in s)

import unicodedata

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


# In[87]:


def ItalyIngredientTagger(ingredientStr):
    """
    
    input: ingredient string in English from Italian data, like "1 pound carrots, young ones if possible"
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

    
    # step 1: if there is “()” in the ingredient phrase, then the preparation is the item inside “()”
    if ingredientStr.find("(") != -1 and ingredientStr.find(")") != -1:
        result["preparation"] = ingredientStr[ingredientStr.find("(")+1:ingredientStr.find(")")]
        # remove string inside braclets
        ingredientStr = re.sub("[\(\[].*?[\)\]]", "", ingredientStr)
        
    # step 2: if there is no digit in the ingredient phrase, item is the whole string.
    if num_there(ingredientStr) == False:
        result["item"] = ingredientStr
        
    # step 3: Otherwise
    else:
        
        # step 3.1: if “&frac” in the ingredient phrase
        if "&frac" in ingredientStr:
            frac = re.search('&frac(.+?);', ingredientStr).group(1)
            frac = frac[0]+"/"+frac[1]
            ingredientStr = re.sub('&frac(.+?);',frac,ingredientStr)
        
        # step 3.2: if the last part in the ingredient phrase is not digit
        if num_there(ingredientStr.split()[-1]) == False:
            result["unit"] = ingredientStr.split()[-1]
            ingredientStr = " ".join(ingredientStr.split()[:-1])
            
        # step 3.3: if there is “00” in the ingredient phrase
        if "00" in ingredientStr:
            result["item"] = " ".join(ingredientStr.split()[:ingredientStr.split().index("00")+1])
            qtyLst = ingredientStr.split()[ingredientStr.split().index("00")+1:]
            
            totalQty = 0
            for qty in qtyLst:
                if "/" in qty:
                    totalQty += fractionToFloat(qty)
                    
                else: 
                    totalQty += float(qty)
                    
            result["qty"] = totalQty
        
        # step 3.4: if there is no "00":
        else:
            
            qtyLst = []
            for i in range(len(ingredientStr.split())):
                if num_there(ingredientStr.split()[i]):
                    qtyLst.append(ingredientStr.split()[i])
                    
            totalQty = 0
            for qty in qtyLst:
                if "/" in qty:
                    totalQty += fractionToFloat(qty)
                    
                else: 
                    totalQty += float(qty)
                    
            result["qty"] = totalQty
            result["item"] = " ".join(list(set(ingredientStr.split())-set(qtyLst)))
            

    return result   


# In[88]:


def ingredientLstTagger(ingredientLst):
    
    """
    input: ingredient in list
    output: ingredient tagger in list
    
    """
    result = []
    
    for i in ingredientLst:
        try:
            result.append(ItalyIngredientTagger(i))
            
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


# ### Get the amount of sugar

# In[92]:


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
            sugarAmount += unitMeasureDic[dic["unit"]]*float(dic["qty"])
            
    for dic in ingredientLstTagger:
        if "sugar" in dic["item"] and sugarAmount == 0:
            sugarAmount = np.nan
            
    return sugarAmount 

data["sugarAmount in tsp(ingredient tagger)"] = data['Ingredient list tagger'].apply(lambda x: sugarAmount(x))


# In[93]:


data['sugarAmount in tsp(ingredient tagger)'].describe()


# ### Save the data

# In[94]:


data.to_csv("/Users/xixi/Dropbox/food4thought/data/intermediate/Italy.csv")


# In[ ]:




