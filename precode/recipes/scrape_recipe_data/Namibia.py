#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Namibia

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


# #### https://www.kochbar.de/kochen/namibisch-kochen-namibische-kueche.html

# In[10]:


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
        'cookie':'_sp_v1_uid=1:909:db4050b0-97a4-4aba-9045-16fe200bfb3e; _sp_v1_csv=null; _sp_v1_lt=1:; consentUUID=7d3e8a32-8e09-4740-a107-a7a3b9ae76f3_6; euconsent-v2=CPXQlsAPXQlsAAGABCENCKCgAP_AAAAAACiQIcgZBCoETWFAUXB4QsMAGYAXREAUAOACChCAASABAEAAICAAkiAAMAQAAAACAQYAIBIBAAAAAAAEAAAAAAAEAAEgAAAAgAAIIAJAAAEAAAAAAAoAAAAAAAAIAAARgAQAiQAAQkKFAGBAQAAQAAAAgCAAAIAEAgMAAAAAAIIAAAAAAAAAAAAAAIIAAAERkAMAJgC8wGeDAAQAKgCxCIAICRBAAEAEgSA6ABUADIAIAAZAA0AB5AEQARQAmABPADeAHMAPwAhABEACWAFKALcAYYA1QB-gGKANwAegBDYCRAFDgLzAacA3UIADABIACoBdAaAKAFwAgsBaAFpASIAzwVAGACYAFyAtAC0gJBAXmAzwUACABUAQUdAqAAqABkAEAAMgAaAA8AB9AEQARQAmABPAC4AGIAN4AcwA_ACIAEsAJgAUYApQBYgC3AGGAP0AiwBYoC0ALSAXUAxQBuAD0AIbAReAkEBIgChwF5gL6AZYA04BuoDixwAcAC4AJACCgEZAMCAa8BdBCAaABkAJgAXAAxABvAFjAWgBaQDFAHoASCAkQBbQDPCAAUAFQBBQCMgFiAXQSgKAAZAB4AEQAJgAXAAxACIAFGAKUAW4A1YC0ALSAXUAxQBuAEXgJEAXmAywBnhIAKABcAXIBGQDXgLoKQIAAKgAZABAADIAGgAPIAiACKAEwAJ4AYgA5gB-AEQAKMAUoAsQBbgDVAH6ARYAxQBuAD0AIvASIAocBeYC-gGWAM8AbqBDMoAHAAuACQAXIBYgC6gGvAXQ.YAAAAAAAAAAA; _ga_oi=true; _showheroes_oi=true; _oewa_oi=true; _chartbeat_oi=true; _ga_aaf=true; _kam_oi=true; _nielsen_oi=true; _vgwort_oi=true; _sp_v1_opt=1:login|true:last_id|11:; iom_consent=0103ff03ff&1649701394786; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; __gads=ID=80b13cb7971c69b7:T=1649701395:S=ALNI_MbyQEJGfvO2x0WpooCOZifofxU-Bw; _sp_v1_ss=1:H4sIAAAAAAAAAItWqo5RKimOUbKKxs_IAzEMamN1YpRSQcy80pwcILsErKC6lpoSSjpwR0Glhp6yWAC2rkFPWQEAAA==; _sp_v1_consent=1!1:1:1:0:0:0; uuidpd=e7c978db-83fb-4073-b170-bda853379769; fptthc=43282a26-6030-4219-8299-374b0ce953ce; publ=; gid=undefined; _gid=GA1.2.44556536.1651852930; nid_prv_last_read=2022-05-06T16:02:10.023Z; outbrain_cid_fetch=true; POPUPCHECK=1651939331753; __gpi=UID=0000040c064f5b9c:T=1649701395:RT=1651852931:S=ALNI_MZ1X-NQUIKCzrVkob0qu5NMx1NqiQ; adp_segs=e0,e1r9,ezz,e1p,e1mw,e1l,e6a,e4d,ejv,e1g,e1te,e2jt,e6,e6s,ec2,e15k,e1u,e2jx,e2le,e2jl,e29r,e2f9,e8v,e1r,e69,e2l2,e2jk,eb,e1tg,e2jo,e1u7,e13e,ekk,e1hf,e6r,e2ju,e2gy,e1m,ezy,e2cc,e63,e15l,e26d,ec,e2jr,ek2,e2jp,e13r,e159,e26u,e3b,e1q,emp,e26l,e1,e26e,e2ay,e2az,e2jn,e2js,emi,e2l4,e26y,e1s,e1t,e2jv,e64,e7,e26p,e34,e2jm,ell,e1o,e26g,e1lh,e1h,e1ra,e1rb,e4v,e2jw,emh,e2jj,e18k,e6t,ej0; kameleoonVisitorCode=_js_xtuv943xms75rtc7; _sp_v1_data=2:375819:1649701390:0:28:0:28:0:0:_:-1; _ga_KJFWQ65HP8=GS1.1.1651852929.5.1.1651852944.0; ioam2018=00144bead56d0c52c62547212:1680286994789:1649701394789:.kochbar.de:29:kochbar:dbusowf_tes_kbrezept:noevent:1651852945049:7kzdrm; _ga=GA1.2.1975985562.1649701394; cto_bundle=2uNt_19nVEUlMkJvajlHTVIlMkJxJTJCU0hEdzhlQjh2OTBmb0JrQWglMkJUR2pURCUyRjkwbyUyRmE1T2dHckpQeHBtcXdzb2wlMkZTRlNMUlpLZG9nTiUyRk0zVWhrJTJCbFBxV1hSUjZSJTJGa1MzZUFxWUlZeEg5NkVyZGxaeGtZdUk3YkpGUWJDSDNiQW9NOXVvM1FQUmlGemJHJTJGWXE5cmVUc1RxbEpwckI1YlRkR0xRYWltJTJGNDhucFU0cGZNUDRiNkRPMmVhU3pxZE81MThQQlglMkJUMg',
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
    for i in sel.xpath('//div[@class="kb-teaser-list-item-wrapper masked-url"]/@data-url'):
        lst.append(i.get().replace("|","/"))
    
    return lst


# In[11]:


htmlOnePageSpider("https://www.kochbar.de/kochen/namibisch-kochen-namibische-kueche.html", htmlLst)


# In[12]:


# page 2
htmlOnePageSpider("https://www.kochbar.de/kochen/namibisch-kochen-namibische-kueche.html?suchbegriff=&page=2", htmlLst)


# In[13]:


# the number of recipes we have in total
len(htmlLst)


# In[18]:


# 3. go through all recipe htmls and scrape the data we want

Namibiadata = {
    "Name of the recipe":[],
    "Total time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def NamibiaSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_sp_v1_uid=1:909:db4050b0-97a4-4aba-9045-16fe200bfb3e; _sp_v1_csv=null; _sp_v1_lt=1:; consentUUID=7d3e8a32-8e09-4740-a107-a7a3b9ae76f3_6; euconsent-v2=CPXQlsAPXQlsAAGABCENCKCgAP_AAAAAACiQIcgZBCoETWFAUXB4QsMAGYAXREAUAOACChCAASABAEAAICAAkiAAMAQAAAACAQYAIBIBAAAAAAAEAAAAAAAEAAEgAAAAgAAIIAJAAAEAAAAAAAoAAAAAAAAIAAARgAQAiQAAQkKFAGBAQAAQAAAAgCAAAIAEAgMAAAAAAIIAAAAAAAAAAAAAAIIAAAERkAMAJgC8wGeDAAQAKgCxCIAICRBAAEAEgSA6ABUADIAIAAZAA0AB5AEQARQAmABPADeAHMAPwAhABEACWAFKALcAYYA1QB-gGKANwAegBDYCRAFDgLzAacA3UIADABIACoBdAaAKAFwAgsBaAFpASIAzwVAGACYAFyAtAC0gJBAXmAzwUACABUAQUdAqAAqABkAEAAMgAaAA8AB9AEQARQAmABPAC4AGIAN4AcwA_ACIAEsAJgAUYApQBYgC3AGGAP0AiwBYoC0ALSAXUAxQBuAD0AIbAReAkEBIgChwF5gL6AZYA04BuoDixwAcAC4AJACCgEZAMCAa8BdBCAaABkAJgAXAAxABvAFjAWgBaQDFAHoASCAkQBbQDPCAAUAFQBBQCMgFiAXQSgKAAZAB4AEQAJgAXAAxACIAFGAKUAW4A1YC0ALSAXUAxQBuAEXgJEAXmAywBnhIAKABcAXIBGQDXgLoKQIAAKgAZABAADIAGgAPIAiACKAEwAJ4AYgA5gB-AEQAKMAUoAsQBbgDVAH6ARYAxQBuAD0AIvASIAocBeYC-gGWAM8AbqBDMoAHAAuACQAXIBYgC6gGvAXQ.YAAAAAAAAAAA; _ga_oi=true; _showheroes_oi=true; _oewa_oi=true; _chartbeat_oi=true; _ga_aaf=true; _kam_oi=true; _nielsen_oi=true; _vgwort_oi=true; _sp_v1_opt=1:login|true:last_id|11:; iom_consent=0103ff03ff&1649701394786; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; __gads=ID=80b13cb7971c69b7:T=1649701395:S=ALNI_MbyQEJGfvO2x0WpooCOZifofxU-Bw; _sp_v1_ss=1:H4sIAAAAAAAAAItWqo5RKimOUbKKxs_IAzEMamN1YpRSQcy80pwcILsErKC6lpoSSjpwR0Glhp6yWAC2rkFPWQEAAA==; _sp_v1_consent=1!1:1:1:0:0:0; uuidpd=e7c978db-83fb-4073-b170-bda853379769; fptthc=43282a26-6030-4219-8299-374b0ce953ce; publ=; gid=undefined; _gid=GA1.2.44556536.1651852930; nid_prv_last_read=2022-05-06T16:02:10.023Z; outbrain_cid_fetch=true; POPUPCHECK=1651939331753; __gpi=UID=0000040c064f5b9c:T=1649701395:RT=1651852931:S=ALNI_MZ1X-NQUIKCzrVkob0qu5NMx1NqiQ; adp_segs=e0,e1r9,ezz,e1p,e1mw,e1l,e6a,e4d,ejv,e1g,e1te,e2jt,e6,e6s,ec2,e15k,e1u,e2jx,e2le,e2jl,e29r,e2f9,e8v,e1r,e69,e2l2,e2jk,eb,e1tg,e2jo,e1u7,e13e,ekk,e1hf,e6r,e2ju,e2gy,e1m,ezy,e2cc,e63,e15l,e26d,ec,e2jr,ek2,e2jp,e13r,e159,e26u,e3b,e1q,emp,e26l,e1,e26e,e2ay,e2az,e2jn,e2js,emi,e2l4,e26y,e1s,e1t,e2jv,e64,e7,e26p,e34,e2jm,ell,e1o,e26g,e1lh,e1h,e1ra,e1rb,e4v,e2jw,emh,e2jj,e18k,e6t,ej0; kameleoonVisitorCode=_js_xtuv943xms75rtc7; _sp_v1_data=2:375819:1649701390:0:28:0:28:0:0:_:-1; _ga_KJFWQ65HP8=GS1.1.1651852929.5.1.1651852944.0; ioam2018=00144bead56d0c52c62547212:1680286994789:1649701394789:.kochbar.de:29:kochbar:dbusowf_tes_kbrezept:noevent:1651852945049:7kzdrm; _ga=GA1.2.1975985562.1649701394; cto_bundle=2uNt_19nVEUlMkJvajlHTVIlMkJxJTJCU0hEdzhlQjh2OTBmb0JrQWglMkJUR2pURCUyRjkwbyUyRmE1T2dHckpQeHBtcXdzb2wlMkZTRlNMUlpLZG9nTiUyRk0zVWhrJTJCbFBxV1hSUjZSJTJGa1MzZUFxWUlZeEg5NkVyZGxaeGtZdUk3YkpGUWJDSDNiQW9NOXVvM1FQUmlGemJHJTJGWXE5cmVUc1RxbEpwckI1YlRkR0xRYWltJTJGNDhucFU0cGZNUDRiNkRPMmVhU3pxZE81MThQQlglMkJUMg',
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

def fillNamibiaData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = NamibiaSpider(html)
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
        fillNamibiaData(html,Namibiadata)
    except:
        time.sleep(5)

# convert data to dataframe
Namibia = pd.DataFrame(Namibiadata)
print(Namibia.shape)
Namibia.head()


# In[19]:


Namibia["Source"] = ["Web1" for i in range(len(Namibia))]
Namibia.head()


# In[20]:


# save dataset
Namibia.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Namibia.csv")


# In[ ]:




