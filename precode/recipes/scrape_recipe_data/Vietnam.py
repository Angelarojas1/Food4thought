#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Vietnam

# In[2]:


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


# Vietnamese recipes are from two webs: 
# 
# (1) https://rasamalaysia.com/recipes/vietnamese-recipes/
# (2) https://www.bbcgoodfood.com/recipes/collection/vietnamese-recipes

# #### (1) https://rasamalaysia.com/recipes/vietnamese-recipes/

# In[18]:


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
        'cookie': '_ga=GA1.2.1298634517.1650842328; _gid=GA1.2.78407197.1650842328; _pbjs_userid_consent_data=3524755945110770; _pubCommonId=cbea3ee3-3286-4db6-a674-2edcc57770b7; _lr_env_src_ats=false; mv_tokens={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; mv_tokens_invalidate-verizon-pushes={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; cto_bidid=QRyr2V9FUVUxcHBPa3VJazE1TWRuV2Y3dCUyRmdFOU5DaWcxMEdZUHo4UjdXTUVwVnFCM2hJd3VKN2d1ZTViWndUUXRsenBKV3o3akI4UE8zdUdVZHFLeTVWUTQ3ZXdNc1NrZjNvSEI1WDVsQmU1UDNjeUN6bzhEaENFYlNEcFJ2MFJ2TjBo; cto_bundle=c9JT2V9iRHkzZm9IbCUyRnZiVDNFMVozbTBRRHRqSCUyRjNxODZubVNiT1FTUklVTmE5SExBa05kRlJrdGQ3UmRHWlR3bGhqYmZUREtWUjhGJTJGczlmMjN3VlpiRG9ZbGhPOGdldTBhN0VnaUpjU0lxVnllOTVETmZQdVd4ckVuMFg2N0YyaUFkMzRDZkM3Y0J1a1FETFBtQzNHdEhNVlElM0QlM0Q; __gads=ID=1f50e15f3097906f:T=1650842332:S=ALNI_MZ_H1g4FuA825XrZ77oTRn9swwTmw; __gpi=UID=0000045a02f923d9:T=1650842332:RT=1650904278:S=ALNI_MbbVHA9v8kD65LJuOWbrsKGaztCvQ',
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
    for i in sel.xpath('//main[@class="content"]/article')[0].xpath("//a[@class='entry-image-link']/@href"):
        lst.append(i.get())
    
    return lst


# In[19]:


htmlOnePageSpider("https://rasamalaysia.com/recipes/vietnamese-recipes/", htmlLst)


# In[22]:


# the number of recipes we have in total
len(htmlLst)


# In[29]:


# 3. go through all recipe htmls and scrape the data we want

Vietnamdata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
}

def VietnamSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': '_ga=GA1.2.1298634517.1650842328; _gid=GA1.2.78407197.1650842328; _pbjs_userid_consent_data=3524755945110770; _pubCommonId=cbea3ee3-3286-4db6-a674-2edcc57770b7; _lr_env_src_ats=false; mv_tokens={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; mv_tokens_invalidate-verizon-pushes={"mv_uuid":"337072d0-b05c-11ec-9a05-61e6dc03c698","version":"invalidate-verizon-pushes"}; cto_bidid=QRyr2V9FUVUxcHBPa3VJazE1TWRuV2Y3dCUyRmdFOU5DaWcxMEdZUHo4UjdXTUVwVnFCM2hJd3VKN2d1ZTViWndUUXRsenBKV3o3akI4UE8zdUdVZHFLeTVWUTQ3ZXdNc1NrZjNvSEI1WDVsQmU1UDNjeUN6bzhEaENFYlNEcFJ2MFJ2TjBo; cto_bundle=c9JT2V9iRHkzZm9IbCUyRnZiVDNFMVozbTBRRHRqSCUyRjNxODZubVNiT1FTUklVTmE5SExBa05kRlJrdGQ3UmRHWlR3bGhqYmZUREtWUjhGJTJGczlmMjN3VlpiRG9ZbGhPOGdldTBhN0VnaUpjU0lxVnllOTVETmZQdVd4ckVuMFg2N0YyaUFkMzRDZkM3Y0J1a1FETFBtQzNHdEhNVlElM0QlM0Q; __gads=ID=1f50e15f3097906f:T=1650842332:S=ALNI_MZ_H1g4FuA825XrZ77oTRn9swwTmw; __gpi=UID=0000045a02f923d9:T=1650842332:RT=1650904278:S=ALNI_MbbVHA9v8kD65LJuOWbrsKGaztCvQ',
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
    
    return content

def fillVietnamData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = VietnamSpider(html)
    dic['Name of the recipe'].append(content['name'])
    dic['Total time'].append(content['totalTime'])
    dic['Prep time'].append(content['prepTime'])
    dic['Cook time'].append(content['cookTime'])
    dic['List of ingredients'].append(content['recipeIngredient'])
    dic['List of instructions'].append(content['recipeInstructions'])
    dic['Number of servings'].append(content['recipeYield'])


# In[30]:


# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillVietnamData(html,Vietnamdata)
    except:
        time.sleep(5)


# In[31]:


# convert data to dataframe
Vietnam = pd.DataFrame(Vietnamdata)
print(Vietnam.shape)
Vietnam.head()


# In[33]:


Vietnam["Source"] = ["Web1" for i in range(len(Vietnam))]
Vietnam.head()


# #### (2) https://www.bbcgoodfood.com/search?q=Vietnamese+recipes

# In[41]:


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
        'cookie':'permutive-id=5835e452-1c7b-4c2e-8967-71d3a86a12d3; _gcl_au=1.1.408235534.1648822842; _hjid=273e0100-d247-42bc-b109-34f0e125c526; ntv_as_us_privacy=1---; _hjSessionUser_1704279=eyJpZCI6IjExOWM4MDFjLTAxZTgtNTdmOS1hNDI2LTFiMGFiYjE5NzNkMiIsImNyZWF0ZWQiOjE2NDg4MjI4NDIwMDcsImV4aXN0aW5nIjp0cnVlfQ==; _ntv_uid=6a8b6277-5f6e-4dab-a3fe-a89932a5a548; euconsent-v2=CPWvoUAPWvoUAAKAoAENCJCsAP_AAH_AAAwIIqNd_X9_bX9j-_5_f_t0eY1P9_r3_-QzjhfNt-8F3L_W_L0X42E7NF36pq4KuR4Eu3LBIQNlHMHUTUmwaokVrzHsYk2cpyNKJ7LEmnMZO2dYGHtPn9lDuYKY7_5___bz3j-v_t_-39T378Xf3_d5_2---vCfV599jbv9f3__39nP___9v-_8_______BFMAkw1LyALsyxwZNo0qhRAjCsJCqBQAUUAwtEVgA4OCnZWAT6ghYAIBUhGBECDEFGDAIABBIAkIiAkALBAIgCIBAACABEAhAARMAgsALAwCAAUA0LEAKAAQJCDI4IjlMCAqRKKCWysQSgr2NMIAyzwIoFEZFQAIkmgBYGQkLBzHAEgJeLJA0xQvkAIwAAAAA.f_gAAAAAAAAA; addtl_consent=1~39.4.3.9.6.9.13.6.4.15.9.5.2.7.4.1.7.1.3.2.10.3.5.4.21.4.6.9.7.10.2.9.2.18.7.6.14.5.20.6.5.1.3.1.11.29.4.14.4.5.3.10.6.2.9.6.6.4.5.4.4.29.4.5.3.1.6.2.2.17.1.17.10.9.1.8.6.2.8.3.4.142.4.8.35.7.15.1.14.3.1.8.10.25.3.7.25.5.18.9.7.41.2.4.18.21.3.4.2.1.6.6.5.2.14.18.7.3.2.2.8.20.8.8.6.3.10.4.20.2.13.4.6.4.11.1.3.22.16.2.6.8.2.4.11.6.5.33.11.8.1.10.28.12.1.3.21.2.7.6.1.9.30.17.4.9.15.8.7.3.6.6.7.2.4.1.7.12.13.22.13.2.12.2.10.1.4.15.2.4.9.4.5.4.7.13.5.15.4.13.4.14.8.2.15.2.5.5.1.2.2.1.2.14.7.4.8.2.9.10.18.12.13.2.18.1.1.3.1.1.9.25.4.1.19.8.4.5.2.1.5.4.8.4.2.2.2.14.2.13.4.2.6.9.6.3.4.3.5.2.3.6.10.11.6.3.16.3.11.3.1.2.3.9.19.11.15.3.10.7.6.4.3.4.6.3.3.3.3.1.1.1.6.11.3.1.1.7.4.6.1.10.5.2.6.3.2.2.4.3.2.2.7.2.13.7.12.2.1.3.3.4.5.4.3.2.2.4.1.3.1.1.1.2.9.1.6.9.1.5.2.1.7.2.8.11.1.3.1.1.2.1.3.2.6.1.11.1.5.3.1.3.1.1.2.2.7.7.1.4.1.2.6.1.2.1.1.3.1.1.4.1.1.2.1.8.1.7.4.3.2.1.3.5.3.9.6.1.15.10.28.1.2.2.12.3.4.1.6.3.4.7.1.3.1.1.3.1.5.3.1.3.2.2.1.1.4.2.1.2.1.1.1.2.2.4.2.1.2.2.2.4.1.1.1.2.2.1.1.1.1.2.1.1.1.2.2.1.1.2.1.2.1.7.1.2.1.1.1.2.1.1.1.1.2.1.1.3.2.1.1.8.1.1.1.5.2.1.6.5.1.1.1.1.1.2.2.3.1.1.4.1.1.2.2.1.1.4.2.1.1.2.2.1.2.1.2.3.1.1.2.4.1.1.1.5.1.3.6.3.1.5.2.3.4.1.2.3.1.4.2.1.2.2.2.1.1.1.1.1.1.11.1.3.1.1.2.2.1.4.2.3.3.4.1.1.1.1.4.2.1.1.2.5.1.9.4.1.1.3.1.7.1.4.5.1.7.2.1.1.1.2.1.1.1.4.2.1.12.1.1.3.1.2.2.3.1.2.1.1.1.2.1.1.2.1.1.1.1.2.1.3.1.5.1.2.4.3.8.2.2.9.7.2.2.1.2.1.4; __pnahc=0; cX_P=l1gijs6lj0m8nycv; __pat=0; cX_G=cx:10zshf2govoi7q2dmu1gfko7s:9cw6x07yr4yl; __gads=ID=f32abf06fadf8f45:T=1648822844:S=ALNI_MatxtBh2Dh9uip2RxShqDHlDFTc0g; cX_S=l1vn15p46ir1tt8g; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; _pbjs_userid_consent_data=3798996786539642; _pubcid=f6504317-56ef-4766-b328-69c37bfe98bb; _gid=GA1.2.759115504.1650766562; cto_bidid=9Ny0718xR0dsdHZzQ1pLRmpYV3RkUUtmTElsSHA5ZUtZWWN5SVVnbTlBOEpLSmlTRW5yTzgzT0xjUDNadFU1VFU0eCUyQjRMaGVYYXpaTUdCNE9YdXhRZDMyM0c1TkJReUx1VFRuVDI1ZEw3SWJLcEVDYzFsdGZQcUprSyUyQnhZU3ZKSU1QT09qJTJCNHlVSSUyQm95ekNYbk1FWnpUUG5rUSUzRCUzRA; cto_bundle=ZRiszl9PaGFsUHJ3bklPVjZyUDhZV2w2elJjN3JmMHQ0TWlJT2VjWTB4c0dpRnlMTGt0YW9ucDN6WFhicjVPYlE4WEVhcmxLN2o5JTJCMFpLaWc0bzhHU2taYyUyQlZaV2pnOWFwUDhsMyUyQkRCS1djOE0wRFB0eDZDT3kzTjZUN2NsdEJnZUtjUmVYSUJaSzZ1czVHbXhaNVoyYkp1a2J4dEVuU1MxYlVkRktzc2R5OVNwZjZIRkRRb2ZXbWx1bHZESnpVb1l4UGxCWVJFZHlPZFR3THlJU0xUa1hXZTdRJTNEJTNE; _lr_env_src_ats=false; pbjs-unifiedid={"TDID":"b8e2d1cd-d84b-4c0b-b941-7dc42e3021de","TDID_LOOKUP":"TRUE","TDID_CREATED_AT":"2022-03-24T02:16:06"}; idl_env=Anm6LivIFUrH8iQ6AjQji4lhT_RxYQd8S-5_e4TO7AcONmRI2Os-38PlpoZpXWZjUWfkY01zjOscLbHtKsnMjWsp2vWEXhJ4BNcjiAPGLuTbOtgwv3UYwxPNNX2B-W9ErM-PEp2c87WXGryWWeGns4dYTNXtVYN3hNXRRon64EJqQbNAWAlnHdxFIE22hbOxuTfNs2jhIfIs-WVlKEPlLqYUirfY; _cc_id=589744b018b77ff0c829dd767a86ed67; panoramaId=eaffbaa0b1b49b5c6c7edf9dac1f4945a702da40840206bc42cc04d32b6506cc; panoramaId_expiry=1651371366975; DM_SitId967=true; DM_SitId967SecId5289=true; _usrp_lq=20220524; lux_uid=165092873747194360; AMP_TOKEN=$NOT_FOUND; _dc_gtm_UA-6065919-6=1; __gpi=UID=000004b0a4a888f9:T=1650766562:RT=1650928739:S=ALNI_MYgxeHnQCYlGaAHoSgAeOPgMcZnJg; _hjIncludedInSessionSample=0; _hjSession_1704279=eyJpZCI6IjVhZjQ1OWM5LTgxYzQtNDk3NS1iZGI5LTQzNGZhNTg1ZmU2OCIsImNyZWF0ZWQiOjE2NTA5Mjg3NDc1NTYsImluU2FtcGxlIjpmYWxzZX0=; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; DM_SitIdT967=true; DM_SitId967SecIdT5289=true; __pvi={"id":"v-l2fccfcgb18pjvyd","domain":".bbcgoodfood.com","time":1650928750567}; __tbc={kpex}TjotZ-RrLOgtQcHulfFH96UlJKcce-hFpY-MlFSyRjd4Tx2_61m1sM1RRp6MznN3; xbc={kpex}Pj5227ObcEz57ooEdnOloNB_Duf79J7GlP0P_hotdIcM2JFDsQTJiTnh8h5QyWOb_1qlfo18DTQE9juYp2YCVyaTXbRygZ10zMQVuqmMwYnkKRZSqEGsnDn6MH6rj9VEAHeTED4NmXNJek7HIm1kNCoSqjMwukVMnhhHqve5A4qscU9koCnjCe96QxEojB5_; _ga=GA1.2.1284257515.1648822841; ntvSession={"id":9791310,"placementID":1099124,"lastInteraction":1650928751577,"sessionStart":1650928751577,"sessionEndDate":1650945600000,"experiment":""}; _ga_DHGVGHHXFP=GS1.1.1650928738.7.1.1650928756.0; _dd_s=logs=1&id=c0718bfa-7f25-48e2-972d-5a763f0617e1&created=1650928737872&expire=1650929662949',
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
    for i in sel.xpath('//div[@class="standard-card-new__thumbnail"]/a/@href'):
        lst.append("https://www.bbcgoodfood.com/"+ i.get())
    
    return lst


# In[42]:


htmlOnePageSpider("https://www.bbcgoodfood.com/search?q=Vietnamese+recipes", htmlLst)


# In[43]:


htmlOnePageSpider("https://www.bbcgoodfood.com/search/recipes/page/2/?q=Vietnamese+recipes&sort=-relevance", htmlLst)


# In[44]:


htmlOnePageSpider("https://www.bbcgoodfood.com/search/recipes/page/3/?q=Vietnamese+recipes&sort=-relevance", htmlLst)


# In[45]:


# the number of recipes we have in total
len(htmlLst)


# In[71]:


# 3. go through all recipe htmls and scrape the data we want

Vietnamdata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def VietnamSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'permutive-id=5835e452-1c7b-4c2e-8967-71d3a86a12d3; _gcl_au=1.1.408235534.1648822842; _hjid=273e0100-d247-42bc-b109-34f0e125c526; ntv_as_us_privacy=1---; _hjSessionUser_1704279=eyJpZCI6IjExOWM4MDFjLTAxZTgtNTdmOS1hNDI2LTFiMGFiYjE5NzNkMiIsImNyZWF0ZWQiOjE2NDg4MjI4NDIwMDcsImV4aXN0aW5nIjp0cnVlfQ==; _ntv_uid=6a8b6277-5f6e-4dab-a3fe-a89932a5a548; euconsent-v2=CPWvoUAPWvoUAAKAoAENCJCsAP_AAH_AAAwIIqNd_X9_bX9j-_5_f_t0eY1P9_r3_-QzjhfNt-8F3L_W_L0X42E7NF36pq4KuR4Eu3LBIQNlHMHUTUmwaokVrzHsYk2cpyNKJ7LEmnMZO2dYGHtPn9lDuYKY7_5___bz3j-v_t_-39T378Xf3_d5_2---vCfV599jbv9f3__39nP___9v-_8_______BFMAkw1LyALsyxwZNo0qhRAjCsJCqBQAUUAwtEVgA4OCnZWAT6ghYAIBUhGBECDEFGDAIABBIAkIiAkALBAIgCIBAACABEAhAARMAgsALAwCAAUA0LEAKAAQJCDI4IjlMCAqRKKCWysQSgr2NMIAyzwIoFEZFQAIkmgBYGQkLBzHAEgJeLJA0xQvkAIwAAAAA.f_gAAAAAAAAA; addtl_consent=1~39.4.3.9.6.9.13.6.4.15.9.5.2.7.4.1.7.1.3.2.10.3.5.4.21.4.6.9.7.10.2.9.2.18.7.6.14.5.20.6.5.1.3.1.11.29.4.14.4.5.3.10.6.2.9.6.6.4.5.4.4.29.4.5.3.1.6.2.2.17.1.17.10.9.1.8.6.2.8.3.4.142.4.8.35.7.15.1.14.3.1.8.10.25.3.7.25.5.18.9.7.41.2.4.18.21.3.4.2.1.6.6.5.2.14.18.7.3.2.2.8.20.8.8.6.3.10.4.20.2.13.4.6.4.11.1.3.22.16.2.6.8.2.4.11.6.5.33.11.8.1.10.28.12.1.3.21.2.7.6.1.9.30.17.4.9.15.8.7.3.6.6.7.2.4.1.7.12.13.22.13.2.12.2.10.1.4.15.2.4.9.4.5.4.7.13.5.15.4.13.4.14.8.2.15.2.5.5.1.2.2.1.2.14.7.4.8.2.9.10.18.12.13.2.18.1.1.3.1.1.9.25.4.1.19.8.4.5.2.1.5.4.8.4.2.2.2.14.2.13.4.2.6.9.6.3.4.3.5.2.3.6.10.11.6.3.16.3.11.3.1.2.3.9.19.11.15.3.10.7.6.4.3.4.6.3.3.3.3.1.1.1.6.11.3.1.1.7.4.6.1.10.5.2.6.3.2.2.4.3.2.2.7.2.13.7.12.2.1.3.3.4.5.4.3.2.2.4.1.3.1.1.1.2.9.1.6.9.1.5.2.1.7.2.8.11.1.3.1.1.2.1.3.2.6.1.11.1.5.3.1.3.1.1.2.2.7.7.1.4.1.2.6.1.2.1.1.3.1.1.4.1.1.2.1.8.1.7.4.3.2.1.3.5.3.9.6.1.15.10.28.1.2.2.12.3.4.1.6.3.4.7.1.3.1.1.3.1.5.3.1.3.2.2.1.1.4.2.1.2.1.1.1.2.2.4.2.1.2.2.2.4.1.1.1.2.2.1.1.1.1.2.1.1.1.2.2.1.1.2.1.2.1.7.1.2.1.1.1.2.1.1.1.1.2.1.1.3.2.1.1.8.1.1.1.5.2.1.6.5.1.1.1.1.1.2.2.3.1.1.4.1.1.2.2.1.1.4.2.1.1.2.2.1.2.1.2.3.1.1.2.4.1.1.1.5.1.3.6.3.1.5.2.3.4.1.2.3.1.4.2.1.2.2.2.1.1.1.1.1.1.11.1.3.1.1.2.2.1.4.2.3.3.4.1.1.1.1.4.2.1.1.2.5.1.9.4.1.1.3.1.7.1.4.5.1.7.2.1.1.1.2.1.1.1.4.2.1.12.1.1.3.1.2.2.3.1.2.1.1.1.2.1.1.2.1.1.1.1.2.1.3.1.5.1.2.4.3.8.2.2.9.7.2.2.1.2.1.4; __pnahc=0; cX_P=l1gijs6lj0m8nycv; __pat=0; cX_G=cx:10zshf2govoi7q2dmu1gfko7s:9cw6x07yr4yl; __gads=ID=f32abf06fadf8f45:T=1648822844:S=ALNI_MatxtBh2Dh9uip2RxShqDHlDFTc0g; cX_S=l1vn15p46ir1tt8g; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; _pbjs_userid_consent_data=3798996786539642; _pubcid=f6504317-56ef-4766-b328-69c37bfe98bb; _gid=GA1.2.759115504.1650766562; cto_bidid=9Ny0718xR0dsdHZzQ1pLRmpYV3RkUUtmTElsSHA5ZUtZWWN5SVVnbTlBOEpLSmlTRW5yTzgzT0xjUDNadFU1VFU0eCUyQjRMaGVYYXpaTUdCNE9YdXhRZDMyM0c1TkJReUx1VFRuVDI1ZEw3SWJLcEVDYzFsdGZQcUprSyUyQnhZU3ZKSU1QT09qJTJCNHlVSSUyQm95ekNYbk1FWnpUUG5rUSUzRCUzRA; cto_bundle=ZRiszl9PaGFsUHJ3bklPVjZyUDhZV2w2elJjN3JmMHQ0TWlJT2VjWTB4c0dpRnlMTGt0YW9ucDN6WFhicjVPYlE4WEVhcmxLN2o5JTJCMFpLaWc0bzhHU2taYyUyQlZaV2pnOWFwUDhsMyUyQkRCS1djOE0wRFB0eDZDT3kzTjZUN2NsdEJnZUtjUmVYSUJaSzZ1czVHbXhaNVoyYkp1a2J4dEVuU1MxYlVkRktzc2R5OVNwZjZIRkRRb2ZXbWx1bHZESnpVb1l4UGxCWVJFZHlPZFR3THlJU0xUa1hXZTdRJTNEJTNE; _lr_env_src_ats=false; pbjs-unifiedid={"TDID":"b8e2d1cd-d84b-4c0b-b941-7dc42e3021de","TDID_LOOKUP":"TRUE","TDID_CREATED_AT":"2022-03-24T02:16:06"}; idl_env=Anm6LivIFUrH8iQ6AjQji4lhT_RxYQd8S-5_e4TO7AcONmRI2Os-38PlpoZpXWZjUWfkY01zjOscLbHtKsnMjWsp2vWEXhJ4BNcjiAPGLuTbOtgwv3UYwxPNNX2B-W9ErM-PEp2c87WXGryWWeGns4dYTNXtVYN3hNXRRon64EJqQbNAWAlnHdxFIE22hbOxuTfNs2jhIfIs-WVlKEPlLqYUirfY; _cc_id=589744b018b77ff0c829dd767a86ed67; panoramaId=eaffbaa0b1b49b5c6c7edf9dac1f4945a702da40840206bc42cc04d32b6506cc; panoramaId_expiry=1651371366975; DM_SitId967=true; DM_SitId967SecId5289=true; _usrp_lq=20220524; lux_uid=165092873747194360; AMP_TOKEN=$NOT_FOUND; _dc_gtm_UA-6065919-6=1; __gpi=UID=000004b0a4a888f9:T=1650766562:RT=1650928739:S=ALNI_MYgxeHnQCYlGaAHoSgAeOPgMcZnJg; _hjIncludedInSessionSample=0; _hjSession_1704279=eyJpZCI6IjVhZjQ1OWM5LTgxYzQtNDk3NS1iZGI5LTQzNGZhNTg1ZmU2OCIsImNyZWF0ZWQiOjE2NTA5Mjg3NDc1NTYsImluU2FtcGxlIjpmYWxzZX0=; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; DM_SitIdT967=true; DM_SitId967SecIdT5289=true; __pvi={"id":"v-l2fccfcgb18pjvyd","domain":".bbcgoodfood.com","time":1650928750567}; __tbc={kpex}TjotZ-RrLOgtQcHulfFH96UlJKcce-hFpY-MlFSyRjd4Tx2_61m1sM1RRp6MznN3; xbc={kpex}Pj5227ObcEz57ooEdnOloNB_Duf79J7GlP0P_hotdIcM2JFDsQTJiTnh8h5QyWOb_1qlfo18DTQE9juYp2YCVyaTXbRygZ10zMQVuqmMwYnkKRZSqEGsnDn6MH6rj9VEAHeTED4NmXNJek7HIm1kNCoSqjMwukVMnhhHqve5A4qscU9koCnjCe96QxEojB5_; _ga=GA1.2.1284257515.1648822841; ntvSession={"id":9791310,"placementID":1099124,"lastInteraction":1650928751577,"sessionStart":1650928751577,"sessionEndDate":1650945600000,"experiment":""}; _ga_DHGVGHHXFP=GS1.1.1650928738.7.1.1650928756.0; _dd_s=logs=1&id=c0718bfa-7f25-48e2-972d-5a763f0617e1&created=1650928737872&expire=1650929662949',
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

def fillVietnamData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = VietnamSpider(html)
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
        fillVietnamData(html,Vietnamdata)
    except:
        time.sleep(5)

# convert data to dataframe
Vietnam2 = pd.DataFrame(Vietnamdata)
print(Vietnam2.shape)
Vietnam2.head()


# In[73]:


Vietnam2["Source"] = ["Web2" for i in range(len(Vietnam2))]
Vietnam2.head()


# In[74]:


VietnamFull = pd.concat([Vietnam,Vietnam2])


# In[75]:


VietnamFull.head()


# In[76]:


VietnamFull.shape


# In[77]:


# save dataset
VietnamFull.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Vietnam.csv")


# In[ ]:




