import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from helpers import extract_soup_from_response, extract_primary_data, extract_advanced_data


def scrape_virtuoso():
    # Virtuoso scrape link
    url = 'https://www.virtuoso.com/travel/luxury-hotels/search'

    # Virtuoso base link
    base_url = 'https://www.virtuoso.com'

    # Use requests and Beautiful Soup for initial page load
    response = requests.get(url)
    soup = extract_soup_from_response(response)

    # Set up the WebDriver for dynamic interactions
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Render all hotel options
    counter = 0
    while True:
        # Parse the current HTML content with Beautiful Soup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Locate the "Show More" button and click it
        try:
            buttons = driver.find_elements(By.XPATH, '//button')
            show_more_button = next(
                (button for button in buttons if "Show More" in button.text), None)
            driver.execute_script("arguments[0].click();", show_more_button)
            print(f'Show More button {counter} clicked.')
            counter += 1
        except:
            print("Show More button not found.")
            break  # Exit the loop if the button is not found

    data = {
        'Name': [], 'Address': [], 'Neighborhood': [], 'Nearest Airport': [],
        'Size': [], 'Room Style': [], 'Vibe': [], 'Icon Tags': [], 'Description': [], 'Insider Tip': [],
        'Virtuoso Traveler Receives': [], 'At the Hotel': [], 'Reviews': []
    }

    aggregate_hotels = soup.find('ol', class_='list-unstyled product-search-results mt-2')
    for hotel in aggregate_hotels.find_all('li'):
        if hotel:
            try:
                h2_element = hotel.find('h2')
                if h2_element:
                    link_element = h2_element.find('a')
                    if link_element and 'href' in link_element.attrs:
                        link = link_element['href']
            except Exception as e:
                continue

        link, name, description, tags = extract_primary_data(hotel)
        link = base_url + link
        if name == '':
            continue
        airport, address, neighborhood, size, style, vibe, tip, benefits, amenities, reviews = extract_advanced_data(link)

        print(name, link)
        print(reviews)
    
        data['Name'].append(name)
        data['Address'].append(address)
        data['Neighborhood'].append(neighborhood)
        data['Nearest Airport'].append(airport)
        data['Size'].append(size)    
        data['Room Style'].append(style)
        data['Vibe'].append(vibe)
        data['Icon Tags'].append(tags)
        data['Description'].append(description)
        data['Insider Tip'].append(tip)
        data['Virtuoso Traveler Receives'].append(benefits)
        data['At the Hotel'].append(amenities)    
        data['Reviews'].append(reviews)    

    df = pd.DataFrame(data)
    df.to_csv('hotel_data.csv', index=False)


if __name__ == "__main__":
    scrape_virtuoso()
