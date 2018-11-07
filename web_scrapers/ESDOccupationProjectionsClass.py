# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 14:24:57 2018
This downloads an occupation projection spreadsheet from Washington State Employment Security Department
@author: carrie
"""
from bs4 import BeautifulSoup
import requests, urllib.request, shutil
import datetime, os


class ESDOccupationProjection:
    '''Download the data at the link called All occupational projections (replacement)'''
    
    #ESD Data Source
    ESD_url = 'https://esd.wa.gov/labormarketinfo/projections'
    page = requests.get(ESD_url)
    titleShouldBe = "ESDWAGOV - Projections"
    
    #Todays Date
    now = datetime.datetime.now()
    formatTime = now.strftime("%Y-%m-%d %H:%M")
    print("Running ESD Occupation Projection Web scraper: {0}".format(formatTime))
    
    
    #First test is if the page will load
    def PageStatus(self):
        status = self.page.status_code
        soup = ""
        if status == 200:
            soup = BeautifulSoup(self.page.text, 'html.parser')
            self.CheckElementonWebsite(soup, self.titleShouldBe)
            print("Downloading...")
            self.DownloadESDOccupationData(soup)
            
        else:
            print("ESD Page will not load")
            log = open("Error_Data.txt","a")
            log.write("Error on ESD Occupation Projection Page Load: Page status is " + "  " + str(status)  + "\t" + "Date: " + self.formatTime + "\n")
    
    
    #Check if the page title has changed if so the rest of the page and downloads may have changed so log the issue
    def CheckElementonWebsite(self,  soup, titletoCheckAgainst ):
        title = soup.title.string
        if title == titletoCheckAgainst:
            print("Title of web page check passed: {0}".format(soup.title.string))

        else:
            print("Title on ESDOccupationProjection website changed")
            log = open("Error_Data.txt","a")
            log.write("Title on Website has changed from '" + str(titletoCheckAgainst)  + "' to '" +  str(title)   + "' \t" + "Date: " + self.formatTime + "\n")
    
    
    def GetFileNamesfromDirectory(self):
        dirpath = os.getcwd()
        print(dirpath+"\log")
        for file in os.listdir(dirpath+"\log"):
            #print(file)
            if file.endswith(".zip"):
                print(os.path.join(dirpath+"\log", file))
                return file
        
        
    #Download ESD worksheet
    def DownloadESDOccupationData(self, soup):
        body = soup.find("article", {"class": "content-item"})
        links = body.find_all('a', href=True)[3]        
        href = links['href']
        url = href
        print(href)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        eSD_OccupationForecast = os.path.join(os.path.sep, dir_path,  'log', 'ESD_OccupationForecast.xlsx')
        folder = os.path.join(os.path.sep, dir_path,  'log')
        
        with urllib.request.urlopen(url) as response, open(eSD_OccupationForecast, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print("Saved {0} in the folder: {1}".format('ESD_OccupationForecast.xlsx', folder))


###MAIN
#wages = ESDOccupationProjection()
#wages.PageStatus()

