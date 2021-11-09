
# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_p = mars_news(browser)

     # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_p,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": mars_hemispheres(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Visit the mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)
    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        # Use the parent element to find the first `a` tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None

    return news_title, news_p

# ### Featured Images

def featured_image(browser):
    # Visit image url
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base URL to create an absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

# ### Mars Info Table

def mars_facts():
    try:
        # Use 'read_html' to scrape the facts table into a DataFrame
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    # Assign columns and set index
    df.columns=['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    # Convert DataFrame into html format
    return df.to_html(classes="table table-striped")

# ### Mars Hemisphere Data

def mars_hemispheres(browser):
    # Visit hemisphere url
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    # Parse the html
    html = browser.html
    mars_soup = soup(html, 'html.parser')
    # Retreive the hemisphere elements
    hems = mars_soup.find_all('div', class_='description')
    i = 0
    for hem in hems:
        try:
            hemispheres = {}
            # clink each hemisphere link
            browser.find_by_tag('h3')[i].click()
            hem_soup = soup(browser.html, 'html.parser')
            # find imgage url and append hemisphere dictionary
            rel_url = hem_soup.find('img', class_='wide-image').get('src')
            img_url = str(rel_url)
            # find image title and append dictionary
            title = str(hem_soup.find('h2').text)
            hemispheres = {"img_url": f"https://marshemispheres.com/{img_url}",
                            "title": title}
            hemisphere_image_urls.append(hemispheres)
            browser.back()
            i += 1
        
        except BaseException:
            return None
        
        return hemisphere_image_urls


if __name__ == "__main__":

    # If running as scrpit, print scraped data
    print(scrape_all())
