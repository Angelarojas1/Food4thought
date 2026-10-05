#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from util.bulgaria.govtach import Govtach


# In[2]:


attrs = {
        'name'       :  'name',
        'ingredients':  'recipeIngredient',
        'total_time':   'totalTime',
        'instructions': 'recipeInstructions',
        'servings':     'recipeYield',
        'category':     'recipeCategory',
        'prep_time':    'prepTime',
        'cook_time':    'cookTime',
}
available_json = {'xpath' : "normalize-space(//script[@type='application/ld+json'][contains(text(), 'recipeIngredient')])"}
listing={'items': '//div[@class="rprev"]/div/a[2]/@href', 'next': { 'next_page_str': '?pn={}', 'type': 'random_pages' , 'max_items': 10000, 'items_per_page': 24, 'max_pages': 2120,}}
seeds = ['https://recepti.gotvach.bg/{page}?n=1']


# In[3]:


govtach_spider = Govtach('https://recepti.gotvach.bg/', seeds=seeds, listing=listing, attrs=attrs, available_json=available_json)


# In[4]:


govtach_spider.scrape_one_item('https://recepti.gotvach.bg/r-213251-%D0%9A%D0%B0%D0%BB%D0%BF%D0%B0%D0%B7%D0%B0%D0%BD%D1%81%D0%BA%D0%B0_%D0%B1%D0%B0%D0%BD%D0%B8%D1%86%D0%B0_%D0%BE%D1%82_%D1%81%D1%82%D0%B0%D1%80_%D1%85%D0%BB%D1%8F%D0%B1')


# In[5]:


results_list = govtach_spider.start_scrape()


# In[6]:


result_df = pd.DataFrame(results_list)


# In[9]:


result_df


# In[12]:


result_df.iloc[2577]


# In[13]:


filter = result_df["name"] != ""


# In[14]:


filter


# In[15]:


new_df = result_df[filter]


# In[16]:


new_df.shape


# In[ ]:




