#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Dependencies
from bs4 import BeautifulSoup as bs
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
import pymongo

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


# In[2]:

def scrape_info():
    browser = init_browser()

# URL of page to be scraped
url = 'https://mars.nasa.gov/news/'


# In[3]:


conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)


# In[4]:


response = requests.get(url)


# In[5]:


soup = bs(response.text, 'lxml')


# In[6]:


print(soup.prettify())


# In[13]:


title_results = soup.find_all('div', class_='content_title')[0]
# results
nasa_first_title = title_results.text.strip()
nasa_first_title


# In[14]:


description_results = soup.find_all('div', class_='rollover_description_inner')[0]
nasa_first_description = description_results.text.strip()
nasa_first_description


# # Image Scraping 

# In[28]:


# Set up splinter
executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path, headless=False)


# In[29]:


# Split url so I could reference image url for the featured image
image_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/'
index = 'index.html'
browser.visit(image_url + index)


# In[30]:


# html and soup config
html = browser.html
soup = bs(html, 'html.parser')

# navigated from home page to featured image page
browser.links.find_by_partial_text('FULL IMAGE').click()

# found code where image was stored
image = soup.find('img', class_='headerimage fade-in')

# captured featured image url route
featured_image = image['src']

# combined the original image url from above with the featured image route
featured_image_url = image_url + featured_image
featured_image_url


# # Pandas Scraping

# In[31]:


space_facts_url = 'https://space-facts.com/mars/'


# In[32]:


tables = pd.read_html(space_facts_url)
mars_facts = tables[0]
mars_facts.rename(columns={0:'Attribute',1:'Description'}, inplace=True)
mars_facts.set_index('Attribute',inplace=True)
mars_table_html = mars_facts.to_html()
mars_table_html


# # Hemisphere image scraping

# In[33]:


# Set up splinter
executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path, headless=False)


# In[34]:


astro_url = 'https://astrogeology.usgs.gov'
hemi_route = '/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
browser.visit(astro_url+hemi_route)


# In[35]:


html = browser.html
soup = bs(html, 'html.parser')
hemisphere_image_urls = []

hemi_names = soup.find_all('div', class_='item')
for i in hemi_names:
    title = i.find("h3").text.strip()
    link = i.find('a')['href']
    enhanced_img_link = astro_url + link
    
    #Navigate to each page
    browser.visit(enhanced_img_link)
    html = browser.html
    soup = bs(html, 'html.parser')

    # Scrape image url
    image = soup.find('img', class_='wide-image')['src']

    # Combine base url with image url
    final_image_url_link = (astro_url + image)

    # Append hemisphere name and image url to dictionary
    hemisphere_image_urls.append({
        "Hemisphere Image" : title,
        "Image URL" : final_image_url_link
    })
    
    # Print summary of hemisphere, original link, and image
    print(f'{title}:')
    print(f'Page link: {enhanced_img_link}')
    print(f'Image link: {final_image_url_link}')
    
    # Print dictionary
print('----------')
hemisphere_image_urls


# In[ ]:




