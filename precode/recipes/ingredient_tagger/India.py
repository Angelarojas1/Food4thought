#!/usr/bin/env python
# coding: utf-8

# #### Ingredient Tagger of India

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
data = pd.read_csv("/Users/xixi/Dropbox/food4thought/data/intermediate/India.csv")
data.drop(['Unnamed: 0'],axis=1,inplace=True)
data.head()


# In[4]:


data.shape


# ### Translate ingredients to English

# In[4]:


# convert string repretention of list to a list
data['List of ingredients'] = data['List of ingredients'].apply(lambda x:ast.literal_eval(x))


# In[5]:


# translate ingredients to English
def transIngredient(content):
    """
    input: ingredient list of one recipe
    output: ingredient list of one recipe in English
    
    """
    if content == []:
        return []
    # detect if the language is English
    from langdetect import detect
    if detect(content[0][1]) == "en":
        ingredientEng = content
        
    else:
        ingredientEng = []
        for i in content:
            temp = []
            for j in i:
                if any(c.isalpha() for c in j):
                    temp.append(GoogleTranslator(source='auto', target='english').translate(j)) 
                else:
                    temp.append(j)
            ingredientEng.append(temp)
        
    return ingredientEng

data['List of ingredients_Eng'] = data['List of ingredients'].apply(lambda x:transIngredient(x))
data.head()


# ### Ingredient tagger

# In[5]:


data['List of ingredients_Eng'] = data['List of ingredients_Eng'].apply(lambda x:ast.literal_eval(x))


# In[113]:


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

def IndiaIngredientTagger(ingredientLst):
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
    
    result["input"] = ingredientLst
    
    result['item'] = ingredientLst[1].lower()
    
    ingredientStr = ingredientLst[0].lower()
    
    if ingredientStr == '':
        result['qty'] = ''
        result['unit'] = ''
        
    else:
        if ingredientStr.split()[-1].isalpha():
            result['unit'] = ingredientStr.split()[-1]
            ingredientStr = " ".join(ingredientStr.split()[:-1])
            
        else:
             result['unit'] = ''
                
        if 'to' in ingredientStr.split():
            if "/" in ingredientStr:
                result['qty'] = fractionToFloat(ingredientStr.split()[-1])
            else:
                result['qty'] = float(ingredientStr.split()[-1])
                
        elif '+' in ingredientStr.split():
            if "/" in ingredientStr:
                result['qty'] = fractionToFloat(ingredientStr.split()[-1])
            else:
                result['qty'] = float(ingredientStr.split()[-1])
                
        elif '-' in ingredientStr:
            if "/" in ingredientStr.split('-')[-1]:
                result['qty'] = fractionToFloat(ingredientStr.split('-')[-1].replace(' ',''))
            else:
                result['qty'] = float(ingredientStr.split('-')[-1])
        
        elif '–' in ingredientStr:
            if "/" in ingredientStr.split('-')[-1]:
                result['qty'] = fractionToFloat(ingredientStr.split('–')[-1].replace(' ',''))
            else:
                result['qty'] = float(ingredientStr.split('–')[-1])
        
        elif len(ingredientStr.split()) == 0:
            result['qty'] = 0
        
        elif bool(re.search(r'\d', ingredientStr)) == False:
            result['qty'] = 0
            
        elif len(ingredientStr.split()) == 1:
            if "/" in ingredientStr:
                result['qty'] = fractionToFloat(ingredientStr)
            else:
                result['qty'] = float(ingredientStr)
                    
        else:
            result['qty'] = float(ingredientStr.split()[0]) + fractionToFloat(ingredientStr.split()[1])
                
    return result
                
        


# In[114]:


def ingredientLstTagger(ingredientLst):
    
    """
    input: ingredient in list
    output: ingredient tagger in list
    
    """
    result = []
    
    for i in ingredientLst:
        try:
            result.append(IndiaIngredientTagger(i))
            
        except:
            result.append({
        "qty":"",
        "unit":"",
        "item":i[1],
        "preparation":"",
        "input":i
    })
        
    return result

data['Ingredient list tagger'] = data["List of ingredients_Eng"].apply(lambda x: ingredientLstTagger(x))


# ### Save the data

# In[115]:


data.to_csv("/Users/xixi/Dropbox/food4thought/data/intermediate/India.csv")


# In[ ]:




