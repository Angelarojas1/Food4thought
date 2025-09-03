#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Senegal
# 

# https://www.cuisineaz.com/cuisine-du-monde/senegal-p248

# In[10]:


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


# In[26]:


# 1. create a list to store all recipe htmls on one page
# initialize htmlLst to store the htmls of all recipes
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
        'cookie':'_pk_id.1.ecc7=d08778f2b7669389.1649735305.; euconsent-v2=CPSkqYAPSkqYAAHABBENCKCsAP_AAAAAAAAAGatf_X9fb2vj-_599_t0eY1f9_63v-wzjheNs-8NyZ_X_L4Xu2MSvA36pq4KmR4Eu3LBAQVlHOHcTQkQwIkVqTDsbk2Mr7NKJ7LEmlMbe2dYGH9vn8XT-ZKY70____77_3-_____7rbgAAAJJQAYAAgiqGgAwABBFUVABgACCKpSADAAEEVR0AGAAIIqkIAMAAQRVCQAYAAgiqIgAwABBFUZABgACCKo.f_gAAAAAAAAA; cmp_purposes_consent=mesureda-HY6ZcLLx,cookieses-R33h7ChN,personnali-jBpkK8Bc,publicite-eLJ3zYea,reseauxso-QbRzQaZJ,cookies,select_basic_ads,create_ads_profile,create_content_profile,measure_ad_performance,measure_content_performance,market_research,improve_products,select_personalized_ads,select_personalized_content,geolocation_data,device_characteristics,; mics_vid=19012670432; __gads=ID=cc70739effffe6fa:T=1649735308:S=ALNI_MY8lzAbm3QNtTn2xhqS8OljDhIivw; cookie_consent_rules=1:1,2:1,3:1,4:1; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; device_id=8bed643741b2eae38efeb9346e006933b68bc1537a128c966ed46798d60abb3a; __aaxsc=2; mics_lts=1650152291935; _gid=GA1.2.1551851492.1650918699; aasd=4|1650918700491; _pk_ref.1.ecc7=["","",1651001554,"https://www.google.com/"]; _pk_ses.1.ecc7=1; __gpi=UID=0000048e61ee9000:T=1650152292:RT=1651001557:S=ALNI_MbODXqOOUXVNX2XVBs8BDbTqdYMog; _gat_UA-642667-1=1; _ga_M8JRPG77BV=GS1.1.1651001553.8.1.1651002037.0; _ga=GA1.2.414860327.1649735308',
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
    for i in json.loads(sel.xpath('//script[@type="application/ld+json"]/text()').get(''))[1]['itemListElement']:
        lst.append(i['url'])
        
    return lst


# In[27]:


htmlOnePageSpider('https://www.cuisineaz.com/cuisine-du-monde/senegal-p248', htmlLst)


# In[28]:


htmlOnePageSpider('https://www.cuisineaz.com/recettes-senegalaises-p248?page=2', htmlLst)


# In[29]:


# the number of recipes we have in total
len(htmlLst)


# In[54]:


# 3. go through all recipe htmls and scrape the data we want

Senegaldata = {
    "Name of the recipe":[],
    "Total time":[],
    "Cook time":[],
    "Prep time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def SenegalSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_pk_id.1.ecc7=d08778f2b7669389.1649735305.; euconsent-v2=CPSkqYAPSkqYAAHABBENCKCsAP_AAAAAAAAAGatf_X9fb2vj-_599_t0eY1f9_63v-wzjheNs-8NyZ_X_L4Xu2MSvA36pq4KmR4Eu3LBAQVlHOHcTQkQwIkVqTDsbk2Mr7NKJ7LEmlMbe2dYGH9vn8XT-ZKY70____77_3-_____7rbgAAAJJQAYAAgiqGgAwABBFUVABgACCKpSADAAEEVR0AGAAIIqkIAMAAQRVCQAYAAgiqIgAwABBFUZABgACCKo.f_gAAAAAAAAA; cmp_purposes_consent=mesureda-HY6ZcLLx,cookieses-R33h7ChN,personnali-jBpkK8Bc,publicite-eLJ3zYea,reseauxso-QbRzQaZJ,cookies,select_basic_ads,create_ads_profile,create_content_profile,measure_ad_performance,measure_content_performance,market_research,improve_products,select_personalized_ads,select_personalized_content,geolocation_data,device_characteristics,; mics_vid=19012670432; __gads=ID=cc70739effffe6fa:T=1649735308:S=ALNI_MY8lzAbm3QNtTn2xhqS8OljDhIivw; cookie_consent_rules=1:1,2:1,3:1,4:1; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; device_id=8bed643741b2eae38efeb9346e006933b68bc1537a128c966ed46798d60abb3a; __aaxsc=2; mics_lts=1650152291935; _gid=GA1.2.1551851492.1650918699; aasd=4|1650918700491; _pk_ref.1.ecc7=["","",1651001554,"https://www.google.com/"]; _pk_ses.1.ecc7=1; __gpi=UID=0000048e61ee9000:T=1650152292:RT=1651001557:S=ALNI_MbODXqOOUXVNX2XVBs8BDbTqdYMog; _gat_UA-642667-1=1; _ga_M8JRPG77BV=GS1.1.1651001553.8.1.1651002037.0; _ga=GA1.2.414860327.1649735308',
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
    content = json.loads(sel.xpath('//script[@type="application/ld+json"]/text()')[0].get())[0]
    
    return content

def fillSenegalData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = SenegalSpider(html)
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


# In[55]:


# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillSenegalData(html,Senegaldata)
    except:
        time.sleep(5)


# In[56]:


# convert data to dataframe
Senegal = pd.DataFrame(Senegaldata)
print(Senegal.shape)
Senegal.head()


# In[57]:


Senegal["Source"] = ["Web1" for i in range(len(Senegal))]
Senegal.head()


# https://cuisine-journaldesfemmes-fr.translate.goog/idees-recettes/2744099-recette-senegalaise/?_x_tr_sl=fr&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp

# In[68]:


# 1. create a list to store all recipe htmls on one page
# initialize htmlLst to store the htmls of all recipes
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
        'cookie':'_ga.group=GA1.3.526890599.1650829648; _ga=GA1.3.526890599.1650829648; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; _ga.group_gid=GA1.3.158473750.1651002046; _gid=GA1.3.2133373155.1651002049; _pbjs_userid_consent_data=6236659365018726; _lr_retry_request=true; _lr_env_src_ats=false; _gat_groupTracker=1; outbrain_cid_fetch=true; cto_bundle=XVtaPF9reHVLUFdDV2NrVXlXRjdaSVkzbGN1cFYlMkZ6aTdGZUU0RFJnYXhFc1NKc0dLTm9ERG1DMWtsJTJCcjdnNEJVYTJCa1Y5TkM1Nzl4dGRJQ3AxSnpXNSUyRkdNaFUyTSUyRlN1MlRZSlRWaEtrMzlSTFNMYiUyRk1FVUY2UGRTQlVhUDU0OHVDZ1htSWZPenZOdW56JTJCckFkYXc3d1hMNzc4dnV2U2ZxVFdQWEU0RE1jeFZzREtMWkVFYmdOWlNDb3dFWmc0M3FiTFQxc2RtNnlUeDRlYUJCQTZOT29BSUV3JTNEJTNE; _gat=1',
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
    for i in json.loads(sel.xpath('//script[@type="application/ld+json"]/text()')[0].get())[2]['itemListElement']:
        lst.append(i['url'])
        
    return lst


# In[69]:


htmlOnePageSpider('https://cuisine-journaldesfemmes-fr.translate.goog/idees-recettes/2744099-recette-senegalaise/?_x_tr_sl=fr&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=wapp', htmlLst)


# In[70]:


# the number of recipes we have in total
len(htmlLst)


# In[72]:


headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_ga.group=GA1.3.526890599.1650829648; _ga=GA1.3.526890599.1650829648; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; _ga.group_gid=GA1.3.158473750.1651002046; _gid=GA1.3.2133373155.1651002049; _pbjs_userid_consent_data=6236659365018726; _lr_retry_request=true; _lr_env_src_ats=false; _gat_groupTracker=1; outbrain_cid_fetch=true; cto_bundle=XVtaPF9reHVLUFdDV2NrVXlXRjdaSVkzbGN1cFYlMkZ6aTdGZUU0RFJnYXhFc1NKc0dLTm9ERG1DMWtsJTJCcjdnNEJVYTJCa1Y5TkM1Nzl4dGRJQ3AxSnpXNSUyRkdNaFUyTSUyRlN1MlRZSlRWaEtrMzlSTFNMYiUyRk1FVUY2UGRTQlVhUDU0OHVDZ1htSWZPenZOdW56JTJCckFkYXc3d1hMNzc4dnV2U2ZxVFdQWEU0RE1jeFZzREtMWkVFYmdOWlNDb3dFWmc0M3FiTFQxc2RtNnlUeDRlYUJCQTZOT29BSUV3JTNEJTNE; _gat=1',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
response = requests.get(htmlLst[0],headers=headers)
sel = Selector(response.text)


# In[74]:


json.loads(sel.xpath('//script[@type="application/ld+json"]/text()')[0].get())[0]


# In[75]:


# 3. go through all recipe htmls and scrape the data we want

Senegaldata = {
    "Name of the recipe":[],
    "Total time":[],
    "Cook time":[],
    "Prep time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def SenegalSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_ga.group=GA1.3.526890599.1650829648; _ga=GA1.3.526890599.1650829648; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; _ga.group_gid=GA1.3.158473750.1651002046; _gid=GA1.3.2133373155.1651002049; _pbjs_userid_consent_data=6236659365018726; _lr_retry_request=true; _lr_env_src_ats=false; _gat_groupTracker=1; outbrain_cid_fetch=true; cto_bundle=XVtaPF9reHVLUFdDV2NrVXlXRjdaSVkzbGN1cFYlMkZ6aTdGZUU0RFJnYXhFc1NKc0dLTm9ERG1DMWtsJTJCcjdnNEJVYTJCa1Y5TkM1Nzl4dGRJQ3AxSnpXNSUyRkdNaFUyTSUyRlN1MlRZSlRWaEtrMzlSTFNMYiUyRk1FVUY2UGRTQlVhUDU0OHVDZ1htSWZPenZOdW56JTJCckFkYXc3d1hMNzc4dnV2U2ZxVFdQWEU0RE1jeFZzREtMWkVFYmdOWlNDb3dFWmc0M3FiTFQxc2RtNnlUeDRlYUJCQTZOT29BSUV3JTNEJTNE; _gat=1',
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
    content = json.loads(sel.xpath('//script[@type="application/ld+json"]/text()')[0].get())[0]
    
    return content

def fillSenegalData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = SenegalSpider(html)
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


# In[76]:


# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillSenegalData(html,Senegaldata)
    except:
        time.sleep(5)


# In[77]:


# convert data to dataframe
Senegal2 = pd.DataFrame(Senegaldata)
print(Senegal2.shape)
Senegal2.head()


# In[78]:


Senegal2["Source"] = ["Web2" for i in range(len(Senegal2))]
Senegal2.head()


# In[79]:


SenegalFull = pd.concat([Senegal,Senegal2])
SenegalFull.head()


# In[81]:


SenegalFull.shape


# In[82]:


# save dataset
Senegal.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Senegal.csv")


# In[ ]:




