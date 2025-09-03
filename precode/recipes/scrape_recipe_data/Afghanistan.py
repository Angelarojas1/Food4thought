#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Afghanistan
# 

# In[3]:


from util.spider import Spider
import pandas as pd


# In[4]:


attrs = {
        'name':         'normalize-space(//h2[@itemprop="name"])',
        'ingredients':  '//li[@class="ingredient"]//text()',
        'total_time':   '//li[@class="ready-in"]/span[@class="value"]//text()',
        'instructions': '//p[@class="instructions"]//text()',
        'servings':     '//li[@class="servings"]/span[@class="value"]//text() | //li[@class="yield"]/span[@class="value"]//text() ',
        'category':     '',
        'prep_time':    '//li[@class="prep-time"]/span[@class="value"]//text()',
        'cook_time':    '//li[@class="cook-time"]/span[@class="value"]//text()',
}

listing={'items': '//div[@class="recipe-info"]/h2/a/@href', 'next': { 'next_page_str': 'page/{}/', 'type': 'url'}}
seeds = {'http://www.afghankitchenrecipes.com/recent-recipes/'}
available_json= {}


# In[5]:


#setup variables

custom_header = { #setup custom header because romania requires certain headers
        'referer': 'http://www.afghankitchenrecipes.com/recipe/norinj-palau-rice-with-orange/',
        'Accept-Language': '*',
        'Accept-Encoding': '*',
        'Accept': '*',
        'user-agent':''}
afghan_spider = Spider('http://www.afghankitchenrecipes.com', seeds= seeds, listing =listing,attrs= attrs, header=custom_header, available_json=available_json)


# In[6]:


afghan_spider.scrape_one_item('http://www.afghankitchenrecipes.com/recipe/norinj-palau-rice-with-orange/') #try out scraping one item


# In[7]:


afghan_spider.scrape_one_item('http://www.afghankitchenrecipes.com/recipe/nan-e-parata-sweet-fried-bread/') #try out scraping one item


# In[8]:


result_list = afghan_spider.start_scrape()


# In[9]:


result_df = pd.DataFrame(result_list)
result_df.head()


# In[ ]:


result_df.to_csv('/Users/xixi/Dropbox/food4thought/data/raw/Afghanistan.csv')

