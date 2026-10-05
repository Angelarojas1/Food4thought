#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Lithuania

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


# #### https://www.lamaistas.lt/virtuve/lietuvos-virtuve

# In[13]:


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
        'cookie':'__utmc=244722072; _ga=GA1.2.1100855750.1650382299; _fbp=fb.1.1650382299846.1620708654; euconsent-v2=CPXq9MAPXq9MAAKAoALTCLCsAP_AAH_AABaYIrtd_X__bX9j-_5_fft0eY1P9_r3_-QzjhfNs-8F3L_W_L0X42E7NF36pq4KuR4Eu3LBIQNlHMHUTUmwaokVrzHsak2cpyNKJ7LEknMZO2dYGH9Pn9lDuYKY7_5___bx3j-v_t_-39T378Xf3_d5_2---vCfV599jbv9fV__39nP___9v-_8_______4IpgEmGpeQBdmWODJtGkUKIEYVhIVQKACigGFoisAHBwU7KwCfUELABAKkIwIgQYgowYBAAIJAEhEQEgBYIBEARAIAAQAIgEIACJgEFgBYGAQACgGhYgBQACBIQZFBEcpgQFSJRQS2ViCUFexphAGWeBFAojIqABEkkAJAQEhYOY4AkBLxZIGmKF8gBGAAAAA.YAAAAAAAAAAA; addtl_consent=1~39.4.3.9.6.9.13.6.4.15.9.5.2.7.4.1.7.1.3.2.10.3.5.4.21.4.6.9.7.10.2.9.2.18.7.6.14.5.20.6.5.1.3.1.11.29.4.14.4.5.3.10.6.2.9.6.6.4.5.4.4.29.4.5.3.1.6.2.2.17.1.17.10.9.1.8.6.2.8.3.4.142.4.8.35.7.15.1.14.3.1.8.10.25.3.7.25.5.18.9.7.41.2.4.18.21.3.4.2.1.6.6.5.2.14.18.7.3.2.2.8.20.8.8.6.3.10.4.20.2.13.4.6.4.11.1.3.22.16.2.6.8.2.4.11.6.5.33.11.8.1.10.28.12.1.3.21.2.7.6.1.9.30.17.4.9.15.8.7.3.6.6.7.2.4.1.7.12.13.22.13.2.12.2.10.1.4.15.2.4.9.4.5.4.7.13.5.15.4.13.4.14.8.2.15.2.5.5.1.2.2.1.2.14.7.4.8.2.9.10.18.12.13.2.18.1.1.3.1.1.9.25.4.1.19.8.4.5.2.1.5.4.8.4.2.2.2.14.2.13.4.2.6.9.6.3.4.3.5.2.3.6.10.11.6.3.16.3.11.3.1.2.3.9.19.11.15.3.10.7.6.4.3.4.6.3.3.3.3.1.1.1.6.11.3.1.1.7.4.6.1.10.5.2.6.3.2.2.4.3.2.2.7.2.13.7.12.2.1.3.3.4.5.4.3.2.2.4.1.3.1.1.1.2.9.1.6.9.1.5.2.1.7.2.8.11.1.3.1.1.2.1.3.2.6.1.11.1.5.3.1.3.1.1.2.2.7.7.1.4.1.2.6.1.2.1.1.3.1.1.4.1.1.2.1.8.1.7.4.3.2.1.3.5.3.9.6.1.15.10.28.1.2.2.12.3.4.1.6.3.4.7.1.3.1.1.3.1.5.3.1.3.2.2.1.1.4.2.1.2.1.1.1.2.2.4.2.1.2.2.2.4.1.1.1.2.2.1.1.1.1.2.1.1.1.2.2.1.1.2.1.2.1.7.1.2.1.1.1.2.1.1.1.1.2.1.1.3.2.1.1.8.1.1.1.5.2.1.6.5.1.1.1.1.1.2.2.3.1.1.4.1.1.2.2.1.1.4.2.1.1.2.2.1.2.1.2.3.1.1.2.4.1.1.1.5.1.3.6.3.1.5.2.3.4.1.2.3.1.4.2.1.2.2.2.1.1.1.1.1.1.11.1.3.1.1.2.2.1.4.2.3.3.4.1.1.1.1.4.2.1.1.2.5.1.9.4.1.1.3.1.7.1.4.5.1.7.2.1.1.1.2.1.1.1.4.2.1.12.1.1.3.1.2.2.3.1.2.1.1.1.2.1.1.2.1.1.1.1.2.1.3.1.5.1.2.4.3.8.2.2.9.7.2.2.1.2.1.4.2; _pbjs_userid_consent_data=3976415588336169; _pubcid=9c125b55-7e01-482a-89ee-716f791f5914; __qca=P0-36920792-1650382299694; __gads=ID=c0d50ad96b19c926:T=1650382302:S=ALNI_MZmK-YO0ywJQInuA991fiXaIqLgEw; discounts-system=1; PHPSESSID=t9h0cvb0aefrtqfg9nrk8l94g5; __gfp_64b=1R_Gn.LIOkNdnD3zMAjHK0DDyCeWuwyQgGFVCSW9n3P.97|1650382300; __utma=244722072.1100855750.1650382299.1651596717.1652108203.4; __utmz=244722072.1652108203.4.4.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not provided); __utmt=1; _gid=GA1.2.441292323.1652108203; __gpi=UID=00000444f1436b53:T=1650382302:RT=1652108204:S=ALNI_MZ6TgvyHCRMX61SRKcss5t7cSyEuw; __utmb=244722072.3.10.1652108203; _gat_UA-9972208-1=1; stpdOrigin={"origin":"direct"}; cto_bidid=6ueR3F9WZHFzOVklMkZMRm9ocFgxYW9aZlNvdDcxcGlJVWNPY2xqSE5TOUNOWk1oOFJTMlhldGFCVllPM0dvVyUyQnNNZERKZEM1bTNyaktsNkklMkZFazFkNWpadThPSERRbnBCTkNTSnd4NGJLYkoyakxYYyUzRA; cto_bundle=MNA2DF82aDRySTE2aXJOd1Fkb0NMdEhkWWVoa0tpN3V1YiUyQkdEd0ZYcTd4MkJsS0dGbGcyQyUyQm95ZzBvUkowcUQ0YVIzblNtaE5oalRHdlIzbUtGckViYlVaN2glMkJDQjBoaiUyRlNrJTJCNkhaNDR3ekhla0JXazZXTyUyQkN0Qmw2ZERCMFJHRjhVN3I0WnhuRGpRMCUyRnZ3QVVUczRMZVFwZyUzRCUzRA; cto_bundle=QRA2tF82aDRySTE2aXJOd1Fkb0NMdEhkWWVqU0pSVVNsT0lSdjBQMmtUaGJoUDZ0bmZjbk00WnBTY0d2VmU3VE9OaVAzQ2lQZlVMM20yMTJDb3djQTV0cTBnWDBFUFhhVHNOeXNKVWJkM05VZm1MWTg4TzVTdSUyQktvbm5RTjFWdTN4NmgzV3NJa2FFZ2pReGt0ZmZHT0VLQjZsdyUzRCUzRA; cto_bundle=QRA2tF82aDRySTE2aXJOd1Fkb0NMdEhkWWVqU0pSVVNsT0lSdjBQMmtUaGJoUDZ0bmZjbk00WnBTY0d2VmU3VE9OaVAzQ2lQZlVMM20yMTJDb3djQTV0cTBnWDBFUFhhVHNOeXNKVWJkM05VZm1MWTg4TzVTdSUyQktvbm5RTjFWdTN4NmgzV3NJa2FFZ2pReGt0ZmZHT0VLQjZsdyUzRCUzRA',
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
    for i in sel.xpath('//div[@class="cell sDef-4 s1280-4 s1024-3 s760-3 s460-2 s320-2"]/div/a/@href'):
        lst.append(i.get())
    
    return lst


# In[14]:


htmlOnePageSpider("https://www.lamaistas.lt/virtuve/lietuvos-virtuve", htmlLst)


# In[16]:


for i in range(2,131):
    htmlOnePageSpider("https://www.lamaistas.lt/virtuve/lietuvos-virtuve/{}".format(i), htmlLst)


# In[19]:


# the number of recipes we have in total
htmlLst = list(set(htmlLst))
len(htmlLst)


# In[22]:


# 3. go through all recipe htmls and scrape the data we want

Lithuaniadata = {
    "Name of the recipe":[],
    "Total time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def LithuaniaSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'__utmc=244722072; _ga=GA1.2.1100855750.1650382299; _fbp=fb.1.1650382299846.1620708654; euconsent-v2=CPXq9MAPXq9MAAKAoALTCLCsAP_AAH_AABaYIrtd_X__bX9j-_5_fft0eY1P9_r3_-QzjhfNs-8F3L_W_L0X42E7NF36pq4KuR4Eu3LBIQNlHMHUTUmwaokVrzHsak2cpyNKJ7LEknMZO2dYGH9Pn9lDuYKY7_5___bx3j-v_t_-39T378Xf3_d5_2---vCfV599jbv9fV__39nP___9v-_8_______4IpgEmGpeQBdmWODJtGkUKIEYVhIVQKACigGFoisAHBwU7KwCfUELABAKkIwIgQYgowYBAAIJAEhEQEgBYIBEARAIAAQAIgEIACJgEFgBYGAQACgGhYgBQACBIQZFBEcpgQFSJRQS2ViCUFexphAGWeBFAojIqABEkkAJAQEhYOY4AkBLxZIGmKF8gBGAAAAA.YAAAAAAAAAAA; addtl_consent=1~39.4.3.9.6.9.13.6.4.15.9.5.2.7.4.1.7.1.3.2.10.3.5.4.21.4.6.9.7.10.2.9.2.18.7.6.14.5.20.6.5.1.3.1.11.29.4.14.4.5.3.10.6.2.9.6.6.4.5.4.4.29.4.5.3.1.6.2.2.17.1.17.10.9.1.8.6.2.8.3.4.142.4.8.35.7.15.1.14.3.1.8.10.25.3.7.25.5.18.9.7.41.2.4.18.21.3.4.2.1.6.6.5.2.14.18.7.3.2.2.8.20.8.8.6.3.10.4.20.2.13.4.6.4.11.1.3.22.16.2.6.8.2.4.11.6.5.33.11.8.1.10.28.12.1.3.21.2.7.6.1.9.30.17.4.9.15.8.7.3.6.6.7.2.4.1.7.12.13.22.13.2.12.2.10.1.4.15.2.4.9.4.5.4.7.13.5.15.4.13.4.14.8.2.15.2.5.5.1.2.2.1.2.14.7.4.8.2.9.10.18.12.13.2.18.1.1.3.1.1.9.25.4.1.19.8.4.5.2.1.5.4.8.4.2.2.2.14.2.13.4.2.6.9.6.3.4.3.5.2.3.6.10.11.6.3.16.3.11.3.1.2.3.9.19.11.15.3.10.7.6.4.3.4.6.3.3.3.3.1.1.1.6.11.3.1.1.7.4.6.1.10.5.2.6.3.2.2.4.3.2.2.7.2.13.7.12.2.1.3.3.4.5.4.3.2.2.4.1.3.1.1.1.2.9.1.6.9.1.5.2.1.7.2.8.11.1.3.1.1.2.1.3.2.6.1.11.1.5.3.1.3.1.1.2.2.7.7.1.4.1.2.6.1.2.1.1.3.1.1.4.1.1.2.1.8.1.7.4.3.2.1.3.5.3.9.6.1.15.10.28.1.2.2.12.3.4.1.6.3.4.7.1.3.1.1.3.1.5.3.1.3.2.2.1.1.4.2.1.2.1.1.1.2.2.4.2.1.2.2.2.4.1.1.1.2.2.1.1.1.1.2.1.1.1.2.2.1.1.2.1.2.1.7.1.2.1.1.1.2.1.1.1.1.2.1.1.3.2.1.1.8.1.1.1.5.2.1.6.5.1.1.1.1.1.2.2.3.1.1.4.1.1.2.2.1.1.4.2.1.1.2.2.1.2.1.2.3.1.1.2.4.1.1.1.5.1.3.6.3.1.5.2.3.4.1.2.3.1.4.2.1.2.2.2.1.1.1.1.1.1.11.1.3.1.1.2.2.1.4.2.3.3.4.1.1.1.1.4.2.1.1.2.5.1.9.4.1.1.3.1.7.1.4.5.1.7.2.1.1.1.2.1.1.1.4.2.1.12.1.1.3.1.2.2.3.1.2.1.1.1.2.1.1.2.1.1.1.1.2.1.3.1.5.1.2.4.3.8.2.2.9.7.2.2.1.2.1.4.2; _pbjs_userid_consent_data=3976415588336169; _pubcid=9c125b55-7e01-482a-89ee-716f791f5914; __qca=P0-36920792-1650382299694; __gads=ID=c0d50ad96b19c926:T=1650382302:S=ALNI_MZmK-YO0ywJQInuA991fiXaIqLgEw; discounts-system=1; PHPSESSID=t9h0cvb0aefrtqfg9nrk8l94g5; __gfp_64b=1R_Gn.LIOkNdnD3zMAjHK0DDyCeWuwyQgGFVCSW9n3P.97|1650382300; __utma=244722072.1100855750.1650382299.1651596717.1652108203.4; __utmz=244722072.1652108203.4.4.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not provided); __utmt=1; _gid=GA1.2.441292323.1652108203; __gpi=UID=00000444f1436b53:T=1650382302:RT=1652108204:S=ALNI_MZ6TgvyHCRMX61SRKcss5t7cSyEuw; __utmb=244722072.3.10.1652108203; _gat_UA-9972208-1=1; stpdOrigin={"origin":"direct"}; cto_bidid=6ueR3F9WZHFzOVklMkZMRm9ocFgxYW9aZlNvdDcxcGlJVWNPY2xqSE5TOUNOWk1oOFJTMlhldGFCVllPM0dvVyUyQnNNZERKZEM1bTNyaktsNkklMkZFazFkNWpadThPSERRbnBCTkNTSnd4NGJLYkoyakxYYyUzRA; cto_bundle=MNA2DF82aDRySTE2aXJOd1Fkb0NMdEhkWWVoa0tpN3V1YiUyQkdEd0ZYcTd4MkJsS0dGbGcyQyUyQm95ZzBvUkowcUQ0YVIzblNtaE5oalRHdlIzbUtGckViYlVaN2glMkJDQjBoaiUyRlNrJTJCNkhaNDR3ekhla0JXazZXTyUyQkN0Qmw2ZERCMFJHRjhVN3I0WnhuRGpRMCUyRnZ3QVVUczRMZVFwZyUzRCUzRA; cto_bundle=QRA2tF82aDRySTE2aXJOd1Fkb0NMdEhkWWVqU0pSVVNsT0lSdjBQMmtUaGJoUDZ0bmZjbk00WnBTY0d2VmU3VE9OaVAzQ2lQZlVMM20yMTJDb3djQTV0cTBnWDBFUFhhVHNOeXNKVWJkM05VZm1MWTg4TzVTdSUyQktvbm5RTjFWdTN4NmgzV3NJa2FFZ2pReGt0ZmZHT0VLQjZsdyUzRCUzRA; cto_bundle=QRA2tF82aDRySTE2aXJOd1Fkb0NMdEhkWWVqU0pSVVNsT0lSdjBQMmtUaGJoUDZ0bmZjbk00WnBTY0d2VmU3VE9OaVAzQ2lQZlVMM20yMTJDb3djQTV0cTBnWDBFUFhhVHNOeXNKVWJkM05VZm1MWTg4TzVTdSUyQktvbm5RTjFWdTN4NmgzV3NJa2FFZ2pReGt0ZmZHT0VLQjZsdyUzRCUzRA',
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
    content = json.loads(sel.xpath('//script[@type="application/ld+json"]/text()').get())
    
    return content

def fillLithuaniaData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = LithuaniaSpider(html)
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
        fillLithuaniaData(html,Lithuaniadata)
    except:
        time.sleep(5)

# convert data to dataframe
Lithuania = pd.DataFrame(Lithuaniadata)
print(Lithuania.shape)
Lithuania.head()


# In[23]:


Lithuania["Source"] = ["Web1" for i in range(len(Lithuania))]
Lithuania.head()


# In[24]:


# save dataset
Lithuania.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Lithuania.csv")


# In[ ]:




