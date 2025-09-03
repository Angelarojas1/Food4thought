#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Armenia

# In[1]:


from util.spider import Spider
import pandas as pd


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
available_json = {'xpath' : "normalize-space(//script[@type='application/ld+json'][contains(text(), 'recipeIngredient')])"}
seeds = ['https://thearmeniankitchen.com/category/main-dishes', 

        'https://thearmeniankitchen.com/category/soups', 
        
        'https://thearmeniankitchen.com/category/appetizers',

        'https://thearmeniankitchen.com/category/salads',

        'https://thearmeniankitchen.com/category/grain-legumes',


        'https://thearmeniankitchen.com/category/vegetables',



        'https://thearmeniankitchen.com/category/fruits',

        'https://thearmeniankitchen.com/category/herbs-spices',



        'https://thearmeniankitchen.com/category/breads-boregs',



        'https://thearmeniankitchen.com/category/eggs-cheese-yogurt',


        'https://thearmeniankitchen.com/category/meatless-lenten-dishes',


        
          ]
listing={'items': '//div[@class="blog-grid-wrap"]//h2[@class="entry-title"]/a/@href', 'next': { 'next_page_str': '/page/{}', 'type': 'url'}}


# In[3]:


custom_header_template = { #setup custom header because this website requires certain headers
        'referer': 'https://thearmeniankitchen.com/',
        'Accept-Language': '*',
        'Accept-Encoding': '*', 
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-fetch-site' : 'same-origin',
        #'cookie': '_ga=GA1.2.1978438003.1649681893; cb-enabled=enabled; _gid=GA1.2.1870821735.1650271735; ao-fpgad=%7B%22fpcRequired%22%3Afalse%2C%22checkTS%22%3A1650271735392%2C%22domain%22%3A%22lauralaurentiu.ro%22%7D; __gads=ID=3dd1ab9c6ddf9fc9-2289c17b2ed20094:T=1649681893:RT=1650271783:S=ALNI_MbZpRpmkjwza5LhQQ1HkGR0H4wMjQ',
        'user-agent': ''}


# In[4]:


armenia_spider = Spider('https://thearmeniankitchen.com', seeds, listing,attrs, available_json=available_json, header=custom_header_template)


# In[5]:


armenia_spider.scrape_one_item('https://thearmeniankitchen.com/leeks-peas-and-sorrel-soup/') #1st variation of recipeJSON


# In[6]:


armenia_spider.scrape_one_item('https://thearmeniankitchen.com/lamb-shank-gouvedge/') #2nd variation of recipe JSON


# In[8]:


result_list = armenia_spider.start_scrape()


# In[9]:


len(result_list)


# In[10]:


copy_result_list = result_list.copy()


# In[12]:


res_df = pd.DataFrame(copy_result_list)


# In[13]:


res_df


# In[17]:


nan_value = float("NaN")


# In[18]:


res_df.replace("", nan_value, inplace=True)


# In[19]:


res_df.tail()


# In[20]:


res_df.dropna(subset=['name'], inplace=True)


# In[22]:


res_df


# In[23]:


res_df.to_csv('data/armenia/armeniankitchen.csv')


# In[ ]:




