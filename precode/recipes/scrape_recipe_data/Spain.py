#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Spain

# recetasderechupete.com

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


# In[2]:


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
        'cookie':'_ga=GA1.2.1367083819.1639425980; __qca=P0-1991604601-1639425980263; __gads=ID=b6bcfc1dc601d9ce-22ed0c9eeacc007a:T=1639425980:RT=1639425980:S=ALNI_MZ9R4flc0vpOC1qHCzxI9qfI6By8g; _gid=GA1.2.549987761.1639577608',
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
    for i in sel.xpath('//div[@class="post"]/a/@href'):   
        lst.append(i.get())

    
    return lst


# In[3]:


# 2. go through all categories and pages in the web and get all recipe htmls

def htmlAllPageSpider(category_url,page_number,htmlLst):
    """
    input: category_url, the url of first page of the recipe web
    input: page number, the total number of pages of one category
    output: htmlLst with all recipes htmls on all pages of one category
    
    """
    # initialize pageLst to store the htmls of all pages
    pageLst = []

    pageLst.append(category_url)
    
    for i in range(2,page_number+1):
        pageLst.append(category_url+"page/"+str(i)+"/")
        
    for i in pageLst:
        fillLst = htmlOnePageSpider(i, htmlLst)
    
    return fillLst


# In[4]:


# 2. go through all categories and pages in the web and get all recipe htmls

htmlLst = []

htmlLst = htmlAllPageSpider('https://www.recetasderechupete.com/todas/recetas/pescados-mariscos/',15,htmlLst)
htmlLst = htmlAllPageSpider('https://www.recetasderechupete.com/todas/recetas/carnes-aves/',15,htmlLst)
htmlLst = htmlAllPageSpider('https://www.recetasderechupete.com/todas/recetas/arroces/',6,htmlLst)
htmlLst = htmlAllPageSpider('https://www.recetasderechupete.com/todas/recetas/pasta-recetas/',4,htmlLst)
htmlLst = htmlAllPageSpider('https://www.recetasderechupete.com/todas/recetas-de-ensaladas/',3,htmlLst)
htmlLst = htmlAllPageSpider('https://www.recetasderechupete.com/todas/recetas/ensaladas-verduras/',7,htmlLst)
htmlLst = htmlAllPageSpider('https://www.recetasderechupete.com/todas/recetas/tapas-aperitivos-pinchos/',8,htmlLst)
htmlLst = htmlAllPageSpider('https://www.recetasderechupete.com/todas/recetas/recetas-de-sopas-y-caldos/',3,htmlLst)
htmlLst = htmlAllPageSpider('https://www.recetasderechupete.com/todas/recetas/legumbres-sopas-guisos/',5,htmlLst)

htmlLst = list(set(htmlLst))
print("The number of recipes is {}".format(len(htmlLst)))


# In[77]:


# 3. go through all recipe htmls and scrape the data we want

Spaindata = {
    "Name of the recipe": [],
    "Total time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}


def Spainspider(recipes_url):
    """
    input: recipes_url, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_ga=GA1.2.1367083819.1639425980; __qca=P0-1991604601-1639425980263; __gads=ID=b6bcfc1dc601d9ce-22ed0c9eeacc007a:T=1639425980:RT=1639425980:S=ALNI_MZ9R4flc0vpOC1qHCzxI9qfI6By8g; _gid=GA1.2.549987761.1639577608',
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
    
    # scrape dictionary containing all information that we need
    try:
        s = sel.xpath('//script[@type="application/ld+json" and @id="recipejson"]/text()').get('').replace('\r\n','').replace('\t','').replace(u'\xa0', u' ').replace("\\", r"\\")
        content = json.loads(s,strict=False)

    except:
        content = ''
    
    return content

def fillSpainData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = Spainspider(html)
    if content != '':
        dic['Name of the recipe'].append(content['name'])
        dic['Total time'].append(content['totalTime'])
        dic['List of ingredients'].append(content['recipeIngredient'])
        dic['List of instructions'].append(content['recipeInstructions'])
        dic['Number of servings'].append(content['recipeYield'])
        dic['Category'].append(content['recipeCategory'])    


# In[78]:


# go through all recipe urls in one category 
import time

for i in htmlLst:
    try:
        fillSpainData(i,Spaindata)
    except:
        time.sleep(5)


# In[79]:


# convert data to dataframe
data = pd.DataFrame(Spaindata)
print(data.shape)
data.head()

# save dataset
data.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Spain.csv")

