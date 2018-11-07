# -*- coding: utf-8 -*-
"""
Created on Wed Dec 13 12:50:10 2017
This calls the preapprenticeship web scraper and it tags different filters including entry requirements and age limits and the like by keyword

This requires selenium.
@author: carrie
"""
from selenium import webdriver
import pandas as pd
import numpy as np
import requests, datetime, sqlalchemy
from pyvirtualdisplay import Display
import os

key = 'fill in'

from web_scrapers.WALaborIndustries_PreApprenticeship import WALaborandIndustriesPreApprenticeship
from DatabaseConnection import DBConnection
from Email import SendEmail


class CleanPreapprenticeshipData:
    #Todays Date
    now = datetime.datetime.now()
    formatTime = now.strftime("%Y-%m-%d %H:%M")
    formatDate = now.strftime("%Y-%m-%d")
    formatHourMin = now.strftime("%H:%M")
    
    
    def callBrowser(self):
        ubuntu = True
        browser = ""
        
        if ubuntu:
            display = Display(visible=0, size=(800, 800))  
            display.start()
            
            path_to_chromedriver = "/usr/bin/chromedriver"
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--no-sandbox')
            browser = webdriver.Chrome(path_to_chromedriver, chrome_options=chrome_options)
            
            url = "http://www.lni.wa.gov/TradesLicensing/Apprenticeship/About/IntroProg/"
            browser.get(url)
            browser.implicitly_wait(10)
        
        else:
            #If windows use the following
            path_to_chromedriver = r"\chromedriver.exe"
            browser = webdriver.Chrome(executable_path = path_to_chromedriver )
            url = "http://www.lni.wa.gov/TradesLicensing/Apprenticeship/About/IntroProg/"
            browser.get(url)
            browser.implicitly_wait(10)
        
        return browser
        
    
    
    def callWALaborandIndustries(self):
        #Open Intial Website with Selenium and Chrome, you will need to upate this and get appropriate Linux versions for Ec2
        browser = self.callBrowser()

        preapprenticeLIResult = WALaborandIndustriesPreApprenticeship()
        df_preapprentice = pd.DataFrame()
        
        #Try to call the scraper for WALaborandIndustriesPreApprenticeship
        try:
            resultsLI = preapprenticeLIResult.grab_data(browser)
            df_preapprentice = pd.DataFrame.from_records(resultsLI)
            
            #Add logic to test if a group served is missing 
            veteran_empty = df_preapprentice.loc[ df_preapprentice['serve_veteran'].str.contains('Yes') ]
            low_income_empty = df_preapprentice.loc[ df_preapprentice['serve_lowincome'].str.contains('Yes') ]
            women_empty = df_preapprentice.loc[ df_preapprentice['serve_women'].str.contains('Yes') ]
            youth_empty = df_preapprentice.loc[ df_preapprentice['serve_youth'].str.contains('Yes') ]
            lastRow = len(df_preapprentice.index)
            print(df_preapprentice.columns)
#            if len(veteran_empty.index) == 0:
#                df_preapprentice.loc[lastRow] = ['Veteran', 'Washington State', np.nan, np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan, np.nan, 'No Data Available', np.nan, np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan ]
#                lastRow += 1
                
            if len(low_income_empty.index) == 0:
                df_preapprentice.loc[lastRow] = ['Low Income', 'Washington State', np.nan, np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan, np.nan, 'No Data Available', np.nan, np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan ]
                lastRow += 1
                
            if len(women_empty.index) == 0:
                df_preapprentice.loc[lastRow] = ['Women', 'Washington State', np.nan, np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan, np.nan, 'No Data Available', np.nan, np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan ]
                lastRow += 1
                
            if len(youth_empty.index) == 0:
                df_preapprentice.loc[lastRow] = ['Youth', 'Washington State', np.nan, np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan, np.nan, 'No Data Available', np.nan, np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan ]
            
            #WALaborIndustries_PreApprenticeship = os.path.join(os.path.sep, 'home','build','test','backups_hardcoded','WALaborIndustries_PreApprenticeship.csv')
            
                        
            dir_path = os.path.dirname(os.path.realpath(__file__))
            waLaborIndustries_PreApprenticeship = os.path.join(os.path.sep, dir_path, 'backups_hardcoded','WALaborIndustries_PreApprenticeship.csv')
            df_preapprentice.to_csv(waLaborIndustries_PreApprenticeship)
            browser.close()
            
            #Hardcoded export
            #df_preapprentice = pd.read_csv('backups_hardcoded/WALaborIndustries_PreApprenticeship.csv', encoding = "ISO-8859-1")
            
            #Check to see if the address is Geocoded already, then Geocode if not
            df_preapprentice = self.checkAddressLookup(df_preapprentice)
            
            #Log success
            df = pd.DataFrame([['WALaborandIndustriesPreApprenticeship', 'PreApprenticeship Dashboard', '1 of 1', 'WA State Dep. Labor & Industries PreApprenticeship data', self.formatDate, self.formatHourMin, 'Successful Download']])
            df.to_csv('Succesful_Download_Log.csv', mode='a', header=False, index=False)
            
        
        #If the scraper can not be called log the issue
        except:
            log = open("Error_Data.txt","a")
            log.write("Error calling WALaborIndustries_PreApprenticeship webscrapper. Location:PreApprenticeship.py  Date: " + self.formatTime + "\n")
            df = pd.DataFrame([['WALaborIndustries_PreApprenticeship', 'PreApprenticeship Dashboard', '1 of 1', 'WA State Dep. Labor & Industries PreApprenticeship data', 'Will use last dowload', 0, 'FAILED Download']])
            df.to_csv('Succesful_Download_Log.csv', mode='a', header=False, index=False)
            
        return df_preapprentice
        
        
    #Check to see if any of the addresses are already geocoded
    def checkAddressLookup(self,results):
        
        #Pull in previously geocoded addresses
        dir_path = os.path.dirname(os.path.realpath(__file__))
        geoCodedAddressesLookup = os.path.join(os.path.sep, dir_path, 'LookupTables','GeoCodedAddressesLookup.csv')
            
        previousGeocoded = pd.read_csv(geoCodedAddressesLookup, encoding = "ISO-8859-1").dropna(subset=['address']) 
        prevAddressesLat = previousGeocoded.set_index('address')['latitude'].to_dict()  
        prevAddressesLong = previousGeocoded.set_index('address')['longitude'].to_dict()
        prevAddressesCity = previousGeocoded.set_index('address')['city'].to_dict() 
        results['latitude'] = results['address'].map(prevAddressesLat)
        results['longitude'] = results['address'].map(prevAddressesLong)
        results['city'] = results['address'].map(prevAddressesCity)
        
        #Find those We Still need to Geocode
        notGeocoded = results.loc[  (results['longitude'].isnull()) & ( results['address'].notnull() ) , ]
        allreadyGeocoded = results.loc[  (results['longitude'].notnull()) | ( results['address'].isnull() ) , ]
        
        #Geocode those that have an address but are not yet in the lookuptable
        newGeocoded = self.geocodeDataFrame(notGeocoded)
        
        #Now update the results with all the addresses you found
        newGeocodedLat = newGeocoded.set_index('address')['latitude'].to_dict()  
        newGeocodedLong = newGeocoded.set_index('address')['longitude'].to_dict() 
        newGeocodedCity = newGeocoded.set_index('address')['city'].to_dict()
        notGeocoded['latitude'] = notGeocoded['address'].map(newGeocodedLat)
        notGeocoded['longitude'] = notGeocoded['address'].map(newGeocodedLong)
        notGeocoded['city'] = notGeocoded['address'].map(newGeocodedCity)
        allResultsGeocoded = pd.concat([notGeocoded, allreadyGeocoded])
        
        #Just select the data wanted
        allResultsGeocoded = allResultsGeocoded[[	'program_name',	'program_description',	'address',	'latitude',	'longitude',	'city',	'cert_firstaid',	'cert_flagging',	'cert_forklift',	'cert_hazwoper',	'cert_osha10or11',	'req_atLeast18',	'req_otherAge',	'req_driversLicense',	'req_noGEDorDiplomaNeeded',	'req_GEDorDiploma',	'serve_general',	'serve_women',	'serve_youth',	'serve_lowincome',	'serve_veteran',  'website', 'Individual_Served_first']]

        
        #Update the Geocode LookupTable, Make sure to only pass Unique Addresses
        allGeocoded = pd.concat([newGeocoded, previousGeocoded])
        saveNewGeocodeLookup = allGeocoded.loc[ :, ['address', 'latitude', 'longitude', 'city']]
        
        dir_path = os.path.dirname(os.path.realpath(__file__))
        geoCodedAddressesLookup = os.path.join(os.path.sep, dir_path, 'LookupTables','GeoCodedAddressesLookup.csv')        
        saveNewGeocodeLookup.to_csv(geoCodedAddressesLookup)
        #print(saveNewGeocodeLookup.head(5))
        
        return allResultsGeocoded
    
    
    #Find those that are not geocoded, drop duplicates, call the address geocoder, then update the csv geocode lookup for the next time
    def geocodeDataFrame(self, notGeocoded):
        #Drop Dupe Addresses
        notGeocoded = notGeocoded.drop_duplicates(['address'], keep='first')
        
        #Geocode and put results in a list
        notGeocoded['place'] = notGeocoded['address'].apply(self.geocodeAddress)
        
        #Parse the returned place info list into the appropriate columns
        notGeocoded[['latitude','longitude', 'city', 'place_id', 'addressfound']] = pd.DataFrame(notGeocoded.place.values.tolist(), index= notGeocoded.index)
        #print(notGeocoded[['latitude','longitude', 'city', 'place_id', 'address', 'place']])
        
        return notGeocoded
    
    
    #This is called per row, Geocode the first 250 addresses
    def geocodeAddress(self, address):
        google_url = "https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}".format(address, key)
        response_geocode = requests.get(google_url).json()
        
        #print(address)
        lat,lng,place_id, city = 0,0,"None", ""
        
        #if results were returned take the first one
        if len(response_geocode['results']) > 0:
            r = response_geocode['results'][0]
            
            findcity = r[u'address_components']
            for f in findcity:
                #print(f)
                if 'locality' in f[u'types']:
                    city = f[u'long_name']
            
            lat = r[u'geometry'][u'location'][u'lat']
            lng = r[u'geometry'][u'location'][u'lng']
            place_id = r[u'place_id']
            #print(lat, lng, place_id, city)
        
        return [lat, lng, city, place_id, address]


if __name__ == '__main__':
    #EMAIL
    email_enabled = True
    linux = True
    emails = SendEmail()
    
    try:
        # Call the scrapers
        preApprenticeship = CleanPreapprenticeshipData()
        date = preApprenticeship.formatDate
        get_preApprenticeship = preApprenticeship.callWALaborandIndustries()
        get_preApprenticeship['id'] = get_preApprenticeship.index
        #print(get_preApprenticeship.head(5))
        
        df = get_preApprenticeship #.reindex_axis(['id','program_name','address'], axis=1)
        dir_path = os.path.dirname(os.path.realpath(__file__))
        results = os.path.join(os.path.sep, dir_path, 'PreApprenticeship.csv')
        df.to_csv(results)
        
        # CONNECT TO DATABASE
        connect = DBConnection()
        engine = connect.engine()

        # MIGRATE DATA INTO DATA FRAME (APPEND NOT REPLACE)
        df = df[['id',	'program_name',	'address',	'latitude',	  'longitude',	'city',	'cert_firstaid',	'cert_flagging',	'cert_forklift',	'cert_hazwoper',	'cert_osha10or11',	'req_atLeast18',	'req_otherAge',	'req_driversLicense',	'req_noGEDorDiplomaNeeded',	'req_GEDorDiploma',	'serve_general',	'serve_women',	'serve_youth',	'serve_lowincome',	'serve_veteran',	'website',	'program_description', 'Individual_Served_first']]
        df.to_sql(name='PreApprenticeship', con=engine, if_exists='replace', index=False, chunksize=10,
                      dtype={
                             'id':  sqlalchemy.types.INTEGER(),
                             'program_name': sqlalchemy.types.NVARCHAR(length=200),
                             'address': sqlalchemy.types.NVARCHAR(length=200),
                             'city': sqlalchemy.types.NVARCHAR(length=100),
                             'cert_firstaid': sqlalchemy.types.NVARCHAR(length=50),
                             'cert_flagging': sqlalchemy.types.NVARCHAR(length=50),
                             'cert_forklift': sqlalchemy.types.NVARCHAR(length=50),
                             'cert_hazwoper': sqlalchemy.types.NVARCHAR(length=50),
                             'cert_osha10or11': sqlalchemy.types.NVARCHAR(length=50),
                             'req_atLeast18': sqlalchemy.types.NVARCHAR(length=100),
                             'req_otherAge': sqlalchemy.types.NVARCHAR(length=100),
                             'req_driversLicense': sqlalchemy.types.NVARCHAR(length=100),
                             'req_noGEDorDiplomaNeeded': sqlalchemy.types.NVARCHAR(length=100),
                             'req_GEDorDiploma': sqlalchemy.types.NVARCHAR(length=100),
                             'serve_general': sqlalchemy.types.NVARCHAR(length=10),
                             'serve_women': sqlalchemy.types.NVARCHAR(length=10),
                             'serve_youth': sqlalchemy.types.NVARCHAR(length=10),
                             'serve_lowincome': sqlalchemy.types.NVARCHAR(length=10),
                             'serve_veteran': sqlalchemy.types.NVARCHAR(length=10),
                             'website': sqlalchemy.types.NVARCHAR(length=500),
                             'program_description': sqlalchemy.types.NVARCHAR(length=2500),
                             'latitude': sqlalchemy.types.Float(precision=32, decimal_return_scale=12, asdecimal=True),
                             'longitude': sqlalchemy.types.Float(precision=32, decimal_return_scale=12, asdecimal=True),
                             'Individual_Served_first': sqlalchemy.types.NVARCHAR(length=2000)
                        })
                             
        print("Pushed data to PreApprenticeship Table. \n Latest Data saved to PreApprenticeship.csv")
        
        #EXPORT FOR DOWNLOAD
        resultsDash = os.path.join(os.path.sep, dir_path, "downloadables_for_s3", "PreApprenticeship_Dashboard.csv")
        formated_for_download_preap = df
        formated_for_download_preap.columns = ['Id',	'Program Name',	'Address',	'Latitude',	  'Longitude',	'City',	'Certificate in Firstaid',	'Certificate in Flagging',	'Forklift Certification',	'Hazwoper Certification',	'Osha10 or 11 Certification',	'Must be at least 18',	'Other age requirements',	'Drivers License Required',	'No GED or Diploma Needed',	'GED or Diploma Required',	'Serve the General Pop',	'Serve Women',	'Serve Youth',	'Serve Low Income',	'Serve Veteran',	'Website',	'Program Description', 'Individuals Served']        
        formated_for_download_preap.to_csv(resultsDash)
        
    except:
        print("Can NOT push data to PreApprenticeship Table.")
        log = open("Error_Data.txt","a")
        log.write("Can not push new PreApprenticeship data to Database. Location:PreApprenticeship.py  Date: " + date + "\n")
        
        try:
            #Email if not successful
            subject = "CCE Web Scrapers - PreApprenticeship Dashboard Can Not be Updated"
            body_text = ("RTC Dashboard - PreApprenticeship Data Could Not be Updated\r\n"
                             "This email was sent because the data collection on the PreApprenticeship websites could not be completed.\r\n"
                             "CARRIE SCHADEN\r\n"
                             "Data Systems Analyst  |  Community Attributes Inc.\r\n"
                            )
            body_html = """<html>
                <head></head>
                <body>
                    <h3>RTC Dashboard - PreApprenticeship Data Could Not be Updated</h3>
                    <p>This email was sent because the data collection on the PreApprenticeship websites could not be completed.</p>
                    <br>
                    <p>CARRIE SCHADEN <br>
                    Data Systems Analyst  |  Community Attributes Inc. </p><br>
                    <a href="www.communityattributes.com">communityattributes.com</a><br>
                    <em>We’ve Moved!</em>Our new address is:<br>
                    500 Union Street, Suite 200<br>
                    Seattle, WA 98101<br>
                    206.523.6683 <br>
                </body>
                </html> """
            if linux:
                emails.send_email_linux( subject, body_text, body_html)
            else:
                emails.send_email( subject, body_text, body_html)
            print("Emailed unsuccessfull attempt alert")
        
        except:
            log = open("Error_Data.txt","a")
            log.write("Can not Email Alerts about unsuccesful attempts. Location:PreApprenticeship.py  Date: " + date + "\n")

            print("Can not email alert")
            
        
    
    
    
    
    
    
#    df.to_sql(name='PreApprenticeship_test', con=engine, if_exists = 'replace', index=False, 
#                      dtype={'id': sqlalchemy.types.INTEGER(), 
#                             'program_name':  sqlalchemy.types.NVARCHAR(length=200),
#                             'address': sqlalchemy.types.NVARCHAR(length=200)
#                             })
#    user = 'caiprof2017'
#    passw = 'Arunthejew3ls!' 
#    host =  'rtcdb.ccytbcwylpsp.us-west-2.rds.amazonaws.com'
#    port = 3306
#    database = 'RentonTechCollegeTD' 
    
#    conn = pymysql.connect(host=host,
#                           port=port,
#                           user=user, 
#                           passwd=passw,  
#                           db=database)
#
#    get_preApprenticeship.to_sql(name='PreApprenticeship_test', con=conn, if_exists = 'replace', index=False, flavor = 'mysql')
