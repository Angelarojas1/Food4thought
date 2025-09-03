#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Australia

# In[26]:


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


# In[27]:


# 1. create a list to store all recipe collection htmls

# initialize collectionLst to store all recipe collection page urls
collectionLst = []

def collectionPageSpider(category_url,lst):
    """
    input: category_url, the url of one page of the recipe web
    input: lst: the initial list
    output: collectionLst with all collection page htmls on the category_url
    
    """
    
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'nk=6a58b6ed906d59ead938957ef3f352c4; onb_login_comp=1; _cb_ls=1; _cb=CdOv1PC2OKAVB9kTKc; _ga=GA1.3.1984142484.1633383785; _gcl_au=1.1.1633263314.1633383785; _hjid=5fa52c5c-bebc-4b1b-8ba8-e453693da0e2; _fbp=fb.2.1633383785287.850317695; _pbjs_userid_consent_data=3524755945110770; _lr_env_src_ats=false; _pin_unauth=dWlkPU5Ua3lZekJpTXpndE1XRTROUzAwTTJFd0xUaGlZMk10WlRFeU9UYzVZVEV6WmpZMg; gig_canary=false; lux_uid=163424338170758208; AMCVS_5FE61C8B533204850A490D4D@AdobeOrg=1; nearSessionCookie=0.1580301119216747; _cb_svref=null; _ncg_sp_ses.f8aa=*; _gid=GA1.3.2087277443.1634243382; _hjAbsoluteSessionInProgress=1; _lr_retry_request=true; gig_bootstrap_3_TfaX-FA1vKPNe3VJh1r2gMnu655two0v7c6yQZ8W-S0_8d0eh2AObunlY9GC-Z8_=login_ver4; nlm_gig_login=0; _ncid=98839ec34a7ce83bab529546e8d0b154; s_gdslv_s=First Visit; s_cc=true; nc_aam_segs=asgmnt=16675898; aam_uuid=87393916760910473647345340690129581144; _lr_sampling_rate=0; __gads=ID=01a902e4ef3620c9:T=1634243383:S=ALNI_MbdjYQFhOvuMPwmxB7bmZ9C81weuA; _ncg_id_=17c807f3741-e1d22672-b2c9-4d69-985a-26def7265c7d; AMCV_5FE61C8B533204850A490D4D@AdobeOrg=77933605|MCIDTS|18915|MCMID|87369867538125815987342953393121797442|MCAAMLH-1634848213|7|MCAAMB-1634848213|RKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y|MCOPTOUT-1634250613s|NONE|MCAID|2FD5C74F0515A8D2-40000649925735BE|vVersion|4.5.1|MCCIDH|-160885546; _v__chartbeat3=CxTidYBR_0xtBJVIlr; cSuburb=Margaret River; cPostcode=6285; trc_cookie_storage=taboola%20global%3Auser-id=074f5e7f-12e2-4f7b-8dd0-b9c4c52e88bf-tuct6587ebc; vidoraUserId=i43m5aojk5c3km6s66r2hspr6g57vu; _cc_id=589744b018b77ff0c829dd767a86ed67; panoramaId_expiry=1634848259633; panoramaId=2afcbfcbd6c567587a0be67eead14945a702fcc603a25c7f187cc14c07f09899; _hjIncludedInSessionSample=1; s_sq=[[B]]; gig_canary_ver=12471-3-27237405; utag_main=v_id:017c4d429faf000a40d27faf0fb903079001907100942$_sn:2$_se:36$_ss:0$_st:1634247151153$ses_id:1634243381838;exp-session$_pn:36;exp-session; _chartbeat2=.1633383784813.1634245351331.10000000001.CVckn4DHLIW4Cm1nd_DM3YHkXkfOo.36; _tb_sess_r=https://www.taste.com.au/recipes/collections?page=1&sort=recent; _tb_t_ppg=https://www.taste.com.au/recipes/collections/pork-slow-cooker-recipes; s_nr=1634245351790-New; s_gdslv=1634245351791; s_ppn=taste|recipe|collection|pork slow cooker recipes; _derived_epik=dj0yJnU9UnU4WmpraW5UVTE3RU4tYkg5Z29TS3hXUzJsNDdSMF8mbj1tUEdJOWJDN1J3U2x1MTByNHl6Ylh3Jm09MSZ0PUFBQUFBR0ZvbXVjJnJtPTEmcnQ9QUFBQUFHRm9tdWM; _ncg_sp_id.f8aa=8e79ccf0-c360-4309-8e36-b75f638dc692.1633383785.2.1634245352.1633383785.d761339e-096c-4a9c-b3fe-c4af9a297465; cto_bundle=TwE7iF9CdjJVUnlOVHZGczRHZEtmZERGbnBsbkVPWjhiQURQY1ByM0dDNDJJQXc3eG44TzZxbkUyclBFdyUyRmk0SkJLQzJmM0VyY1llSjV2QjhWNW8yJTJGWSUyQkZJZlRQSXhsZUM5QUwlMkIxWEl5Tk1OUU5sc1VWVCUyQkNXZzBkbnBDc3BSRnIySVo2dVlmNEY0Nkg2bnNjNUJCWklJR1JoZW84WFNlOXc1Y0JKd0xVZ3J4RUcxNGYzWWVEa0Vkczl5S2ZlUW00T1JB; tp=8883; s_ppv=taste%7Crecipes%7Cindex%7Ccollections,14,14,1245',
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
    for i in sel.xpath('//ol[@class="content-lists-items list-unstyled"]/li'):
        collectionPage = "https://www.taste.com.au/"+ i.xpath('.//a[@class="col-sm-5"]/@href').get('')
        lst.append(collectionPage)
        
    return lst


# In[28]:


# test with the first page:
collectionPageSpider("https://www.taste.com.au/recipes/collections?page=1&sort=recent",collectionLst)


# In[29]:


# go through all pages in the web and get all recipe collection pages

def AllcollectionPageSpider(page_number):
    """
    input: page_number, the total number of pages of one category
    output: collectionLst with all recipe collection htmls on all pages
    
    """
    # initialize pageLst to store the htmls of all pages
    pageLst = []
    
    for i in range(1,page_number+1):
        pageLst.append("https://www.taste.com.au/recipes/collections?page={}&sort=recent".format(i))
    
    # go over each page and get recipe collection urls    
    collectionLst = []
    for i in pageLst:
        collectionLst = collectionPageSpider(i,collectionLst) 
        
    return collectionLst

collectionLst = AllcollectionPageSpider(73)


# In[30]:


collectionLst


# In[42]:


# 2. go through all recipe collection pages and get the recipe urls inside

# initialize htmlDic to store the htmls of all recipes
htmlLst = []

def RecipePageSpider(collection_url,lst):
    """
    input: collection_url, the url of recipe collection page
    input: lst, the initial htmlLst
    output: htmlDic with all recipe htmls on one collection page
    
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'nk=6a58b6ed906d59ead938957ef3f352c4; onb_login_comp=1; _cb_ls=1; _cb=CdOv1PC2OKAVB9kTKc; _ga=GA1.3.1984142484.1633383785; _gcl_au=1.1.1633263314.1633383785; _hjid=5fa52c5c-bebc-4b1b-8ba8-e453693da0e2; _fbp=fb.2.1633383785287.850317695; _pbjs_userid_consent_data=3524755945110770; _lr_env_src_ats=false; _pin_unauth=dWlkPU5Ua3lZekJpTXpndE1XRTROUzAwTTJFd0xUaGlZMk10WlRFeU9UYzVZVEV6WmpZMg; gig_canary=false; lux_uid=163424338170758208; AMCVS_5FE61C8B533204850A490D4D@AdobeOrg=1; nearSessionCookie=0.1580301119216747; _cb_svref=null; _ncg_sp_ses.f8aa=*; _gid=GA1.3.2087277443.1634243382; _hjAbsoluteSessionInProgress=1; _lr_retry_request=true; gig_bootstrap_3_TfaX-FA1vKPNe3VJh1r2gMnu655two0v7c6yQZ8W-S0_8d0eh2AObunlY9GC-Z8_=login_ver4; nlm_gig_login=0; _ncid=98839ec34a7ce83bab529546e8d0b154; s_gdslv_s=First Visit; s_cc=true; nc_aam_segs=asgmnt=16675898; aam_uuid=87393916760910473647345340690129581144; _lr_sampling_rate=0; __gads=ID=01a902e4ef3620c9:T=1634243383:S=ALNI_MbdjYQFhOvuMPwmxB7bmZ9C81weuA; _ncg_id_=17c807f3741-e1d22672-b2c9-4d69-985a-26def7265c7d; AMCV_5FE61C8B533204850A490D4D@AdobeOrg=77933605|MCIDTS|18915|MCMID|87369867538125815987342953393121797442|MCAAMLH-1634848213|7|MCAAMB-1634848213|RKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y|MCOPTOUT-1634250613s|NONE|MCAID|2FD5C74F0515A8D2-40000649925735BE|vVersion|4.5.1|MCCIDH|-160885546; _v__chartbeat3=CxTidYBR_0xtBJVIlr; cSuburb=Margaret River; cPostcode=6285; trc_cookie_storage=taboola%20global%3Auser-id=074f5e7f-12e2-4f7b-8dd0-b9c4c52e88bf-tuct6587ebc; vidoraUserId=i43m5aojk5c3km6s66r2hspr6g57vu; _cc_id=589744b018b77ff0c829dd767a86ed67; panoramaId_expiry=1634848259633; panoramaId=2afcbfcbd6c567587a0be67eead14945a702fcc603a25c7f187cc14c07f09899; _hjIncludedInSessionSample=1; s_sq=[[B]]; gig_canary_ver=12471-3-27237405; utag_main=v_id:017c4d429faf000a40d27faf0fb903079001907100942$_sn:2$_se:36$_ss:0$_st:1634247151153$ses_id:1634243381838;exp-session$_pn:36;exp-session; _chartbeat2=.1633383784813.1634245351331.10000000001.CVckn4DHLIW4Cm1nd_DM3YHkXkfOo.36; _tb_sess_r=https://www.taste.com.au/recipes/collections?page=1&sort=recent; _tb_t_ppg=https://www.taste.com.au/recipes/collections/pork-slow-cooker-recipes; s_nr=1634245351790-New; s_gdslv=1634245351791; s_ppn=taste|recipe|collection|pork slow cooker recipes; _derived_epik=dj0yJnU9UnU4WmpraW5UVTE3RU4tYkg5Z29TS3hXUzJsNDdSMF8mbj1tUEdJOWJDN1J3U2x1MTByNHl6Ylh3Jm09MSZ0PUFBQUFBR0ZvbXVjJnJtPTEmcnQ9QUFBQUFHRm9tdWM; _ncg_sp_id.f8aa=8e79ccf0-c360-4309-8e36-b75f638dc692.1633383785.2.1634245352.1633383785.d761339e-096c-4a9c-b3fe-c4af9a297465; cto_bundle=TwE7iF9CdjJVUnlOVHZGczRHZEtmZERGbnBsbkVPWjhiQURQY1ByM0dDNDJJQXc3eG44TzZxbkUyclBFdyUyRmk0SkJLQzJmM0VyY1llSjV2QjhWNW8yJTJGWSUyQkZJZlRQSXhsZUM5QUwlMkIxWEl5Tk1OUU5sc1VWVCUyQkNXZzBkbnBDc3BSRnIySVo2dVlmNEY0Nkg2bnNjNUJCWklJR1JoZW84WFNlOXc1Y0JKd0xVZ3J4RUcxNGYzWWVEa0Vkczl5S2ZlUW00T1JB; tp=8883; s_ppv=taste%7Crecipes%7Cindex%7Ccollections,14,14,1245',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    response = requests.get(collection_url,headers=headers)
    sel = Selector(response.text)
    for i in sel.xpath('//ol[@class="col-items-2-with-lead"]/li'):
        recipePage = "https://www.taste.com.au/"+ i.xpath('.//a/@href').get('')
        lst.append(recipePage)
        
    return lst
    
for i in collectionLst:
    htmlLst = RecipePageSpider(i,htmlLst)
    
print("The number of recipes is {}".format(len(htmlLst)))


# In[43]:


htmlLst


# In[68]:


# 3. go through all recipe htmls and scrape the data we want

Australiadata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def AustraliaSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'nk=6a58b6ed906d59ead938957ef3f352c4; onb_login_comp=1; _cb_ls=1; _cb=CdOv1PC2OKAVB9kTKc; _ga=GA1.3.1984142484.1633383785; _gcl_au=1.1.1633263314.1633383785; _hjid=5fa52c5c-bebc-4b1b-8ba8-e453693da0e2; _fbp=fb.2.1633383785287.850317695; _pbjs_userid_consent_data=3524755945110770; _lr_env_src_ats=false; _pin_unauth=dWlkPU5Ua3lZekJpTXpndE1XRTROUzAwTTJFd0xUaGlZMk10WlRFeU9UYzVZVEV6WmpZMg; gig_canary=false; lux_uid=163424338170758208; AMCVS_5FE61C8B533204850A490D4D@AdobeOrg=1; nearSessionCookie=0.1580301119216747; _cb_svref=null; _ncg_sp_ses.f8aa=*; _gid=GA1.3.2087277443.1634243382; _hjAbsoluteSessionInProgress=1; _lr_retry_request=true; gig_bootstrap_3_TfaX-FA1vKPNe3VJh1r2gMnu655two0v7c6yQZ8W-S0_8d0eh2AObunlY9GC-Z8_=login_ver4; nlm_gig_login=0; _ncid=98839ec34a7ce83bab529546e8d0b154; s_gdslv_s=First Visit; s_cc=true; nc_aam_segs=asgmnt=16675898; aam_uuid=87393916760910473647345340690129581144; _lr_sampling_rate=0; __gads=ID=01a902e4ef3620c9:T=1634243383:S=ALNI_MbdjYQFhOvuMPwmxB7bmZ9C81weuA; _ncg_id_=17c807f3741-e1d22672-b2c9-4d69-985a-26def7265c7d; AMCV_5FE61C8B533204850A490D4D@AdobeOrg=77933605|MCIDTS|18915|MCMID|87369867538125815987342953393121797442|MCAAMLH-1634848213|7|MCAAMB-1634848213|RKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y|MCOPTOUT-1634250613s|NONE|MCAID|2FD5C74F0515A8D2-40000649925735BE|vVersion|4.5.1|MCCIDH|-160885546; _v__chartbeat3=CxTidYBR_0xtBJVIlr; cSuburb=Margaret River; cPostcode=6285; trc_cookie_storage=taboola%20global%3Auser-id=074f5e7f-12e2-4f7b-8dd0-b9c4c52e88bf-tuct6587ebc; vidoraUserId=i43m5aojk5c3km6s66r2hspr6g57vu; _cc_id=589744b018b77ff0c829dd767a86ed67; panoramaId_expiry=1634848259633; panoramaId=2afcbfcbd6c567587a0be67eead14945a702fcc603a25c7f187cc14c07f09899; _hjIncludedInSessionSample=1; s_sq=[[B]]; gig_canary_ver=12471-3-27237405; utag_main=v_id:017c4d429faf000a40d27faf0fb903079001907100942$_sn:2$_se:36$_ss:0$_st:1634247151153$ses_id:1634243381838;exp-session$_pn:36;exp-session; _chartbeat2=.1633383784813.1634245351331.10000000001.CVckn4DHLIW4Cm1nd_DM3YHkXkfOo.36; _tb_sess_r=https://www.taste.com.au/recipes/collections?page=1&sort=recent; _tb_t_ppg=https://www.taste.com.au/recipes/collections/pork-slow-cooker-recipes; s_nr=1634245351790-New; s_gdslv=1634245351791; s_ppn=taste|recipe|collection|pork slow cooker recipes; _derived_epik=dj0yJnU9UnU4WmpraW5UVTE3RU4tYkg5Z29TS3hXUzJsNDdSMF8mbj1tUEdJOWJDN1J3U2x1MTByNHl6Ylh3Jm09MSZ0PUFBQUFBR0ZvbXVjJnJtPTEmcnQ9QUFBQUFHRm9tdWM; _ncg_sp_id.f8aa=8e79ccf0-c360-4309-8e36-b75f638dc692.1633383785.2.1634245352.1633383785.d761339e-096c-4a9c-b3fe-c4af9a297465; cto_bundle=TwE7iF9CdjJVUnlOVHZGczRHZEtmZERGbnBsbkVPWjhiQURQY1ByM0dDNDJJQXc3eG44TzZxbkUyclBFdyUyRmk0SkJLQzJmM0VyY1llSjV2QjhWNW8yJTJGWSUyQkZJZlRQSXhsZUM5QUwlMkIxWEl5Tk1OUU5sc1VWVCUyQkNXZzBkbnBDc3BSRnIySVo2dVlmNEY0Nkg2bnNjNUJCWklJR1JoZW84WFNlOXc1Y0JKd0xVZ3J4RUcxNGYzWWVEa0Vkczl5S2ZlUW00T1JB; tp=8883; s_ppv=taste%7Crecipes%7Cindex%7Ccollections,14,14,1245',
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
    content = json.loads(sel.xpath('//script[@type="application/ld+json" and @data-schema-entity="recipe"]/text()').get(''))
    
    return content

def fillAustraliaData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = AustraliaSpider(html)
    dic['Name of the recipe'].append(content['name'])
    dic['Total time'].append(content['totalTime'])
    dic['Prep time'].append(content['prepTime'])
    dic['Cook time'].append(content['cookTime'])
    dic['List of ingredients'].append(content['recipeIngredient'])
    dic['List of instructions'].append(content['recipeInstructions'])
    dic['Number of servings'].append(content['recipeYield'])
    dic['Category'].append(content['recipeCategory'])    


# In[69]:


# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillAustraliaData(html,Australiadata)
    except:
        time.sleep(5)


# In[70]:


# convert data to dataframe
Australia = pd.DataFrame(Australiadata)
print(Australia.shape)
Australia.head()

# save dataset
Australia.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Australia.csv")


# In[ ]:




