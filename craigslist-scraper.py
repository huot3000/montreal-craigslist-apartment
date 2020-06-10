#! python3

#SETUP
#import get to call a get request on the site
from requests import get
from bs4 import BeautifulSoup

#get the first page of the Montreal housing
response = get('https://montreal.craigslist.org/search/apa?hasPic=1&availabilityMode=0&sale_date=all+dates&lang=en&cc=us')

#create a BeautifulSoup object
html_soup = BeautifulSoup(response.text, 'html.parser')

#get the listing container
listings = html_soup.find_all('li', class_='result-row')

##CHECKS

#checking if find_all is resturning a result set
print(type(listings))
#checking if appropriate number of results
print(len(listings))

##PARSING ONE POST

#grab the first listing
listing_one = (listings[0])
#check HMTL contents of one listing
print(listings[0])

#grab the first listing's price
listing_one_price = listing_one.a.text
listing_one_price.strip()
print(listing_one_price)

#grab the time and datetime it was posted
listing_one_time = listing_one.find('time', class_='result-date')
listing_one_datetime = listing_one_time['datetime']
print(listing_one_datetime)

#grab URL and post title
listing_one_title = listing_one.find('a', class_="result-title hdrlnk")
listing_one_URL = listing_one_title['href']
listing_one_title = listing_one_title.text

#grab apartment characteristics (number of bedrooms, sqft, hood)
listing_one_num_bedrooms =  listing_one.find('span', class_='housing').text.split()[0]
listing_one_num_sqft = listing_one.find('span', class_='housing').text.split()[2][:-3] #cleaning ft^2 from the end of the string (ommit last 3 characters from string in third string item of list)
listing_one_num_hood = listing_one.find('span', class_='result-hood').text

print(listing_one_num_bedrooms)
print(listing_one_num_sqft)

#BUILDING THE LOOP

#setup
from time import sleep
import re #regulat expressions
from random import randint #avoid throttling by not sending too many requests one after the other
from IPython.core.display import clear_output
import numpy as np 

#find the total number of listings to find the number of loop iterations
search_header = html_soup.find('div', class_= 'search-legend')
results_total = int(search_header.find('span', class_='totalcount').text) # upper bound of the number of listings

#each page has 119 posts, a new page is defined as a multiple of 120
pages = np.arange(0, results_total + 1, 120)

iterations = 0

listing_time = []
listing_hoods = []
listing_title_texts = []
bedroom_counts = []
sqfts = []
listing_links = []
listing_prices = []

for page in pages:

    #get request
    response = get('https://montreal.craigslist.org/search/apa?'
        + 's=' #URL parameter defining the page number
        + str(page) #the page number in the pages array created with np.arange
        + '&hasPic=1' #making sure all listings have photos
        + '&availabilityMode=0&sale_date=all+dates&lang=en&cc=us') #the other parameters (e.g. language, etc.)

    sleep(randint(1,5)) # waiting a bit to avoid throttling

    #create BeautifulSoup object with response
    page_html = BeautifulSoup(response.text, 'html.parser')

    #define the listings
    listings = html_soup.find_all('li', class_='result-row')

    #extract listings characteristics
    for listing in listings:
        if listing.find('span', class_= 'result-hood') is not None:
            # listing_timing
            listing_datetime = listing.find('time', class_= 'result-date')['datetime']
            listing_time.append(listing_datetime)
    
            # listing_hoods
            listing_hood = listing.find('span', class_='result-hood').text
            listing_hoods.append(listing_hood)
            
            # listing_title_texts
            listing_title = listing.find('a', class_='result-title hdrlnk')
            listing_title_text = listing_title.text
            listing_title_texts.append(listing_title_text)
            
            # listing_links
            listing_link = listing_title['href']
            listing_links.append(listing_link)
            
            # listing_prices
            listing_price = int(listing.a.text.strip().replace('$','')) # removes the dollar sign, turns value to integer
            listing_prices.append(listing_price)
            
            #the next two characteristics (bedroom_counts and sqfts) are not always present in a listing, I am hence creating an 'if' clause

            if listing.find('span', class_= 'housing') is not None:
                #if the first element is sqft
                if 'ft2' in listing.find('span', class_='housing').text.split()[0]:
                    #make bedroom count NaN
                    bedroom_count = np.nan
                    bedroom_counts.append(bedroom_count)

                    #make sqft the first element
                    sqft = int(listing.find('span', class_='housing').text.split()[0][:-3])
                    sqfts.append(sqft)

                #if the length of the housing details element is more than 2 (implying there is both bedroom_count and sqft)
                elif len(listing.find('span', class_='housing').text.split()) > 2:

                    #element 0 would be bedroom_count
                    bedroom_count = listing.find('span', class_='housing').text.replace('br','').split()[0]
                    bedroom_counts.append(bedroom_count)

                    #and element 2 would be sqft
                    sqft = listing.find('span', class_='housing').text.split()[2][:-3]
                    sqfts.append(sqft)

                #if there is a number of bedroom but no sqft, the number of elements will be 2
                elif len(listing.find('span', class_='housing').text.split()) == 2:

                    # element 0 would be bedroom count
                    bedroom_count = listing.find('span', class_='housing').text.replace('br','').split()[0]
                    bedroom_counts.append(bedroom_count)

                    # and element 2 would be sqft, but is NaN
                    sqft = np.nan
                    sqfts.append(sqft)

                else:
                    bedroom_count = np.nan
                    bedroom_counts.append(bedroom_count)

                    sqft = np.nan
                    sqfts.append(sqft)
            
            #if none of these conditions work, make bedroom_count and sqft NaN
            else:
                bedroom_count = np.nan
                bedroom_counts.append(bedroom_count)

                sqft = np.nan
                sqfts.append(sqft)

    iterations +=1
    print('Page ' + str(iterations) + ' scraped succesfully.')

print('\n')

print('Scrape complete!' + str(iterations) + 'pages scraped.')

# CREATING A DATAFRAME

# setup

import pandas as pd

# creating dataframe and naming variables

mtl_apts = pd.DataFrame({'posted': listing_time,
                        'neighborhood': listing_hoods,
                        'listing_title': listing_title_texts,
                        'number_bedrooms': bedroom_counts,
                        'sqft': sqfts,
                        'URL': listing_links,
                        'price': listing_prices})

print(mtl_apts.info())
mtl_apts.head(10)

#save to csv
mtl_apts.to_csv('mtl_apts.csv', encoding='utf-8')

### UP-TO-DATE VERSION IN JUPYTER NOTEBOOK