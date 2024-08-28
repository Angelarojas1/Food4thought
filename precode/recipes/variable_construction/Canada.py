#!/usr/bin/env python
# coding: utf-8

# #### Variable constructions of Canada

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
from nltk.stem.wordnet import WordNetLemmatizer


# In[2]:


# import dataset
data = pd.read_csv("/Users/xixi/Dropbox/food4thought/data/final/Canada.csv")
data.drop(['Unnamed: 0'],axis=1,inplace=True)

data.head()


# In[7]:


# convert string repretention of list to a list
data['Ingredient list tagger'] = data['Ingredient list tagger'].apply(lambda x:ast.literal_eval(x))


# In[3]:


data.shape


# ### Recipes with inactive verbs

# In[9]:


# convert string repretention of list to a list
def convert(instructionLst):
    if instructionLst == instructionLst:
        return ast.literal_eval(instructionLst)
    else:
        return []
    
data['List of instructions'] = data['List of instructions'].apply(lambda x:convert(x))


# In[12]:


def extractVerb(instruction):
    """
    input: instruction in English
    output: the verb in the instruction with the pretense form
    
    """
    splitInstruction = ''
    
    # split the instruction by minutes/hours
    for word in ["minute","minutes","hour","hours",'day','days']:
        if word in instruction:
            splitInstruction = instruction.split(word)[0]+word
        
    # apply natural language processing to analyze the sentence
    tokens = word_tokenize(splitInstruction) 
    text = Text(tokens) 
    tags = pos_tag(text) 
    
    # extract verbs
    verb = ""
    verb_tag = 0
    # if there is verb in the sentence
    for pairs in tags: 
        if pairs[1] == 'VB' or pairs[1] =='VBP' or pairs[1] == 'VBN' or pairs[1] =='VBG':
            verb = pairs[0]
            verb_tag = 1
            
    if verb_tag == 0:
        for pairs in tags:
            if pairs[1] == 'NNP':
                verb = pairs[0]
    
    return WordNetLemmatizer().lemmatize(verb,'v').lower()

def verbList(instruction):
    """
    input: instruction list
    output: verb lists
    
    """
    
    # step 1: find sentences with time
    # initialize the list to store instructions with time
    timeInstruction = []
    instructionLst = []
    for i in instruction:
        try:
            instructionLst.append(i['text'])
        except:
            instructionLst.append('')
    
    for instruction in instructionLst:
        if isinstance(instruction, dict):
            instruction = instruction['text'].lower()
        else:
            instruction = instruction.lower()
            
        for word in ["minute","minutes","hour","hours",'day','days']:
            if word in instruction:
                timeInstruction.append(instruction)
            
    # step 1: translate instructions related to time to English
    timeInstructionEng = timeInstruction
    
    # step 2: initialize a list to store verbs
    verbs = []
    
    for instruction in timeInstructionEng:
        verbs.append(extractVerb(instruction))
        
    return verbs

data['verbList'] = data['List of instructions'].apply(lambda x: verbList(x))
data.head()


# In[13]:


inactiveList = ['bake',  'simmer', 'cool', 'take', 'stand', 'add', 'boil', 'bring', 'leave', 'let', 'soak', 
                'keep', 'close', 'rest', 'remain', 'cook', 'cover', 'pour']


# In[14]:


data['inactiveVerbs'] = data['verbList'].apply(lambda x: len(list(set(inactiveList) & set(x))) > 0)
data.head()


# #### Total Time

# In[4]:


# extract numbers from time columns
data['Cook time'] = data['Cook time'].str.extract('(\d+)')
data['Prep time'] = data['Prep time'].str.extract('(\d+)')

# replace those with nan values
data['Cook time'] = data['Cook time'].replace(np.nan,0)
data['Prep time'] = data['Prep time'].replace(np.nan,0)

# transfer object type to int type
data[['Cook time','Prep time']] = data[['Cook time','Prep time']].astype(int)


# In[5]:


data['Total time'] = data['Cook time']+data['Prep time']
data['Total time'] = data['Cook time'].replace(0,np.nan)
data.head()


# In[6]:


data['Total time'].describe()


# ### Number of ingredients

# In[3]:


data['List of ingredients'] = data['List of ingredients'].apply(lambda x:ast.literal_eval(x))
data['Number of ingredients_raw'] = data['List of ingredients'].apply(lambda x: len(x))
data.head()


# In[8]:


def calNumIngredients(IngredientLstTagger):
    """
    input: ingredient list tagger in English
    output: the number of ingredients removing duplicates
    
    """
    coreLst = []
    for i in range(len(IngredientLstTagger)):
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

# In[9]:


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


# In[10]:


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


# In[11]:


data['Core ingredient'] = data['Ingredient list tagger'].apply(lambda x: [i['item'] for i in x])
data['Number of spices'] = data['Core ingredient'].apply(lambda x: calNumSpices(x))
data.head()


# ### Get the amount of sugar

# In[12]:


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
        if "sugar" in dic["item"] and dic["unit"] != "" and dic["unit"] in unitMeasureDic:
            sugarAmount += unitMeasureDic[unitInLst(dic["unit"])]*float(dic["qty"])
            
    for dic in ingredientLstTagger:
        if "sugar" in dic["item"] and sugarAmount == 0:
            sugarAmount = np.nan
            
    return sugarAmount 

data["sugarAmount in tsp(ingredient tagger)"] = data['Ingredient list tagger'].apply(lambda x: sugarAmount(x))


# In[13]:


data['sugarAmount in tsp(ingredient tagger)'].describe()


# #### Save the data

# In[15]:


data.to_csv("/Users/xixi/Dropbox/food4thought/data/final/Canada.csv")


# In[ ]:




