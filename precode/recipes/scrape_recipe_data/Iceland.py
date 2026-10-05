#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Iceland

# In[3]:


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


# #### https://www.food.com/topic/icelandic

# In[4]:


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
        'cookie':'AMCVS_BC501253513148ED0A490D45@AdobeOrg=1; check=true; gig_canary=false; s_ecid=MCMID|87199266229062475467323993245959094502; _fbp=fb.1.1649197880741.970039124; gig_bootstrap_3_-YpMMN5PDDnj1ri65ssss6K9Hq9y-y13U1TnjyjKSIxXJOuvE81IhyaP-BOkmb0v=_gigya_ver4; _pbjs_userid_consent_data=3524755945110770; __gads=ID=c153fc9a493737e4:T=1649197881:S=ALNI_MaK1CLbcDjfbBcPAZ5AMf6HYWnCog; s_cc=true; _li_dcdm_c=.food.com; _lc2_fpi=7a090ec0c3f7--01fzxy8jhz6db62f8g5g8skn4g; _lr_env_src_ats=false; pbjs_identitylink=AsFH2v6hbXK6-fNcJZnFQsq5cFXH6aRSHu1xLJCPRNFRKgfyH7nOPMC50RlXblRau-M_ys9L62uLpVu9Xr0kVyg_-kLBdob3QonhQWIG9VavFVBiiHYE4r9aFwbebHfeHW_PFoUNU852pQDDKUrEqoacbZZLVwzJ0Kom3itp1-zle68QzBjnL_z6sJTQiSEIxfieIEGScM6t7TbxvaZlc4Bg7_vO; s_nr=1649198528811; krg_uid={"v":{"clientId":"29a31191-27c8-4668-bfa4-8f6f0c26d1c1","userId":"3080d979-e7d4-1894-14c7-7656b6603df5","optOut":false}}; gig_canary_ver=13023-3-27512805; s_sq=[[B]]; _lr_geo_location=US; AMCV_BC501253513148ED0A490D45@AdobeOrg=1406116232|MCIDTS|19109|MCMID|87199266229062475467323993245959094502|MCAAMLH-1651589578|7|MCAAMB-1651589578|RKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y|MCOPTOUT-1650991978s|NONE|MCAID|NONE|vVersion|2.5.0; __gpi=UID=000004563261f73e:T=1649346243:RT=1650984779:S=ALNI_MYpE5zi6yY-JOvY5NvICGXJUtnIVw; gig_canary_ver=13023-3-27516435; aam_fw=aam=318092;aam=9354365;aam=312337;aam=3337949;aam=3337952;aam=317738;aam=120908;aam=116961;aam=807145;aam=498421;aam=311691;aam=690080;aam=313979;aam=311692;aam=311667;aam=445063;aam=242439;aam=317732;aam=318093;aam=317779;aam=312338;aam=1629460;aam=1629252; krg_crb={"v":"eyJjbGllbnRJZCI6IjI5YTMxMTkxLTI3YzgtNDY2OC1iZmE0LThmNmYwYzI2ZDFjMSIsInRkSUQiOiJiOGUyZDFjZC1kODRiLTRjMGItYjk0MS03ZGM0MmUzMDIxZGUiLCJsZXhJZCI6IjMwODBkOTc5LWU3ZDQtMTg5NC0xNGM3LTc2NTZiNjYwM2RmNSIsInN5bmNJZHMiOnsiMiI6IjAzNWU3Yjc2LWI5M2MtNGI0NC1hZGJiLTBiMjdlYmQ4OTliZCIsIjE2IjoiWDExeE5kSE00VFFBQUVpamIyNEFBQUNPJjExMDAiLCIxNyI6IjY4ZDEwMGUyLWY2NDctMTFlYS04NTNjLTE1ZWQ2ZTJjZGFkOSIsIjIzIjoiMGU4MzYxZGMtZmYyZC00NjAwLWFhNWUtMzg3MjY1ZDU5ZGM4IiwiMjQiOiJYMTF4TmRITTRUUUFBRWlqYjI0QUFBQ08mMTEwMCIsIjI1IjoiYjhlMmQxY2QtZDg0Yi00YzBiLWI5NDEtN2RjNDJlMzAyMWRlIiwiMjkiOiI2MTQ3MjkwODIxNjkzNjM1NzU1IiwiNzQiOiJDQUVTRU9wX0NoYUdBRGJJalp6WE5QSzctSVkiLCI4MiI6Ikc5QlRpYnFiaUJ6RCIsIjg0IjoidWNCZ0RfQkN0YXNGeFMzUmR5bnAiLCI4NiI6ImstN2lrRTlfSXVEZkVXUzVyQjhtWDhiX3ZiRW82Z2NVbTNXQW5lOUEiLCI4NyI6IkFRRUl4a0lnRVE4N3pnRlRtcERRQVFBLWh3RSIsIjg5IjoiZGlfYmZkZWQxMGJhNWI3NDVjMWFkNzI0IiwiOTAiOiJ4Z2tIOEMtS1JXRm9kV19idXpxOWVzLXNnM0UiLCI5NyI6InktTThtMVF3QkUycHV3aG13SUVUa0tBOUU3RWZTUXpUMGNxRlktfkEiLCIxMDAiOiJoaDVsejFXY2xhdSIsIjEwMSI6IlJYLTQ2ZjQwODY1LWY4ZjktNGExMS05YmQ1LTc3ZGMxODAzMjUxMy0wMDUiLCIyXzE2IjoiQ0FFU0VPcF9DaGFHQURiSWpaelhOUEs3LUlZIiwiMl80NiI6ImstN2lrRTlfSXVEZkVXUzVyQjhtWDhiX3ZiRW82Z2NVbTNXQW5lOUEiLCIyXzgwIjoiMGU4MzYxZGMtZmYyZC00NjAwLWFhNWUtMzg3MjY1ZDU5ZGM4IiwiMl85MyI6ImI4ZTJkMWNkLWQ4NGItNGMwYi1iOTQxLTdkYzQyZTMwMjFkZSIsImlkbF9lbnYiOiJBdWFudDloTGtKczhPS3A3NjIwUlhMVjc3NXNPU0xWWmVTV3Z6OXdUZ0R4RmRDRkZfY3Z0U3BsOU5aT1Q3Y2haSjJmeU5uT2xKQ2MzdzZTejRUa2IyWm5NVzdnWXRtdFRNdmFFZk5MYUp5ZHlxS3kzWlJCS0Znc1R6dzgtRElFc2M2NXh4YnFuWDVtWGgzcXBxMXdaeUJmQ0dOOFl5WVo3R3Q5VmRWYlFQd2NiZnpjaktiVk0tekVsNHIzSjdFbXpoV1oxSWZDNldfSHRlaUdNcnFSWERMVDR5aGJEIn0sImt0Y0lkIjoiZmE1YWRiMDgtNDM4My0wZDc0LTU1M2ItZWUzMjZjY2ViNzk4IiwiZXhwaXJlVGltZSI6MTY1MTA3NDU4MDg4MSwibGFzdFN5bmNlZEF0IjoxNjUwOTg4MTgwODgxLCJwYWdlVmlld0lkIjoiIiwicGFnZVZpZXdUaW1lc3RhbXAiOjE2NTA5ODgxODAxMzksInBhZ2VWaWV3VXJsIjoiaHR0cHM6Ly93d3cuZm9vZC5jb20vcmVjaXBlL2NhaXJvLWFsbW9uZHMtNDg3NjIwIiwidXNwIjpudWxsfQ=="}; mbox=PC#e4a61e36b34443188cfe39f0a8217fd0.34_0#1712442681|session#53fb79ef29e549239a7fa0cd6052fe13#1650990205; nol_fpid=7jmrvh5n3fghcmhqyzojriv1isv0z1649197883|1649197883065|1650988346221|1650988346285; gpv_pn=topic|www.food.com/topic/sudanese',
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
    for i in sel.xpath('//div[@class="fd-tile fd-recipe  "]/@data-url'):
        lst.append(i.get())
    
    return lst


# In[5]:


htmlOnePageSpider("https://www.food.com/topic/icelandic", htmlLst)


# In[6]:


for i in range(2,10):
    htmlOnePageSpider("https://www.food.com/topic/icelandic?pn={}".format(i), htmlLst)


# In[7]:


# the number of recipes we have in total
len(htmlLst)


# In[8]:


# 3. go through all recipe htmls and scrape the data we want

Icelanddata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def IcelandSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'AMCVS_BC501253513148ED0A490D45@AdobeOrg=1; check=true; gig_canary=false; s_ecid=MCMID|87199266229062475467323993245959094502; _fbp=fb.1.1649197880741.970039124; gig_bootstrap_3_-YpMMN5PDDnj1ri65ssss6K9Hq9y-y13U1TnjyjKSIxXJOuvE81IhyaP-BOkmb0v=_gigya_ver4; _pbjs_userid_consent_data=3524755945110770; __gads=ID=c153fc9a493737e4:T=1649197881:S=ALNI_MaK1CLbcDjfbBcPAZ5AMf6HYWnCog; s_cc=true; _li_dcdm_c=.food.com; _lc2_fpi=7a090ec0c3f7--01fzxy8jhz6db62f8g5g8skn4g; _lr_env_src_ats=false; pbjs_identitylink=AsFH2v6hbXK6-fNcJZnFQsq5cFXH6aRSHu1xLJCPRNFRKgfyH7nOPMC50RlXblRau-M_ys9L62uLpVu9Xr0kVyg_-kLBdob3QonhQWIG9VavFVBiiHYE4r9aFwbebHfeHW_PFoUNU852pQDDKUrEqoacbZZLVwzJ0Kom3itp1-zle68QzBjnL_z6sJTQiSEIxfieIEGScM6t7TbxvaZlc4Bg7_vO; s_nr=1649198528811; krg_uid={"v":{"clientId":"29a31191-27c8-4668-bfa4-8f6f0c26d1c1","userId":"3080d979-e7d4-1894-14c7-7656b6603df5","optOut":false}}; gig_canary_ver=13023-3-27512805; s_sq=[[B]]; _lr_geo_location=US; AMCV_BC501253513148ED0A490D45@AdobeOrg=1406116232|MCIDTS|19109|MCMID|87199266229062475467323993245959094502|MCAAMLH-1651589578|7|MCAAMB-1651589578|RKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y|MCOPTOUT-1650991978s|NONE|MCAID|NONE|vVersion|2.5.0; __gpi=UID=000004563261f73e:T=1649346243:RT=1650984779:S=ALNI_MYpE5zi6yY-JOvY5NvICGXJUtnIVw; gig_canary_ver=13023-3-27516435; aam_fw=aam=318092;aam=9354365;aam=312337;aam=3337949;aam=3337952;aam=317738;aam=120908;aam=116961;aam=807145;aam=498421;aam=311691;aam=690080;aam=313979;aam=311692;aam=311667;aam=445063;aam=242439;aam=317732;aam=318093;aam=317779;aam=312338;aam=1629460;aam=1629252; krg_crb={"v":"eyJjbGllbnRJZCI6IjI5YTMxMTkxLTI3YzgtNDY2OC1iZmE0LThmNmYwYzI2ZDFjMSIsInRkSUQiOiJiOGUyZDFjZC1kODRiLTRjMGItYjk0MS03ZGM0MmUzMDIxZGUiLCJsZXhJZCI6IjMwODBkOTc5LWU3ZDQtMTg5NC0xNGM3LTc2NTZiNjYwM2RmNSIsInN5bmNJZHMiOnsiMiI6IjAzNWU3Yjc2LWI5M2MtNGI0NC1hZGJiLTBiMjdlYmQ4OTliZCIsIjE2IjoiWDExeE5kSE00VFFBQUVpamIyNEFBQUNPJjExMDAiLCIxNyI6IjY4ZDEwMGUyLWY2NDctMTFlYS04NTNjLTE1ZWQ2ZTJjZGFkOSIsIjIzIjoiMGU4MzYxZGMtZmYyZC00NjAwLWFhNWUtMzg3MjY1ZDU5ZGM4IiwiMjQiOiJYMTF4TmRITTRUUUFBRWlqYjI0QUFBQ08mMTEwMCIsIjI1IjoiYjhlMmQxY2QtZDg0Yi00YzBiLWI5NDEtN2RjNDJlMzAyMWRlIiwiMjkiOiI2MTQ3MjkwODIxNjkzNjM1NzU1IiwiNzQiOiJDQUVTRU9wX0NoYUdBRGJJalp6WE5QSzctSVkiLCI4MiI6Ikc5QlRpYnFiaUJ6RCIsIjg0IjoidWNCZ0RfQkN0YXNGeFMzUmR5bnAiLCI4NiI6ImstN2lrRTlfSXVEZkVXUzVyQjhtWDhiX3ZiRW82Z2NVbTNXQW5lOUEiLCI4NyI6IkFRRUl4a0lnRVE4N3pnRlRtcERRQVFBLWh3RSIsIjg5IjoiZGlfYmZkZWQxMGJhNWI3NDVjMWFkNzI0IiwiOTAiOiJ4Z2tIOEMtS1JXRm9kV19idXpxOWVzLXNnM0UiLCI5NyI6InktTThtMVF3QkUycHV3aG13SUVUa0tBOUU3RWZTUXpUMGNxRlktfkEiLCIxMDAiOiJoaDVsejFXY2xhdSIsIjEwMSI6IlJYLTQ2ZjQwODY1LWY4ZjktNGExMS05YmQ1LTc3ZGMxODAzMjUxMy0wMDUiLCIyXzE2IjoiQ0FFU0VPcF9DaGFHQURiSWpaelhOUEs3LUlZIiwiMl80NiI6ImstN2lrRTlfSXVEZkVXUzVyQjhtWDhiX3ZiRW82Z2NVbTNXQW5lOUEiLCIyXzgwIjoiMGU4MzYxZGMtZmYyZC00NjAwLWFhNWUtMzg3MjY1ZDU5ZGM4IiwiMl85MyI6ImI4ZTJkMWNkLWQ4NGItNGMwYi1iOTQxLTdkYzQyZTMwMjFkZSIsImlkbF9lbnYiOiJBdWFudDloTGtKczhPS3A3NjIwUlhMVjc3NXNPU0xWWmVTV3Z6OXdUZ0R4RmRDRkZfY3Z0U3BsOU5aT1Q3Y2haSjJmeU5uT2xKQ2MzdzZTejRUa2IyWm5NVzdnWXRtdFRNdmFFZk5MYUp5ZHlxS3kzWlJCS0Znc1R6dzgtRElFc2M2NXh4YnFuWDVtWGgzcXBxMXdaeUJmQ0dOOFl5WVo3R3Q5VmRWYlFQd2NiZnpjaktiVk0tekVsNHIzSjdFbXpoV1oxSWZDNldfSHRlaUdNcnFSWERMVDR5aGJEIn0sImt0Y0lkIjoiZmE1YWRiMDgtNDM4My0wZDc0LTU1M2ItZWUzMjZjY2ViNzk4IiwiZXhwaXJlVGltZSI6MTY1MTA3NDU4MDg4MSwibGFzdFN5bmNlZEF0IjoxNjUwOTg4MTgwODgxLCJwYWdlVmlld0lkIjoiIiwicGFnZVZpZXdUaW1lc3RhbXAiOjE2NTA5ODgxODAxMzksInBhZ2VWaWV3VXJsIjoiaHR0cHM6Ly93d3cuZm9vZC5jb20vcmVjaXBlL2NhaXJvLWFsbW9uZHMtNDg3NjIwIiwidXNwIjpudWxsfQ=="}; mbox=PC#e4a61e36b34443188cfe39f0a8217fd0.34_0#1712442681|session#53fb79ef29e549239a7fa0cd6052fe13#1650990205; nol_fpid=7jmrvh5n3fghcmhqyzojriv1isv0z1649197883|1649197883065|1650988346221|1650988346285; gpv_pn=topic|www.food.com/topic/sudanese',
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
    content = json.loads(sel.xpath('//script[@type="application/ld+json"]/text()')[0].get())
    
    return content

def fillIcelandData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = IcelandSpider(html)
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
        fillIcelandData(html,Icelanddata)
    except:
        time.sleep(5)

# convert data to dataframe
Iceland = pd.DataFrame(Icelanddata)
print(Iceland.shape)
Iceland.head()


# In[9]:


Iceland["Source"] = ["Web1" for i in range(len(Iceland))]
Iceland.head()


# In[10]:


# save dataset
Iceland.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Iceland.csv")


# In[ ]:




