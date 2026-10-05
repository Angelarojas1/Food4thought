#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of China
# 

# In[150]:


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


# #### https://home.meishichina.com/recipe-type.html#hmsr=www&hmpl=index&hmcu=magicside&hmkw=D1&hmci=D1_type

# In[27]:


# 1. create a list to store all recipe htmls on one page
def htmlOnePageSpider(category_url):
    """
    input: category_url, the url of first page of the recipe web
    output: htmlDic with all recipe htmls on one page of one category
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'msc-user-sign-mark=1; pid=65411629134318284; BAIDU_SSP_lcr=https://www.google.com/; Hm_lvt_fb9cd9dcdda23cee0c7357db9be24acb=1629134295,1629135380,1629135503,1629324431; PHPSESSID=7r13ln72sv0regc5jvtlbnqhit; Hm_lpvt_fb9cd9dcdda23cee0c7357db9be24acb=1629339945; __gads=ID=c6e2483d1323675d-22d50712e5c90078:T=1629134319:RT=1629339946:S=ALNI_MZcoXDUUrFtlitbmduE1nu78l9NTg',
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
    
    lst = []
    for i in sel.xpath('//div[@id="J_list"]/ul/li'):
        lst.append(i.xpath('.//h2/a[@target="_blank"]/@href').get(''))
    
    return lst


# In[28]:


# test
htmlOnePageSpider('https://home.meishichina.com/recipe/chuancai/')


# In[47]:


pageDic = {
    "chuancai":413,
    "lucai":198,
    "mincai":59,
    "yuecai":344,
    "sucai": 10,
    "zhecai":82,
    "xiangcai":99,
    "huicai":40,
    "huaiyangcai":58,
    "yucai": 25,
    "jincai": 21,
    "ecai": 31,
    "yunnancai":19,
    "beijingcai":103,
    "dongbeicai":125,
    "xibeicai": 52,
    "guizhoucai": 12,
    "shanghaicai": 9,
    "xinjiangcai": 37,
    "gancai": 26      
}


# In[68]:


# 2. create a dic to store all htmls by category
for cuisine in pageDic:
    htmlDic = {}
    lst = htmlOnePageSpider("https://home.meishichina.com/recipe/{}/".format(cuisine))
    for i in range(2,pageDic[cuisine]+1):
        lst += htmlOnePageSpider("https://home.meishichina.com/recipe/{}/page/{}/".format(cuisine,i))
        
    htmlDic[cuisine] = lst 
    
    # store the dictionary to a json file
    a_file = open("/Users/xixi/Dropbox/food4thought/data/raw/ChinaHtml/{}Html.json".format(cuisine),"w")
    json.dump(htmlDic,a_file,ensure_ascii=False)
    a_file.close()


# In[142]:


# 3. go through all recipe htmls and scrape the data we want
Chinadata = {
    "Name of the recipe": [],
    "Total time": [],
    "List of ingredients": [],
    "List of instructions": [],
    "Appliance used":[],
    "Category":[]
}


# In[143]:


def Chinaspider(recipes_url,cuisine):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': 'msc-user-sign-mark=1; pid=65411629134318284; BAIDU_SSP_lcr=https://www.google.com/; Hm_lvt_fb9cd9dcdda23cee0c7357db9be24acb=1629134295,1629135380,1629135503,1629324431; PHPSESSID=7r13ln72sv0regc5jvtlbnqhit; Hm_lpvt_fb9cd9dcdda23cee0c7357db9be24acb=1629339945; __gads=ID=c6e2483d1323675d-22d50712e5c90078:T=1629134319:RT=1629339946:S=ALNI_MZcoXDUUrFtlitbmduE1nu78l9NTg',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
    response = requests.get(recipes_url,headers=headers)
    response.encoding="utf-8"
    sel = Selector(response.text)
    
    dic = {}
    
    dic['Name of the recipe'] = sel.xpath("//h1[@class='recipe_De_title']/a/text()").get()
    
    instructionLst= []
    for i in sel.xpath('//div[@class="recipeStep"]/ul/li/div[@class="recipeStep_word"]/text()'):
         instructionLst.append(i.get())  
    dic['List of instructions'] = instructionLst
    
    ingredientLst = []
    length = len(sel.xpath('//div[@class="recipeCategory_sub_R clear"]/ul/li'))
    for i in range(length):
        ingredientLst.append([sel.xpath('//div[@class="recipeCategory_sub_R clear"]/ul/li/span[@class="category_s2"]/text()')[i].get(),
                              sel.xpath('//div[@class="recipeCategory_sub_R clear"]/ul/li/span[@class="category_s1"]/a/b/text()|//div[@class="recipeCategory_sub_R clear"]/ul/li/span[@class="category_s1"]/b/text()')[i].get()])
    
    dic['List of ingredients'] = ingredientLst
    
    try:
        dic['Total time'] = sel.xpath('.//div[@class="recipeCategory_sub_R mt30 clear"]').xpath('.//span[@class="category_s1" and following-sibling::span="耗时"]').xpath('.//a/@title').get('')
    except:
        dic['Total time'] = ''
        
    dic['Appliance used'] = sel.xpath('//div[@class="recipeTip mt16"]')[1].get().split('\n')[1] 
    dic['Category'] = cuisine
    
    return dic


# In[144]:


def fillChinaData(url,dic,cuisine):
    content = Chinaspider(url,cuisine)
    dic["Name of the recipe"].append(content['Name of the recipe'])
    dic["Total time"].append(content['Total time'])
    dic["List of ingredients"].append(content['List of ingredients'])
    dic["List of instructions"].append(content['List of instructions'])
    dic["Appliance used"].append(content['Appliance used'])
    dic['Category'].append(content['Category'])


# In[145]:


import time
for cuisine in pageDic:
    f = open("/Users/xixi/Dropbox/food4thought/data/raw/ChinaHtml/{}Html.json".format(cuisine))
    json_file = json.load(f)
    lst = json_file[cuisine]
    
    for html in lst:
        try:
            fillChinaData(html,Chinadata,cuisine)
            
        except:
            time.sleep(5)


# In[146]:


# 4. convert dictionary to data frame
China = pd.DataFrame(Chinadata)
China.head()


# In[147]:


China.shape


# In[148]:


China["Source"] = ["Web1" for i in range(len(China))]
China.head()


# In[149]:


# save the dataset
China.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/China.csv")


# In[ ]:




