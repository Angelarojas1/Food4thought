#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Austria

# In[7]:


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


# In[8]:


# 1. create a list to store all recipe htmls on one page
# initialize htmlLst to store the htmls of all recipes
htmlLst = {}

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
        'cookie': '_ga=GA1.2.1143897606.1633404040; sp_ga=1; _sp_v1_uid=1:751:39f45dc2-7edd-4b81-a8ff-01db90a2e5de; _sp_v1_csv=null; _sp_v1_lt=1:; amp-access=amp-2MxlvFY65-5PY3Zx04mRRw; AMP_TOKEN=$NOT_FOUND; _gid=GA1.2.1089152604.1634323334; consentUUID=b7e8a53e-9def-4316-a0a3-2d4e6686a129; euconsent-v2=CPOIfNpPOIfNpAGABCENBxCgAP_AAE_AACiQHpgZBDoUTWHAUXh4QvtAGYQSEEQVIGACCBCAIiABAAAEMDQAkkAAoASAAAACAQQAIBIBAAAECAAEAAAAAAAEAAEgAAAAhAAIIAJAABAAAAAAAAoCAAAAAAAIAAAQAAAAmACAA2KFAGAAAAAQAAAAgAAAAAAAAAEAAAAAAIF5wEQALwAnACgALoAZABfADNAIKAQgAjIBYgC6gGBAMUAa8BKwC2gF5gJBIEAAFQAMgAeABAADIAGgAPIAiACKAEwAJ4AbwA5gB-AEMAJYATQApQBbgDDAGqAPgAfoBHADFAG4APQAhsBF4CRAFDgKRAacFABQAnACgAXwQACACQdApAAqABkAEAAMgAaAA8AB9AEQARQAmABPAC4AF8AMQAbwA5gB-AEMAJYATAAmgBSgCxAFuAMMAaIA_QCLAEcALEAWgAxQBuAD0AIbAReAkEBIgChwGJAMsAacPABAC-AIyOAAgAkDQBwAuACGAIKAWgBF4CRAFIiIAgAhgEXgJEAUiIAAgAkGQAwAmAEcAXmKgDABMAC4ARwAtACQQF5kIBwAGQAmABcAC-AGIAN4AsQCOAFoAMUAegBIICRAGJEQAQAvgCMkoCQAGQAeABEACYAFwAL4AYgBDAClAFuANUAjgBaADFAG4AReAkQBlhMACARkpAbAAqABkAEAAMgAaAA8gCIAIoATAAngBfADEAHMAPwAhgBSgCxAFuANEAaoA_QCLAEcANwAegBF4CRAFDlQAIAvigAIAEgBOwAA.YAAAAAAAAAAA; _sp_v1_opt=1:login|true:last_id|11:; iom_consent=0103ff03ff&1634323338758; euconsent-addtl=1~; uuidpd=3dc1b90a-937e-46b5-abe8-004eb942eceb; fptthc=76aafcc6-02f8-48d9-8147-c2b9a3e4b82d; publ=; POPUPCHECK=1634409747461; _sp_v1_ss=1:H4sIAAAAAAAAAItWqo5RKimOUbKKRmbkgRgGtbE6MUqpIGZeaU4OkF0CVlBdi1tCSQduIFQKu7JYAAaOo-l5AAAA; _sp_v1_consent=1!1:1:1:0:0:0; _pbjs_userid_consent_data=6480138721822873; PubCommenId=12bbc4ec-7c80-49fd-92eb-7b9c9315f511; pbjs-unifiedid={"TDID":"b8e2d1cd-d84b-4c0b-b941-7dc42e3021de","TDID_LOOKUP":"TRUE","TDID_CREATED_AT":"2021-09-15T18:43:01"}; id5_storage={"created_at":"2021-10-15T18:43:01.801863Z","id5_consent":true,"original_uid":"ID5*xATJC7ViMfSAiQ281dCX-O0rldmNxxac-3W2gbAlhA8AAO_RMSGR1-tKwEea-qxU","universal_uid":"ID5*nKOzyHKttzEZRnEYpAa7pLCBArxlFi67JeNzdvfmXJQAAFgswDQpsvSIiZmyI6L6","signature":"ID5_AXWnhf_LF6ZJYtWHJki3VwpOfBS3VKeUgi2SoeTxcF9p8rF8fJThCZpMt4YpS7UlmXVZEX_pw0ol0knWjliSwGQ","link_type":2,"cascade_needed":true,"privacy":{"jurisdiction":"gdpr","id5_consent":true}}; panoramaId_expiry=1634928181902; _cc_id=589744b018b77ff0c829dd767a86ed67; panoramaId=2afcbfcbd6c567587a0be67eead14945a702fcc603a25c7f187cc14c07f09899; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; gujfirstimp=1634323638456; _sp_v1_data=2:330889:1633404046:0:12:0:12:0:0:_:-1; gid=676217712; adp_segs=e0,e3m,e4v,e6n,e3g,e3t,ec,e3o,e3b,e14c,e2,e8; cto_bundle=k0hf019lM2hjbDhmTWR2dnc5M3VOU2x3TkdpenZEMjNQYmx1aXZmakpvNXE0enJKWGtOREpMbTZDTXR1ZVlkUzVKZWNNNTJHaGp0V3VubXZaeGlFbG10VkhuNUFFVmdlMVI0WkdjeFMlMkJRNFo3V3QyMWIlMkJqYjdpSk52biUyQkQ0dTNtQzJ4RERtcyUyQjd6Qk14bm1CcmozSlZWZ3NzRXNoTG9oRiUyRjhWeG04UlE3dTduQ3RpdXlWVmt3d2tkWU9ZODYlMkJSYXF1dE8; cto_bundle=k0hf019lM2hjbDhmTWR2dnc5M3VOU2x3TkdpenZEMjNQYmx1aXZmakpvNXE0enJKWGtOREpMbTZDTXR1ZVlkUzVKZWNNNTJHaGp0V3VubXZaeGlFbG10VkhuNUFFVmdlMVI0WkdjeFMlMkJRNFo3V3QyMWIlMkJqYjdpSk52biUyQkQ0dTNtQzJ4RERtcyUyQjd6Qk14bm1CcmozSlZWZ3NzRXNoTG9oRiUyRjhWeG04UlE3dTduQ3RpdXlWVmt3d2tkWU9ZODYlMkJSYXF1dE8; __gads=ID=9894a25dd50cc484:T=1634323339:S=ALNI_MZAhRqYHI3sMTcTkpTqfqFhS2EVVg; _pubcid=ec98f69a-9b38-4252-bce7-beb2b6ea47c5; cto_bidid=B5y0k19vNnRnZmNlbFMyY1NjNTZIajNtYVI5NDNCaGE0OVIzRUdrUUdVJTJCWnlQQlZ4emFSRVVzekFUQUFuYVhyN2YlMkI5UTRxS21FZyUyQnVzNzExcThmeGlTMUNHR0ZJeWFkdjRhYW4lMkZjcnZheEVJVFYzanlPbGJGVCUyQjlaU2lZMiUyQnl1Y1VlUyUyRm1EJTJGJTJCeFUxNkFIUVNPUEU4WnFrT2clM0QlM0Q; cto_bundle=YzJmSl9lM2hjbDhmTWR2dnc5M3VOU2x3Tkdrd0t2eEpmTSUyRkt4TW44U1M3TkVlTTlMJTJCSEhyd21VREwyZnpQbUE3RHR0VGFNWmwxQzYlMkJ4ck9GemlEMFluVDFmOUlWY1dGZUtXWkkyaGNtcTBOJTJCczJ5JTJCWlIzQm9BVWxJMDIyMHV0WSUyQlAzM2Jnd3B5WXZreWVtTzYwSUM3MEdrQ0F2clZhM0NpZ0YzazNJejF6JTJGVXMlMkZBQU1CZ2pSTzVFcTglMkZPT3pFQzVuTlE; _lr_retry_request=true; _lr_env_src_ats=false; idl_env=AnNX5Js3cH9I-gDSme_s2rQlnBW9LtiJK--3AuC4F1oQHPEEs1KKRpJyTPzbp4XgCrKDJaS_vJCYY9ZURX0NxmtJaN_zr0QDU8gvbj1r0-lIuysNsiKxslyY5rAzbWCRgIg6ARwSSHTyllZMJxDQUdOCPzdjz1ovDu1LMzo4GZgulGENcU9lriyy8UAYg3EBtye0xrUJhaAgbkgOHOPnsaqvvG6D',
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
    for i in json.loads(sel.xpath('//script[@type = "application/ld+json"]')[1].xpath('text()').get())['itemListElement']:
           lst.append(i['url'])
        
    
    return lst


# In[9]:


# 2. go through all pages in the web and get all recipe htmls

def htmlAllPageSpider(page_number):
    """
    input: page_number, the total number of pages of one category
    output: htmlDic with all recipe htmls on all pages of one category
    
    """
    # initialize pageLst to store the htmls of all pages
    pageLst = []

    for i in range(page_number):
        pageLst.append("https://www.chefkoch.de/rs/s{}g90/oesterreichische-Rezepte.html".format(i*30))
    
    # go over each page and get recipe urls    
    htmlLst = []
    for i in pageLst:
        htmlLst = htmlOnePageSpider(i, htmlLst)
        
    print("The number of recipes is {}".format(len(htmlLst)))
    return htmlLst

htmlLst = htmlAllPageSpider(34)


# In[10]:


htmlLst


# In[11]:


# 3. go through all recipe htmls and scrape the data we want

Austriadata = {
    "Name of the recipe": [],
    "Total time": [],
    "Prep time":[],
    "Cook time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def AustriaSpider(recipes_url):
    """
    input: recipes_url, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': '_ga=GA1.2.1143897606.1633404040; sp_ga=1; _sp_v1_uid=1:751:39f45dc2-7edd-4b81-a8ff-01db90a2e5de; _sp_v1_csv=null; _sp_v1_lt=1:; amp-access=amp-2MxlvFY65-5PY3Zx04mRRw; AMP_TOKEN=$NOT_FOUND; _gid=GA1.2.1089152604.1634323334; consentUUID=b7e8a53e-9def-4316-a0a3-2d4e6686a129; euconsent-v2=CPOIfNpPOIfNpAGABCENBxCgAP_AAE_AACiQHpgZBDoUTWHAUXh4QvtAGYQSEEQVIGACCBCAIiABAAAEMDQAkkAAoASAAAACAQQAIBIBAAAECAAEAAAAAAAEAAEgAAAAhAAIIAJAABAAAAAAAAoCAAAAAAAIAAAQAAAAmACAA2KFAGAAAAAQAAAAgAAAAAAAAAEAAAAAAIF5wEQALwAnACgALoAZABfADNAIKAQgAjIBYgC6gGBAMUAa8BKwC2gF5gJBIEAAFQAMgAeABAADIAGgAPIAiACKAEwAJ4AbwA5gB-AEMAJYATQApQBbgDDAGqAPgAfoBHADFAG4APQAhsBF4CRAFDgKRAacFABQAnACgAXwQACACQdApAAqABkAEAAMgAaAA8AB9AEQARQAmABPAC4AF8AMQAbwA5gB-AEMAJYATAAmgBSgCxAFuAMMAaIA_QCLAEcALEAWgAxQBuAD0AIbAReAkEBIgChwGJAMsAacPABAC-AIyOAAgAkDQBwAuACGAIKAWgBF4CRAFIiIAgAhgEXgJEAUiIAAgAkGQAwAmAEcAXmKgDABMAC4ARwAtACQQF5kIBwAGQAmABcAC-AGIAN4AsQCOAFoAMUAegBIICRAGJEQAQAvgCMkoCQAGQAeABEACYAFwAL4AYgBDAClAFuANUAjgBaADFAG4AReAkQBlhMACARkpAbAAqABkAEAAMgAaAA8gCIAIoATAAngBfADEAHMAPwAhgBSgCxAFuANEAaoA_QCLAEcANwAegBF4CRAFDlQAIAvigAIAEgBOwAA.YAAAAAAAAAAA; _sp_v1_opt=1:login|true:last_id|11:; iom_consent=0103ff03ff&1634323338758; euconsent-addtl=1~; uuidpd=3dc1b90a-937e-46b5-abe8-004eb942eceb; fptthc=76aafcc6-02f8-48d9-8147-c2b9a3e4b82d; publ=; POPUPCHECK=1634409747461; _sp_v1_ss=1:H4sIAAAAAAAAAItWqo5RKimOUbKKRmbkgRgGtbE6MUqpIGZeaU4OkF0CVlBdi1tCSQduIFQKu7JYAAaOo-l5AAAA; _sp_v1_consent=1!1:1:1:0:0:0; _pbjs_userid_consent_data=6480138721822873; PubCommenId=12bbc4ec-7c80-49fd-92eb-7b9c9315f511; pbjs-unifiedid={"TDID":"b8e2d1cd-d84b-4c0b-b941-7dc42e3021de","TDID_LOOKUP":"TRUE","TDID_CREATED_AT":"2021-09-15T18:43:01"}; id5_storage={"created_at":"2021-10-15T18:43:01.801863Z","id5_consent":true,"original_uid":"ID5*xATJC7ViMfSAiQ281dCX-O0rldmNxxac-3W2gbAlhA8AAO_RMSGR1-tKwEea-qxU","universal_uid":"ID5*nKOzyHKttzEZRnEYpAa7pLCBArxlFi67JeNzdvfmXJQAAFgswDQpsvSIiZmyI6L6","signature":"ID5_AXWnhf_LF6ZJYtWHJki3VwpOfBS3VKeUgi2SoeTxcF9p8rF8fJThCZpMt4YpS7UlmXVZEX_pw0ol0knWjliSwGQ","link_type":2,"cascade_needed":true,"privacy":{"jurisdiction":"gdpr","id5_consent":true}}; panoramaId_expiry=1634928181902; _cc_id=589744b018b77ff0c829dd767a86ed67; panoramaId=2afcbfcbd6c567587a0be67eead14945a702fcc603a25c7f187cc14c07f09899; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; gujfirstimp=1634323638456; _sp_v1_data=2:330889:1633404046:0:12:0:12:0:0:_:-1; gid=676217712; adp_segs=e0,e3m,e4v,e6n,e3g,e3t,ec,e3o,e3b,e14c,e2,e8; cto_bundle=k0hf019lM2hjbDhmTWR2dnc5M3VOU2x3TkdpenZEMjNQYmx1aXZmakpvNXE0enJKWGtOREpMbTZDTXR1ZVlkUzVKZWNNNTJHaGp0V3VubXZaeGlFbG10VkhuNUFFVmdlMVI0WkdjeFMlMkJRNFo3V3QyMWIlMkJqYjdpSk52biUyQkQ0dTNtQzJ4RERtcyUyQjd6Qk14bm1CcmozSlZWZ3NzRXNoTG9oRiUyRjhWeG04UlE3dTduQ3RpdXlWVmt3d2tkWU9ZODYlMkJSYXF1dE8; cto_bundle=k0hf019lM2hjbDhmTWR2dnc5M3VOU2x3TkdpenZEMjNQYmx1aXZmakpvNXE0enJKWGtOREpMbTZDTXR1ZVlkUzVKZWNNNTJHaGp0V3VubXZaeGlFbG10VkhuNUFFVmdlMVI0WkdjeFMlMkJRNFo3V3QyMWIlMkJqYjdpSk52biUyQkQ0dTNtQzJ4RERtcyUyQjd6Qk14bm1CcmozSlZWZ3NzRXNoTG9oRiUyRjhWeG04UlE3dTduQ3RpdXlWVmt3d2tkWU9ZODYlMkJSYXF1dE8; __gads=ID=9894a25dd50cc484:T=1634323339:S=ALNI_MZAhRqYHI3sMTcTkpTqfqFhS2EVVg; _pubcid=ec98f69a-9b38-4252-bce7-beb2b6ea47c5; cto_bidid=B5y0k19vNnRnZmNlbFMyY1NjNTZIajNtYVI5NDNCaGE0OVIzRUdrUUdVJTJCWnlQQlZ4emFSRVVzekFUQUFuYVhyN2YlMkI5UTRxS21FZyUyQnVzNzExcThmeGlTMUNHR0ZJeWFkdjRhYW4lMkZjcnZheEVJVFYzanlPbGJGVCUyQjlaU2lZMiUyQnl1Y1VlUyUyRm1EJTJGJTJCeFUxNkFIUVNPUEU4WnFrT2clM0QlM0Q; cto_bundle=YzJmSl9lM2hjbDhmTWR2dnc5M3VOU2x3Tkdrd0t2eEpmTSUyRkt4TW44U1M3TkVlTTlMJTJCSEhyd21VREwyZnpQbUE3RHR0VGFNWmwxQzYlMkJ4ck9GemlEMFluVDFmOUlWY1dGZUtXWkkyaGNtcTBOJTJCczJ5JTJCWlIzQm9BVWxJMDIyMHV0WSUyQlAzM2Jnd3B5WXZreWVtTzYwSUM3MEdrQ0F2clZhM0NpZ0YzazNJejF6JTJGVXMlMkZBQU1CZ2pSTzVFcTglMkZPT3pFQzVuTlE; _lr_retry_request=true; _lr_env_src_ats=false; idl_env=AnNX5Js3cH9I-gDSme_s2rQlnBW9LtiJK--3AuC4F1oQHPEEs1KKRpJyTPzbp4XgCrKDJaS_vJCYY9ZURX0NxmtJaN_zr0QDU8gvbj1r0-lIuysNsiKxslyY5rAzbWCRgIg6ARwSSHTyllZMJxDQUdOCPzdjz1ovDu1LMzo4GZgulGENcU9lriyy8UAYg3EBtye0xrUJhaAgbkgOHOPnsaqvvG6D',
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
    
    # scrape dictionary containing all information that we need
    content = json.loads(sel.xpath('//script[@type = "application/ld+json"]')[1].xpath('text()').get(''))
    
    return content


def fillAustriaData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = AustriaSpider(html)
    dic['Name of the recipe'].append(content['name'])
    dic['Total time'].append(content['totalTime'])
    dic['Prep time'].append(content['prepTime'])
    dic['Cook time'].append(content['cookTime'])
    dic['List of ingredients'].append(content['recipeIngredient'])
    dic['List of instructions'].append(content['recipeInstructions'])
    dic['Number of servings'].append(content['recipeYield'])
    dic['Category'].append(content['recipeCategory'])


# In[ ]:


# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillAustriaData(html,Austriadata)
    except:
        time.sleep(5)


# In[ ]:


# convert data to dataframe
Austria = pd.DataFrame(Austriadata)
print(Austria.shape)
Austria.head()

# save dataset
Austria.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Austria.csv")


# In[ ]:




