#!/usr/bin/env python
# coding: utf-8

# In[16]:


import pandas as pd

from  util.spider import Spider
from util.user_agent import get_random_ua


# In[17]:


user_agent = get_random_ua()
custom_header = { #setup custom header because romania requires certain headers
        'referer': 'https://www.google.com/',
        'Accept-Language': '*',
        'Accept-Encoding': '*',
        'Accept': '*',
        'user-agent': user_agent}


# In[18]:


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
listing={'items': '//div[@class="css-ciggwi"]/a/@href', 'next': { 'next_page_str': '&page={}', 'type': 'url'}}
seeds = ['https://food.walla.co.il/recipes?kitchen-type=3']
available_json = {'xpath' : "normalize-space(//script[@type='application/ld+json'][contains(text(), 'recipeIngredient')])"}


# In[19]:


walla_spider= Spider('https://food.walla.co.il', seeds= seeds, listing =listing,attrs= attrs, available_json=available_json, header=custom_header)


# In[20]:


walla_spider.scrape_one_item('https://food.walla.co.il/item/3348492')


# In[21]:


result_list = walla_spider.start_scrape(max_pages=13) #max page is 13


# In[22]:


result_df = pd.DataFrame(result_list)


# In[23]:


result_df


# In[24]:


row_1=result_df.iloc[0]


# In[25]:


print(row_1['ingredients'])


# In[10]:


result_df.to_csv('data/israel/israel_walla.csv')


# In[ ]:





# In[ ]:




