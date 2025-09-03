#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import json
import requests
import random
from lxml import html
import re

from  util.spider import Spider
# from util.http_utility import get_http_headers
# from util.user_agent import get_random_ua


# In[2]:


attrs = {
        'name':         'name',
        'ingredients':  'recipeIngredient',
        'total_time':   'totalTime',
        'instructions': 'recipeInstructions',
        'servings':     'recipeYield',
        'category':     'recipeCategory',
        'prep_time':    'prepTime',
        'cook_time':    'cookTime',
}
listing={'items': '//div[contains(@class,"fd-tile fd-recipe")]//h2//a/@href', 'next': { 'next_page_str': '?pn={}', 'type': 'url'}}
seeds = ['https://www.food.com/topic/new-zealand']
available_json = {'xpath' : "normalize-space(//script[@type='application/ld+json'][contains(text(), 'recipeIngredient')])"}


# In[3]:


nz_spider =  Spider('https://www.food.com/', seeds= seeds, listing =listing,attrs= attrs, available_json=available_json)


# In[4]:


nz_spider.scrape_one_item('https://www.food.com/recipe/fluffernutter-181487')


# In[5]:


result_list = nz_spider.start_scrape(max_pages=130) #max page is only 130


# In[6]:


result_df = pd.DataFrame(result_list)


# In[7]:


result_df


# In[8]:


result_df.to_csv('data/new-zealand/food_com_nz.csv')


# In[ ]:




