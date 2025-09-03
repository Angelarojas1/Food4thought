#!/usr/bin/env python
# coding: utf-8

# #### Ingredient Tagger of Algeria

# In[235]:


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


# In[236]:


from google.colab import drive
drive.mount('/content/drive')


# In[237]:


# import dataset
data = pd.read_csv("/content/drive/MyDrive/DATA/Algeria.csv")
data.shape


# In[238]:


#drop those with missing values 
data.dropna(subset=['List of ingredients'], inplace= True)
data.shape


# ##### Formating

# In[239]:


# convert string repretention of list to a list
data['List of ingredients'] = data['List of ingredients'].apply(lambda x: list(x.split('\n')))
data['List of ingredients'] = data['List of ingredients'].apply(lambda x:ast.literal_eval(str(x)))
data['List of ingredients'][0]


# ### Ingredient tagger

# In[240]:


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


# In[241]:


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
    


# In[242]:


def AlgeriaIngredientTagger(ingredientLst):
    """
    input: ingredient string in English, like "carrots: 1 pound (young ones if possible)"
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
    #Step 0: transfer ingredient to lower case
    ingredientLst = ingredientLst.lower()
    result["input"] = ingredientLst
       
    #Step 1: There is ':' in the string, split by ':' and get the 'item name'
    if "," in ingredientLst: 
      result['preparation'] = ' '.join(ingredientLst.split(',')[1:])
      ingredientStr = ingredientLst.split(',')[0]  
    else: 
      ingredientStr = ingredientLst
    # step 2: if we have '/'  in the string transfere the fraction to float
    if "/" in ingredientStr:
        # Case 1: e.g 1 2/3 g
        if len(list(ingredientStr.split()[0]))==1:
          temp =  int(list(ingredientStr.split('/')[0])[0]) + (int(list(ingredientStr.split('/')[0])[2])/int(list(ingredientStr.split('/')[1])[0]))
          ingredientStr = ingredientStr.replace(' '.join(ingredientStr.split()[:2]), str(temp) + '' )
        # Case 2: e.g 12/3 g, supposed to be 1 2/3 g
        elif len(list(ingredientStr.split()[0].split('/')[0]))==2:
          temp =  int(list(ingredientStr.split()[0].split('/')[0])[0]) + (int(list(ingredientStr.split()[0].split('/')[0])[1])/int(list(ingredientStr.split()[0].split('/')[1])[0]))
          ingredientStr = ingredientStr.replace(ingredientStr.split()[0],str(temp) + ' ' + ''.join(list(ingredientStr.split()[0].split('/')[1])[1:]))
         # Case 3: e.g 2/3 g
        else: 
          temp = int(list(ingredientStr.split()[0].split('/')[0])[0])/int(list(ingredientStr.split()[0].split('/')[1])[0])       
          ingredientStr = ingredientStr.replace(ingredientStr.split()[0],str(temp) + ' ' + ''.join(list(ingredientStr.split()[0].split('/')[1])[1:]))
        ingredientStr = ingredientStr
    # step 3: if we have a unit and a number 
    if ifUnit(ingredientStr)[0] == True and num_there(ingredientStr) == True:
      '''
      step 3.1: if we have '-', concantenate the qty range, get the qty, 
      unit and optional preparation 
      '''
      if "-" in ingredientStr:
        result["qty"] = ''.join(ingredientStr.split()[:3])
        result["unit"] = ingredientStr.split()[3]
        result["item"] = ' '.join(ingredientStr.split()[4:])
      
      #get the qty, unit and optional preparation directly 

      else:
        result["qty"] = ingredientStr.split()[0]
        result["unit"] = ingredientStr.split()[1]
        result["item"] = ' '.join(ingredientStr.split()[2:])
    # step 4: we have a unit but no number 
    elif ifUnit(ingredientStr)[0] == True and num_there(ingredientStr) == False:
      #step 4.1: get the unit directly 
        result["unit"] = ingredientStr
    # step 5: we do not  have a unit bu we have a number 
    elif ifUnit(ingredientStr)[0] == False and num_there(ingredientStr) == True:
      # step 5.1: the first part after ':' is a number e.g. 'eggs: 4 throughly beaten', obtain the qty and optional preparation 
      if num_there(list(ingredientStr.split()[0])[-1])==True:
        result["qty"] = ingredientStr.split()[0]
        result["item"] =' '.join(ingredientStr.split()[1:])
      # step 5.2: the first part after ':' is a number with a embedded unit e.g. 'milk: 4ml cold', obtain the qty, unit and optional preparation 
      else: 
        if ifUnit((re.sub(r"[-+]?(?:\d*\.\d+|\d+)", '', ingredientStr)).split()[0])[0] == True:
          result["qty"] = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", ingredientStr)[0]
          result["unit"] = (re.sub(r"[-+]?(?:\d*\.\d+|\d+)", '', ingredientStr)).split()[0]
          result["item"] = ' '.join((re.sub(r"[-+]?(?:\d*\.\d+|\d+)", '', ingredientStr)).split()[1:])
        else:
          result["qty"] = ingredientStr.split()[0]
          result["item"] = ' '.join(ingredientStr.split()[1:])
    # step 6: if the part after ":" does not have a number or unit, transfer the valur to 'preparation'
    else:
      result["item"] = ingredientStr
  
   
    return result


# In[244]:





# In[245]:


def IngredientTagger(ingredientLst):
    
    """
    input: ingredient in list
    output: ingredient tagger in list
    
    """
    result = []
    
    for i in ingredientLst:
        try:
            result.append(AlgeriaIngredientTagger(i))
            
        except:
            result.append({
        "qty":"",
        "unit":"",
        "item":i,
        "preparation":"",
        "input":i
    })
        
    return result

data['Ingredient list tagger'] = data["List of ingredients"].apply(lambda x: IngredientTagger(x))


# In[245]:





# In[245]:





# In[248]:


data['Ingredient list tagger'].head(20)[5]


# ### Save the data

# In[249]:


data.to_csv("/content/drive/MyDrive/DATA/INTERMEDIATE/Algeria.csv")


# In[247]:




