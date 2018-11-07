# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 13:54:37 2017
Source: WA State Dep. Labor & Industries, Apprenticeship Data
@author: carrie
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pandas as pd
import geocoder
import datetime, os, re
from pyvirtualdisplay import Display

key = 'fill in'


class WALaborandIndustries:
    
    def select_construction(self, browser):
        #Enter in the Construction SOC Id and Click Search to recieve Apprenticeship Results
        print("Yes We are Grabbing the Second Set")
        browser.find_element_by_xpath("//input[@id='ProgramByOccupationLookup1_txtOccupationId']").clear();
        browser.find_element_by_xpath("//input[@id='ProgramByOccupationLookup1_txtStandardCode']").send_keys('47')
        browser.find_element_by_xpath('//*[@name="ProgramByOccupationLookup1$btnSearch"]').click()
        time.sleep(3)
        print("Wait 3 seconds")
        
        #Find how many pages of results you need to navigate through
        nav_pages = browser.find_elements_by_css_selector("table#ProgramByOccupationLookup1_grdResult tr span").pop()
        
        #get last number from page text
        nav_text = nav_pages.text
        page_number = int(re.findall(r'\S+', nav_text)[-1])
        print("Number of pages to search: {0}".format(int(page_number)))
        
        return page_number
        
    def select_construction_engineers(self, browser):
        #Enter in the Construction SOC Id and Click Search to recieve Apprenticeship Results
        browser.find_element_by_xpath("//input[@id='ProgramByOccupationLookup1_txtOccupationId']").send_keys('186')
        browser.find_element_by_xpath('//*[@name="ProgramByOccupationLookup1$btnSearch"]').click()
        time.sleep(2)
        print("Wait 2 seconds for Stationary Engineers")
        
        #Find how many pages of results you need to navigate through
        nav_pages = browser.find_elements_by_css_selector("table#ProgramByOccupationLookup1_grdResult tr span")
        print(nav_pages)
        
        return nav_pages
        
        
    #Format Todays Date
    def get_date(self):
        self.now = datetime.datetime.now()
        return self.now.strftime("%Y-%m-%d %H:%M")
    
    
    def single_page_table_data(self, browser, page_number, id_or_code):
        #Only grab the rows with data, the first is a filler for the header and the last has page navigation
        tableRows = ""
        if id_or_code == "standard_occupation_code":
            tableRows = browser.find_elements_by_css_selector("table#ProgramByOccupationLookup1_grdResult tr")[1:-1]
            print("Page Number {0}".format(page_number))
            time.sleep(5)
        else:
            tableRows = browser.find_elements_by_css_selector("table#ProgramByOccupationLookup1_grdResult tr")[1:]
            print("Page Number {0}".format(page_number))
            time.sleep(5)

        if len(tableRows) > 1:
            result = []
        
            for row in tableRows:
                # Get the columns    
                col = row.find_elements(By.TAG_NAME, "td")
                
                view_id = row.find_elements(By.TAG_NAME, "a")[0]
                view_id = view_id.get_attribute('id')
                print(view_id)
                
                col_clean = [c.text for c in col]
                
                if len(col_clean) == 8:
                    occupation_name = col_clean[0]
                    occupation_id = col_clean[1]
                    soc = col_clean[2]
                    occupation_status = col_clean[3]
                    pgm_name = col_clean[4]
                    pgm_id = col_clean[5]
                    pgm_status = col_clean[6]
                    page_link_more_info = col_clean[7]
                    #print(page_link_more_info)
                    result.append({"view_id": "{0}_{1}".format(view_id, page_number), "occupation_name": occupation_name, "occupation_id": occupation_id, "soc": soc, "occupation_status": 	occupation_status, "pgm_name": pgm_name, "pgm_id": pgm_id, "pgm_status":pgm_status })
                    print("Result Appended")
                elif len(col_clean) < 8:
                    print("Table format has changed, a column was subtracted from the table");
                else:
                    print("Table format has changed, a column was added to the table");
            
            print("BEfore url_results" )
            #Navigate to each program page by clicking view
            url_results = self.click_view_grab_website(browser, page_number)
            print("After url_results" )
            return result, url_results
    
    def click_view_grab_website(self, browser, page_number):
        browser.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't') 
        time.sleep(3)
        print("Wait 3 second after new tab")
        view = browser.find_elements_by_xpath( "//tr[@class='dataRow']/td[8]")
        number_of_rows =  len(view)
        print(number_of_rows)
        
        hyperlinks = browser.find_elements_by_css_selector("table#ProgramByOccupationLookup1_grdResult tr.dataRow a")
        links = [ category.get_attribute("id") for category in hyperlinks]
        print(links)
        
        count = 1
        url_results = []
        
        for v in links:
            www_url_final = ''
            app_form_url_final = ''
            
            count+=1
            #Move page down to element for selection
            view_location = browser.find_element_by_xpath('//a[@id="' + v +'"]')
            view_location = view_location.location
            browser.execute_script("window.scrollTo(0, "+ str(view_location['y']) +");")
            print(count)
            
            #Click link
            browser.find_element_by_xpath('//a[@id="' + v +'"]').click()
            
            #Find elements
            try:
                www_site = browser.find_element_by_xpath( "//*[contains(text(), 'WWW Site')]")
                #Find the parent td and the parent tr row
                www_site_parent = www_site.find_element_by_xpath("..").find_element_by_xpath("..")  #.get_attribute('outerHTML')
                www_url_final = www_site_parent.text.replace('WWW Site', '')
                print(www_url_final)
            
            except:
                print("No url")
            try:
                app_form_url = browser.find_element_by_xpath( "//*[contains(text(), 'Program Application Form URL')]")
                #Find the parent td and the parent tr row
                app_form_url_parent = app_form_url.find_element_by_xpath("..").find_element_by_xpath("..")  #.get_attribute('outerHTML')
                app_form_url_final = app_form_url_parent.text.replace('Program Application Form URL', '')
                print(app_form_url_final)
            
            except:
                print("No url")
            
            
            browser.back()
            time.sleep(1)
            url_results.append({"view_id": "{0}_{1}".format(v, page_number), "www_site": www_url_final, "app_form_url": app_form_url_final})
        return url_results
        
            
   
            
        
    def navigate_through_pages(self, browser):
        all_page_results = []
        all_url_results = []
        
        #Select Engineers
        list_engineer = self.select_construction_engineers(browser)
        first_page_data, first_urls = self.single_page_table_data(browser, 9999, "occupation_id")
        all_page_results.extend(first_page_data)
        all_url_results.extend(first_urls)
        print("Stationary")
        print( first_page_data )
        
        
        #Select construction
        page_number = self.select_construction(browser)
        
        
        #Get data from the first page
        first_page_data, first_urls = self.single_page_table_data(browser, 9988, "standard_occupation_code")
        all_page_results.extend(first_page_data)
        all_url_results.extend(first_urls)
        print(first_page_data[0])
        
        #start looping through pages, if the next button exists click the button and get data from next page
        for i in range(page_number-1):
            #Find the page navigation button at the bottom of the page to see the other results
            try:
                next_button = browser.find_element_by_xpath('//*[@name="ProgramByOccupationLookup1$grdResult$ctl33$ImgNext"]')
        
                #click the next button then grab data 
                next_button.click()
                time.sleep(3)
                print("Wait 3 second")
                
                page_data, next_urls = self.single_page_table_data(browser,i, "standard_occupation_code")
                all_page_results.extend(page_data)
                all_url_results.extend(next_urls)
                
            except Exception as e:
                date = self.get_date()
                print("No button next on page found")
                log = open("Error_Data.txt","a")
                log.write("Source: WA State Dep. Labor & Industries, Apprenticeship Data \nError Searching for Next Button: Page status is " + "  " + str(e)  + "\t" + "Date: " + date + "\n")
        

        
        
        return all_page_results, all_url_results




#
###Open Intial Website with Selenium and Chrome, you will need to upate this and get appropriate Linux versions for Ec2
#path_to_chromedriver = r"C:\AWSRTC\chromedriver_win32_233\chromedriver.exe"
#browser = webdriver.Chrome(executable_path = path_to_chromedriver )
#url = 'https://fortress.wa.gov/lni/arts/ProgramByOccupationLookup.aspx'
#browser.get(url)
#ubuntu = False
#
#if ubuntu:
#    display = Display(visible=0, size=(800, 800))  
#    display.start()
#    
#    path_to_chromedriver = "/usr/bin/chromedriver"
#    chrome_options = webdriver.ChromeOptions()
#    chrome_options.add_argument('--no-sandbox')
#    browser = webdriver.Chrome(path_to_chromedriver, chrome_options=chrome_options)
#    
#    url = 'https://fortress.wa.gov/lni/arts/ProgramByOccupationLookup.aspx'
#    browser.get(url)
#    
#    #Call the HTML Scraper
#    apprenticeLIResult = WALaborandIndustries()
#    apprenticeLI = pd.DataFrame()
#    
#
#    #Turn the data into a dataframe for export
#    all_results, url_results = apprenticeLIResult.navigate_through_pages(browser)
#    df_main = pd.DataFrame.from_records(all_results)
#    df_urls = pd.DataFrame.from_records(url_results)
#    apprenticeLI = pd.merge(df_main, df_urls, on='view_id')
#    
#    browser.close()
#else:
#    #If windows use the following
#    path_to_chromedriver = r"C:\AWSRTC\chromedriver_win32_233\chromedriver.exe"
#    browser = webdriver.Chrome(executable_path = path_to_chromedriver )
#    url = 'https://fortress.wa.gov/lni/arts/ProgramByOccupationLookup.aspx'
#    browser.get(url)
#    
#    #Call the HTML Scraper
#    apprenticeLIResult = WALaborandIndustries()
#    apprenticeLI = pd.DataFrame()
#
#    #Turn the data into a dataframe for export
#    all_results, url_results = apprenticeLIResult.navigate_through_pages(browser)
#    df_main = pd.DataFrame.from_records(all_results)
#    df_urls = pd.DataFrame.from_records(url_results)
#    apprenticeLI = pd.merge(df_main, df_urls, on='view_id')
#    apprenticeLI.to_csv("AddStationaryEngineers.csv")
#    
#    browser.close()
