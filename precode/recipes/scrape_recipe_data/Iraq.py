#!/usr/bin/env python
# coding: utf-8

# In[9]:


import pandas as pd

from  util.iraq.atyabtabkha import Atyabtabkha


# In[10]:


custom_header_template = { #setup custom header because romania requires certain headers
        'referer': 'https://www.google.com/',
        'Accept-Language': '*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html, */*; q=0.01',
        'user-agent': ''}


# In[11]:


attrs = {
        'name'       :  'name',
        'ingredients':  'recipeIngredient',
        'total_time':   'totalTime',
        'instructions': 'recipeInstructions',
        'servings':     'recipeYield',
        'category':     'recipeCategory',
        'prep_time':    'prepTime',
        'cook_time':    'cookTime',
}
available_json = {'xpath' : "normalize-space(//script[@type='application/ld+json'][contains(text(), 'recipeIngredient')])"}
seeds= [
        #soup
        '&post_type=recipe&post_per_page=24&taxonomy=post_tag&tag_name=%d8%ad%d8%b3%d8%a7%d8%a1&term_slug=%d8%ad%d8%b3%d8%a7%d8%a1&ingredient_id=0&featured_id2=0&featured_id=182902&pageNumber={}&maxPages=37&action=more_post_ajax',
        
        #authority? - salad
        '&post_type=recipe&post_per_page=24&taxonomy=post_tag&tag_name=%d8%b3%d9%84%d8%b7%d8%a9&term_slug=%d8%b3%d9%84%d8%b7%d8%a9&ingredient_id=0&featured_id2=0&featured_id=181819&pageNumber={}&maxPages=43&action=more_post_ajax',

        #appetizers
        '&post_type=recipe&post_per_page=24&taxonomy=post_tag&tag_name=%d9%85%d9%82%d8%a8%d9%84%d8%a7%d8%aa&term_slug=%d9%85%d9%82%d8%a8%d9%84%d8%a7%d8%aa&ingredient_id=0&featured_id2=0&featured_id=183239&pageNumber=2&maxPages=139&action=more_post_ajax',
        

        #sandwiches
        '&post_type=recipe&post_per_page=24&taxonomy=post_tag&tag_name=%d8%b3%d9%86%d8%af%d9%88%d9%8a%d8%b4%d8%a7%d8%aa&term_slug=%d8%b3%d9%86%d8%af%d9%88%d9%8a%d8%b4%d8%a7%d8%aa&ingredient_id=0&featured_id2=0&featured_id=183228&pageNumber=2&maxPages=13&action=more_post_ajax',
        
        #breakfast
        '&post_type=recipe&post_per_page=24&taxonomy=post_tag&tag_name=%d9%81%d8%b7%d9%88%d8%b1&term_slug=%d9%81%d8%b7%d9%88%d8%b1&ingredient_id=0&featured_id2=0&featured_id=183161&pageNumber=2&maxPages=81&action=more_post_ajax'

]
listing = {}


# In[ ]:





# # Testing Requests POST with custom payload

# In[ ]:


# payload = """&post_type=recipe&post_per_page=24&taxonomy=post_tag&tag_name=%d8%ad%d8%b3%d8%a7%d8%a1&term_slug=%d8%ad%d8%b3%d8%a7%d8%a1&ingredient_id=0&featured_id2=0&featured_id=182902&pageNumber={}&maxPages=37&action=more_post_ajax"""
# max_page = int(re.findall('(?<=&maxPages=)(.*)(?=&)', payload)[0])
# print('max page: ', max_page)
# POST_URL = 'https://www.atyabtabkha.com/wp-admin/admin-ajax.php'
# session = requests.Session() 
# #randomize user-agent in every request
# random_ua =  get_random_ua()
# header_template = post_request_header_template
# header_template['user-agent'] = random_ua
# session.headers.update(header_template)
# res = session.post(POST_URL, data=payload, headers=header_template)
# if res.status_code == 200:
#     try:
#         doc = html.document_fromstring(res.text)
#         items_xpath = '//div[contains(@class,"article--alt")]/a/@href'
#         urls = doc.xpath(items_xpath)
#         #print(urls)
#         print('amount of urls we got: ', len(urls))
#     except:
#         print('doc is probably empty')
# else:
#     print('failed')
#     print(res.status_code)


# In[12]:


iraq_spider = Atyabtabkha('https://www.atyabtabkha.com', seeds= seeds, listing =listing,attrs= attrs, available_json=available_json,header = custom_header_template)


# In[6]:


one_url = 'https://www.atyabtabkha.com/recipe/%d8%b7%d8%b1%d9%8a%d9%82%d8%a9-%d8%b9%d9%85%d9%84-%d8%b4%d9%88%d8%b1%d8%a8%d8%a9-%d9%84%d8%b3%d8%a7%d9%86-%d8%a7%d9%84%d8%b9%d8%b5%d9%81%d9%88%d8%b1-%d9%85%d8%ab%d9%84-%d8%a7%d9%84%d9%85%d8%b7%d8%a7%d8%b9%d9%85-2327219'


# In[7]:


iraq_spider.scrape_one_item(one_url)


# In[13]:


results_list = iraq_spider.start_scrape()


# In[ ]:




