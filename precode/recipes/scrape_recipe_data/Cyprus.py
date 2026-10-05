#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Cyprus

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


# #### https://afroditeskitchen.com/recipe_category/traditional-cyprus-recipes/

# In[5]:


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
        'cookie':'apbct_site_landing_ts=1650152457; ct_timezone=-4; _ga=GA1.2.1429055419.1650152458; ct_checked_emails=0; apbct_prev_referer=https://afroditeskitchen.com/recipe_category/traditional-cyprus-recipes/; apbct_timestamp=1652798371; apbct_page_hits=7; apbct_cookies_test=%7B%22cookies_names%22%3A%5B%22apbct_timestamp%22%2C%22apbct_site_landing_ts%22%2C%22apbct_page_hits%22%5D%2C%22check_value%22%3A%2256dc38fa10f293aebfaf9a91bead798e%22%7D; apbct_urls={"afroditeskitchen.com\/recipe_category\/traditional-cyprus-recipes\/":[1652798371]}; apbct_site_referer=UNKNOWN; ct_sfw_pass_key=21b5014f836e2b529790bd76acc262d70; ct_ps_timestamp=1652798373; _gid=GA1.2.909104411.1652798373; ct_screen_info={"fullWidth":1225,"fullHeight":4788,"visibleWidth":1225,"visibleHeight":679}; apbct_visible_fields={"0":{"visible_fields":"s","visible_fields_count":1,"invisible_fields":"","invisible_fields_count":0},"1":{"visible_fields":"recipe_type[] recipe_course[] recipe_season[]","visible_fields_count":3,"invisible_fields":"","invisible_fields_count":0},"2":{"visible_fields":"your-name your-email","visible_fields_count":2,"invisible_fields":"_wpcf7 _wpcf7_version _wpcf7_locale _wpcf7_unit_tag _wpcf7_container_post _wpcf7_posted_data_hash _wpcf7_recaptcha_response ct_checkjs_cf7 referer-page","invisible_fields_count":9},"3":{"visible_fields":"your-name your-email","visible_fields_count":2,"invisible_fields":"_wpcf7 _wpcf7_version _wpcf7_locale _wpcf7_unit_tag _wpcf7_container_post _wpcf7_posted_data_hash _wpcf7_recaptcha_response order-title ct_checkjs_cf7 referer-page","invisible_fields_count":10}}; ct_has_scrolled=true; ct_checkjs=1502722237; ct_fkp_timestamp=1652798444; ct_pointer_data=[[19,812,19],[51,847,159],[58,846,813],[112,795,912],[301,718,1062],[385,715,3011],[385,715,6111],[388,852,6162],[207,176,18344],[167,120,18695],[166,127,18896],[154,147,18912],[13,496,19129],[199,338,19211],[154,372,19363],[11,529,42944],[296,173,66754],[329,107,67127],[329,117,67214],[314,310,70811],[179,456,70962],[173,414,71112],[542,503,73782],[464,516,74629]]',
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
    for i in sel.xpath('//div[@class="image"]/a/@href'):
        lst.append(i.get())
    
    return lst


# In[6]:


htmlOnePageSpider("https://afroditeskitchen.com/recipe_category/traditional-cyprus-recipes/", htmlLst)


# In[7]:


for i in range(2,5):
    htmlOnePageSpider("https://afroditeskitchen.com/recipe_category/traditional-cyprus-recipes/page/{}/".format(i), htmlLst)


# In[8]:


# the number of recipes we have in total
len(htmlLst)


# In[20]:


# 3. go through all recipe htmls and scrape the data we want

Cyprusdata = {
    "Name of the recipe":[],
    "Total time":[],
    "List of ingredients": [],
    "List of instructions":[]
}

def CyprusSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'apbct_site_landing_ts=1650152457; ct_timezone=-4; _ga=GA1.2.1429055419.1650152458; ct_checked_emails=0; apbct_prev_referer=https://afroditeskitchen.com/recipe_category/traditional-cyprus-recipes/; apbct_timestamp=1652798371; apbct_page_hits=7; apbct_cookies_test=%7B%22cookies_names%22%3A%5B%22apbct_timestamp%22%2C%22apbct_site_landing_ts%22%2C%22apbct_page_hits%22%5D%2C%22check_value%22%3A%2256dc38fa10f293aebfaf9a91bead798e%22%7D; apbct_urls={"afroditeskitchen.com\/recipe_category\/traditional-cyprus-recipes\/":[1652798371]}; apbct_site_referer=UNKNOWN; ct_sfw_pass_key=21b5014f836e2b529790bd76acc262d70; ct_ps_timestamp=1652798373; _gid=GA1.2.909104411.1652798373; ct_screen_info={"fullWidth":1225,"fullHeight":4788,"visibleWidth":1225,"visibleHeight":679}; apbct_visible_fields={"0":{"visible_fields":"s","visible_fields_count":1,"invisible_fields":"","invisible_fields_count":0},"1":{"visible_fields":"recipe_type[] recipe_course[] recipe_season[]","visible_fields_count":3,"invisible_fields":"","invisible_fields_count":0},"2":{"visible_fields":"your-name your-email","visible_fields_count":2,"invisible_fields":"_wpcf7 _wpcf7_version _wpcf7_locale _wpcf7_unit_tag _wpcf7_container_post _wpcf7_posted_data_hash _wpcf7_recaptcha_response ct_checkjs_cf7 referer-page","invisible_fields_count":9},"3":{"visible_fields":"your-name your-email","visible_fields_count":2,"invisible_fields":"_wpcf7 _wpcf7_version _wpcf7_locale _wpcf7_unit_tag _wpcf7_container_post _wpcf7_posted_data_hash _wpcf7_recaptcha_response order-title ct_checkjs_cf7 referer-page","invisible_fields_count":10}}; ct_has_scrolled=true; ct_checkjs=1502722237; ct_fkp_timestamp=1652798444; ct_pointer_data=[[19,812,19],[51,847,159],[58,846,813],[112,795,912],[301,718,1062],[385,715,3011],[385,715,6111],[388,852,6162],[207,176,18344],[167,120,18695],[166,127,18896],[154,147,18912],[13,496,19129],[199,338,19211],[154,372,19363],[11,529,42944],[296,173,66754],[329,107,67127],[329,117,67214],[314,310,70811],[179,456,70962],[173,414,71112],[542,503,73782],[464,516,74629]]',
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
    
    content['name'] = sel.xpath('//div[@class="container"]/h1/span/text()').get()
    content['totalTime'] = sel.xpath('//div[@class="item"]/span/text()')[1].get()
    
    lst = []
    for i in sel.xpath('//div[@class="item addSpace"]/p/text()'):
        lst.append(i.get())
    content['recipeIngredient'] = lst
    
    lst = []
    for i in sel.xpath('//div[@class="item the_recipe"]/p/text()'):
        lst.append(i.get())
    content['recipeInstructions'] = lst
    
    return content

def fillCyprusData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = CyprusSpider(html)
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
        

# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillCyprusData(html,Cyprusdata)
    except:
        time.sleep(5)

# convert data to dataframe
Cyprus = pd.DataFrame(Cyprusdata)
print(Cyprus.shape)
Cyprus.head()


# In[21]:


Cyprus["Source"] = ["Web1" for i in range(len(Cyprus))]
Cyprus.head()


# In[22]:


# save dataset
Cyprus.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Cyprus.csv")


# In[ ]:




