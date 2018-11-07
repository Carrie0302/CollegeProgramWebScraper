# -*- coding: utf-8 -*-
"""
Created on Tue Jan 16 12:50:48 2018
This creates the JobsForecast Dashboard data.  It calls wage data, training req, and job forecasts from ESD and BLS webscrapers.  
The sources are joined and shown by WDA area for each SOC. 
If an error occurs it is written to the Error_Data.txt. 
If the downloads from the webscraper are sucesful it is written to the Succesful_Download_Log.csv.

This does not require selenium.
@author: carrie
"""
import pandas as pd
import re, datetime, sqlalchemy
import os

from web_scrapers.ESDOccupationProjectionsClass import ESDOccupationProjection
from web_scrapers.BLSOccupationTrainingClass import BLSOccupationTraining
from web_scrapers.BLSWagesClass import BLSWages
from DatabaseConnection import DBConnection
from Email import SendEmail


class MatchESDandBLSSources():
        '''This will call the BLS  web scraper and match the items to ESD'''
        #Todays Date
        now = datetime.datetime.now()
        formatTime = now.strftime("%Y-%m-%d %H:%M")
        formatDate = now.strftime("%Y-%m-%d")
        formatHourMin = now.strftime("%H:%M")
        dir_path = os.path.dirname(os.path.realpath(__file__))
            
        def runTheESDOccupationProjection(self):
            occupations = ESDOccupationProjection()
            try:
                occupations.PageStatus()
                df = pd.DataFrame([['ESDOccupationProjection', 'JobsForecast Dashboard', '1 of 3', 'Washington State Employment Security Department Occupation Forecast', self.formatDate, self.formatHourMin, 'Successful Download']])
                df.to_csv('Succesful_Download_Log.csv', mode='a', header=False, index=False)
                print("ESDOccupationProjection loaded")
            except:
                log = open("Error_Data.txt","a")
                log.write("Error calling ESDOccupationProjection webscrapper. Location:JobsForecast.py  Date: " + self.formatTime + "\n")
                df = pd.DataFrame([['ESDOccupationProjection', 'JobsForecast Dashboard', '1 of 3', 'Washington State Employment Security Department Occupation Forecast', 'Will use last dowload', 0, 'FAILED Download']])
                df.to_csv('Succesful_Download_Log.csv', mode='a', header=False, index=False)
            return occupations
            
        
        def runTheBLSOccupationTraining(self):
            training = BLSOccupationTraining()            
            try:
                training.PageStatus()
                df = pd.DataFrame([['BLSOccupationTraining', 'JobsForecast Dashboard', '2 of 3', 'U.S. Bureau of Labor Statistics Occupation Training Requirements', self.formatDate, self.formatHourMin, 'Successful Download']])
                df.to_csv('Succesful_Download_Log.csv', mode='a', header=False, index=False)
                print("BLSOccupationTraining loaded")
            except:
                log = open("Error_Data.txt","a")
                log.write("Error calling BLSOccupationTraining webscrapper. Location:JobsForecast.py Date: " + self.formatTime + "\n")
                df = pd.DataFrame([['BLSOccupationTraining', 'JobsForecast Dashboard', '2 of 3', 'U.S. Bureau of Labor Statistics Occupation Training Requirements', 'Will use last dowload', 0, 'FAILED Download']])
                df.to_csv('Succesful_Download_Log.csv', mode='a', header=False, index=False)
                
            return training
        

        def runTheBLSWages(self):
            wages = BLSWages()            
            try:
                wages.PageStatus()
                df = pd.DataFrame([['BLSWages', 'JobsForecast Dashboard', '3 of 3', 'U.S. Bureau of Labor Statistics MSA and State wage data', self.formatDate, self.formatHourMin, 'Successful Download']])
                df.to_csv('Succesful_Download_Log.csv', mode='a', header=False, index=False)
                print("BLSWages loaded")
            except:
                log = open("Error_Data.txt","a")
                log.write("Error calling BLSWages webscrapper. Location:JobsForecast.py  Date: " + self.formatTime + "\n")
                df = pd.DataFrame([['BLSWages', 'JobsForecast Dashboard', '3 of 3', 'U.S. Bureau of Labor Statistics MSA and State wage data', 'Will use last dowload', 0, 'FAILED Download']])
                df.to_csv('Succesful_Download_Log.csv', mode='a', header=False, index=False)
            return wages
            
            
        def callESDProjections(self):
            #Open the files that are already downloaded
            dir_path = os.path.dirname(os.path.realpath(__file__))
            eSD_OccupationForecast = os.path.join(os.path.sep, dir_path, 'web_scrapers', 'log', 'ESD_OccupationForecast.xlsx')
            jobProjection = pd.read_excel(eSD_OccupationForecast, sheetname=0 )
            
            #See if it has the same number of columns, else throw error
            if len(jobProjection.columns) == 19:
                
                #Since the current year estimated employment field name will be changing in the future, we are grabing the name of the field based on the location and running a regex check to make sure it is estimated employment
                estEmpFieldName = jobProjection.columns[6]
                openingsFieldName = jobProjection.columns[17]
                
                #Select all the columns you need now that you've found the current year and rename them
                dataJobs = jobProjection.iloc[:, [0,1,2,3,6,17,18]]
                dataJobs.columns = ['SOC',	'SOC_Name', 'WDA_ID',	'WDA_Name',	'CurrentEmployment',	'ProjectedOpenings',	'SOC_Level']
                
                dataJobs.loc[:, 'WDA_MATCH'] = dataJobs.loc[:, 'WDA_Name']             
                dataJobs.loc[  (dataJobs['WDA_Name'] == "Seattle-King County") , 'WDA_MATCH'] = "Snohomish County"
                
                #Add in the Years Pulled from the Field Names
                dataJobs.loc[:, 'CurrentYear'] = "2018Q2"
                dataJobs.loc[:,'ProjectedYear'] =  2025
                #dataJobs.to_csv("ESDJobProjections.csv")
                return dataJobs

                
                
        def callBLSStateWages(self):
            #Open the files that are already downloaded
            dir_path = os.path.dirname(os.path.realpath(__file__))
            state_M2016_dl = os.path.join(os.path.sep, dir_path, 'web_scrapers', 'log', 'oesm16st' , 'state_M2016_dl.xlsX')
            statewages = pd.read_excel(state_M2016_dl, sheetname=0)
            statewageData = statewages[['ST', 'AREA', 'STATE', 'OCC_CODE', 'OCC_GROUP', 'A_MEDIAN', 'A_PCT90']]
            statewageData.columns = ['PRIM_STATE', 'AREA', 'AREA_NAME', 'OCC_CODE', 'OCC_GROUP', 'A_MEDIAN', 'A_PCT90']
            
            #Drop anything that is not a detailed SOC Code and not in Washington
            statewageData = statewageData[(statewageData.OCC_GROUP == 'detailed') & (statewageData.AREA_NAME ==  'Washington')]
            return statewageData
            
        
        def callBLSMetroWages(self):
            #Open the files that are already downloaded
            dir_path = os.path.dirname(os.path.realpath(__file__))
            mSA_M2016_dl = os.path.join(os.path.sep, dir_path, 'web_scrapers', 'log', 'oesm16ma', 'MSA_M2016_dl.xlsx')
   
            metroWages = pd.read_excel(mSA_M2016_dl, sheetname=0 )
            metroWageData = metroWages[['PRIM_STATE', 'AREA', 'AREA_NAME', 'OCC_CODE', 'OCC_GROUP', 'A_MEDIAN', 'A_PCT90']]
            
            #Open the MSA to WDA Lookup Table
            mSA_to_WDA_Lookup = os.path.join(os.path.sep, dir_path, 'LookupTables', 'MSA_to_WDA_Lookup.csv')
            msaToWdaLookup = pd.read_csv(mSA_to_WDA_Lookup)
            
            #Lookup the WDA associated with the MSA, Some have no match
            wdaLookup = msaToWdaLookup.set_index('MSA_ID')['WDA_Name'].to_dict()
            metroWageData.loc[:, 'WDA_Name'] = metroWageData['AREA'].map(wdaLookup)
            
            #Drop anything that is not a detailed SOC Code
            metroWageData = metroWageData[metroWages.OCC_GROUP == 'detailed']
            
            #Concatenate WDA and SOC fields to join to the ESD forecast data
            metroWageData.loc[:, 'WDA_SOC'] = metroWageData.apply(lambda row: str(row.WDA_Name) + str(row.OCC_CODE), axis=1)
            
            #metroWageData.to_csv("WDAWagesMetro.csv")
            return metroWageData
            
            
        def matchESDWagestoBLSOccupations(self):
            #Call the three data sets
            esdProjections = self.callESDProjections()
            metroWages = self.callBLSMetroWages()
            stateWages = self.callBLSStateWages()
            
            #Filter out anything under level 4, which is equal to 6 digit codes
            esdProjections = esdProjections[esdProjections.SOC_Level == 4]
            
            #Concatenate WDA and SOC fields to join on
            esdProjections.loc[:, 'WDA_SOC'] = esdProjections.apply(lambda row: str(row.WDA_MATCH) + str(row.SOC), axis=1)
            
            #Merge based on WDA_SOC combo
            #The first match is based on Metro data 
            matchedMetro = esdProjections.merge(metroWages,how='left', left_on='WDA_SOC', right_on='WDA_SOC')
            matchedMetroOccandWages = matchedMetro[matchedMetro.PRIM_STATE.notnull() ]
            unmatchedOcc = matchedMetro[matchedMetro.PRIM_STATE.isnull() ]
            matchedMetroOccandWages = matchedMetroOccandWages[['SOC',	'SOC_Name',	'WDA_ID',	'WDA_Name_x',	'CurrentEmployment',	'ProjectedOpenings',	'SOC_Level',	'CurrentYear',	'ProjectedYear',	'PRIM_STATE',	'AREA',	'AREA_NAME',	'OCC_CODE',	'OCC_GROUP',	'A_MEDIAN',	'A_PCT90',	'WDA_SOC']]
            #matchedMetroOccandWages.to_csv("matchedMetroOccandWages.csv")
            
            #If it was not matched based on WDA and SOC then we must match it to the state level
            unmatchedOcc = unmatchedOcc[['SOC',	'SOC_Name', 'WDA_ID',	'WDA_Name_x',	'CurrentEmployment',	'ProjectedOpenings',	'SOC_Level', 'CurrentYear', 'ProjectedYear']]
            #unmatchedOcc.to_csv('unmatchedOcc.csv')
            matchedStateOccandWage = unmatchedOcc.merge(stateWages, how='left', left_on='SOC', right_on='OCC_CODE')
            
            #Add WDA_SOC field to show those that are just matched on the SOC 
            matchedStateOccandWage.loc[:, 'WDA_SOC'] = matchedStateOccandWage.loc[:, 'SOC']            
            
            #Join the two dataframes that have been matched based on different methods
            finalOccandWages = pd.concat([matchedStateOccandWage, matchedMetroOccandWages], ignore_index=True)
            return finalOccandWages
            
            
        def matchtoCAICategories(self):
            wagesandOccupations = self.matchESDWagestoBLSOccupations()
            #wagesandOccupations = pd.read_csv('finalOccandWages.csv', encoding = "ISO-8859-1")
            dir_path = os.path.dirname(os.path.realpath(__file__))
            cAICategoriesandIDs = os.path.join(os.path.sep, dir_path, 'LookupTables', 'CAICategoriesandIDs.csv')
            
            #Open the SOC to CAI Category Table, make sure the csv is saved without utf8
            soctoCaiCategory = pd.read_csv(cAICategoriesandIDs, encoding = "ISO-8859-1")
            catLookup = soctoCaiCategory.set_index('SOC')['CAI_Category_ID'].to_dict()
            wagesandOccupations.loc[:, 'CAI_Category_ID'] = wagesandOccupations['SOC'].map(catLookup)
            catDescLookup = soctoCaiCategory.set_index('SOC')['CAI_Category_Name'].to_dict()
            wagesandOccupations.loc[:, 'CAICategory'] = wagesandOccupations['SOC'].map(catDescLookup)
            
            #Drop off Socs that are not matched to a CAI Category
            df = wagesandOccupations.dropna(subset = ['CAI_Category_ID'])
            return df 

        
        def matchtoTrainingData(self):
            #Open the BLS training data downloaded from ESD on the last sheet of the spreadsheet
            dir_path = os.path.dirname(os.path.realpath(__file__))
            bLS_OccupationTraining = os.path.join(os.path.sep, dir_path, 'web_scrapers',  'log', 'BLS_OccupationTraining.xlsx')
    
            trainingData = pd.read_excel(bLS_OccupationTraining, sheetname=12, header=1)
            trainingData.columns = [ 'Occupation_Name', 'SOC', 'Training_Education', 'Training_WorkExperience','Training_OntheJob']
            
            #Match the national training data to the WDA wage and occupation info
            wagesandOccupationData = self.matchtoCAICategories()
            wagesandOccupationData = wagesandOccupationData.merge(trainingData, how='left', left_on='SOC', right_on='SOC')

            #Format for Export
            wagesandOccupationData.loc[:, 'Matched_MSA_orWA']  =  wagesandOccupationData.loc[:, 'WDA_SOC']
            wagesandOccupationData.loc[:, 'WDA_SOC'] = wagesandOccupationData[['WDA_Name_x', 'SOC']].apply(lambda x: '_'.join(x.astype(str)), axis=1)            
            wagesandOccupationData.columns = ['SOC',  'SOC_Name',	'WDA_ID',	'WDA_Name',	'CurrentEmployment',	'ProjectedOpenings',	'SOC_Level',	'CurrentYear',	'ProjectedYear',	'PRIM_STATE',	'AREA',	'AREA_NAME',	'OCC_CODE',	'OCC_GROUP',	'Wage_Median',	'Wage_90',	'WDA_SOC',	'CAICategoryID',	'CAICategory',	'Occupation_Name',	'Training_Education',	'Training_WorkExperience',	'Training_OntheJob',	'Matched_MSA_orWA']
            final = wagesandOccupationData[['SOC',	'SOC_Name',	'WDA_ID',	'WDA_Name',	'CurrentEmployment',	'CurrentYear',	'ProjectedOpenings',	'ProjectedYear',	'SOC_Level',	'Training_Education',	'Training_WorkExperience',	'Training_OntheJob',	'WDA_SOC',	'Matched_MSA_orWA',	'Wage_Median',	'Wage_90',	'CAICategoryID',	'CAICategory']]
            
            print(final.head())
            return final

            

if __name__ == '__main__':
    #EMAIL
    email_enabled = True
    linux = True
    emails = SendEmail()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    try:
    
        # Call the scrapers
        jobforecast = MatchESDandBLSSources()
        date = jobforecast.formatDate
        jobforecast.runTheESDOccupationProjection()
        jobforecast.runTheBLSOccupationTraining()
        jobforecast.runTheBLSWages()
        
        # Format Job Data
        jobforecast = jobforecast.matchtoTrainingData()
        jobforecast['Id'] = jobforecast.index
        
        # MIGRATE DATA INTO DATA FRAME (APPEND NOT REPLACE)
        # CONNECT TO DATABASE
        connect = DBConnection()
        engine = connect.engine()
                
        jobforecast = jobforecast[['Id',	'SOC',	'SOC_Name',	'WDA_ID',	'WDA_Name',	'CurrentEmployment',	'CurrentYear',	'ProjectedOpenings',	'ProjectedYear',	'SOC_Level',	'Training_Education',	'Training_WorkExperience',	'Training_OntheJob',	'WDA_SOC',	'Matched_MSA_orWA',	'Wage_Median',	'Wage_90']]
        results = os.path.join(os.path.sep, dir_path, 'JobForecast.csv')
        jobforecast.to_csv( results )
        
        
        jobforecast.to_sql(name='JobsForecast', con=engine, if_exists='replace', index=False, chunksize=10, 
                      dtype={
                             'Id':  sqlalchemy.types.INTEGER(),
                             'SOC': sqlalchemy.types.NVARCHAR(length=20),
                             'SOC_Name': sqlalchemy.types.NVARCHAR(length=500),
                             'WDA_ID': sqlalchemy.types.INTEGER(),
                             'WDA_Name': sqlalchemy.types.NVARCHAR(length=500),
                             'CurrentEmployment': sqlalchemy.types.INTEGER(),
                             'CurrentYear': sqlalchemy.types.NVARCHAR(length=50),
                             'ProjectedOpenings': sqlalchemy.types.INTEGER(),
                             'ProjectedYear': sqlalchemy.types.INTEGER(),
                             'SOC_Level': sqlalchemy.types.INTEGER(),
                             'Training_Education': sqlalchemy.types.NVARCHAR(length=100),
                             'Training_WorkExperience': sqlalchemy.types.NVARCHAR(length=100),
                             'Training_OntheJob': sqlalchemy.types.NVARCHAR(length=100),
                             'WDA_SOC': sqlalchemy.types.NVARCHAR(length=100),
                             'Matched_MSA_orWA': sqlalchemy.types.NVARCHAR(length=100),
                             'Wage_Median': sqlalchemy.types.INTEGER(),
                             'Wage_90': sqlalchemy.types.INTEGER()})
                             
        print("Pushed data to JobsForecast Table. \n Latest Data saved to JobForecast.csv")
        
        #EXPORT FOR DOWNLOAD
        resultsDash = os.path.join(os.path.sep, dir_path, "downloadables_for_s3", "JobForecast_Dashboard.csv")
        formated_for_download_jobs = jobforecast[['Id',	'SOC',	'SOC_Name',	'WDA_ID',	'WDA_Name',	'CurrentEmployment',	'CurrentYear',	'ProjectedOpenings',	'ProjectedYear',	'Training_Education',	'Training_WorkExperience',	'Training_OntheJob',	'Wage_Median',	'Wage_90']]
        formated_for_download_jobs.columns = [ 'Id',	'Soc Code',	'Soc Name',	'Workforce Development Areas ID',	'Workforce Development Areas Name',	'Current Employment',	'Current Year',	'Projected Openings (Average annual total openings  2020-2025)',	'Projected Year',		'Typical education needed for entry',	'Work experience in a related occupation',	'Typical on-the-job training needed to attain competency in the occupation',	'Median Wage',	'Top Wage Potential']
        formated_for_download_jobs.to_csv(resultsDash)

    except:
        print("Can NOT push data to JobsForecast Table.")
        log = open("Error_Data.txt","a")
        log.write("Can not push new JobsForecast data to Database. Location:JobsForecast.py  Date: " + date + "\n")

        try:
            #Email if not successful
            subject = "CCE Web Scrapers - Jobs Forecast Dashboard Can Not be Updated"
            body_text = ("RTC Dashboard - Jobs Forecast Data Could Not be Updated\r\n"
                             "This email was sent because the data collection on the Jobs Forecast websites could not be completed.\r\n"
                             "CARRIE SCHADEN\r\n"
                             "Data Systems Analyst  |  Community Attributes Inc.\r\n"
                            )
            body_html = """<html>
                <head></head>
                <body>
                    <h3>RTC Dashboard - Jobs Forecast Data Could Not be Updated</h3>
                    <p>This email was sent because the data collection on the Jobs Forecast websites could not be completed.</p>
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
            log.write("Can not Email Alerts about unsuccesful attempts. Location:JobsForecast.py  Date: " + date + "\n")

            print("Can not email alert")
                
    

    