#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd

from  util.spider import Spider


# In[16]:


OUTPUT = '~/Dropbox/food4thought/data/raw/'


# # Scrape Japan - Delishkitchen
# 
# 
# 

# https://delishkitchen.tv/

# In[7]:


attrs = {
        'name'       :         'name',
        'ingredients':  'recipeIngredient',
        'total_time':   'totalTime',
        'instructions': 'recipeInstructions',
        'servings':     'recipeYield',
        'category':     'recipeCategory',
        'prep_time':    'prepTime',
        'cook_time':    'cookTime',
}
listing={'items': '//ul[@class="columns with-max-three"]//div[contains(@class,"delish-renewal-recipe-item-card")]//a/@href', 'next': { 'next_page_str': '&page={}', 'type': 'url'}}
#seeds = ['https://delishkitchen.tv/categories/19878?annotation_kind_ids=432'] #for testing 
seeds = ['https://delishkitchen.tv/categories/19878?annotation_kind_ids=432', 'https://delishkitchen.tv/categories/655?annotation_kind_ids=432', 'https://delishkitchen.tv/categories/17359', 'https://delishkitchen.tv/categories/753?annotation_kind_ids=432', 'https://delishkitchen.tv/categories/17304?annotation_kind_ids=432', 'https://delishkitchen.tv/categories/14500?annotation_kind_ids=432',  ]
available_json = {'xpath' : "normalize-space(//script[@type='application/ld+json'][contains(text(), 'recipeIngredient')])"}


# In[8]:


delishtv_spider= Spider('https://delishkitchen.tv', seeds= seeds, listing =listing,attrs= attrs, available_json=available_json)


# check case when there's no cooking time:

# In[9]:


delishtv_spider.scrape_one_item('https://delishkitchen.tv/recipes/243458362560217385')


# In[10]:


delishtv_spider.scrape_one_item('https://delishkitchen.tv/recipes/216142397518644383')


# In[11]:


result_list = delishtv_spider.start_scrape(max_pages=500) #max page is 500


# In[12]:


result_df = pd.DataFrame(result_list)


# In[13]:


result_df.head()


# In[17]:


result_df.to_csv(OUTPUT+'japan_delishkitchen.csv')


# In[ ]:




