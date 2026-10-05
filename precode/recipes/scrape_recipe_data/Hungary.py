#!/usr/bin/env python
# coding: utf-8

# #### Scrape all recipes of Hungary

# https://www.chefkoch.de/rs/s0t29,85,86/Europa-Ungarn-Osteuropa-Rezepte.html

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
        'cookie':'amp-access=amp-2MxlvFY65-5PY3Zx04mRRw; _sp_v1_uid=1:587:77db6f98-749e-4f3e-b268-ba9bc16bd456; _sp_v1_csv=null; _sp_v1_lt=1:; consentUUID=7e360bc6-3ca9-4a55-af31-632a0ff3cba6_3; euconsent-v2=CPSnipaPSnipaAGABCENB9CgAP_AAAAAACiQHsgZBDoUTWHAUXh4QvtAGYQSEEQVIGACCBCAIiABAAAEMDQAkkAAoASAAAACAQQAIBIBAAAECAAEAAAAAAAEAAEgAAAAhAAIIAJAABAAAAAAAAoCAAAAAAAIAAARAAAAmQCAA0KFAGAAAAAQAAAAgAAAAAAAAAEAAAAAAIIAAAEQkCAACoAGQAPAAgABkADQAHkARABFACYAE8AN4AcwA_ACGAEsAJoAUoAtwBhgDVAHwAP0AjgBigDcAHoAQ2AkQBQ4CkQF5gNOCAAwASADNASsOgWAAVAAyACAAGQANAAeAA-gCIAIoATAAnwBcAF0AL4AYgA3gBzAD8AIYASwAmABNAClAFiALcAYYA0QB-gEWAI4AWIAtABdQDFAG4APQAhsBF4CQQEiAKHAXmAvoBiQDLAGnDgBIAFwASABkAGaAQUAhABgQDXgJWDQBgAuACGAIKAWgBIgCkREAMAQwCRAFIiAAIAJBkAMAJgBHAF5jAAIBYhUAYAJgAXACOAFoASCAvMUABAIKQgHgAZACYAFwAL4AYgA3gCxAI4AWgAxQB6AEggJEAW0AxIgACAIKAWIlAUAAyADwAIgATAAuABfADEAIYAUoAtwBqgEcALQAXUAxQBuAEXgJEAXmAywkAEAAuAGQA14CVikB4ACoAGQAQAAyABoADyAIgAigBMACeAF8AMQAcwA_ACGAFKALEAW4A0QBqgD9AIsARwAxQBuAD0AIvASIAocBeYC-igAcAC4AJAAyAE7ALEAXUA14AAA.YAAAAAAAAAAA; sp_ga=1; sp_rewe=1; _ga=GA1.2.1308220345.1641848278; iom_consent=0103ff03ff&1641848278658; uuidpd=3ad5dee9-68f0-4340-8e44-848adb6a4c0f; fptthc=55e5d1af-0b8e-486c-a6f2-e0032dcdc8d9; publ=; _pbjs_userid_consent_data=3524755945110770; PubCommenId=2fd6faf7-05e8-4a39-8993-80083d915e59; pbjs-unifiedid={"TDID":"b8e2d1cd-d84b-4c0b-b941-7dc42e3021de","TDID_LOOKUP":"TRUE","TDID_CREATED_AT":"2021-12-10T20:58:11"}; id5_storage={"created_at":"2022-01-10T20:58:11.209285Z","id5_consent":true,"original_uid":"ID5*ySB8Et17HM5CJ7y6-rvZn0kEpdDRmO1tDmxwDDGRIKsEVSzS3NvgZX_3Wd3xL3i9BFaSnGMnX7MSXCk4jWOtZQRXfrwyTQgFf2Fczvtk5AYEWARi3pICvARHbiT3ZLQmBFmFNf7bcuQKWXX4ESqB6ARaate-31KYBfQRvD15B58EW2PaFAwe6HXwa2oYTz6nBFydO4qQ8NBgm-rswSWgowRdH4Bij7yOV3D9_WRrbZkEXg2T3bszjCnmkuDYeGf4BF8wAyHDPuTA5EmrEFRbwwRgz52JxJ_fdCuXo0fW8PgEYTxCDZfJVxQL8UVPtni1BGJJH5ObSfUeu_6lG56ZcARjbusa1ejDm_hnPlQFC2AEZDvY4VytQJHH0_PZ9AreBGXaCJCapiug4KCjZxvEQgRmsRhMaTd-HsYmO0rlM2kEZ8cEGdc4I725r4nVBQDOBGiIs4anENOajlEGKcnf5ARpZ8p6G3Yk_lY5ntTo5GgEajpUAy3GVOWnJWz85mu7BGtuYSVeToevN-MuH9BnCwTfK3e1C1TFovhZgMTv7SIE5R5DBzmMKhInlB-4zBQS","universal_uid":"ID5*8EMbdB5NH411ptmkyOYTGNxhqgAJ9oYHSQPbypsG9CgEVXCnkyljQgL1v5yq5xgXBFZC1yzK7F8MI06UTtGZYQRXnxSB6avBY3bEWI6JpQgEWAM86G9Q-BJVo8yGILhfBFkWSi9O946jT4qhbiyBkQRagVh6-N5gbN91lj8orvwEW_cxBqw97u9ngOnF2F5sBFwGxGVfaKG-N6dBJjm53QRdl1kGNPuSoAXmqsRSykwEXp9NqIdP3gpqQWheHrzYBF-Jl0svNw7hqFXVPCnMWwRgt-3Rj3ymubwaW45lt8MEYUzgOSURYAopZgXSHCaUBGLLKFS_kQPQJgxz0rakZwRjIupYZOOSevcP8MjyZy8EZBTSmGnsiy_zIaDSTUiiBGVeJ7No7V-fEDYuqJX87gRmiUpN4kRhXopqS5PmYzUEZyZ2SAhjMxdfOQb9GOOoBGiGFIKYXqyUi3rSC83-KwRpbFBp86SeDUdTh_9kmJMEajWJ1wwHxpiaTaIvNwILBGvlujIkGYUZ6rffUgwc-ATf989ddAY7l135HY-1mtgE5TMzEGW05eh_Slimv8yT","signature":"ID5_Af7FcZ44YZ9YO-o5c7pwRMocMixrsLSxLQIba4d5GJ-musGQnodEq8YU1Lhnbs5Crn9lJXhmO1ARbKjnoq3gsWs","link_type":2,"cascade_needed":true,"privacy":{"jurisdiction":"other","id5_consent":true}}; _cc_id=589744b018b77ff0c829dd767a86ed67; panoramaId=eaffbaa0b1b49b5c6c7edf9dac1f4945a702da40840206bc42cc04d32b6506cc; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; _sp_v1_ss=1:H4sIAAAAAAAAAItWqo5RKimOUbLKK83J0YlRSkVil4AlqmtrlXSIUxYLAPL1gztPAAAA; _sp_v1_opt=1:; panoramaId_expiry=1643169598566; cto_bidid=fLI0ZV9vNnRnZmNlbFMyY1NjNTZIajNtYVI5NDNCaGE0OVIzRUdrUUdVJTJCWnlQQlZ4emFSRVVzekFUQUFuYVhyN2YlMkI5UXAlMkIlMkZ1SlZOUmR5eWdoZ2taJTJGVFhBemtrNDA4YzdtVTBpbnNHMGJWU09TS1ZOUnM0YUlOdll4YkNvTkFqczVKbHp2TUZObUx1TXN3Rk9xUWxsZmllVUxRJTNEJTNE; cto_bundle=2LyQt19lM2hjbDhmTWR2dnc5M3VOU2x3TkdxUU93TkZoS3V5WTZlMm1SUjZSYmt2RlI2WW8wU2ExbmNCMnJxNGZiRmJQNjdVOXAxamtpVG9jZngzQXM4eVpWeFUlMkJqMmdFcHZVa3hqQ002TDl2RnZ0Zkc0eSUyQjkwdXZtcmklMkZ3aUdOYXV0Q3lqaW1KeGVjbGJDdHBwa2VhOEZKeTIyY1BZWVVKYjltR0ZXc2pDWG91UzJpWnY2aUlBNkd4WnlTWEx5RU9IQ1Q; _sp_v1_consent=1!1:1:1:0:0:1; _gid=GA1.2.409045250.1642984974; adp_segs=e0,e13g,e13t,ev6,e1p,e4,e3m,e1l,e6a,e4d,e1g,e1te,e13x,e6,eka,e1wv,emj,ezx,e67,e1u,e1th,ey,e29r,e69,e1i,eb,e2j3,e1wq,e1hf,e2gy,ezy,e1t9,e1wt,e26j,e26d,e2j2,ec,ev5,ek2,ev1,e26u,eva,e1,e26e,ejl,e2ay,e11f,emi,e1ta,e26y,e1t,e64,e7,ej1,e34,e2ak,e1o,e1wy,e1h,e1wx,e1ra,ejm,e3o,e1e1,e9,e1j,e3a,e1rb,e4v,e38,e13h,e68,e1ws,e18k; POPUPCHECK=1643071406459; AMP_TOKEN=$NOT_FOUND; gid=undefined; _gat=1; gujfirstimp=1643000096853; _sp_v1_data=2:437077:1642562187:0:83:0:83:0:0:_:-1; ioam2018=0014e6dcd5ef7a9dd61dc9dd6:1668113878662:1641848278662:.chefkoch.de:183:chefkoch:rezept_suche:noevent:1643000097205:xh4fh4; _gat_gaTracker=1; cto_bundle=LdHnAV9lM2hjbDhmTWR2dnc5M3VOU2x3TkdtV3FzdVNBUWN4TnJiNjB3NlElMkZMaTVQUXZiaEZQZFY5bzdNWW9qZVgwako3UHBtdlJ2Nm8yNXNJUUdqUzRmJTJCWktxcUNWczFUWTNYJTJCNUsxZU1YTU1sdDZ0Tm54aWhta0pPbDZXRmppWTlzMkpzdk5oSWNBRnVUMkllRkgxTlQ3aG82VjJ1a1RJWm5SSlA3NUE0NDlKUmhHYjQ0WTM1alAlMkZGUHp2U0dmeTVKQQ; cto_bundle=LdHnAV9lM2hjbDhmTWR2dnc5M3VOU2x3TkdtV3FzdVNBUWN4TnJiNjB3NlElMkZMaTVQUXZiaEZQZFY5bzdNWW9qZVgwako3UHBtdlJ2Nm8yNXNJUUdqUzRmJTJCWktxcUNWczFUWTNYJTJCNUsxZU1YTU1sdDZ0Tm54aWhta0pPbDZXRmppWTlzMkpzdk5oSWNBRnVUMkllRkgxTlQ3aG82VjJ1a1RJWm5SSlA3NUE0NDlKUmhHYjQ0WTM1alAlMkZGUHp2U0dmeTVKQQ; __gads=ID=a448373a0c96e368-22d5f01861d00026:T=1641848278:RT=1643000119:S=ALNI_MYkRlVpqOhMh04cY_t4_lTz_EOfjw',
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
    for i in json.loads(sel.xpath('//script[@type="application/ld+json"]/text()').get(''))['itemListElement']:
        lst.append(i['url'])
        
    return lst


# In[3]:


htmlOnePageSpider('https://www.chefkoch.de/rs/s0t29,85,86/Europa-Ungarn-Osteuropa-Rezepte.html', htmlLst)


# In[4]:


# 2. go through all categories and pages in the web and get all recipe htmls

def htmlAllPageSpider(htmlLst):
    """
    output: htmlLst with all recipes htmls on all pages of one category
    
    """
    # initialize pageLst to store the htmls of all pages
    pageLst = []
    
    for i in range(14):
        pageLst.append('https://www.chefkoch.de/rs/s{}t29,85,86/Europa-Ungarn-Osteuropa-Rezepte.html'.format(i))
        
    for i in pageLst:
        fillLst = htmlOnePageSpider(i, htmlLst)
    
    return list(set(fillLst))


# In[5]:


htmlAllPageSpider(htmlLst)


# In[6]:


# the number of recipes we have in total
len(htmlLst)


# In[7]:


# 3. go through all recipe htmls and scrape the data we want

Hungarydata = {
    "Name of the recipe":[],
    "Total time":[],
    "Prep time":[],
    "List of ingredients": [],
    "List of instructions":[],
    "Number of servings":[],
    "Category":[]
}

def HungarySpider(recipe_url):
    """
    input: recipe_url,, the url of the recipe web
    output: Dic with all information we need for one recipe 
    
    """
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie':'amp-access=amp-2MxlvFY65-5PY3Zx04mRRw; _sp_v1_uid=1:587:77db6f98-749e-4f3e-b268-ba9bc16bd456; _sp_v1_csv=null; _sp_v1_lt=1:; consentUUID=7e360bc6-3ca9-4a55-af31-632a0ff3cba6_3; euconsent-v2=CPSnipaPSnipaAGABCENB9CgAP_AAAAAACiQHsgZBDoUTWHAUXh4QvtAGYQSEEQVIGACCBCAIiABAAAEMDQAkkAAoASAAAACAQQAIBIBAAAECAAEAAAAAAAEAAEgAAAAhAAIIAJAABAAAAAAAAoCAAAAAAAIAAARAAAAmQCAA0KFAGAAAAAQAAAAgAAAAAAAAAEAAAAAAIIAAAEQkCAACoAGQAPAAgABkADQAHkARABFACYAE8AN4AcwA_ACGAEsAJoAUoAtwBhgDVAHwAP0AjgBigDcAHoAQ2AkQBQ4CkQF5gNOCAAwASADNASsOgWAAVAAyACAAGQANAAeAA-gCIAIoATAAnwBcAF0AL4AYgA3gBzAD8AIYASwAmABNAClAFiALcAYYA0QB-gEWAI4AWIAtABdQDFAG4APQAhsBF4CQQEiAKHAXmAvoBiQDLAGnDgBIAFwASABkAGaAQUAhABgQDXgJWDQBgAuACGAIKAWgBIgCkREAMAQwCRAFIiAAIAJBkAMAJgBHAF5jAAIBYhUAYAJgAXACOAFoASCAvMUABAIKQgHgAZACYAFwAL4AYgA3gCxAI4AWgAxQB6AEggJEAW0AxIgACAIKAWIlAUAAyADwAIgATAAuABfADEAIYAUoAtwBqgEcALQAXUAxQBuAEXgJEAXmAywkAEAAuAGQA14CVikB4ACoAGQAQAAyABoADyAIgAigBMACeAF8AMQAcwA_ACGAFKALEAW4A0QBqgD9AIsARwAxQBuAD0AIvASIAocBeYC-igAcAC4AJAAyAE7ALEAXUA14AAA.YAAAAAAAAAAA; sp_ga=1; sp_rewe=1; _ga=GA1.2.1308220345.1641848278; iom_consent=0103ff03ff&1641848278658; uuidpd=3ad5dee9-68f0-4340-8e44-848adb6a4c0f; fptthc=55e5d1af-0b8e-486c-a6f2-e0032dcdc8d9; publ=; _pbjs_userid_consent_data=3524755945110770; PubCommenId=2fd6faf7-05e8-4a39-8993-80083d915e59; pbjs-unifiedid={"TDID":"b8e2d1cd-d84b-4c0b-b941-7dc42e3021de","TDID_LOOKUP":"TRUE","TDID_CREATED_AT":"2021-12-10T20:58:11"}; id5_storage={"created_at":"2022-01-10T20:58:11.209285Z","id5_consent":true,"original_uid":"ID5*ySB8Et17HM5CJ7y6-rvZn0kEpdDRmO1tDmxwDDGRIKsEVSzS3NvgZX_3Wd3xL3i9BFaSnGMnX7MSXCk4jWOtZQRXfrwyTQgFf2Fczvtk5AYEWARi3pICvARHbiT3ZLQmBFmFNf7bcuQKWXX4ESqB6ARaate-31KYBfQRvD15B58EW2PaFAwe6HXwa2oYTz6nBFydO4qQ8NBgm-rswSWgowRdH4Bij7yOV3D9_WRrbZkEXg2T3bszjCnmkuDYeGf4BF8wAyHDPuTA5EmrEFRbwwRgz52JxJ_fdCuXo0fW8PgEYTxCDZfJVxQL8UVPtni1BGJJH5ObSfUeu_6lG56ZcARjbusa1ejDm_hnPlQFC2AEZDvY4VytQJHH0_PZ9AreBGXaCJCapiug4KCjZxvEQgRmsRhMaTd-HsYmO0rlM2kEZ8cEGdc4I725r4nVBQDOBGiIs4anENOajlEGKcnf5ARpZ8p6G3Yk_lY5ntTo5GgEajpUAy3GVOWnJWz85mu7BGtuYSVeToevN-MuH9BnCwTfK3e1C1TFovhZgMTv7SIE5R5DBzmMKhInlB-4zBQS","universal_uid":"ID5*8EMbdB5NH411ptmkyOYTGNxhqgAJ9oYHSQPbypsG9CgEVXCnkyljQgL1v5yq5xgXBFZC1yzK7F8MI06UTtGZYQRXnxSB6avBY3bEWI6JpQgEWAM86G9Q-BJVo8yGILhfBFkWSi9O946jT4qhbiyBkQRagVh6-N5gbN91lj8orvwEW_cxBqw97u9ngOnF2F5sBFwGxGVfaKG-N6dBJjm53QRdl1kGNPuSoAXmqsRSykwEXp9NqIdP3gpqQWheHrzYBF-Jl0svNw7hqFXVPCnMWwRgt-3Rj3ymubwaW45lt8MEYUzgOSURYAopZgXSHCaUBGLLKFS_kQPQJgxz0rakZwRjIupYZOOSevcP8MjyZy8EZBTSmGnsiy_zIaDSTUiiBGVeJ7No7V-fEDYuqJX87gRmiUpN4kRhXopqS5PmYzUEZyZ2SAhjMxdfOQb9GOOoBGiGFIKYXqyUi3rSC83-KwRpbFBp86SeDUdTh_9kmJMEajWJ1wwHxpiaTaIvNwILBGvlujIkGYUZ6rffUgwc-ATf989ddAY7l135HY-1mtgE5TMzEGW05eh_Slimv8yT","signature":"ID5_Af7FcZ44YZ9YO-o5c7pwRMocMixrsLSxLQIba4d5GJ-musGQnodEq8YU1Lhnbs5Crn9lJXhmO1ARbKjnoq3gsWs","link_type":2,"cascade_needed":true,"privacy":{"jurisdiction":"other","id5_consent":true}}; _cc_id=589744b018b77ff0c829dd767a86ed67; panoramaId=eaffbaa0b1b49b5c6c7edf9dac1f4945a702da40840206bc42cc04d32b6506cc; OB-USER-TOKEN=57170f9e-be05-4c47-af7f-a5cad9a56a87; _sp_v1_ss=1:H4sIAAAAAAAAAItWqo5RKimOUbLKK83J0YlRSkVil4AlqmtrlXSIUxYLAPL1gztPAAAA; _sp_v1_opt=1:; panoramaId_expiry=1643169598566; cto_bidid=fLI0ZV9vNnRnZmNlbFMyY1NjNTZIajNtYVI5NDNCaGE0OVIzRUdrUUdVJTJCWnlQQlZ4emFSRVVzekFUQUFuYVhyN2YlMkI5UXAlMkIlMkZ1SlZOUmR5eWdoZ2taJTJGVFhBemtrNDA4YzdtVTBpbnNHMGJWU09TS1ZOUnM0YUlOdll4YkNvTkFqczVKbHp2TUZObUx1TXN3Rk9xUWxsZmllVUxRJTNEJTNE; cto_bundle=2LyQt19lM2hjbDhmTWR2dnc5M3VOU2x3TkdxUU93TkZoS3V5WTZlMm1SUjZSYmt2RlI2WW8wU2ExbmNCMnJxNGZiRmJQNjdVOXAxamtpVG9jZngzQXM4eVpWeFUlMkJqMmdFcHZVa3hqQ002TDl2RnZ0Zkc0eSUyQjkwdXZtcmklMkZ3aUdOYXV0Q3lqaW1KeGVjbGJDdHBwa2VhOEZKeTIyY1BZWVVKYjltR0ZXc2pDWG91UzJpWnY2aUlBNkd4WnlTWEx5RU9IQ1Q; _sp_v1_consent=1!1:1:1:0:0:1; _gid=GA1.2.409045250.1642984974; adp_segs=e0,e13g,e13t,ev6,e1p,e4,e3m,e1l,e6a,e4d,e1g,e1te,e13x,e6,eka,e1wv,emj,ezx,e67,e1u,e1th,ey,e29r,e69,e1i,eb,e2j3,e1wq,e1hf,e2gy,ezy,e1t9,e1wt,e26j,e26d,e2j2,ec,ev5,ek2,ev1,e26u,eva,e1,e26e,ejl,e2ay,e11f,emi,e1ta,e26y,e1t,e64,e7,ej1,e34,e2ak,e1o,e1wy,e1h,e1wx,e1ra,ejm,e3o,e1e1,e9,e1j,e3a,e1rb,e4v,e38,e13h,e68,e1ws,e18k; POPUPCHECK=1643071406459; AMP_TOKEN=$NOT_FOUND; gid=undefined; _gat=1; gujfirstimp=1643000096853; _sp_v1_data=2:437077:1642562187:0:83:0:83:0:0:_:-1; ioam2018=0014e6dcd5ef7a9dd61dc9dd6:1668113878662:1641848278662:.chefkoch.de:183:chefkoch:rezept_suche:noevent:1643000097205:xh4fh4; _gat_gaTracker=1; cto_bundle=LdHnAV9lM2hjbDhmTWR2dnc5M3VOU2x3TkdtV3FzdVNBUWN4TnJiNjB3NlElMkZMaTVQUXZiaEZQZFY5bzdNWW9qZVgwako3UHBtdlJ2Nm8yNXNJUUdqUzRmJTJCWktxcUNWczFUWTNYJTJCNUsxZU1YTU1sdDZ0Tm54aWhta0pPbDZXRmppWTlzMkpzdk5oSWNBRnVUMkllRkgxTlQ3aG82VjJ1a1RJWm5SSlA3NUE0NDlKUmhHYjQ0WTM1alAlMkZGUHp2U0dmeTVKQQ; cto_bundle=LdHnAV9lM2hjbDhmTWR2dnc5M3VOU2x3TkdtV3FzdVNBUWN4TnJiNjB3NlElMkZMaTVQUXZiaEZQZFY5bzdNWW9qZVgwako3UHBtdlJ2Nm8yNXNJUUdqUzRmJTJCWktxcUNWczFUWTNYJTJCNUsxZU1YTU1sdDZ0Tm54aWhta0pPbDZXRmppWTlzMkpzdk5oSWNBRnVUMkllRkgxTlQ3aG82VjJ1a1RJWm5SSlA3NUE0NDlKUmhHYjQ0WTM1alAlMkZGUHp2U0dmeTVKQQ; __gads=ID=a448373a0c96e368-22d5f01861d00026:T=1641848278:RT=1643000119:S=ALNI_MYkRlVpqOhMh04cY_t4_lTz_EOfjw',
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

def fillHungaryData(html,dic):
    """
    input: html, the recipe html
    input: dic, the dictionary containing the information we need
    output: fill in data
    
    """
    content = HungarySpider(html)
    dic['Name of the recipe'].append(content['name'])
    dic['Total time'].append(content['totalTime'])
    dic['Prep time'].append(content['prepTime'])
    dic['List of ingredients'].append(content['recipeIngredient'])
    dic['List of instructions'].append(content['recipeInstructions'])
    dic['Number of servings'].append(content['recipeYield'])
    dic['Category'].append(content['recipeCategory'])    


# In[8]:


# go through all recipe urls
import time

for html in htmlLst:
    try:
        fillHungaryData(html,Hungarydata)
    except:
        time.sleep(5)


# In[9]:


# convert data to dataframe
Hungary = pd.DataFrame(Hungarydata)
print(Hungary.shape)
Hungary.head()

# save dataset
Hungary.to_csv("/Users/xixi/Dropbox/food4thought/data/raw/Hungary.csv")


# In[ ]:





# In[ ]:




