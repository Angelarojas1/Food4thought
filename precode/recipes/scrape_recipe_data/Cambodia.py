#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Cambodia

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


# #### https://www.cambodiarecipe.com/cuisine/cambodian/?sort=date

# In[14]:


headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_ga=GA1.1.1053005383.1650146600; __gads=ID=36e785f9b64cf6d5-2237ac0f2ed20056:T=1650146600:RT=1650146600:S=ALNI_MY1QEZkIbs2FOzPr_uI6_u9KC0xmw; __gpi=UID=00000587166a93ea:T=1652122570:RT=1652805624:S=ALNI_MYhxzGiyU1IV2AnPQ2Seq8BfTeTtA; _ga_T8D7MQ0FR0=GS1.1.1652805625.3.0.1652805625.0',
        'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
    }
response = requests.get('https://www.cambodiarecipe.com/cuisine/cambodian/?sort=date',headers=headers)
sel = Selector(response.text)


# In[12]:


sel.xpath('//div[@class="rcps-item-featured-img"]/a/@href')[-1].get()


# In[ ]:


r'C:\Utility\BrowserDrivers\chromedriver.exe'


# In[20]:


from selenium import webdriver
import time
from selenium.common.exceptions import StaleElementReferenceException

driver = webdriver.Chrome(executable_path=r"/usr/local/bin/chromedriver")
driver.maximize_window()
driver.implicitly_wait(10)
driver.get("https://www.allrecipes.com/recipes/233/world-cuisine/asian/indian/")
receipes = driver.find_elements_by_class_name("card__detailsContainer")
for rec in receipes:
    name = rec.find_element_by_tag_name("h3").get_attribute("innerText")
    print(name)
loadmore = driver.find_element_by_id("category-page-list-related-load-more-button")
j = 0
try:
    while loadmore.is_displayed():
        loadmore.click()
        time.sleep(5)
        lrec = driver.find_elements_by_class_name("recipeCard__detailsContainer")
        newlist = lrec[j:]
        for rec in newlist:
            name = rec.find_element_by_tag_name("h3").get_attribute("innerText")
            print(name)
        j = len(lrec)+1
        time.sleep(5)
except StaleElementReferenceException:
    pass
driver.quit()


# In[16]:


import requests
from bs4 import BeautifulSoup

size = 24
page = 0

hasNext = True
while hasNext == True:
    page +=1
    print('\tPage: %s' %page)
    url = 'https://www.allrecipes.com/element-api/content-proxy/aggregate-load-more?sourceFilter%5B%5D=alrcom&id=cms%2Fonecms_posts_alrcom_2007692&excludeIds%5B%5D=cms%2Fallrecipes_recipe_alrcom_142967&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_231026&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_247233&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_246179&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_256599&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_247204&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_34591&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_245131&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_220560&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_212721&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_236563&excludeIds%5B%5D=cms%2Fallrecipes_recipe_alrcom_14565&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_8189766&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_8188886&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_8189135&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_2052087&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_7986932&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_2040338&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_280310&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_142967&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_14565&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_228957&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_46822&excludeIds%5B%5D=cms%2Fonecms_posts_alrcom_72349&page={page}&orderBy=Popularity30Days&docTypeFilter%5B%5D=content-type-recipe&docTypeFilter%5B%5D=content-type-gallery&size={size}&pagesize={size}&x-ssst=iTv629LHnNxfbQ1iVslBTZJTH69zVWEa&variant=food'.format(size=size, page=page)
    jsonData = requests.get(url).json()
    
    hasNext = jsonData['hasNext']

    soup = BeautifulSoup(jsonData['html'], 'html.parser')
    cardTitles = soup.find_all('h3',{'class':'recipeCard__title'})
    for title in cardTitles:
        print(title.text.strip())
        


# In[7]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

options = webdriver.ChromeOptions() 
options.add_argument("start-maximized")
options.add_argument('disable-infobars')
driver = webdriver.Chrome(chrome_options=options, executable_path=r'C:\Utility\BrowserDrivers\chromedriver.exe')
driver.get("https://www.nytimes.com/search?%20endDate=20181231&query=trump&sort=best&startDate=20180101")
myLength = len(WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "//main[@id='site-content']//figure[@class='css-rninck toneNews']//following::a[1]"))))

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    try:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Show More']"))).click()
        WebDriverWait(driver, 20).until(lambda driver: len(driver.find_elements_by_xpath("//main[@id='site-content']//figure[@class='css-rninck toneNews']//following::a[1]")) > myLength)
        titles = driver.find_elements_by_xpath("//main[@id='site-content']//figure[@class='css-rninck toneNews']//following::a[1]")
        myLength = len(titles)
    except TimeoutException:
        break

for title in titles:
    print(title.get_attribute("href"))
driver.quit()


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
        'cookie':'_ga=GA1.1.1053005383.1650146600; __gads=ID=36e785f9b64cf6d5-2237ac0f2ed20056:T=1650146600:RT=1650146600:S=ALNI_MY1QEZkIbs2FOzPr_uI6_u9KC0xmw; __gpi=UID=00000587166a93ea:T=1652122570:RT=1652805624:S=ALNI_MYhxzGiyU1IV2AnPQ2Seq8BfTeTtA; _ga_T8D7MQ0FR0=GS1.1.1652805625.3.0.1652805625.0',
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
    for i in json.loads(sel.xpath("//script[@type='application/ld+json' and @data-testid='itemlist-structured-data']/text()").get())['itemListElement']:
        lst.append(i['url'])
    
    return lst


# In[13]:


htmlOnePageSpider("https://www.smulweb.nl/recepten/surinaamse", htmlLst)


# In[14]:


for i in range(2,35):
    htmlOnePageSpider("https://www.smulweb.nl/recepten/surinaamse?page={}".format(i), htmlLst)


# In[15]:


# the number of recipes we have in total
len(htmlLst)


# In[20]:


# 3. go through all recipe htmls and scrape the data we want

Surinamedata = {
    "Name of the recipe":[],
    "Total time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def SurinameSpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'_ga=GA1.1.1053005383.1650146600; __gads=ID=36e785f9b64cf6d5-2237ac0f2ed20056:T=1650146600:RT=1650146600:S=ALNI_MY1QEZkIbs2FOzPr_uI6_u9KC0xmw; __gpi=UID=00000587166a93ea:T=1652122570:RT=1652805624:S=ALNI_MYhxzGiyU1IV2AnPQ2Seq8BfTeTtA; _ga_T8D7MQ0FR0=GS1.1.1652805625.3.0.1652805625.0',
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
    content = json.loads(sel.xpath('//script[@type="application/ld+json" and @data-testid="recipe-structured-data"]/text()').get())
    
    return content

def fillSurinameData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = SurinameSpider(html)
    dic['Name of the recipe'].append(content['name'])
    try:
        dic['Total time'].append(content['totalTime'])
    except:
        dic['Total time'].append('')
                
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
        fillSurinameData(html,Surinamedata)
    except:
        time.sleep(5)

# convert data to dataframe
Suriname = pd.DataFrame(Surinamedata)
print(Suriname.shape)
Suriname.head()


# In[21]:


Suriname["Source"] = ["Web1" for i in range(len(Suriname))]
Suriname.head()


# In[22]:


# save dataset
Suriname.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Suriname.csv")


# In[ ]:




