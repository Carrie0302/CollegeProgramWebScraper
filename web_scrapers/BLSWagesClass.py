# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 14:42:14 2017
This downloads and unzips the wage data by MSA and States from the BLS website
@author: carrie
"""
from bs4 import BeautifulSoup
import requests, urllib.request, shutil, zipfile
import datetime, os, time

#import re, webbrowser
#import schedule
#import datetime
#import time
#
## Obtain current time
#start = datetime.datetime.now()
#
## Simple callable for example
#class DummyClock:
#  def __call__(self):
#    print datetime.datetime.now()
#
#schedule.every(1).seconds.do(DummyClock())
#
#while True:
#    schedule.run_pending()
#    # 5 minutes == 300 seconds
#    if (datetime.datetime.now() - start).seconds >= 300:
#        break
#    # And here we halt execution for a second
#    time.sleep(1)


class BLSWages:
    '''Download the zipped folders from BLS with wage data from Metro Areas and the State'''
    
    #BLS Data Source
    BLS_url = 'https://www.bls.gov/oes/tables.htm'
    BLS_main_link = 'https://www.bls.gov/'
    page = requests.get(BLS_url)
    titleShouldBe = "Tables Created by BLS"
    
    #Todays Date
    now = datetime.datetime.now()
    formatTime = now.strftime("%Y-%m-%d %H:%M")
    print("Running BLS Wage Web scraper: {0}".format(formatTime))
    
    
    #First test is if the page will load
    def PageStatus(self):
        status = self.page.status_code
        soup = ""
        if status == 200:
            soup = BeautifulSoup(self.page.text, 'html.parser')
            self.CheckElementonWebsite(soup, self.titleShouldBe)
            print("Downloading...")
            self.DownloadStateData(soup)
            time.sleep(2)
            self.DownloadMetroData(soup)
            
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
            print("Title on BLSWages website changed")
            log = open("Error_Data.txt","a")
            log.write("Title on Website has changed from '" + str(titletoCheckAgainst)  + "' to '" +  str(title)   + "' \t" + "Date: " + self.formatTime + "\n")
    
    
    def GetFileNamesfromDirectory(self):
        dirpath = os.getcwd()
        print(dirpath+"\log")
        for file in os.listdir(dirpath+"\log"):
            print(file)
            
            if file.endswith(".zip"):
                print(os.path.join(dirpath+"\log", file))
                return file
        
        
    #Download BLS Data unzip it and delete the zip container
    def DownloadMetroData(self, soup):
        body = soup.find("div", {"id": "bodytext"})
        links = body.find_all('a', href=True)[6]
        href = links['href']
        url = self.BLS_main_link+href
        print(url)
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        bLS_WageMetro = os.path.join(os.path.sep, dir_path,  'log', 'BLS_WageMetro.zip')
        folder = os.path.join(os.path.sep, dir_path,  'log')
        
        with urllib.request.urlopen(url) as response, open(bLS_WageMetro, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            
            #Extract files from zip
            with zipfile.ZipFile(bLS_WageMetro) as zf:
                zf.extractall(folder)
                
        #Remove the zip file and remove unnecissary files
        os.remove(bLS_WageMetro)
    
        #webbrowser.open(url)
    
        #if href == "/oes/special.requests/oesm16ma.zip":
        #    print("Data for May 2016 allready downloaded" + href)
    
    
    #Download BLS Data unzip it and delete the zip container
    def DownloadStateData(self, soup):
        body = soup.find("div", {"id": "bodytext"})
        links = body.find_all('a', href=True)[4]
        href = links['href']
        url = self.BLS_main_link+href
        print(url)
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        bLS_WageState = os.path.join(os.path.sep, dir_path, 'log', 'BLS_WageState.zip')
        folder = os.path.join(os.path.sep, dir_path, 'log')
        
        with urllib.request.urlopen(url) as response, open(bLS_WageState, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        
        #Extract files from zip
        time.sleep(8)
        z = zipfile.ZipFile(bLS_WageState)
        z.extractall(folder)
        z.close()
        del z
        os.unlink(bLS_WageState)
    

##MAIN
#wages = BLSWages()
#wages.PageStatus() 


    
