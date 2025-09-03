#!/usr/bin/env python
# coding: utf-8

# In[8]:


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
listing={'items': '//div[@class="postInfo"]/a/@href', 'next': { 'next_page_str': '/page/{}', 'type': 'url'}}
seeds = [
        'https://www.lauralaurentiu.ro/retete-culinare/supe-ciorbe', 

        'https://www.lauralaurentiu.ro/retete-culinare/retete-de-salate', 

        'https://www.lauralaurentiu.ro/retete-culinare/retete-cu-paste',


        'https://www.lauralaurentiu.ro/retete-culinare/peste-fructe-de-mare',
        
        'https://www.lauralaurentiu.ro/retete-culinare/aperitive',


        'https://www.lauralaurentiu.ro/tag/retete-cu-carne',
        'https://www.lauralaurentiu.ro/tag/fara-carne',
        
        
        ]


# In[3]:


custom_header_template = { #setup custom header because this website requires certain headers
        'referer': 'https://www.lauralaurentiu.ro/retete-culinare/supe-ciorbe/ramen-cu-miso-reteta-video-de-supa-ramen-japoneza.html',
        'Accept-Language': '*',
        'Accept-Encoding': '*', #accept encoding for this website has to be *
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
        'sec-fetch-site' : 'same-origin',
        'cookie': '_ga=GA1.2.1978438003.1649681893; cb-enabled=enabled; _gid=GA1.2.1870821735.1650271735; ao-fpgad=%7B%22fpcRequired%22%3Afalse%2C%22checkTS%22%3A1650271735392%2C%22domain%22%3A%22lauralaurentiu.ro%22%7D; __gads=ID=3dd1ab9c6ddf9fc9-2289c17b2ed20094:T=1649681893:RT=1650271783:S=ALNI_MbZpRpmkjwza5LhQQ1HkGR0H4wMjQ',
        'user-agent': ''}


# In[4]:


laural_spider = Spider('https://www.lauralaurentiu.ro', seeds, listing,attrs, available_json=available_json,header=custom_header_template)


# In[5]:


laural_spider.scrape_one_item('https://www.lauralaurentiu.ro/retete-culinare/supe-ciorbe/ramen-cu-miso-reteta-video-de-supa-ramen-japoneza.html')


# In[6]:


result_list = laural_spider.start_scrape(multithread=False)


# In[9]:


result_df = pd.DataFrame(result_list)


# In[10]:


result_df


# In[11]:


result_df.to_csv('data/romania/romania_lauralaurentiu.csv')


# In[ ]:




