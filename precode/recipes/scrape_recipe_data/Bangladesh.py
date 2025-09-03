#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Bangladesh

# In[1]:


from util.bangladesh.thebangladeshikitchen import BangladeshiKitchen
import pandas as pd


# In[2]:


attrs = {
        'name':         'normalize-space(//span[@property="v:title"]//text())',
        'ingredients':  '//div[@id="recipe_content_pro"]/ul//li//text()',
        'total_time':   'normalize-space(//div[@class="time-single-pro"]/span//text())',
        'instructions': '//div[@id="recipe_content_pro"]/ol//li//text()',
        'servings':     '',
        'category':     'normalize-space(//div[@id="category-talisa-pro"]//li//text())',
        'prep_time':    '',
        'cook_time':    '',
}

listing={'items': '//h4[@class="menu-title"]/a/@href', 'next': { 'next_page_str': 'page/{}/', 'type': 'url'}}
seeds = ['https://www.thebangladeshikitchen.com/recipes/']
available_json= {}


# In[3]:


bangladesh_spider = BangladeshiKitchen('https://www.thebangladeshikitchen.com', seeds= seeds, listing =listing,attrs= attrs, available_json=available_json)


# In[4]:


bangladesh_spider.scrape_one_item('https://www.thebangladeshikitchen.com/recipes/chicken-pakora/')


# In[5]:


bangladesh_spider.scrape_one_item('https://www.thebangladeshikitchen.com/recipes/kata-moshlar-mangsho-meat-with-whole-spices/')


# In[6]:


result_list = bangladesh_spider.start_scrape()


# In[7]:


result_df = pd.DataFrame(result_list)


# In[8]:


result_df


# In[9]:


result_df.to_csv('data/bangladesh/bangladesh.csv')


# In[ ]:




