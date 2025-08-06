"""
Notes:
- this script scrapes the Esri support website to check for any patches available for ArcGIS Enterprise or Pro
- you can change the filters on the website via web browser to generate the "url" variable to check for patches for the Esri producs of your interest
- current solution only gets content from first group in pagination
- you can deal with the information gathered (email, write to file, etc)
- you can add logic to write status messages and errors to a file using the logging module
- you can adjust the day and week deltas based upon how often you want to run this script
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from time import sleep
from datetime import datetime, timedelta
import sys

try:
    # Set up Chrome options
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run headlessly
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    # Set up ChromeDriver using webdriver-manager
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # URL for ArcGIS Enterprise related patches
    url = "https://support.esri.com/en-us/search?product=arcgis+server&product=arcgis+data+store&product=portal+for+arcgis&product=arcgis+web+adaptor+iis&product=arcgis+web+adaptor+java&s=Newest&cardtype=support_patches_updates&product=arcgis+enterprise"
    # ArcGIS Pro patches URL : https://support.esri.com/en-us/search?s=Newest&cardtype=support_patches_updates&product=arcgis+pro

    # Open the URL
    driver.get(url)

    # Wait for content to load
    sleep(10)  # Adjust based on network speed

    # Get the page source and parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Close the browser
    driver.quit()

    # Find all support article cards
    articles = soup.find_all("article", class_="card-job-block lighttheme support-card")

    # container for outputs
    data_list = []

    #for i, article in enumerate(articles, start=1):
    for article in articles:
        # HTML elements
        # title of patch
        title_tag = article.find("h2")
        # link to page describing patch
        link_tag = article.find("a", href=True)
        # date of article
        date_tag = article.select(".support-bottomText")
        
        # extract text from HTML elements
        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        link = f"{link_tag['href']}" if link_tag else "No Link"
        date = date_tag[0].get_text(strip=True) if date_tag else "No Date"
        # placeholder for date object
        date_obj = None

        # check date
        try:
            date_obj = datetime.strptime(date, "%B %d, %Y")
        except:
            pass
        # only run if date_obj is a date object
        if date_obj is not None:
            # get current date
            now = datetime.now()
            # can modify number of days based upon how often you run this script
            # Check if within the last day
            within_last_day = now - timedelta(days=1) <= date_obj <= now
            # Check if within the last week
            within_last_week = now - timedelta(weeks=1) <= date_obj <= now
            
            # add patch notice if it is newer than when you last ran this script
            """
            if within_last_day is True:
                data_list.append([date, title, link])
            """
            """
            if within_last_week is True:
                data_list.append([date, title, link])
            """

        # add entry to list
        # un-comment to see what result is for all patches on first page
        #data_list.append([date, title, link])    

    # print out returned results
    for el in data_list:
        print(f'{el[0]} | {el[1]} | {el[2]}\n')
    
    # send email of data or write to log file
except (Exception, EnvironmentError) as e:
    # information about the error
    tbE = sys.exc_info()[2]
    # print the line number the error occured on
    print("Failed at Line {}".format(tbE.tb_lineno))
    # print error message
    print("Error: {}".format(e))