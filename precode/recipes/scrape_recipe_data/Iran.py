#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Iran

# In[1]:


# import packages
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import json
import re
from google_trans_new import google_translator 
import requests
from parsel import Selector
from pprint import pprint
import ast
import pandas as pd
from lxml import html
import requests
import pandas as pd
import numpy as np


# #### https://iran-cuisine.com/iranian-recipes/

# In[12]:


# 1. create a list to store all recipe htmls on one page
# initialize htmlDic to store the htmls of all recipes
htmlLst = []

def htmlOnePageSpider(category_url, lst):
    """
    input: category_url, the url of first page of the recipe web
    input: the initial htmlLst
    output: htmlDic with all recipe htmls on one page of one category
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'pll_language=en; ezosuibasgeneris-1=c38b0779-9c62-47c2-6cc7-33f2a13ba96a; ezds=ffid=1,w=1440,h=900; __qca=P0-868175274-1650165052857; _pbjs_userid_consent_data=3524755945110770; ezux_ifep_333915=true; ezoadgid_333915=-1; ezoref_333915=; ezoab_333915=mod58; ezopvc_333915=1; ezepvv=141; ezovid_333915=1755270437; lp_333915=https://iran-cuisine.com/iranian-recipes/; ezovuuidtime_333915=1652703592; ezovuuid_333915=9a1e33e8-b413-4c84-4c8b-33b8c1820fa3; active_template::333915=pub_site.1652703593; ezohw=w=1225,h=679; _ga_W40GTCHD53=GS1.1.1652703593.1.0.1652703593.0; _ga=GA1.2.1345797369.1650165053; _gid=GA1.2.817137236.1652703594; _clck=ksb0hg|1|f1i|0; _clsk=opn2vt|1652703593787|1|1|i.clarity.ms/collect; __gads=ID=4a6a2a08b3527288:T=1650165060:S=ALNI_MYKMHjjJYWJaq7c4zVogtiwLO9sRw; ezouspvh=550; __gpi=UID=000004380d67521a:T=1650165061:RT=1652703594:S=ALNI_MaSXYHvVabrbiFn68ittMHowwFdyw; MCPopupClosed=yes; ezux_lpl_333915=1652703595660|ef18e87d-e8c9-4d56-48c4-746c9dba299d|true; cto_bundle=WZXogV9NRjZpTlVoUGo5UnRjJTJCcVZUcGVJUjNFUFNzb2VPRGpVNE1Td09GbmhmcEtqamdhNGVSYXlOU2VxM3p1Q3hFYllvQTQ1Y3c0VUg2N2FvdndLS1d1bkltdHglMkJQZHRBbTNicUQ3VFBYeDZWZ2h0Sm9rTGppZFlFTnklMkZhNkEyeiUyRmRVdUtrNSUyRjJzVmRwYkp3UFdkdzlQVFpmNHJzN210TGxQN3lHb0p3ZHd6UVZ2dDc2QUh6YjQwYXJuOTFBc2VxQzB4NG0wcXRsS2daYVlyOWQlMkJ3cHdjRVN3JTNEJTNE; cto_bidid=kzhBX19iaTE1cG5VTjlmRnhGalRSbUh0M09oNjYyMnNSdU5NY2VxV0c4aCUyRnNmNnd3QXpVaDN4Rlo5TmpZbmdYMFlOU0R0OHBETWtMJTJGM3JFWkhodjIwSVNHamxoNHg1bWl4SkVLS29sTTlxOUhmY1lBJTJCejVyQXY4dTFzMmlsME50RzAxZndBQ2Z0ZWxLZUcxZyUyRlViU3YlMkJ3WTJnJTNEJTNE; ezouspvv=1380; ezouspva=4; ezux_et_333915=93; ezux_tos_333915=162',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    response = requests.get(category_url,headers=headers)
    sel = Selector(response.text)
    for i in sel.xpath('//div[@class="archive-item-share-icons"]/a[@class="archive-item-share-link aisl-twitter"]/@href'):
        lst.append(re.search('url=(.*)&text=',i.get()).group(1))
    
    return lst


# In[13]:


htmlOnePageSpider("https://iran-cuisine.com/iranian-recipes/", htmlLst)


# In[14]:


for i in range(2,6):
    htmlOnePageSpider("https://iran-cuisine.com/iranian-recipes/page/{}/".format(i), htmlLst)


# In[15]:


# the number of recipes we have in total
len(htmlLst)


# In[34]:


# 3. go through all recipe htmls and scrape the data we want

Irandata = {
    "Name of the recipe":[],
    "Total time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def IranSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'pll_language=en; ezosuibasgeneris-1=c38b0779-9c62-47c2-6cc7-33f2a13ba96a; ezds=ffid=1,w=1440,h=900; __qca=P0-868175274-1650165052857; _pbjs_userid_consent_data=3524755945110770; ezux_ifep_333915=true; ezoadgid_333915=-1; ezoref_333915=; ezoab_333915=mod58; ezopvc_333915=1; ezepvv=141; ezovid_333915=1755270437; lp_333915=https://iran-cuisine.com/iranian-recipes/; ezovuuidtime_333915=1652703592; ezovuuid_333915=9a1e33e8-b413-4c84-4c8b-33b8c1820fa3; active_template::333915=pub_site.1652703593; ezohw=w=1225,h=679; _ga_W40GTCHD53=GS1.1.1652703593.1.0.1652703593.0; _ga=GA1.2.1345797369.1650165053; _gid=GA1.2.817137236.1652703594; _clck=ksb0hg|1|f1i|0; _clsk=opn2vt|1652703593787|1|1|i.clarity.ms/collect; __gads=ID=4a6a2a08b3527288:T=1650165060:S=ALNI_MYKMHjjJYWJaq7c4zVogtiwLO9sRw; ezouspvh=550; __gpi=UID=000004380d67521a:T=1650165061:RT=1652703594:S=ALNI_MaSXYHvVabrbiFn68ittMHowwFdyw; MCPopupClosed=yes; ezux_lpl_333915=1652703595660|ef18e87d-e8c9-4d56-48c4-746c9dba299d|true; cto_bundle=WZXogV9NRjZpTlVoUGo5UnRjJTJCcVZUcGVJUjNFUFNzb2VPRGpVNE1Td09GbmhmcEtqamdhNGVSYXlOU2VxM3p1Q3hFYllvQTQ1Y3c0VUg2N2FvdndLS1d1bkltdHglMkJQZHRBbTNicUQ3VFBYeDZWZ2h0Sm9rTGppZFlFTnklMkZhNkEyeiUyRmRVdUtrNSUyRjJzVmRwYkp3UFdkdzlQVFpmNHJzN210TGxQN3lHb0p3ZHd6UVZ2dDc2QUh6YjQwYXJuOTFBc2VxQzB4NG0wcXRsS2daYVlyOWQlMkJ3cHdjRVN3JTNEJTNE; cto_bidid=kzhBX19iaTE1cG5VTjlmRnhGalRSbUh0M09oNjYyMnNSdU5NY2VxV0c4aCUyRnNmNnd3QXpVaDN4Rlo5TmpZbmdYMFlOU0R0OHBETWtMJTJGM3JFWkhodjIwSVNHamxoNHg1bWl4SkVLS29sTTlxOUhmY1lBJTJCejVyQXY4dTFzMmlsME50RzAxZndBQ2Z0ZWxLZUcxZyUyRlViU3YlMkJ3WTJnJTNEJTNE; ezouspvv=1380; ezouspva=4; ezux_et_333915=93; ezux_tos_333915=162',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    response = requests.get(recipe_url,headers=headers)
    sel = Selector(response.text)
    
    # scrape dictionary containing all information that we need
    content = json.loads(sel.xpath('//script[@type="application/ld+json"]/text()')[1].get())
    
    content['totalTime'] = sel.xpath('//li[@class="single-meta-cooking-time"]/span/text()').get()
    
    return content

def fillIranData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = IranSpider(html)
    dic['Name of the recipe'].append(content['name'])
    try:
        dic['Total time'].append(content['totalTime'])
    except:
        dic['Total time'].append('')
                
    try:
        dic['List of ingredients'].append(content['recipeIngredient'])
    except:
        dic['List of ingredients'].append('')
        
    try:
        dic['List of instructions'].append(content['recipeInstructions'])
    except:
        dic['List of instructions'].append('')
        
    try:
        dic['Number of servings'].append(content['recipeYield'])
    except:
        dic['Number of servings'].append('')
        
    try:
        dic['Category'].append(content['recipeCategory'])
    except:
        dic['Category'].append('')

# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillIranData(html,Irandata)
    except:
        time.sleep(5)

# convert data to dataframe
Iran = pd.DataFrame(Irandata)
print(Iran.shape)
Iran.head()


# In[35]:


Iran["Source"] = ["Web1" for i in range(len(Iran))]
Iran.head()


# In[36]:


# save dataset
Iran.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Iran.csv")


# In[ ]:





# In[ ]:




