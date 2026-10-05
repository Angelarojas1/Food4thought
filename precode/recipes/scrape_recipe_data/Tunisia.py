#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Tunisia

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


# #### https://www.196flavors.com/category/continent/africa/north-africa/tunisia/

# In[9]:


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
        'cookie':'growme_version={"name":"7.78.4","version":"7.78.4"}; _ga=GA1.2.1755121398.1649702597; _gcl_au=1.1.322581374.1649702597; _fbp=fb.1.1649702596904.1977149928; _omappvp=d0UEqYG0rB7SzidiCnftdmAWwTYlgbf4tqAAkxiV4mBNPbKT0dvEv4WwdcOw8Fk3dBQX5wPTdtpFgETSL7WGrfmYPFGt0bUk; _hjid=9050d0dc-1b8e-4132-9a13-f43b832f5298; _hjSessionUser_2009453=eyJpZCI6IjE5M2EyYjQzLWM0ODktNWExNC05NjIzLTlmYjY5MDIzYWU5MyIsImNyZWF0ZWQiOjE2NDk3MDI1OTcwNjUsImV4aXN0aW5nIjp0cnVlfQ==; _webpushrEndPoint=https://fcm.googleapis.com/fcm/send/c6jdcg09sBg:APA91bGczIEINno0QkwhY_z84qCtgw1G38P8q-jyVf8vuOcxtdvGF035qYJehQPNtVYZfKWt09j-V_aQTX2nR1MuyHk4GibQaMwToMLsP1YzWy3oEtpWIFD-WoQtc4w3fkPSTpwt0l6W; _pbjs_userid_consent_data=3524755945110770; _pubCommonId=b7b6a79d-d2f4-42a6-be7b-da132278772f; _lr_env_src_ats=false; mv_tokens={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; mv_tokens_invalidate-verizon-pushes={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; __gads=ID=e985f0ca3fe3b1da:T=1649702603:S=ALNI_MbolT-9fMQ6NqDnTyn5sK9PHnyo1Q; __qca=P0-1245797746-1649704752031; om-qet8oqg8mpvqr7qhvdzy=1650146547556; omSeen-sfekjgtav5l22qraquhm=1650146567231; omSeen-oytivucntmfxjtppcqyy=1650146567231; omSeen-uldpg6edpofyhtel2pip=1650146567231; omSeen-qet8oqg8mpvqr7qhvdzy=1650146585658; _gid=GA1.2.583269835.1650821838; _webpushrLastVisit=4/24/2022 00:00; omCountdown-c1vlexf7flaph9yts8qa-af43UMRBDXHJH2Q6SMOp=1650989625702; omSeen-c1vlexf7flaph9yts8qa=1650917385895; _uetsid=303b6400c3f511eca0416197b0741e58; _uetvid=6489b6608f2f11ec85088d2b10417c24; _hjSession_2009453=eyJpZCI6IjNhNzFkYTA4LTEyNTgtNDFmNS05NTJiLTZjZDIxNWQwMTZiMyIsImNyZWF0ZWQiOjE2NTA5NDA2Nzc2OTUsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0; _lr_retry_request=true; _svsid=6bad20d9de804b2eb86fe053e180057e; cto_bundle=U5nKIl9wRnhnRSUyQjBKUExXT2tNVkdzb1d5ZXJDMVZCQnNEWkJxS1BTWkV6WHZHWEYyNjVsZyUyRmJTa2FTVHMyQ1BIUGdYN3BTbUclMkZpdWpSV1d5ZXVvc0k2ZlNVaDVqOWtkaEhjMWpXempiZU1oWTVSc21Qb1d5b2d1eDh4d0FnVUxseUIlMkJ4UWphaVFIYmtrJTJGM1hxUURoaVA2SGtnJTNEJTNE; cto_bidid=AYcZ2F9Jb3czczAlMkJBWnBOYWpKbEZtZnNwM1JvZ1Y5RXRuek9ZOUg2R1QlMkZKNkZwMTZEbDZqNkdLQnF3blFKSGRodVhXNjJTdnhTdWhkR09yUk9vcU9OSUhLbVhCblJYRWF5Q3Z6TG9CMTRwJTJCMGtXUE1JRW02USUyRnhpQVR3cnM2NzJTRSUyRkQ; __gpi=UID=0000048bd14c9718:T=1650144849:RT=1650940680:S=ALNI_MYKVIpUp8ZiraY43wmOxYFwUXV_Xw',
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
    for i in sel.xpath("//main[@class='content']/article/header/a/@href"):
        lst.append(i.get())
    
    return lst


# In[10]:


htmlOnePageSpider("https://www.196flavors.com/category/continent/africa/north-africa/tunisia/", htmlLst)


# In[11]:


for i in range(2,8):
    htmlOnePageSpider("https://www.196flavors.com/category/continent/africa/north-africa/tunisia/page/{}/".format(i), htmlLst)


# In[12]:


# the number of recipes we have in total
len(htmlLst)


# In[26]:


# 3. go through all recipe htmls and scrape the data we want

Tunisiadata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def TunisiaSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'growme_version={"name":"7.78.4","version":"7.78.4"}; _ga=GA1.2.1755121398.1649702597; _gcl_au=1.1.322581374.1649702597; _fbp=fb.1.1649702596904.1977149928; _omappvp=d0UEqYG0rB7SzidiCnftdmAWwTYlgbf4tqAAkxiV4mBNPbKT0dvEv4WwdcOw8Fk3dBQX5wPTdtpFgETSL7WGrfmYPFGt0bUk; _hjid=9050d0dc-1b8e-4132-9a13-f43b832f5298; _hjSessionUser_2009453=eyJpZCI6IjE5M2EyYjQzLWM0ODktNWExNC05NjIzLTlmYjY5MDIzYWU5MyIsImNyZWF0ZWQiOjE2NDk3MDI1OTcwNjUsImV4aXN0aW5nIjp0cnVlfQ==; _webpushrEndPoint=https://fcm.googleapis.com/fcm/send/c6jdcg09sBg:APA91bGczIEINno0QkwhY_z84qCtgw1G38P8q-jyVf8vuOcxtdvGF035qYJehQPNtVYZfKWt09j-V_aQTX2nR1MuyHk4GibQaMwToMLsP1YzWy3oEtpWIFD-WoQtc4w3fkPSTpwt0l6W; _pbjs_userid_consent_data=3524755945110770; _pubCommonId=b7b6a79d-d2f4-42a6-be7b-da132278772f; _lr_env_src_ats=false; mv_tokens={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; mv_tokens_invalidate-verizon-pushes={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; __gads=ID=e985f0ca3fe3b1da:T=1649702603:S=ALNI_MbolT-9fMQ6NqDnTyn5sK9PHnyo1Q; __qca=P0-1245797746-1649704752031; om-qet8oqg8mpvqr7qhvdzy=1650146547556; omSeen-sfekjgtav5l22qraquhm=1650146567231; omSeen-oytivucntmfxjtppcqyy=1650146567231; omSeen-uldpg6edpofyhtel2pip=1650146567231; omSeen-qet8oqg8mpvqr7qhvdzy=1650146585658; _gid=GA1.2.583269835.1650821838; _webpushrLastVisit=4/24/2022 00:00; omCountdown-c1vlexf7flaph9yts8qa-af43UMRBDXHJH2Q6SMOp=1650989625702; omSeen-c1vlexf7flaph9yts8qa=1650917385895; _uetsid=303b6400c3f511eca0416197b0741e58; _uetvid=6489b6608f2f11ec85088d2b10417c24; _hjSession_2009453=eyJpZCI6IjNhNzFkYTA4LTEyNTgtNDFmNS05NTJiLTZjZDIxNWQwMTZiMyIsImNyZWF0ZWQiOjE2NTA5NDA2Nzc2OTUsImluU2FtcGxlIjpmYWxzZX0=; _hjAbsoluteSessionInProgress=0; _lr_retry_request=true; _svsid=6bad20d9de804b2eb86fe053e180057e; cto_bundle=U5nKIl9wRnhnRSUyQjBKUExXT2tNVkdzb1d5ZXJDMVZCQnNEWkJxS1BTWkV6WHZHWEYyNjVsZyUyRmJTa2FTVHMyQ1BIUGdYN3BTbUclMkZpdWpSV1d5ZXVvc0k2ZlNVaDVqOWtkaEhjMWpXempiZU1oWTVSc21Qb1d5b2d1eDh4d0FnVUxseUIlMkJ4UWphaVFIYmtrJTJGM1hxUURoaVA2SGtnJTNEJTNE; cto_bidid=AYcZ2F9Jb3czczAlMkJBWnBOYWpKbEZtZnNwM1JvZ1Y5RXRuek9ZOUg2R1QlMkZKNkZwMTZEbDZqNkdLQnF3blFKSGRodVhXNjJTdnhTdWhkR09yUk9vcU9OSUhLbVhCblJYRWF5Q3Z6TG9CMTRwJTJCMGtXUE1JRW02USUyRnhpQVR3cnM2NzJTRSUyRkQ; __gpi=UID=0000048bd14c9718:T=1650144849:RT=1650940680:S=ALNI_MYKVIpUp8ZiraY43wmOxYFwUXV_Xw',
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
    content = json.loads(sel.xpath('//script[@type="application/ld+json"]/text()').get())['@graph'][-1]
    
    return content

def fillTunisiaData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = TunisiaSpider(html)
    dic['Name of the recipe'].append(content['name'])
    try:
        dic['Total time'].append(content['totalTime'])
    except:
        dic['Total time'].append('')
        
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
        fillTunisiaData(html,Tunisiadata)
    except:
        time.sleep(5)

# convert data to dataframe
Tunisia = pd.DataFrame(Tunisiadata)
print(Tunisia.shape)
Tunisia.head()


# In[27]:


Tunisia["Source"] = ["Web1" for i in range(len(Tunisia))]
Tunisia.head()


# In[28]:


# save dataset
Tunisia.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Tunisia.csv")


# In[ ]:




