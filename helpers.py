import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import time
import json

# Abstract parts of Beautiful Soup
def extract_soup_from_response(response):
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print(
            f"Error: Unable to fetch the hotel page. Status code: {response.status_code}")
        return None

# Function to extract soup from a webpage using Selenium
def extract_soup_with_selenium(link):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(link)

    try:
        # Wait for the reviews element to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'tc-reviews'))
        )

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup
    except TimeoutException:
        print("Timed out waiting for reviews element.")

        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        return soup
    finally:
        driver.quit()

# Get primary data (name, link, tags, description)
def extract_primary_data(hotel):
    link = ''
    name = ''
    description = ''
    tags = ''

    try:
        link = hotel.find('h2').find('a')['href']
        name = hotel.find('h2').find('a').text.strip()
        description = hotel.find('div', class_='mt-2').text.strip()
        experiences = [li.text.strip() for li in hotel.find('ul', class_='hotel-experiences').find_all('li')]
        tags = ', '.join(experiences)

        return link, name, description, tags
    except AttributeError:
        return link, name, description, tags

# Get address data
def get_address_data(script):
    address_str = ''
    try:
        data = json.loads(script)
        address_data = data.get('address', {})
        address = [
            address_data.get('streetAddress'),
            address_data.get('addressLocality'),
            address_data.get('addressRegion'),
            address_data.get('addressCountry')
        ]
        address_str = ', '.join(filter(None, address))
    except (json.JSONDecodeError, AttributeError, KeyError):
        print("Error: Unable to fetch address data.")
    
    return address_str

# Get neighborhood data
def get_neighborhood_data(neighborhood_element):
    neighborhood = ''
    if neighborhood_element:
        neighborhood = neighborhood_element.get_text(strip=True).replace('NEIGHBORHOOD:', '')
    return neighborhood

# Get nearest airport data
def get_airport_data(text):
    airport = ''
    if text:
        airport = text.split(':', 1)[1].strip()
    return airport

# Get neighborhood data
def get_neighborhood_data(text):
    neighborhood = ''
    if text:
        neighborhood = text.split(':', 1)[1].strip()
    return neighborhood

# Get size data
def get_size_data(text):
    size = ''
    if text:
        size = text.split(':', 1)[1].strip()
    return size

# Get room style data
def get_room_style_data(text):
    room_style = ''
    if text:
        room_style = text.split(':', 1)[1].strip()
    return room_style

# Get room style data
def get_vibe_data(text):
    vibe = ''
    if text:
        vibe = text.split(':', 1)[1].strip()
    return vibe

# Get insider tip
def get_insider_tip(element):
    tip = ''
    if element:
        tip = element.find('div', class_='mt-2').get_text(strip=True)
    return tip

def get_virtuoso_benefits(element):
    benefits = ''
    if element:
        header = element.find('h2', class_='text--serif').text
        benefits += f"{header}\n\n"

        for li in element.select('ul li'):
            benefits += f"- {li.get_text(strip=True)}\n"

        note = element.find('div', class_='mt-3').text
        benefits += f"\nNote: {note}"
    return benefits

def get_amenities(element):
    amenities = ''
    if element:
        header = element.find('h2', class_='text--serif').text
        amenities += f"{header}\n\n"

        for category in element.find_all('div', class_="-category"):
            category_title = category.find('h4').text
            amenities += f"{category_title}\n"
            for item in category.find_all('li'):
                amenities += f"- {item.get_text(strip=True)}\n"
    return amenities

def get_reviews(element):
    reviews = {}
    reviews_list = []
    recommended = False
    recommended_percentage = ''
    total_reviews = ''

    if element:
        percentage_raw_element = element.find('h2', class_='text--serif')
        if percentage_raw_element:
            recommended_percentage_raw = percentage_raw_element.text
            recommended_percentage = recommended_percentage_raw.split('%')[0]

        total_reviews_element = element.find('h4', class_='mb-3')
        if total_reviews_element:
            total_reviews_raw = total_reviews_element.text
            total_reviews = total_reviews_raw.split(' ')[0]

        for review in element.find_all('li'):
            recommended_text_element = review.find('b', class_='text-gray')
            if recommended_text_element:
                recommended_text = recommended_text_element.text.strip()
                if recommended_text == 'Recommended':
                    recommended = True
                elif recommended_text == 'Not Recommended':
                    recommended = False

            review_date_element = review.find('div', class_='text-right')
            review_date = review_date_element.text.strip() if review_date_element else ''
            
            headline_element = review.find('h3', class_="-headline text--serif")
            headline = headline_element.text.strip() if headline_element else ''
            
            reviewer_name_element = review.find('div', class_='text--small')
            reviewer_name = reviewer_name_element.text.strip() if reviewer_name_element else ''

            review_content_element = review.find('div', class_='-content')
            review_content = review_content_element.text.strip() if review_content_element else ''

            review_data = {
                'recommended': recommended,
                'review_date': review_date,
                'headline': headline,
                'reviewer_name': reviewer_name,
                'review_content': review_content,
            }

            reviews_list.append(review_data)
    
            reviews = {
                'recommended_percentage': recommended_percentage,
                'total_reviews': total_reviews,
                'reviews': reviews_list
            }

    return reviews

# Extract advanced data
def extract_advanced_data(link):
    soup = extract_soup_with_selenium(link)

    neighborhood = ''
    address = ''
    airport = ''
    size = ''
    style = ''
    vibe = ''
    tip = ''
    benefits = ''
    reviews = {}

    if soup:
        # Pull address data
        script_content = soup.find('script', {'type': 'application/ld+json'}).string
        address = get_address_data(script_content)

        # Pull neighborhood and airport data
        info_element = soup.find('div', class_='-info')
        if info_element:
            for div in info_element.find_all('div'):
                text = div.get_text(strip=True)
                if 'NEAREST AIRPORT' in text:
                    airport = get_airport_data(text)
                if 'NEIGHBORHOOD' in text:
                    neighborhood = get_neighborhood_data(text)

        additional_element = soup.find('div', class_='d-md-flex mt-0')
        if additional_element:
            for div in additional_element.find_all('div'):
                text = div.get_text(strip=True)
                if 'SIZE' in text:
                    size = get_size_data(text)
                if 'ROOM STYLE' in text:
                    style = get_room_style_data(text)
                if 'VIBE' in text:
                    vibe = get_vibe_data(text)

        tip_element = soup.find('div', class_='advisor-tip mt-3 mb-0')
        tip = get_insider_tip(tip_element)

        benefits_element = soup.find('div', class_="-amenities")
        benefits = get_virtuoso_benefits(benefits_element)

        amenities_element = soup.find('div', class_='slab slab--gray product-features mt-6')
        amenities = get_amenities(amenities_element)

        reviews_element = soup.find('li', id='tc-reviews')
        reviews = get_reviews(reviews_element)

    return airport, address, neighborhood, size, style, vibe, tip, benefits, amenities, reviews