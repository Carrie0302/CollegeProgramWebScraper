# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 14:24:57 2018
This downloads an occupation training data from the BLS website
@author: carrie
"""
from bs4 import BeautifulSoup
import requests, urllib.request, shutil
import datetime, os


class BLSOccupationTraining:
    '''Download the data at the link called Other available formats: (XLSX) on the Education and training assignments by detailed occupation page'''
    
    #BLS Data Source
    BLS_url = 'https://www.bls.gov/emp/ep_table_112.htm'
    base_url = "https://www.bls.gov/"
    page = requests.get(BLS_url)
    titleShouldBe = "Education and training assignments by detailed occupation"
    
    #Todays Date
    now = datetime.datetime.now()
    formatTime = now.strftime("%Y-%m-%d %H:%M")
    print("Running BLS Occupation Training Web scraper: {0}".format(formatTime))
    
    
    #First test is if the page will load
    def PageStatus(self):
        status = self.page.status_code
        soup = ""
        if status == 200:
            soup = BeautifulSoup(self.page.text, 'html.parser')
            self.CheckElementonWebsite(soup, self.titleShouldBe)
            print("Downloading...")
            self.DownloadBLSOccTraining(soup)
            
        else:
            print("Page will not load")
            log = open("Error_Data.txt","a")
            log.write("Error on Page Load: Page status is " + "  " + str(status)  + "\t" + "Date: " + self.formatTime + "\n")
    
    
    #Check if the page title has changed if so the rest of the page and downloads may have changed so log the issue
    def CheckElementonWebsite(self,  soup, titletoCheckAgainst ):
        title = soup.title.string
        if title == titletoCheckAgainst:
            print("Title of web page check passed: {0}".format(soup.title.string))
        else:
            print("Title on BLSOccupationTraining website changed")
            log = open("Error_Data.txt","a")
            log.write("Title on Website has changed from '" + str(titletoCheckAgainst)  + "' to '" +  str(title)   + "' \t" + "Date: " + self.formatTime + "\n")
    
        
    #Download BLS worksheet
    def DownloadBLSOccTraining(self, soup):
        body = soup.find("div", {"id": "bodytext"})
        links = body.find_all('a', href=True)[0]
        
        href = links['href']
        url = self.base_url + href
        dir_path = os.path.dirname(os.path.realpath(__file__))
        bLS_OccupationTraining = os.path.join(os.path.sep, dir_path,  'log', 'BLS_OccupationTraining.xlsx')
        
        with urllib.request.urlopen(url) as response, open(bLS_OccupationTraining, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)


##MAIN
#wages = BLSOccupationTraining()
#wages.PageStatus()


    
