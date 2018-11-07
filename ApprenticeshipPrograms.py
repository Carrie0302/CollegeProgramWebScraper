# -*- coding: utf-8 -*-
"""
Created on Tue Nov 28 13:18:31 2017
This calls the 2 different sources for apprenticeship data one provides the soc code, the other has contextual info, they are matched by name and keyword.

This requires selenium.
@author: carrie
"""
from selenium import webdriver
import pandas as pd
import difflib, requests, os
import numpy as np
import datetime, sqlalchemy
from pyvirtualdisplay import Display
from random import *

key = 'fill in'

from web_scrapers.CareerBridgeClass import CareerBridge
from web_scrapers.WALaborIndustriesClass import WALaborandIndustries
from DatabaseConnection import DBConnection
from Email import SendEmail


class MatchCareerBridgetoLandI:
        '''This will call the Career Bridge  web scraper for apprenticeship and Match to L and I data.  Then it will tag entry reqs after.'''
        #Todays Date
        now = datetime.datetime.now()
        formatTime = now.strftime("%Y-%m-%d %H:%M")
        formatDate = now.strftime("%Y-%m-%d")
        formatHourMin = now.strftime("%H:%M")
        
        
        def callBrowser(self):
            ubuntu = True
            browser = ""
            
            if ubuntu:
                display = Display(visible=0, size=(1000, 1000))  
                display.start()
                
                path_to_chromedriver = "/usr/bin/chromedriver"
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--no-sandbox')
                browser = webdriver.Chrome(path_to_chromedriver, chrome_options=chrome_options)
            
            else:
                #If windows use the following
                path_to_chromedriver = r"\chromedriver.exe"
                browser = webdriver.Chrome(executable_path = path_to_chromedriver )
            print("Browser")
            return browser
            
            
        def callCareerBridge(self):
            #Open Intial Website with Selenium and Chrome, you will need to upate this and get appropriate Linux versions for Ec2
            browserCB = self.callBrowser()
            urlApprentice = 'http://www.careerbridge.wa.gov/Search_Program.aspx?cmd=saved&gsid=apprenticeship'
            browserCB.get(urlApprentice)
            
            apprenticeResult = CareerBridge()
            apprenticeCareerBPrograms = pd.DataFrame()
            dir_path = os.path.dirname(os.path.realpath(__file__))
            #Try to do call the scraper for Career Bridge
            try:
                apprenticeResult.type = "apprenticeship"
                apprenticeLinks = apprenticeResult.href_apprenticeship(browserCB)
                cleanedApprenticePages = apprenticeResult.download_apprenticeship_data(apprenticeLinks, browserCB)
                
                careerBridge_Apprenticeship = os.path.join(os.path.sep, dir_path, 'backups_hardcoded','CareerBridge_Apprenticeship.csv')
                apprenticeResult.merge_export_to_csv(apprenticeLinks, cleanedApprenticePages,careerBridge_Apprenticeship)
                apprenticeCareerBPrograms = pd.read_csv(careerBridge_Apprenticeship, encoding = "ISO-8859-1")
                
                #Log success
                df = pd.DataFrame([['CareerBridge', 'Apprenticeship Dashboard', '1 of 2', 'Career Bridge Web Scraper Apprenticeship data', self.formatDate, self.formatHourMin, 'Successful Download']])
                df.to_csv('Succesful_Download_Log.csv', mode='a', header=False, index=False)
                 
            #If the scraper can not be called log the issue
            except:
                log = open("Error_Data.txt","a")
                log.write("Error calling CareerBridge webscrapper. Location:Apprenticeship.py  Date: " + self.formatTime + "\n")
                df = pd.DataFrame([['CareerBridge', 'Apprenticeship Dashboard', '1 of 2', 'Career Bridge Web Scraper Apprenticeship data', 'Will use last dowload', 0, 'FAILED Download']])
                df.to_csv('Succesful_Download_Log.csv', mode='a', header=False, index=False)
                
            browserCB.close()
            return apprenticeCareerBPrograms
            

        def callWALaborandIndustries(self):
            #Open Intial Website with Selenium and Chrome, you will need to upate this and get appropriate Linux versions for Ec2
            browserLI = self.callBrowser()
            url = 'https://fortress.wa.gov/lni/arts/ProgramByOccupationLookup.aspx'
            browserLI.get(url)
            dir_path = os.path.dirname(os.path.realpath(__file__))
            
            #Call the HTML Scraper
            apprenticeLIResult = WALaborandIndustries()
            apprenticeLI = pd.DataFrame()
            
            #Try to do call the scraper for Career Bridge
            try:
                #Turn the data into a dataframe for export
                all_results, url_results = apprenticeLIResult.navigate_through_pages(browserLI)
                df_main = pd.DataFrame.from_records(all_results)
                df_urls = pd.DataFrame.from_records(url_results)
                apprenticeLI = pd.merge(df_main, df_urls, on='view_id')
                wALaborIndustries_Apprenticeship = os.path.join(os.path.sep, dir_path, 'backups_hardcoded','WALaborIndustries_apprenticeship.csv')
                apprenticeLI.to_csv(wALaborIndustries_Apprenticeship)
                
                print("Success at L and I")
                #Log success
                df = pd.DataFrame([['WALaborandIndustries', 'Apprenticeship Dashboard', '2 of 2', 'WA State Dep. Labor & Industries Apprenticeship data', self.formatDate, self.formatHourMin, 'Successful Download']])
                df.to_csv('Succesful_Download_Log.csv', mode='a', header=False, index=False)
                browserLI.close()
                
            #If the scraper can not be called log the issue
            except:
                log = open("Error_Data.txt","a")
                log.write("Error calling WALaborandIndustries webscrapper. Location:Apprenticeship.py  Date: " + self.formatTime + "\n")
                df = pd.DataFrame([['WALaborandIndustries', 'Apprenticeship Dashboard', '2 of 2', 'WA State Dep. Labor & Industries Apprenticeship data', 'Will use last dowload', 0, 'FAILED Download']])
                df.to_csv('Succesful_Download_Log.csv', mode='a', header=False, index=False)
                print("Can not scrape WALaborandIndustries")
                browserLI.close()
                
            
            return apprenticeLI
    
        
        #Check to see if any of the addresses are already geocoded
        def checkAddressLookup(self,results):
            
            #Remove stuff in parenthesis at the end from the address
            results['address'] = results['address'].str.replace(r"\(.*\)","").str.strip()
            dir_path = os.path.dirname(os.path.realpath(__file__))
            
            #Pull in previously geocoded addresses
            geoCodedAddressesLookup = os.path.join(os.path.sep, dir_path, 'LookupTables','GeoCodedAddressesLookup.csv')
            previousGeocoded = pd.read_csv(geoCodedAddressesLookup).dropna(subset=['address']) 
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
            print("notGeocoded")
            print(notGeocoded.columns)
            allResultsGeocoded = pd.concat([notGeocoded, allreadyGeocoded])
            
            allResultsGeocoded = allResultsGeocoded[['pgm_name',	'occupation_name', 'cai_category', 'category_description', 	'soc',	'web', 'award_type',	'pay',	'training_length',	'evenings_weekends',	'license_from_program',	'license_req_to_work',	 'online_courses', 'address', 'latitude', 'longitude', 'city',  'description',	'entrance_req']]
            
            #Update the Geocode LookupTable, Make sure to only pass Unique Addresses
            allGeocoded = pd.concat([newGeocoded, previousGeocoded])
            saveNewGeocodeLookup = allGeocoded.loc[ :, ['address', 'latitude', 'longitude', 'city']]
            saveNewGeocodeLookup.to_csv(geoCodedAddressesLookup)
            
            return allResultsGeocoded
        
        
        #Find those that are not geocoded, drop duplicates, call the address geocoder, then update the csv geocode lookup for the next time
        def geocodeDataFrame(self, notGeocoded):            
            #Drop Dupe Addresses
            notGeocoded = notGeocoded.drop_duplicates(['address'], keep='first')
            if notGeocoded.empty:
                print("Nothing new to geocode")
                
            else:
                #Geocode and put results in a list
                notGeocoded['place'] = notGeocoded['address'].apply(self.geocodeAddress)
                
                #Parse the returned place info list into the appropriate columns
                #print(notGeocoded[['latitude','longitude', 'city', 'place_id','address', 'place']])
                notGeocoded[['latitude','longitude', 'city', 'place_id', 'addressfound']] = pd.DataFrame(notGeocoded.place.values.tolist(), index=notGeocoded.index)
                
            return notGeocoded
            
        
        
        #This is called per row, Geocode the first 250 addresses
        def geocodeAddress(self, address):
            google_url = "https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}".format(address, key)
            response_geocode = requests.get(google_url).json()
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
            
            
        def cleanofColumnSchemaandDataTypes(self, matched_results):
            #Drop the nulls, so that only Labor and Industry apprenticeships appear
            #matched_results = matched_results.loc[matched_results['occupation_name'].notnull()]
            matched_results.dropna(subset=['pgm_name'], how='all', inplace = True)
            
            #Clean up the fields to be used
            matched_results['soc'] = matched_results['soc'].str[:7]
            
            #Pull in CAI categories To match soc_codes to Cai Category
            dir_path = os.path.dirname(os.path.realpath(__file__))
            
            #Pull in previously geocoded addresses
            cAIConstructionLookup = os.path.join(os.path.sep, dir_path, 'LookupTables','CAIConstructionLookup.csv')
            caiCategories = pd.read_csv(cAIConstructionLookup)
            cai_category = caiCategories.set_index('detailed_occupation')['cai_category'].to_dict()    
            matched_results['cai_category'] = matched_results['soc'].map(cai_category)
            
            
            
            
            
            #If Cai Category does not exist in data add Data not avail row
            #First look at the socs found during scraping and map to the existing socs we want in our look up table and save the unique set of their related categories to a list
            print("Existing Categories")
            existingCategories = matched_results.set_index('soc')['cai_category'].to_dict()
            print(existingCategories)
            caiCategories['soc_exists'] = caiCategories['detailed_occupation'].map(existingCategories)
            tradesExist = caiCategories['soc_exists'].tolist()
            tradesExistUniq = set(tradesExist)

            
            #Lookup all categories that Exist regardless of the soc
            caiCategories['category_exists'] = caiCategories['cai_category'].isin(tradesExistUniq)            
            
            #Drop those categories that exist and add the ones we didnt find scraping to a searchable list
            dataNotAvailbyCat = caiCategories[caiCategories['category_exists'] == False]
            dataNotAvailbyCat = dataNotAvailbyCat.drop_duplicates(['cai_category'], keep = 'first')
            dataNotAvail = dataNotAvailbyCat['detailed_occupation'].tolist()
            print("No Data Available for:")
            print(dataNotAvail)
            
            #For any trade category missing add a row
            matched_results['pgm_name'] = np.where( matched_results['pgm_name'].isnull(),  'NULL', matched_results['pgm_name'])
            print(matched_results.columns)
            lastRow = matched_results.index.max() + 1
            for soc in dataNotAvail:
                    matched_results.loc[lastRow] = [ np.nan, 'No Data Available', soc, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, 'No Data Available',  'Washington State', np.nan, np.nan, np.nan,np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan  ]
                    lastRow += 1      
            
            
            
            #Pull in CAU Category descriptions
            cAICategoryDescriptions = os.path.join(os.path.sep, dir_path, 'LookupTables','CAICategoryDescriptions.csv')
            caiCategoryDesc = pd.read_csv(cAICategoryDescriptions)
            cai_category_desc = caiCategoryDesc.set_index('cai_category')['category_description'].to_dict()    
            matched_results['category_description'] = matched_results['cai_category'].map(cai_category_desc)            
            results = matched_results[['pgm_name',	'occupation_name', 'cai_category', 'category_description', 	'soc',	'description',	'entrance_req',	'web',	'award_type',	'pay',	'training_length',	'evenings_weekends',	'license_from_program',	'license_req_to_work',	 'online_courses', 'address']]

            
            #Check to see if the address has already been geocoded
            results = self.checkAddressLookup(results)
            return results
            
            
            
        def matchLandItoCareerBridge(self, csvLandI, csvCareerBridge):
            dir_path = os.path.dirname(os.path.realpath(__file__))
            
            #Addd a unique ID to CB to join to the L&I dataset
            csvCareerBridge = csvCareerBridge.reset_index()
            csvCareerBridge['Unique_ID_CB'] = csvCareerBridge.index + 100

            #Drop duplicates from website
            csvLandI = csvLandI.drop_duplicates(['occupation_id',	'occupation_name',	'occupation_status',	'pgm_id',	'pgm_name',	'pgm_status',	'soc'], keep='first')
            csvLandI.loc[ csvLandI['occupation_status'] == 'Active' ]
            
            
            #First Match is Based on a Slightly Cleaned Position Name Joined to the School Name
            #Clean the position names, lower case and parenthesis removed
            csvLandI['position'] = csvLandI['occupation_name'].str.lower().replace(r"\(.*\)","")
            csvCareerBridge['position'] = csvCareerBridge['position'].str.lower().replace(r"\(.*\)","")
            
            #Concatenate the position/occupation and school name
            csvLandI['One_CPos_NSchool'] = csvLandI[['position', 'pgm_name']].apply(lambda x: '_'.join(x.astype(str)), axis=1)
            csvCareerBridge['One_CPos_NSchool'] = csvCareerBridge[['position', 'school_name']].apply(lambda x: '_'.join(x.astype(str)), axis=1)
            
            #Convert the Unique Id to a Dictionary with a lookup based on the exact Position Name and School Name 
            prog_school = csvCareerBridge.set_index('One_CPos_NSchool')['Unique_ID_CB'].to_dict()
            csvLandI['Unique_ID_MatchOne'] = csvLandI['One_CPos_NSchool'].map(prog_school)
            #matchOne = csvLandI[csvLandI['Unique_ID_MatchOne'].notnull()]

            

            
            #Second Match on occupation/position and Websites.   
            #Clean the website names
            csvLandI['web'] = csvLandI['www_site'].replace(r" ","").replace({r'http://': ''}, regex=True).replace({r'https://': ''}, regex=True).replace({r'/$': ''}, regex=True).str.strip()
            csvCareerBridge['web'] = csvCareerBridge['website'].replace(r" ","").replace({r'http://': ''}, regex=True).replace({r'https://': ''}, regex=True).replace({r'/$': ''}, regex=True).replace(r' ', '').str.strip()

            #Concatenate the position/occupation and website
            csvLandI['Two_CPos_NWebsite'] = csvLandI[['position', 'web']].apply(lambda x: '_'.join(x.astype(str)), axis=1)
            csvCareerBridge['Two_CPos_NWebsite'] = csvCareerBridge[['position', 'web']].apply(lambda x: '_'.join(x.astype(str)), axis=1)
            
            #Convert the Unique Id to a Dictionary with a lookup based on the exact Position Name and School Name 
            prog_web = csvCareerBridge.set_index('Two_CPos_NWebsite')['Unique_ID_CB'].to_dict()
            csvLandI['Unique_ID_MatchTwo'] = csvLandI['Two_CPos_NWebsite'].map(prog_web)
            
            #Remove Bogus Joins if nan in the field
            csvLandI.loc[csvLandI['Two_CPos_NWebsite'].str.contains('_nan'), 'Unique_ID_MatchTwo'] = np.nan
            
            #matchTwo = csvLandI[csvLandI['Unique_ID_MatchTwo'].notnull()]
            csvLandI['Unique_ID'] = np.where( csvLandI['Unique_ID_MatchTwo'].isnull(), csvLandI['Unique_ID_MatchOne'], csvLandI['Unique_ID_MatchTwo'])
            


            #Third Match on occupation and lookup for the school name
            #Pull in SOC Lookup Table to Match the SOC to Occupation List per Program
            cAIApprenticeshipProgramNameLookup = os.path.join(os.path.sep, dir_path,  "LookupTables", "CAIApprenticeshipProgramNameLookup.csv")
            programLookup = pd.read_csv(cAIApprenticeshipProgramNameLookup)
            #print(programLookup.columns)
            testing = os.path.join(os.path.sep, dir_path,  "testingCAIApprenticeshipProgramNameLookup.csv")
            programLookup.to_csv(testing)
            
            
            #prog = programLookup.set_index('program_name_LI_match')['﻿program_name_CareerBridge'].to_dict()
            prog = programLookup.set_index('program_name_LI_match').ix[:,0].to_dict()
            csvLandI['program_lookup'] = csvLandI['pgm_name'].map(prog)
            
            #Get just those that are not null and lookup based on the cleaned position and cleaned program name and Create the New Position plus Cleaned School name field
            #programLandI = csvLandI[csvLandI['program_lookup'].notnull()]
            csvLandI['Three_CPos_CSchool'] = csvLandI[['position', 'program_lookup']].apply(lambda x: '_'.join(x.astype(str)), axis=1)

            #Use the prog_school dictionary created above to lookup 
            csvLandI['Unique_ID_MatchThree'] = csvLandI['Three_CPos_CSchool'].map(prog_school)
            
            #Update Unique ID with new info
            csvLandI['Unique_ID'] = np.where( csvLandI['Unique_ID'].isnull(), csvLandI['Unique_ID_MatchThree'], csvLandI['Unique_ID'])
            #matchThree = csvLandI[csvLandI['Unique_ID_MatchThree'].notnull()]
            

            #Filter for active programs
            csvLandI = csvLandI[csvLandI['occupation_status'] == 'Active']
            
            
      
            #Fourth Match is Fuzzy Match from Position and School name      
            #Merge the two sources on the ID to find what is unmatched from CareerBridge and Export the program and school names to a list so you can just look through what is not matched in CB
            csvCareerBridge['One_CPos_NSchool2'] = csvCareerBridge['One_CPos_NSchool']     
            csvCareerBridge = csvCareerBridge[['Unique_ID_CB',	'program_name', 'address',	'position',	'school_name',	'award_type',	'link',	'entrance_req',	'description',	'clock_hours',	'etp',	'evenings_weekends',	'license_from_program',	'license_req_to_work',	'license_test_prep',	'online_courses',	'pay',	'total_tuition',	'training_length',	'tuition',	'web',	'One_CPos_NSchool2',	'Two_CPos_NWebsite']]
            csvLandI['Unique_ID_FindUnmatched'] = csvLandI['Unique_ID']
            
            csvLandI = csvLandI[['occupation_name',	'occupation_status',	'pgm_name',	'soc',	'web',	'position', 	'One_CPos_NSchool',	'Two_CPos_NWebsite',	'Three_CPos_CSchool',	'program_lookup',	'Unique_ID_MatchOne',	'Unique_ID_MatchTwo',	'Unique_ID_MatchThree',	'Unique_ID',	'Unique_ID_FindUnmatched']]          
            csvLandI_unm =  csvLandI.dropna(subset = ['Unique_ID']).set_index('Unique_ID')
            csvCareerBridge_unm = csvCareerBridge.set_index('Unique_ID_CB')

            unmatched = pd.concat([ csvCareerBridge_unm, csvLandI_unm ], axis=1, join_axes=[csvCareerBridge_unm.index])
            
            
            #Drop nulls to find only unmatched and save the program school name combo from CB in a list
            unmatched =  unmatched.loc[ unmatched['Unique_ID_FindUnmatched'].isnull(), ]
            fuzzyCB = unmatched['One_CPos_NSchool2'].tolist()
            
            #Some additional cleanup of the data
            csvLandI['One_CPos_NSchool'] = csvLandI['One_CPos_NSchool'].replace('painter and decorator', 'painter-decorator', regex=True).replace('CITC of WA - Painter', 'Construction Industry Training Council of Washington - Painter', regex=True).replace('E WA & N ID Painters & Allied Trades', 'Eastern Washington and Northern Idaho Painters and Allied Trades Apprenticeship Committee', regex=True)
            csvLandI['Four_Fuzzy_CPos_NSchool'] = csvLandI['One_CPos_NSchool'].apply(lambda x: difflib.get_close_matches(x, fuzzyCB, 1))
            
            #Remove null matches and return the first element in a list
            csvLandI['Four_Fuzzy_CPos_NSchool'] = csvLandI['Four_Fuzzy_CPos_NSchool'].apply(lambda x: x[0] if  len(x) > 0  else '')
        
            #Use the prog_school dictionary created above to lookup 
            csvLandI['Unique_ID_MatchFour'] = csvLandI['Four_Fuzzy_CPos_NSchool'].map(prog_school)

            
            #This only updates the ID field if it wasn't already matched in an earlier process
            csvLandI['Unique_ID'] = np.where( csvLandI['Unique_ID'].isnull(), csvLandI['Unique_ID_MatchFour'], csvLandI['Unique_ID'])
            csvLandI['Unique_ID'] = np.where( csvLandI['Unique_ID'].isnull(), csvLandI.index + 5000, csvLandI['Unique_ID'])
            #Find any duplicated matchs and make any value after the first null to be filled in later
            csvLandI['Real_Unique'] = csvLandI.duplicated(subset='Unique_ID')            
            csvLandI.loc[ csvLandI['Real_Unique'] == True, 'Unique_ID'] = np.nan
            csvLandI.groupby('Unique_ID').Unique_ID.fillna(50, limit=1)

            
            
            #Merge together the two sources together based on the Final ID 
            #Fill the null index matches so that you can still have a unique id, Anything over the 9999 is not Matched
            csvLandI['counter'] = csvLandI.index + 9999
            csvLandI.loc[ csvLandI['Unique_ID'].isnull(), 'Unique_ID'] = csvLandI.loc[csvLandI['Unique_ID'].isnull()].counter
            csvLandI =  csvLandI.set_index('Unique_ID')
            csvCareerBridge =  csvCareerBridge.set_index('Unique_ID_CB')
            
            csvLandI = csvLandI[['occupation_name', 'pgm_name',   'soc',	'web',	'One_CPos_NSchool',	'Two_CPos_NWebsite',	'Three_CPos_CSchool',	'Four_Fuzzy_CPos_NSchool',	'Unique_ID_MatchOne',	'Unique_ID_MatchTwo',	'Unique_ID_MatchThree',	'Unique_ID_MatchFour']]
            csvCareerBridge = csvCareerBridge[[ 'position',	'school_name',	'award_type',	'address',  'link',	'entrance_req',	'description',	'clock_hours',	'etp',	'evenings_weekends',	'license_from_program',	'license_req_to_work',	'license_test_prep',	'online_courses',	'pay',	'total_tuition',	'training_length',	'tuition']]
            matched_results = pd.concat([ csvLandI, csvCareerBridge], axis=1)
            
            #Clean up the reamining columns and export the results and match to CAI categories
            results = self.cleanofColumnSchemaandDataTypes(matched_results)
            
            #Update null lat and long with 0s
            results.loc[results['longitude'] == np.nan, 'longitude'] = 0
            results.loc[results['latitude'] == np.nan, 'latitude'] = 0
            
            #print(results.head(5))
            return results





#Main Call to Both Web scrapers and Matching Filter
if __name__ == '__main__':
    #TEST
    data = [1,2,3,4,5]
    df = pd.DataFrame(data)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    apprenticeisRunning = os.path.join(os.path.sep, dir_path, 'ApprenticeisRunning.csv')
    df.to_csv(apprenticeisRunning)
    
    #EMAIL
    email_enabled = True
    linux = True
    emails = SendEmail()


    try:
        #Call Career Bridge and WA Labor and Industries Scrapers
        apprenticePrograms = MatchCareerBridgetoLandI()
        date = apprenticePrograms.formatDate
        
        #Backups if one of the scrapers no longer works
        apprenticePrograms.callWALaborandIndustries()
        wALaborIndustries_apprenticeship = os.path.join(os.path.sep, dir_path,  "backups_hardcoded", "WALaborIndustries_apprenticeship.csv")

        apprenticePrograms.callCareerBridge()
        careerBridge_Apprenticeship = os.path.join(os.path.sep, dir_path,  "backups_hardcoded", "CareerBridge_Apprenticeship.csv")

        LI_apprenticePrograms = pd.read_csv( wALaborIndustries_apprenticeship, encoding = "ISO-8859-1")
        CB_apprenticePrograms = pd.read_csv( careerBridge_Apprenticeship, encoding = "ISO-8859-1")


        #MATCH THE TWO WEBSITES
        apprentice_results = apprenticePrograms.matchLandItoCareerBridge( LI_apprenticePrograms, CB_apprenticePrograms )
        apprentice_results['id'] = apprentice_results.index
        
        results = os.path.join(os.path.sep, dir_path, "Apprenticeship.csv")
        apprentice_results.to_csv(results)

        # CONNECT TO DATABASE
        connect = DBConnection()
        engine = connect.engine()
        apprentice_results = apprentice_results[['id',	'pgm_name',	'occupation_name',  'soc',	'description',	'entrance_req',	'web',	'award_type',	'pay',	'training_length',	'evenings_weekends',	'license_from_program',	'license_req_to_work',	'online_courses',	'address',	'city',  'latitude',	'longitude']]
        
        # MIGRATE DATA INTO DATA FRAME (APPEND NOT REPLACE)    
        apprentice_results.to_sql(name='Apprenticeship', con=engine, if_exists='replace', index=False, chunksize=10, 
                        dtype={
                            'id':  sqlalchemy.types.INTEGER(),
                            'pgm_name': sqlalchemy.types.NVARCHAR(length=600),
                            'occupation_name': sqlalchemy.types.NVARCHAR(length=600),
                            'soc': sqlalchemy.types.NVARCHAR(length=10),
                            'description': sqlalchemy.types.NVARCHAR(length=3500),
                            'entrance_req': sqlalchemy.types.NVARCHAR(length=3000),
                            'web': sqlalchemy.types.NVARCHAR(length=700),
                            'award_type': sqlalchemy.types.NVARCHAR(length=200),
                            'pay': sqlalchemy.types.NVARCHAR(length=200),
                            'training_length': sqlalchemy.types.NVARCHAR(length=200),
                            'evenings_weekends': sqlalchemy.types.NVARCHAR(length=50),
                            'license_from_program': sqlalchemy.types.NVARCHAR(length=50),
                            'license_req_to_work': sqlalchemy.types.NVARCHAR(length=50),
                            'online_courses': sqlalchemy.types.NVARCHAR(length=50),
                            'address': sqlalchemy.types.NVARCHAR(length=500),
                            'city': sqlalchemy.types.NVARCHAR(length=200),
                            'latitude': sqlalchemy.types.Float(precision=32, decimal_return_scale=12, asdecimal=True),
                            'longitude': sqlalchemy.types.Float(precision=32, decimal_return_scale=12, asdecimal=True)})
                            
        #      'cai_category': sqlalchemy.types.NVARCHAR(length=50),
        #      'category_description': sqlalchemy.types.NVARCHAR(length=2000),
        print("Pushed data to Apprenticeship Table. \n Latest Data saved to Apprenticeship.csv")
            
        #EXPORT FOR DOWNLOAD
        resultsDash = os.path.join(os.path.sep, dir_path, "downloadables_for_s3", "Apprenticeship_Dashboard.csv")
        formated_for_download_apprentice = apprentice_results
        formated_for_download_apprentice.columns =  ['Unique Id',	'Program Name',	'Occupation Name',  'SOC Code',	'Program Description',	'Entrance Requirements',	'Website',	 'Award Type',	'Excpected Pay',	'Training Length',	'Classes are offered on Evenings or Weekends',	'Certification or license obtained from program',	'Certification or license required to work',	'Online courses available',	'Address',	'City',  'Latitude',	'Longitude']
        formated_for_download_apprentice.to_csv(resultsDash)
            
            
    except:
        print("Can NOT push data to Apprenticeship Table.")
        log = open("Error_Data.txt","a")
        log.write("Can not push new Apprenticeship data to Database. Location:Apprenticeship.py  Date: " + date + "\n")
        
        try:
            #Email if not successful
            subject = "CCE Web Scrapers - Apprenticeship Dashboard Can Not be Updated"
            body_text = ("RTC Dashboard - Apprenticeship Data Could Not be Updated\r\n"
                     "This email was sent because the data collection on the Apprenticeship websites could not be completed.\r\n"
                     "CARRIE SCHADEN\r\n"
                     "Data Systems Analyst  |  Community Attributes Inc.\r\n"
                    )
            body_html = """<html>
                <head></head>
                <body>
                    <h3>RTC Dashboard - Apprenticeship Data Could Not be Updated</h3>
                    <p>This email was sent because the data collection on the Apprenticeship websites could not be completed.</p>
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
            log.write("Can not Email Alerts about unsuccesful attempts. Location:Apprenticeship.py  Date: " + date + "\n")
            print("Can not email alert")


        
        