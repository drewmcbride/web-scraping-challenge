from bs4 import BeautifulSoup as bs
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import requests
import pymongo
import time


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)
    return browser


def scrape_info():
    browser = init_browser()

    # Visit NASA news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    time.sleep(1)

    # Scrape page into Soup
    # html = browser.html
    # soup = bs(html, "html.parser")
    # response = requests.get(url)
    # soup = bs(response.text, 'lxml')
    
    soup = bs(browser.html, 'html.parser')

    # Get the news title 
    title_results = soup.find_all('div', class_='content_title')[1]
    nasa_first_title = title_results.text.strip()

    # Get the news description
    description_results = soup.find_all('div', class_='article_teaser_body')[0]
    nasa_first_description = description_results.text.strip()

    # -----------

    # Visit featured image site
    image_url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/'
    index = 'index.html'
    browser.visit(image_url + index)  

    # HTML and soup config 
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


    # ------------

    # Space facts

    space_facts_url = 'https://space-facts.com/mars/'

    tables = pd.read_html(space_facts_url)
    mars_facts = tables[0]
    mars_facts.rename(columns={0:'Description',1:'Mars'}, inplace=True)
    mars_facts.set_index('Description',inplace=True)
    mars_table_html = mars_facts.to_html(classes="table table-stripped")

    # -------------

    # Hemisphere data

    astro_url = 'https://astrogeology.usgs.gov'
    hemi_route = '/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(astro_url+hemi_route)

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

    # Store data in a dictionary
    mars_data = {
        "nasa_news_title": nasa_first_title,
        "nasa_news_desc": nasa_first_description,
        "featured_image": featured_image_url,
        "mars_facts": mars_table_html,
        "hemisphere_urls": hemisphere_image_urls
         }

    # Close the browser after scraping
    browser.quit()

    # Return results
    return mars_data
