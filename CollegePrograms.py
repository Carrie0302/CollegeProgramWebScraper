# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 16:15:31 2017
This creates the CollegePrograms Dashboard. It calls the Career Bridge class and Matches it to a SOC based on the listed occupation, industry, keywords and lookups.

This requires selenium.
@author: carrie
"""
from selenium import webdriver
import pandas as pd
import requests, sqlalchemy, datetime
import numpy as np
from pyvirtualdisplay import Display
import os

key = 'fill in'

from web_scrapers.CareerBridgeClass import CareerBridge
from DatabaseConnection import DBConnection
from Email import SendEmail


class MatchConstructionSOCtoCollegePrograms:
        '''This will call the Career Bridge  web scraper and match the items to SOC Codes'''
        #Todays Date
        now = datetime.datetime.now()
        formatTime = now.strftime("%Y-%m-%d %H:%M")
        formatDate = now.strftime("%Y-%m-%d")
        formatHourMin = now.strftime("%H:%M")
        
        def callBrowser(self):
            ubuntu = False
            browser = ""
            
            if ubuntu:
                display = Display(visible=0, size=(800, 800))  
                display.start()
                
                path_to_chromedriver = "/usr/bin/chromedriver"
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--no-sandbox')
                browser = webdriver.Chrome(path_to_chromedriver, chrome_options=chrome_options)
                
                urlTechCollege = 'http://www.careerbridge.wa.gov/Search_Program.aspx?cmd=txt&adv=true&txt='
                browser.get(urlTechCollege)
                browser.implicitly_wait(10)
            
            else:
                #If windows use the following
                path_to_chromedriver = r"\chromedriver.exe"
                browser = webdriver.Chrome(executable_path = path_to_chromedriver )
                urlTechCollege = 'http://www.careerbridge.wa.gov/Search_Program.aspx?cmd=txt&adv=true&txt='
                browser.get(urlTechCollege)
            
            return browser
        
        def callCareerBridge(self):
            #Open Intial Website with Selenium and Chrome, you will need to upate this and get appropriate Linux versions for Ec2
            browserCB = self.callBrowser()
            
            #Call the HTML Scraper for College Programs
            technicalCollegeResult = CareerBridge()
            techCollegePrograms = pd.DataFrame()
            occupationsPerProgam = pd.DataFrame()
            
            #Try to do call the scraper for Career Bridge
            try:
                technicalCollegeResult.type = "technicalCollege"
                techResults = technicalCollegeResult.href_per_school(browserCB)
                cleaned_pages, occupation_pages = technicalCollegeResult.download_tech_college_programs(techResults, browserCB)
                
                #Concatenate dataframes into final exports for csv
                dir_path = os.path.dirname(os.path.realpath(__file__))
                careerBridge_CollegePrograms = os.path.join(os.path.sep, dir_path, 'backups_hardcoded','CareerBridge_CollegePrograms.csv')
                careerBridge_CollegePrograms_Occupations = os.path.join(os.path.sep, dir_path, 'backups_hardcoded','CareerBridge_CollegePrograms_Occupations.csv')
                technicalCollegeResult.merge_export_to_csv(techResults, cleaned_pages, careerBridge_CollegePrograms)
                technicalCollegeResult.export_career_data_to_csv(occupation_pages, careerBridge_CollegePrograms_Occupations)

                #Hardcoded export                
                techCollegePrograms = pd.read_csv(careerBridge_CollegePrograms, encoding = "ISO-8859-1")
                occupationsPerProgam = pd.read_csv(careerBridge_CollegePrograms_Occupations, encoding = "ISO-8859-1")
                
                #Log success
                df = pd.DataFrame([['CareerBridge', 'College Programs Dashboard', '1 of 1', 'Career Bridge Web Scraper College data', self.formatDate, self.formatHourMin, 'Successful Download']])
                df.to_csv('Succesful_Download_Log.csv', mode='a', header=False, index=False)
                 
            #If the scraper can not be called log the issue
            except:
                log = open("Error_Data.txt","a")
                log.write("Error calling CareerBridge webscrapper. Location:CollegePrograms.py  Date: " + self.formatTime + "\n")
                df = pd.DataFrame([['CareerBridge', 'College Programs Dashboard', '1 of 1', 'Career Bridge Web Scraper College data', 'Will use last dowload', 0, 'FAILED Download']])
                df.to_csv('Succesful_Download_Log.csv', mode='a', header=False, index=False)
     
            browserCB.close()
            
            final = self.identify_construction_programs(techCollegePrograms, occupationsPerProgam)
            return final
        
        
        #Check to see if any of the addresses are already geocoded
        def checkAddressLookup(self,results):
            #Remove stuff in parenthesis at the end from the address
            results['address'] = results['address'].str.replace(r"\(.*\)","").str.strip()
            
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
            
            #Update the Geocode LookupTable, Make sure to only pass Unique Addresses
            allGeocoded = pd.concat([newGeocoded, previousGeocoded])
            saveNewGeocodeLookup = allGeocoded.loc[ :, ['address', 'latitude', 'longitude', 'city']]
            saveNewGeocodeLookup.to_csv(geoCodedAddressesLookup)
            
            #If the geocoding is way off override
            allResultsGeocoded.loc[allResultsGeocoded['latitude'] <= 45.0, 'latitude'] = 0
            allResultsGeocoded.loc[allResultsGeocoded['longitude'] >= -116.0, 'longitude'] = 0
            allResultsGeocoded.loc[(allResultsGeocoded['longitude'] >= -116.0) & (allResultsGeocoded['address'] == 'S. 16th Ave. & Nob Hill Blvd, Yakima, WA 98902'), 'city'] = 'Yakima'
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
                newAddresses = pd.DataFrame(notGeocoded.place.values.tolist(), index=notGeocoded.index)
                #Parse the returned place info list into the appropriate columns
                notGeocoded[['latitude','longitude', 'city', 'place_id', 'addressfound']] = newAddresses
                
            return notGeocoded
            
        
        def geocodeAddress(self, address):
            google_url = "https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}".format(address, key)
            response_geocode = requests.get(google_url).json()
            
            lat,lng,place_id, city = 0,0,"None", ""
            
            #if results were returned take the first one
            if len(response_geocode['results']) > 0:
                r = response_geocode['results'][0]
                
                findcity = r[u'address_components']
                for f in findcity:
                    if 'locality' in f[u'types']:
                        city = f[u'long_name']
                
                lat = r[u'geometry'][u'location'][u'lat']
                lng = r[u'geometry'][u'location'][u'lng']
                place_id = r[u'place_id']
            
            #print([lat, lng, city, place_id, address])
            return [lat, lng, city, place_id, address]
            
        #Identify Construction in College Programs
        def identify_construction_programs(self, df_cleaned, occ_df):
            
            df = df_cleaned.dropna(how='all')
            df['match_construction_description'] = 'No'
            df['match_construction_name'] = 'No'
            #print(df.head(5))
            
            #First Tag
            #If construction in description or name add field identifying a match to construction occupations
            #df['description'] = df['description'].fillna("No")
            
            
            df.loc[df['program'].str.contains('Construction', na=False), 'match_construction_name'] = "Yes"
            df.loc[df['description'].str.contains('construction', na=False), 'match_construction_description'] = "Yes"
            
            #Second Tag
            #Pull in SOC Lookup Table to Match the SOC to Occupation List per Program
            dir_path = os.path.dirname(os.path.realpath(__file__))
            sOCCodeLookup = os.path.join(os.path.sep, dir_path, 'LookupTables','SOCCodeLookup.csv')
                
            socLookUp = pd.read_csv(sOCCodeLookup, encoding="utf-8", index_col=0)
            #soc = socLookUp.set_index('﻿SOCName')['SOCID'].to_dict()
            soc = socLookUp.ix[:,0].to_dict()

            #construction = socLookUp.set_index('﻿SOCName')['Construction'].to_dict()
            construction = socLookUp.ix[:,1].to_dict()
            occ_df['soc_codes_by_occupation'] = occ_df['occupation'].map(soc)
            occ_df['match_construction_occ'] = occ_df['occupation'].map(construction)
            occ_df['match_construction_occ'] = occ_df['match_construction_occ'].fillna("No")
            
            
            #Remove any programs from the match through the description based on Program Key Words that We Do Not want
            dir_path = os.path.dirname(os.path.realpath(__file__))
            remove_NonConstruction_KeyWords = os.path.join(os.path.sep, dir_path, 'LookupTables','Remove_NonConstruction_KeyWords.csv')
            
            removeLookup = pd.read_csv(remove_NonConstruction_KeyWords)
            df['remove_keyword'] = df['program_name'].apply(lambda x: [key for key in removeLookup['remove'] if key in str(x) ])
            df['remove_keyword'] = df['remove_keyword'].str[0]
            df['remove_keyword'] = df['remove_keyword'].fillna("None")
            df['match_construction_final'] = "None"
            df.loc[ df['remove_keyword'] != "None" , 'match_construction_final'] = "No"
            
        
            #Pull in Keyword Search in order to Associate Programs to SOCS and Get the First Best Match to the Program Name
            cAIConstructionKeywordLookup = os.path.join(os.path.sep, dir_path, 'LookupTables','CAIConstructionKeywordLookup.csv')
            keywordsDetailed = pd.read_csv(cAIConstructionKeywordLookup)
            df['program_keyword_join'] = df['program'].str.lower()
            #df['match_keyword'] = df['program_keyword_join'].apply(lambda x: difflib.get_close_matches(x, keywordsDetailed['keyword1'], 1))
            df['match_keyword'] =  df['program_keyword_join'].apply(lambda x: [key for key in keywordsDetailed['keyword_if_matched'] if key in str(x) ])    
            df['match_keyword'] = df['match_keyword'].str[0]
            
            
            #If there is a keyword match but no mention of construction in the name or description remove keyword 
            df['match_keyword'] = df['match_keyword'].fillna("None")
            df.loc[ (df['match_keyword'] != "None") &  ((df['match_construction_description'] == "No")  &  (df['match_construction_name'] == "No")), 'match_keyword'] = "None"
            
            
            #Add Soc Codes based on Key Words
            soc_keyword = keywordsDetailed.set_index('keyword_if_matched')['soc_codes'].to_dict()
            df['soc_codes_by_keyword'] = df['match_keyword'].map(soc_keyword)
            df['soc_codes_by_keyword'] = df['soc_codes_by_keyword'].fillna("None")
            #occ_df.to_csv("FINAL_CollegePrograms_Occupations.csv")
        
            
            #Filter One, Filter the ocupation dataframe by only those occupations that are construction
            occ_construction = occ_df.loc[(occ_df.match_construction_occ == "Yes")]
            occ_construction = occ_construction[['program_id', 'soc_codes_by_occupation','match_construction_occ']]
            
            
            #Set the index to the program id, format column order, and remove duplicates from occupations, Keep the First that Matches The SOCS We Want
            occ_construction_i = occ_construction.set_index('program_id')
            df = df.set_index('program_id')
            occupation_con = occ_construction_i[~occ_construction_i.index.duplicated(keep='first')]
            #print(occupation_con)
            
            
            #Pull in Occupation SOCS for The SOCS We Don't Want that Do Not Match Contruction, to Use to as a Filter Later
            occ_df =  occ_df.loc[(occ_df.match_construction_occ == "No")]
            occ_df['soc_codes_by_occupation_not_construction'] = occ_df['soc_codes_by_occupation']
            occ_df =  occ_df[['program_id', 'soc_codes_by_occupation_not_construction']]
            occ_df =  occ_df.set_index('program_id')
            occupation_not_matched = occ_df[~occ_df.index.duplicated(keep='first')]
            occupation_full = pd.concat([ occupation_con,occupation_not_matched], axis=1)
            occupation_full['match_construction_occ'] = occupation_full['match_construction_occ'].fillna("No")
            #print(occupation_full)
            
            
            #Merge dataframes so construction info is brought over
            #apprenticeship = df.loc[(df.construction_related == "Yes")]
            result = pd.concat([df, occupation_full], axis=1)
            result['soc_code'] = "None"
            result['soc_code'] = np.where( result['soc_codes_by_occupation'].isnull(), result['soc_codes_by_keyword'], result['soc_codes_by_occupation'])
            
            
            #If Soc Code Pulled in for Program Then Update Match Construction Field 
            #If the removal keywords is associated with a program but the program returned a construciton occupation link then change to Yes
            #result.loc[  (result['match_construction_final'] == "No")  &  (result['match_construction_occ'] == "Yes") , 'match_construction_final'] = "Yes" 
            
            #Make Sure that a Removal Key word has not been associated and that a Soc has been found
            result.loc[  (result['match_construction_final'] != "No") & (result['soc_code'] != "None") , 'match_construction_final'] = "Yes"
            
            
            #For the remaining few that said construction in the description, but which have not been removed by keyword or matched to a SOC by keyword, Add the generic 47-4099 as their SOC
            df['match_construction_final'] = df['match_construction_final'].fillna("None")    
            result.loc[  (result['match_construction_final'] == "None") & ((result['match_construction_description'] == "Yes") | (result['match_construction_name'] == "Yes")) , 'soc_code'] = "47-4099"
            result.loc[  (result['soc_code'] == "47-4099") , 'match_construction_final'] = "Yes"
            
            
            #Do Another Round of KeyWord Matches for Those Without a SOC Where there Is No Removal keyword associated
            #1. if there is no key word add to the generic category
            result['match_keyword2'] =  result['program_keyword_join'].apply(lambda x: [key for key in keywordsDetailed['keyword_if_not_matched'] if key in str(x) ])    
            result['match_keyword2'] = result['match_keyword2'].str[0]
            #result.loc[  (result['match_keyword2'] == "None") & ((result['match_construction_description'] == "Yes") | (result['match_construction_name'] == "Yes")) , 'soc_code'] = "47-4099"
            
            #2. if there was no occupation information available then try to find the associated SOC even if it was not tagged previously
            soc_keyword2 = keywordsDetailed.set_index('keyword_if_not_matched')['soc_codes'].to_dict()
            result['soc_codes_by_keyword2'] = result['match_keyword2'].map(soc_keyword2)
            result['soc_codes_by_keyword2'] = result['soc_codes_by_keyword2'].fillna("None")
            result['soc_codes_by_occupation_not_construction'] = result['soc_codes_by_occupation_not_construction'].fillna("None")
            result['soc_codes_by_keyword2'] = np.where( (result['match_construction_final'] == "None")  & ( result['soc_codes_by_occupation_not_construction'] == "None" ) ,  result['soc_codes_by_keyword2'], "")
            result['soc_code'] = np.where( result['match_construction_final'] == "None",  result['soc_codes_by_keyword2'], result['soc_code'])
            
            result['soc_code'] = result['soc_code'].replace('', 'None', regex=True)
            result.loc[  (result['match_construction_final'] != "No") & (result['soc_code'] != "None") , 'match_construction_final'] = "Yes"
            result['soc_code'] = result['soc_code'].replace('None', np.nan)
            result.loc[ (result['match_construction_final'] == "No")  , 'soc_code'] =  np.nan
            #print(result.head(23))
            
            #Pull in CAI categories To match soc_codes to Cai Category
            cAIConstructionLookup = os.path.join(os.path.sep, dir_path, 'LookupTables','CAIConstructionLookup.csv')
            caiCategories = pd.read_csv(cAIConstructionLookup)
            cai_category = caiCategories.set_index('detailed_occupation')['cai_category'].to_dict()    
            result['cai_category'] = result['soc_code'].map(cai_category)
            print(result[['cai_category', 'soc_code']])
            #result.to_csv("read.csv")
            
            

            #If Cai Category does not exist in data add Data not avail row
            #First look at the socs found during scraping and map to the existing socs we want in our look up table and save the unique set of their related categories to a list
            existingCategories = result.set_index('soc_code')['cai_category'].to_dict()
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
            result['program'] = np.where( result['program'].isnull(),  'NULL', result['program'])
            lastRow = result.index.max() + 1
            print(result.columns)
            for soc in dataNotAvail:
                if soc != '47-2061':
                    result.loc[lastRow] = ['No Data Available', 'No Data Available', 'No Data Available', 'Washington State', 'No Data Available', np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,  '', np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,  np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan,  soc,  np.nan, np.nan, np.nan ]
                    lastRow += 1
                
            
            
            
            
            #Pull in CAU Category descriptions
            cAICategoryDescriptions = os.path.join(os.path.sep, dir_path, 'LookupTables','CAICategoryDescriptions.csv')
            caiCategoryDesc = pd.read_csv(cAICategoryDescriptions)
            cai_category_desc = caiCategoryDesc.set_index('cai_category')['category_description'].to_dict()    
            result['category_description'] = result['cai_category'].map(cai_category_desc)
            
            #Check to see if the address has already been geocoded
            result = self.checkAddressLookup(result)
  
            #Update null with 0s
            result.loc[result['longitude'] == np.nan, 'longitude'] = 0
            result.loc[result['latitude'] == np.nan, 'latitude'] = 0
            dbexport = result[[ 'program',	'school_name',  'website',	'address',	'latitude',	 'longitude',	'city',	'award_type',	'books_material_costs',	'clock_hours',	'credits',	'evenings_weekends',	'fees',	'length_of_training',	'license_from_program',	'license_req_to_work',	'license_test_prep',	'online_courses',	'other_costs',	'total_tuition',	'tuition',	'tuition_per_credit',	'cai_category',	'category_description',	'soc_code',	  'description',	'entrance_req']]            
            
            #Update the db when data not avail
            dbexport['program'] = np.where( dbexport['program'].isnull(),  'No Data Available', dbexport['program'])
            return dbexport
            

if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    #TEST
    data = [1,2,3,4,5]
    df = pd.DataFrame(data)
    collegeisRunning = os.path.join(os.path.sep, dir_path, 'CollegeisRunning.csv')
    df.to_csv(collegeisRunning)
    
    #EMAIL
    email_enabled = True
    linux = False
    emails = SendEmail()
    
    try:
        #CALL WEBSCRAPERS
        collegePrograms = MatchConstructionSOCtoCollegePrograms()
        date = collegePrograms.formatDate
        get_collegePrograms = collegePrograms.callCareerBridge()
        get_collegePrograms['id'] = get_collegePrograms.index
        
        #Drop anything not tagged construction
        df = get_collegePrograms.dropna(subset = ['soc_code'])
        collegePrograms = os.path.join(os.path.sep, dir_path, 'CollegePrograms.csv')
        df.to_csv(collegePrograms)
        
        # CONNECT TO DATABASE
        connect = DBConnection()
        engine = connect.engine()
        df = df[['id',	'program',	'school_name',	'website',	'address',	'latitude',	'longitude',	'city',	'award_type',	'books_material_costs',	'clock_hours',	'credits',	'evenings_weekends',	'fees',	'length_of_training',	'license_from_program',	'license_req_to_work',	'license_test_prep',	'online_courses',	'other_costs',	'total_tuition',	'tuition',	'tuition_per_credit',	'soc_code',	'description',	'entrance_req']]
    
        
        # MIGRATE DATA INTO DATA FRAME (APPEND NOT REPLACE)    
        df.to_sql(name='CollegeProgram_new', con=engine, if_exists='replace', index=False, chunksize=10, 
                      dtype={
                             'id':  sqlalchemy.types.INTEGER(),
                             'program': sqlalchemy.types.NVARCHAR(length=500),
                             'school_name': sqlalchemy.types.NVARCHAR(length=500),
                             'website': sqlalchemy.types.NVARCHAR(length=300),
                             'address': sqlalchemy.types.NVARCHAR(length=300),
                             'latitude': sqlalchemy.types.Float(precision=32, decimal_return_scale=12, asdecimal=True),
                             'longitude': sqlalchemy.types.Float(precision=32, decimal_return_scale=12, asdecimal=True),
                             'city': sqlalchemy.types.NVARCHAR(length=300),
                             'award_type': sqlalchemy.types.NVARCHAR(length=300),
                             'books_material_costs': sqlalchemy.types.NVARCHAR(length=2000),
                             'clock_hours': sqlalchemy.types.NVARCHAR(length=100),
                             'credits': sqlalchemy.types.INTEGER(),
                             'evenings_weekends': sqlalchemy.types.NVARCHAR(length=50),
                             'fees': sqlalchemy.types.NVARCHAR(length=50),
                             'length_of_training': sqlalchemy.types.NVARCHAR(length=50),
                             'license_from_program': sqlalchemy.types.NVARCHAR(length=50),
                             'license_req_to_work': sqlalchemy.types.NVARCHAR(length=50),
                             'license_test_prep': sqlalchemy.types.NVARCHAR(length=50),
                             'online_courses': sqlalchemy.types.NVARCHAR(length=50),
                             'other_costs': sqlalchemy.types.NVARCHAR(length=50),
                             'total_tuition': sqlalchemy.types.NVARCHAR(length=200),
                             'tuition': sqlalchemy.types.NVARCHAR(length=200),
                             'tuition_per_credit': sqlalchemy.types.NVARCHAR(length=200),
                             'soc_code': sqlalchemy.types.NVARCHAR(length=20),
                             'description': sqlalchemy.types.NVARCHAR(length=3000),
                             'entrance_req': sqlalchemy.types.NVARCHAR(length=3000)})
     
        print("Pushed data to CollegeProgram Table. \n Latest Data saved to CollegePrograms.csv")
    
        #EXPORT FOR DOWNLOAD
        resultsDash = os.path.join(os.path.sep, dir_path, "downloadables_for_s3", "CollegePrograms_Dashboard.csv")
        formated_for_download_college = df
        formated_for_download_college.columns = ['id',	'Program Name',	'School Name',	'Website',	'Address',	'Latitude',	 'Longitude',	'City',	'Award Type',	'Costs of Books and Materials',	'Clock Hours for Program',	'Credits Needed for Program',	'Classes are offered on Evenings or Weekends',	'Additional Fees',	'Training Length',	'Certification or license obtained from program',	'Certification or license required to work',   'Certification or license test preparation provided',	'Online courses available', 	'Other Costs',	'Total Tuition',	'Tuition',	'Tuition per credit',	'Soc Code',	 'Description',	'Entrance Requirements']
        formated_for_download_college.to_csv(resultsDash)
        
    except:
        print("Can NOT push data to CollegePrograms Table.")
        log = open("Error_Data.txt","a")
        log.write("Can not push new Apprenticeship data to Database. Location:Apprenticeship.py  Date: " + date + "\n")
        
        try:
            #Email if not successful
            subject = "CCE Web Scrapers - College Programs Dashboard Can Not be Updated"
            body_text = ("RTC Dashboard - College Programs Data Could Not be Updated\r\n"
                             "This email was sent because the data collection on the College Programs websites could not be completed.\r\n"
                             "CARRIE SCHADEN\r\n"
                             "Data Systems Analyst  |  Community Attributes Inc.\r\n"
                            )
            body_html = """<html>
                <head></head>
                <body>
                    <h3>RTC Dashboard - College Programs Data Could Not be Updated</h3>
                    <p>This email was sent because the data collection on the College Programs websites could not be completed.</p>
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
            log.write("Can not Email Alerts about unsuccesful attempts. Location:CollegeProgams.py  Date: " + date + "\n")

            print("Can not email alert")
            


    
