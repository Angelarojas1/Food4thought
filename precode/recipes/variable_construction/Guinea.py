#!/usr/bin/env python
# coding: utf-8

# ### Variable constructions for Guinea

# In[1]:


#pip install openpyxl
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
from nltk.stem.wordnet import WordNetLemmatizer


# In[12]:


# import dataset
data = pd.read_csv("/Users/xixi/Dropbox/food4thought/data/intermediate/Guinea.csv")
data.drop(['Unnamed: 0', 'Unnamed: 0.1'],axis=1,inplace=True)

data.head()


# In[13]:


# convert string repretention of list to a list
data['Ingredient list tagger'] = data['Ingredient list tagger'].apply(lambda x:ast.literal_eval(x))


# In[14]:


data.shape


# #### Total time

# In[15]:


def getTime(string):
    digits = re.findall(r'\d+',string)
    
    if len(digits) == 1:
        if "min" in string:
            return float(digits[0])
        elif "h" in string:
            return float(digits[0])*60
    elif len(digits) == 0:
        return float("nan")
    else:
        return float(digits[0])*60+float(digits[1])


# In[16]:


# extract numbers from time columns
data['Prep time'] = data['Prep time'].apply(lambda x: getTime(x))
data['Cook time'] = data['Cook time'].apply(lambda x: getTime(x))
data['Total time'] = data['Prep time'] + data['Cook time']


# In[17]:


data.head()


# ### Number of ingredients

# In[18]:


data['List of ingredients'] = data['List of ingredients'].apply(lambda x:ast.literal_eval(x))
data['Number of ingredients_raw'] = data['List of ingredients'].apply(lambda x: len(x))
data.head()


# In[19]:


def calNumIngredients(IngredientLstTagger):
    """
    input: ingredient list tagger in English
    output: the number of ingredients removing duplicates
    
    """
    coreLst = []
    for i in range(len(IngredientLstTagger)):
        if IngredientLstTagger[i]['item'] == '':
            coreLst.append(IngredientLstTagger[i]['input'])
        elif IngredientLstTagger[i]['item'] != None:
            coreLst.append(IngredientLstTagger[i]['item'])
    
    # remove duplicated ingredients
    compareLst = []
    compareLst.extend(coreLst)
    
    for i in coreLst:
        count = 0
        for j in compareLst:
            if fuzz.ratio(i.lower(),j.lower()) >= 90:
                count += 1
        if count > 1:
            compareLst.remove(i)
               
    return len(compareLst)

data['Number of ingredients'] = data['Ingredient list tagger'].apply(lambda x: calNumIngredients(x))
data.head()


# ### Number of spices

# In[20]:


# create a list to store all spice

# import spice data
spice = pd.read_excel("/Users/xixi/Dropbox/food4thought/data/intermediate/roster_spices_edited.xlsx", engine='openpyxl', sheet_name="Spices").dropna(how='all')
mixes = pd.read_excel("/Users/xixi/Dropbox/food4thought/data/intermediate/roster_spices_edited.xlsx", engine='openpyxl', sheet_name="Mixes").dropna(how='all')


# drop first row as it's empty
spice = spice.iloc[1:,:]
spice.head()

# add spice to list
spiceLst = []
for i in range(1,len(spice)+1):
    spiceLst.append(spice.loc[i,"Spice"])
    
# add mixes to list
for i in range(len(mixes)):
    spiceLst.append(mixes.loc[i,"Name"])
    
# converts all uppercase characters to lowercase characters
spiceLstLower = []
for i in spiceLst:
    spiceLstLower.append(i.lower())


# In[21]:


# count the number of spices
# algorithm: fuzzy match
def calFuzzScores(ingredient):
    """
    ingredient: one ingredient in English
    output: a list of fuzz scores for the ingredient, [a,b],
    where a is the fuzz scores for the full ingredient, b is the highest fuzz scores for splited ingredients
    
    """
    # initialize the output list
    fuzzScore = []
    
    # Step 1: compute partio ratio for the full ingredient
    fullScore = []
    for ele in spiceLstLower:
        fullScore.append(fuzz.partial_ratio(ingredient.lower(),ele))
    
    fuzzScore.append(max(fullScore))
    
    # exclude salt
    if "salt" == ingredient.lower() or "water" == ingredient.lower() or "lemon" == ingredient.lower():
        fuzzScore[0] = 0

    # Step 2: split ingredients into different parts, compute ratio for each part and return the highest one
    splitScore = []
    for i in ingredient.split(" "):
        tempScore = []
        for ele in spiceLstLower:
            tempScore.append(fuzz.ratio(i.lower(),ele))
        
        splitScore.append(max(tempScore))
        
    fuzzScore.append(max(splitScore))
    
    return fuzzScore   

def calNumSpices(content):
    """
    content: list of ingredients in English
    output: the number of spices
    
    """
        
    spiceDic = {}
    for i in content:
        # count the ingredient as spices if FuzzScore is larger than 90
        if calFuzzScores(i)[0]  >= 90 or calFuzzScores(i)[1] >= 90:
            spiceDic[i] = calFuzzScores(i) 
            
    # remove duplicated spices
    keyLst = []
    for key in spiceDic:
        keyLst.append(key)
    
    compareLst = keyLst

    for i in keyLst:
        count = 0
        for j in compareLst:
            if fuzz.partial_ratio(i.lower(),j.lower()) >= 90:
                count += 1
        if count > 1:
            compareLst.remove(i)
            del spiceDic[i]     
    
    return len(spiceDic)  


# In[22]:


data['Core ingredient'] = data['Ingredient list tagger'].apply(lambda x: [i['item'] for i in x if i['item'] != None])
data['Number of spices'] = data['Core ingredient'].apply(lambda x: calNumSpices(x))
data.head()


# ### Get the amount of sugar

# In[23]:


def unitInLst(unitTagger):
    """
    input: unit from ingredient tagger
    
    output: unit from the unit list that is most similar to the unit
    
    """
    
    # import unit data
    unitData = pd.read_excel("/Users/xixi/Dropbox/food4thought/material/unit_data/roster_unit.xlsx", engine='openpyxl')
    unit = unitData.dropna(how='all')

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
    unitMeasure = pd.read_excel("/Users/xixi/Dropbox/food4thought/material/unit_data/Unit standard.xlsx", engine='openpyxl')
    unitMeasureDic = dict(unitMeasure.dropna(how='all').values)
        
    for dic in ingredientLstTagger:
        if dic["item"] != None and "sugar" in dic["item"] and dic["unit"] != "" and dic["unit"] in unitMeasureDic:
            sugarAmount += unitMeasureDic[unitInLst(dic["unit"])]*float(dic["qty"])
            
    for dic in ingredientLstTagger:
        if dic["item"] != None and "sugar" in dic["item"] and sugarAmount == 0:
            sugarAmount = np.nan
            
    return sugarAmount 

data["sugarAmount in tsp(ingredient tagger)"] = data['Ingredient list tagger'].apply(lambda x: sugarAmount(x))


# In[24]:


data['sugarAmount in tsp(ingredient tagger)'].describe()


# #### Save the data

# In[25]:


data.to_csv("/Users/xixi/Dropbox/food4thought/data/final/Guinea.csv")


# In[ ]:





# In[ ]:




