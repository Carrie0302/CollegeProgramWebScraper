# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 13:49:21 2017
Source: WA State Dep. Labor & Industries, PreApprenticeship Data
@author: carrie
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import pandas as pd
#import geocoder
import datetime, os, re
from pyvirtualdisplay import Display

key = 'fill in'

class WALaborandIndustriesPreApprenticeship:

    #Expand the ul for each program    
    def expand_accordian(self, browser):
        expand_all = browser.find_elements_by_xpath('//*[@src="/common/images/expandPlus.gif"]')
        number_preapprentice = len(expand_all)
        print("Program Number {0}".format(number_preapprentice))
        
        expanded_list = []
        for e in expand_all:
            e.click()
            expanded_list.append(e)
            time.sleep(1)
        return expanded_list


    def find_certifaction_offered(self, program_name, program_description, description_list):
        osha10 = ""
        firstaid = ""
        forklift = ""
        flagging = ""
        hazwoper = ""

        program_des_l = program_description.lower()
        
        keyword_osha10 = ["osha 10", "osha"]
        keyword_firstaid = ["first aid", "cpr card", "/cpr"]
        keyword_forklift = ["forklift"]
        keyword_flagging = ["flagging", "flagger", "traffic control"]
        keyword_hazwoper = ["hazwoper", "hazardous waste operations and emergency response standard"]
        
        if any(key in program_des_l for key in keyword_osha10):
            osha10 = "Yes"
        if any(key in program_des_l for key in keyword_firstaid):
            firstaid = "Yes"
        if any(key in program_des_l for key in keyword_forklift):
            forklift = "Yes"
        if any(key in program_des_l for key in keyword_flagging):
            flagging = "Yes"
        if any(key in program_des_l for key in keyword_hazwoper):
            hazwoper = "Yes"

        certification_offered = [ osha10, firstaid, forklift, flagging, hazwoper]       
        return certification_offered
    
    
    
    def get_location(self, program_name, program_description, description_list):
        address = ""
        address_street = ""
        address_state = ""
        phone = ''
        
        if description_list:
            i = 1
        else:
            description_list = [program_description]
            
        #If it specifies Location at a certain point with a line break
        if "Location:" in description_list:
            find_title = description_list.index("Location:")
            #print(find_title)
            group_search = description_list[find_title: -1]
            address_pattern = '^\d{3}.*'
            address_state_pattern = '[a-zA-Z,]* Wash. \d{5}'
            
            for g in group_search:
                address_found = re.match(address_pattern, g, flags = 0)
                address_state_found = re.match(address_state_pattern, g, flags = 0)
                
                if address_found:
                    address_street = address_found.group()                    

                if address_state_found:
                    address_state = address_state_found.group()
                
                    
        #if the address is burried somewhere
        else:
            address_pattern = '^\d{3}.*'
            address_pattern_alt = 'Location: \d{3}.*'
            address_state_pattern = '[a-zA-Z,]* Wash. \d{5}'
            address_state_pattern_alt = '[a-zA-Z\,]* WA \d{5}'
            address_state_pattern_alt2 = '[a-zA-Z\,]* WA, \d{5}'
            phone_pattern = '^[1-9]\d{2}-\d{3}-\d{4}'
            #print(program_name)
            #print(description_list)
            
            for g in description_list:
                address_found = re.match(address_pattern, g, flags = 0)
                address_alt_found = re.match(address_pattern_alt, g, flags = 0)
                address_state_found = re.match(address_state_pattern, g, flags = 0)
                address_state_found_alt = re.match(address_state_pattern_alt, g, flags = 0)
                address_state_found_alt2 = re.match(address_state_pattern_alt2, g, flags = 0)
                
                phone_found = re.match(phone_pattern, g, flags = 0)
                
                #it could be the street address or a phone number
                if address_found:
                    address_street_temp = address_found.group()                    
                    
                    if phone_found:
                        phone = phone_found.group()
                    else:
                        address_street = address_street_temp
                        
                if address_alt_found:
                    address_street = address_alt_found.group()                    
                    
                if address_state_found:
                    address_state = address_state_found.group()
                    
                elif address_state_found_alt:
                    address_state = address_state_found_alt.group()
                    
                elif address_state_found_alt2:
                    address_state = address_state_found_alt2.group()
        
        #combine to format
        if  address_street != "" and address_state != "":
            address = "{0} {1}".format(address_street, address_state)
        elif address_street != "" and address_state == "":
            address = address_street

        return address.replace('Location: ', '')
        
    
    def find_who_they_serve(self, program_name, program_description, description_list, program_count):
        youth = ""
        women = ""
        general = ""
        low_income =""
        veteran = ""
        program = program_name.lower()      
        
        
        keyword_women = ["women", "woman", "girls", "lady", "ladies", "girl"]
        keyword_youth = ["youth", " teen", "young ", " kids"]
        keyword_income = ["low income", "low-income", "poverty"]
        key_return = "All Others"
        
        #Check Program Names
        if any(key in program for key in keyword_youth):
            youth = "Yes"
            key_return = "Youth"
        
        if any(key in program for key in keyword_women):
            women = "Yes"
            key_return = "Women"
            
        if "veteran" in program:
            veteran = ""            
            key_return = "Veteran"
            
        if any(key in program for key in keyword_income):
            low_income = "Yes"            
            key_return = "Low Income"
            
        if women == '' and youth == '' and low_income == '' and veteran == '':
            general = "Yes"
        
        
        
        who_they_serve_tags = [ youth, women, general, veteran, low_income, key_return]       
        return who_they_serve_tags




    def find_website(self, program_name, description_list):
        web = ''
        
        #Find the website if called it
        r = re.compile("Website:.*")
        websites = filter(r.match, description_list)
        websites = [i for i in websites]
        if len(websites) > 0:
            web = websites[0].replace('Website: ', '')
        else:
            #If nothing was returned look for websites
            rc = re.compile("Websites:.*")
            
            websites2 = filter(rc.match, description_list)
            websites2 = [i for i in websites2]
            if len(websites2) > 0:
                web = websites2[0].replace('Websites: ', '')
    
        #Check to see if it is an actual url
        if '.com' in web:
            web = web
        elif 'www.' in web:
            web = web
        elif '.aspx' in web:
            web = web
        elif '.org' in web:
            web = web
        elif '.edu' in web:
            web = web
        else:
            web = ''
        return web
        
        
        
        
    def find_entry_requirements(self, program_name, program_description, description_list):
        atleast18 = ""
        otherageReq = ""
        noGEDorDiplomaNeeded = ""
        GEDorDiplomaReq = ""
        licenseReq = ""
        otherReq = ""
        
        atleast18_key = ['at least 18', 'over 18', 'minimum 18', '18 or ']
        otherage_key = ['18 to 24', '18 and 24']
        noGEDorDiploma_key = ['not finished their high school diploma', 'lack a diploma', 'lack a GED', 'opportunity to earn their GED', 'goal of attaining either their diploma']
        GEDorDiploma_key = ['Have high school diploma or GED', 'have a high school diploma' ]
        license_key = ['must have a valid driver’s license', 'have a license']
        other_key = [ 'resident.']
        
        #Search description_list
        for d in description_list:

            if any(key in d for key in atleast18_key):
                atleast18 = [key for key in  atleast18_key if key in d].pop()
            if any(key in d for key in otherage_key):
                otherageReq = [key for key in  otherage_key if key in d].pop()
            if any(key in d for key in noGEDorDiploma_key):
                noGEDorDiplomaNeeded = [key for key in  noGEDorDiploma_key if key in d].pop()
            if any(key in d for key in GEDorDiploma_key):
                GEDorDiplomaReq = [key for key in  GEDorDiploma_key if key in d].pop()
            if any(key in d for key in license_key):
                licenseReq = [key for key in  license_key if key in d].pop()
            if any(key in d for key in other_key):
                otherReq = [key for key in  other_key if key in d].pop()

#            if any(key in d for key in atleast18_key):
#                atleast18 = "At Least 18 Years Old"
#            if any(key in d for key in otherage_key):
#                otherageReq = key
#            if any(key in d for key in noGEDorDiploma_key):
#                noGEDorDiplomaNeeded = key
#            if any(key in d for key in GEDorDiploma_key):
#                GEDorDiplomaReq = key
#            if any(key in d for key in license_key):
#                licenseReq = key
#            if any(key in d for key in other_key):
#                otherReq = key
        
        entry_requirements = [ atleast18, otherageReq, noGEDorDiplomaNeeded, GEDorDiplomaReq, licenseReq, otherReq]
        #print(entry_requirements)
        return entry_requirements
        

    def grab_data(self, browser):
        program_list = []
        all_program_data = []
        #return selenium elements associated with each drop down in the accordian
        expanded_list = self.expand_accordian(browser)
        
        i = 0
        for e in expanded_list:
            i+=1
            
            #Get parent link to grab name of program
            program = e.find_element_by_xpath("..")
            program_name = program.text
            
            #One program is not listed as the parent element, but instead as the sibling      
            if program_name != '':
                program_list.append(program_name)
            else:
                program = e.find_element_by_xpath("../following-sibling::a")
                program_name = program.text
                program_list.append(program_name)
            
            program_description = e.find_element_by_xpath("../following-sibling::div").text
            description_list= program_description.splitlines()
            
            #Who do they serve?
            focus_groups = self.find_who_they_serve(program_name, program_description, description_list, len(expanded_list))
            youth = focus_groups[0]
            women = focus_groups[1]
            general = focus_groups[2]
            veteran = focus_groups[3]
            lowincome = focus_groups[4]
            Individual_Served_first = focus_groups[5]
            
            certs_offered = self.find_certifaction_offered(program_name, program_description, description_list)
            osha10 = certs_offered[0]
            firstaid = certs_offered[1]
            forklift = certs_offered[2]
            flagging = certs_offered[3]
            hazwoper = certs_offered[4]
            
            website = self.find_website(program_name, description_list)
            
            #Where is it?
            location_info = self.get_location(program_name, program_description, description_list)
            
            #Entry Reqs
            entry_reqs = self.find_entry_requirements(program_name, program_description, description_list)
            atleast18 = entry_reqs[0]
            otherageReq = entry_reqs[1]
            noGEDorDiplomaNeeded = entry_reqs[2]
            GEDorDiplomaReq = entry_reqs[3]
            licenseReq = entry_reqs[4] 
            otherReq = entry_reqs[5] 
            
            program_data = {'id': i, 'program_name': program_name, 'address': location_info, 'website': website, 'description_list': description_list,  'serve_veteran': veteran,  'serve_lowincome': lowincome,   'program_description': program_description, 'type': 'PreApprenticeship', 'serve_youth': youth, 'serve_women': women,  'serve_general': general, 'cert_osha10or11': osha10,  'cert_firstaid': firstaid, 'cert_forklift': forklift, 'cert_flagging': flagging,  'cert_hazwoper': hazwoper, 'req_atLeast18': atleast18, 'req_otherAge': otherageReq, 'req_noGEDorDiplomaNeeded': noGEDorDiplomaNeeded, 'req_GEDorDiploma': GEDorDiplomaReq, 'req_driversLicense': licenseReq, 'req_other': otherReq, 'Individual_Served_first': Individual_Served_first}
            all_program_data.append(program_data)
        
        return all_program_data
        
        
        




##Open Intial Website with Selenium and Chrome, you will need to upate this and get appropriate Linux versions for Ec2
#ubuntu = True
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
#    url = "http://www.lni.wa.gov/TradesLicensing/Apprenticeship/About/IntroProg/"
#    browser.get(url)
#    browser.implicitly_wait(10)
#    
#    #Call the HTML Scraper
#    preapprenticeLIResult = WALaborandIndustriesPreApprenticeship()
#    resultsLI = preapprenticeLIResult.grab_data(browser)
#    df_preapprentice = pd.DataFrame.from_records(resultsLI)
#    df_preapprentice.to_csv('WALaborIndustries_PreApprenticeship.csv')
#    print(df_preapprentice['website'])
#    browser.close()
#
#else:
#    #If windows use the following
#    path_to_chromedriver = r"C:\AWSRTC\chromedriver_win32_233\chromedriver.exe"
#    browser = webdriver.Chrome(executable_path = path_to_chromedriver )
#    url = "http://www.lni.wa.gov/TradesLicensing/Apprenticeship/About/IntroProg/"
#    browser.get(url)
#    browser.implicitly_wait(10)
#    
#    #Call the HTML Scraper
#    preapprenticeLIResult = WALaborandIndustriesPreApprenticeship()
#    resultsLI = preapprenticeLIResult.grab_data(browser)
#    df_preapprentice = pd.DataFrame.from_records(resultsLI)
#    df_preapprentice.to_csv('WALaborIndustries_PreApprenticeship.csv')
#    print(df_preapprentice['website'])
#    browser.close()
