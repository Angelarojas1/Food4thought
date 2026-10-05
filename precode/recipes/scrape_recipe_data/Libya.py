#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Libya

# In[73]:


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


# #### https://www.justfood.tv/%D9%88%D8%B5%D9%81%D8%A7%D8%AA/%D8%A7%D9%84%D8%A8%D9%84%D8%AF/%D8%A7%D9%83%D9%84%D8%A7%D8%AA-%D9%84%D8%A8%D9%86%D8%A7%D9%86%D9%8A%D8%A9/50

# In[74]:


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
        'cookie':'UserIdCookieHttponly=a7e3c56a-137a-4648-9ad3-9520535cd857; UserIdCookieHttponlyExpDate=4/1/2023 6:33:47 PM; _ga=GA1.2.1792171615.1648827229; _fbp=fb.1.1648827229010.621556014; _em_vt=d270c7b7-a949-4909-81fd-cdb483a885a8-17fe57eece1-655ea44c; _em_gc=US; _em_mb=0; __gads=ID=0648f930c0fd88b8:T=1648827230:S=ALNI_MaZPA6NVPyj7zKoE1IknyWRT0qnCQ; _cb_ls=1; _cb=B86uyRDfJRdqDwZQVO; NpsGuid=0a9307e8-cdba-4679-955b-87db49a59822; NpsCreateDate=1648827241; _gcl_au=1.1.1308101560.1648827244; ASP.NET_SessionId=w1yjrfkocf1qrp1tlqsvhmj2; _em_dmp=1652635455750; _chartbeat2=.1641849490991.1652635457241.0000000000000001.C0LeTqh5kFvBLXtmxBZ9aoRCIXf9_.1; permutive-id=07e8e3e5-2095-4cb6-8dde-058b1491fb4e; _gid=GA1.2.2057239003.1652808755; _em_c3=1; _em_vi=a3edced0-e5b4-4cda-b9f9-80598bb979f7-180d31427cb-692764d8; _em_ft=1652808755147; _em_scf=[]; __gpi=UID=0000044cdd15c596:T=1649198253:RT=1652808756:S=ALNI_MZCZpX0IjN9liRcu9tbHQW73FDaZA; _gat=1; _em_lt=1652808825967; _em_pc=2; pv_per_sess=30; datadome=TWq7WMgvsaOAi4abmoryM.CBQtjZ0CR1izR_qCSStO0VOtXJ9aIMBFrZGiJ0DFn8qtfEO-M~WwjvejsHC8QwWUWEULxcB.3wSwv23PGjMp0-QETCM6KWKIFLJ8DCXV4',
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
    for i in sel.xpath('//div[@class="inlined-img lstimg"]/a/@href'):
        lst.append("https://www.justfood.tv/"+i.get())
    
    return lst


# In[75]:


htmlOnePageSpider("https://www.justfood.tv/%D9%88%D8%B5%D9%81%D8%A7%D8%AA/%D8%A7%D9%84%D8%A8%D9%84%D8%AF/%D8%A7%D9%83%D9%84%D8%A7%D8%AA-%D9%84%D8%A8%D9%86%D8%A7%D9%86%D9%8A%D8%A9/50", htmlLst)


# In[12]:


for i in range(2,11):
    htmlOnePageSpider("https://www.justfood.tv/%D9%88%D8%B5%D9%81%D8%A7%D8%AA/%D8%A7%D9%84%D8%A8%D9%84%D8%AF/%D8%A7%D9%83%D9%84%D8%A7%D8%AA-%D9%84%D8%A8%D9%86%D8%A7%D9%86%D9%8A%D8%A9/50/{}".format(i), htmlLst)


# In[13]:


# the number of recipes we have in total
len(htmlLst)


# In[70]:


headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'UserIdCookieHttponly=a7e3c56a-137a-4648-9ad3-9520535cd857; UserIdCookieHttponlyExpDate=4/1/2023 6:33:47 PM; _ga=GA1.2.1792171615.1648827229; _fbp=fb.1.1648827229010.621556014; _em_vt=d270c7b7-a949-4909-81fd-cdb483a885a8-17fe57eece1-655ea44c; _em_gc=US; _em_mb=0; __gads=ID=0648f930c0fd88b8:T=1648827230:S=ALNI_MaZPA6NVPyj7zKoE1IknyWRT0qnCQ; _cb_ls=1; _cb=B86uyRDfJRdqDwZQVO; NpsGuid=0a9307e8-cdba-4679-955b-87db49a59822; NpsCreateDate=1648827241; _gcl_au=1.1.1308101560.1648827244; ASP.NET_SessionId=w1yjrfkocf1qrp1tlqsvhmj2; _em_dmp=1652635455750; _chartbeat2=.1641849490991.1652635457241.0000000000000001.C0LeTqh5kFvBLXtmxBZ9aoRCIXf9_.1; permutive-id=07e8e3e5-2095-4cb6-8dde-058b1491fb4e; _gid=GA1.2.2057239003.1652808755; _em_c3=1; _em_vi=a3edced0-e5b4-4cda-b9f9-80598bb979f7-180d31427cb-692764d8; _em_ft=1652808755147; _em_scf=[]; __gpi=UID=0000044cdd15c596:T=1649198253:RT=1652808756:S=ALNI_MZCZpX0IjN9liRcu9tbHQW73FDaZA; _gat=1; _em_lt=1652808825967; _em_pc=2; pv_per_sess=30; datadome=TWq7WMgvsaOAi4abmoryM.CBQtjZ0CR1izR_qCSStO0VOtXJ9aIMBFrZGiJ0DFn8qtfEO-M~WwjvejsHC8QwWUWEULxcB.3wSwv23PGjMp0-QETCM6KWKIFLJ8DCXV4',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
response = requests.get('https://www.justfood.tv/%D9%88%D8%B5%D9%81%D8%A7%D8%AA/3775/%D8%B7%D8%B1%D9%8A%D9%82%D8%A9-%D8%B9%D9%85%D9%84-%D8%B4%D9%8A%D8%B4-%D8%B7%D8%A7%D9%88%D9%88%D9%82-%D8%A8%D8%A7%D9%84%D9%84%D9%8A%D9%85%D9%88%D9%86-%D9%88%D8%A7%D9%84%D9%82%D8%B1%D9%81%D8%A9',headers=headers)
sel = Selector(response.text)


# In[72]:


sel


# In[71]:


sel.xpath('//div[@itemprop="ingredients"]/div/text() |//span[@itemprop="recipeIngredient"]/text()')


# In[51]:


sel.xpath('//span[@itemprop="recipeIngredient"]/text()')


# In[53]:


# 3. go through all recipe htmls and scrape the data we want

Libyadata = {
    "Name of the recipe":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[]
}

def LibyaSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'UserIdCookieHttponly=a7e3c56a-137a-4648-9ad3-9520535cd857; UserIdCookieHttponlyExpDate=4/1/2023 6:33:47 PM; _ga=GA1.2.1792171615.1648827229; _fbp=fb.1.1648827229010.621556014; _em_vt=d270c7b7-a949-4909-81fd-cdb483a885a8-17fe57eece1-655ea44c; _em_gc=US; _em_mb=0; __gads=ID=0648f930c0fd88b8:T=1648827230:S=ALNI_MaZPA6NVPyj7zKoE1IknyWRT0qnCQ; _cb_ls=1; _cb=B86uyRDfJRdqDwZQVO; NpsGuid=0a9307e8-cdba-4679-955b-87db49a59822; NpsCreateDate=1648827241; _gcl_au=1.1.1308101560.1648827244; ASP.NET_SessionId=w1yjrfkocf1qrp1tlqsvhmj2; _em_dmp=1652635455750; _chartbeat2=.1641849490991.1652635457241.0000000000000001.C0LeTqh5kFvBLXtmxBZ9aoRCIXf9_.1; permutive-id=07e8e3e5-2095-4cb6-8dde-058b1491fb4e; _gid=GA1.2.2057239003.1652808755; _em_c3=1; _em_vi=a3edced0-e5b4-4cda-b9f9-80598bb979f7-180d31427cb-692764d8; _em_ft=1652808755147; _em_scf=[]; __gpi=UID=0000044cdd15c596:T=1649198253:RT=1652808756:S=ALNI_MZCZpX0IjN9liRcu9tbHQW73FDaZA; _gat=1; _em_lt=1652808825967; _em_pc=2; pv_per_sess=30; datadome=TWq7WMgvsaOAi4abmoryM.CBQtjZ0CR1izR_qCSStO0VOtXJ9aIMBFrZGiJ0DFn8qtfEO-M~WwjvejsHC8QwWUWEULxcB.3wSwv23PGjMp0-QETCM6KWKIFLJ8DCXV4',
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
    content = {}
    
    content['name'] = sel.xpath('//label[@itemprop="name"]/text()').get()
    content['prepTime'] = sel.xpath('//meta[@itemprop="prepTime"]/@content').get()
    content['cookTime'] = sel.xpath('//meta[@itemprop="cookTime"]/@content').get()
    content['recipeYield'] = sel.xpath('//b[@itemprop="recipeYield"]/text()').get()
    
    lst = []
    for i in sel.xpath('//div[@itemprop="ingredients"]/div/text() |//span[@itemprop="recipeIngredient"]/text()'):
        lst.append(i.get())
    content['recipeIngredient'] = lst
    
    lst = []
    for i in sel.xpath('//span[@itemprop="recipeInstructions"]/text() |//span[@itemprop="recipeInstructions"]/span/text()'):
        lst.append(i.get())
    content['recipeInstructions'] = lst
    
    
    return content

def fillLibyaData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = LibyaSpider(html)
    dic['Name of the recipe'].append(content['name'])
    try:
        dic['Prep time'].append(content['prepTime'])
    except:
        dic['Prep time'].append('')
                
    try:
        dic['Cook time'].append(content['cookTime'])
    except:
        dic['Cook time'].append('')
    
    try:
        dic['List of ingredients'].append(content['recipeIngredient'])
    except:
        dic['List of ingredients'].append('')
        
    try:
        dic['List of instructions'].append(content['recipeInstructions'])
    except:
        dic['List of instructions'].append('')
        
# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillLibyaData(html,Libyadata)
    except:
        time.sleep(5)

# convert data to dataframe
Libya = pd.DataFrame(Libyadata)
print(Libya.shape)
Libya.head()


# In[57]:


LibyaSpider(htmlLst[-1])


# In[56]:


htmlLst[-1]


# In[66]:


headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'UserIdCookieHttponly=a7e3c56a-137a-4648-9ad3-9520535cd857; UserIdCookieHttponlyExpDate=4/1/2023 6:33:47 PM; _ga=GA1.2.1792171615.1648827229; _fbp=fb.1.1648827229010.621556014; _em_vt=d270c7b7-a949-4909-81fd-cdb483a885a8-17fe57eece1-655ea44c; _em_gc=US; _em_mb=0; __gads=ID=0648f930c0fd88b8:T=1648827230:S=ALNI_MaZPA6NVPyj7zKoE1IknyWRT0qnCQ; _cb_ls=1; _cb=B86uyRDfJRdqDwZQVO; NpsGuid=0a9307e8-cdba-4679-955b-87db49a59822; NpsCreateDate=1648827241; _gcl_au=1.1.1308101560.1648827244; ASP.NET_SessionId=w1yjrfkocf1qrp1tlqsvhmj2; _em_dmp=1652635455750; _chartbeat2=.1641849490991.1652635457241.0000000000000001.C0LeTqh5kFvBLXtmxBZ9aoRCIXf9_.1; permutive-id=07e8e3e5-2095-4cb6-8dde-058b1491fb4e; _gid=GA1.2.2057239003.1652808755; _em_c3=1; _em_vi=a3edced0-e5b4-4cda-b9f9-80598bb979f7-180d31427cb-692764d8; _em_ft=1652808755147; _em_scf=[]; __gpi=UID=0000044cdd15c596:T=1649198253:RT=1652808756:S=ALNI_MZCZpX0IjN9liRcu9tbHQW73FDaZA; _gat=1; _em_lt=1652808825967; _em_pc=2; pv_per_sess=30; datadome=TWq7WMgvsaOAi4abmoryM.CBQtjZ0CR1izR_qCSStO0VOtXJ9aIMBFrZGiJ0DFn8qtfEO-M~WwjvejsHC8QwWUWEULxcB.3wSwv23PGjMp0-QETCM6KWKIFLJ8DCXV4',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
response = requests.get('https://www.justfood.tv/%D9%88%D8%B5%D9%81%D8%A7%D8%AA/%D8%A7%D9%84%D8%A8%D9%84%D8%AF/%D8%A7%D9%83%D9%84%D8%A7%D8%AA-%D9%84%D8%A8%D9%86%D8%A7%D9%86%D9%8A%D8%A9/50',headers=headers)
sel = Selector(response.text)


# In[67]:


sel


# In[65]:


sel.xpath('//meta[@itemprop="prepTime"]')


# In[54]:


Libya["Source"] = ["Web1" for i in range(len(Libya))]
Libya.head()


# In[55]:


# save dataset
Libya.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Libya.csv")


# In[ ]:




