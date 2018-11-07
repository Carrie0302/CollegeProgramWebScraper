# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 09:22:41 2017
Career Bridge Scraper Class, will pull data based on apprenticeship or tech program when called and it can pull occupation info and location info per program type
@author: carrie
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time, requests, datetime, json, os
import pandas as pd
from bs4 import BeautifulSoup
import urllib.request
from pyvirtualdisplay import Display

key = 'fill in'


class CareerBridge:
    '''Career Bridge object is a web scraper that pulls info from the apprenticeship or technical college programs and can also pull occupation and location information'''
    
    def __init__(self, type="technicalCollege"):
        """Return a Scraper object based on the type of information wanted; Options include technicalCollege and apprenticeship"""
        self.type = type
        self.college_links = []
        
 
    def get_type(self):
      return self.type
      
    
    #Iterate through the school names and get the program list for each with the output as a list of hyperlinks
    def href_per_school(self, browser):
        #Select Dropdown with Education Type
        if self.type == "technicalCollege":
            techResults_all = []
            #browser.find_element_by_xpath('//*[@name="ctl00$ContentPlaceHolder1$cboProviderType"]/option[contains(text(), "Public Community and Technical Colleges")]').click()
            
            #Select Particular School for the Tech colleges since there are more than 500 results
            school_names = ['Perry Technical Institute - Yakima, WA...',  'Bates Technical College - Tacoma, WA...',	'Bellevue College - Bellevue, WA...',	'Bellingham Technical College - Bellingha...',	'Big Bend Community College - Moses Lake,...',	'Cascadia College - Bothell, WA...',	'Centralia College - Centralia, WA...',	'Clark College - Vancouver, WA...',	'Clover Park Technical College - Lakewood...',	'Columbia Basin College - Pasco, WA...',	'Edmonds Community College - Lynnwood, WA...',	'Everett Community College - Everett, WA...',	'Grays Harbor College - Aberdeen, WA...',	'Green River College - Auburn, WA...',	'Highline College - Des Moines, WA...',	'Lake Washington Institute of Technology ...',	'Lower Columbia College - Longview, WA...',	'North Seattle College - Seattle, WA...',	'Olympic College - Bremerton, WA...',	'Peninsula College - Port Angeles, WA...',	'Pierce College - Lakewood, WA...',		'Renton Technical College - Renton, WA...',	'Seattle Central College - Seattle, WA...',	'Shoreline Community College - Shoreline,...',	'Skagit Valley College - Mount Vernon, WA...',	'South Puget Sound Community College - Ol...',	'South Seattle College - Seattle, WA...',	'Spokane Community College - Spokane, WA...',	'Spokane Falls Community College - Spokan...',	'Tacoma Community College - Tacoma, WA...',	'Walla Walla Community College - Walla Wa...',	'Wenatchee Valley College - Wenatchee, WA...',	'Whatcom Community College - Bellingham, ...',	'Yakima Valley Community College - Yakima...' , "Flagger Training at It's Best - Roy, WA...",   'GMC Training Institute - Grandview, WA...',   'Inside Out Inspection Services - Seattle...',   'Kyron Environmental, Inc. - Spokane, WA...',   "Let's Work Together, LLC - Bremerton, WA...",  'Martinez Technical Institute - Pasco, WA...',   'N.A.R.I.E.S.  - Edmonds, WA...',   'Northwest Energy Efficiency Council/Ever...',   'Pacific Northwest OSHA Education Center/...',   'Puget Sound OIC - Renton, WA...',   'Statewide Forklift Certification - Lakew...',   'T Enterprises, Inc. - Pasco, WA...',   'TERO Vocational Training Center - Tulali...',   'Thrive Industries LLC - Zillah, WA...',   'West Coast Training - Woodland, WA...',   'Central Washington University/Des Moines...',   'Central Washington University/Ellensburg...',   'Central Washington University/Everett - ...',   'Central Washington University/Lynnwood  ...',   'Central Washington University/Moses Lake...',   'Central Washington University/Pierce Cou...',   'Central Washington University/Wenatchee ...',   'Central Washington University/Yakima - Y...',   'Charter College/Yakima - Yakima, WA...',   'City University of Seattle - Seattle, WA...',   'Clark College Economic and Community Dev...',   'Eastern Washington University - Cheney, ...',   'Heavy Equipment College of Washington - ...',   'Northwest University - Kirkland, WA...',   'Pacific Lutheran University/Continuing E...',   'Pacific Lutheran University/School of Ed...',   'Pacific Lutheran University/School of Nu...',   'Saybrook University - Bellevue, WA...',   'Seattle University - Seattle, WA...',   'Seattle Vocational Institute - Seattle, ...',   "St. Martin's University/Fort Lewis - Lac...",  'Trinity Western University Bellingham - ...',   'University of Washington - Seattle, WA...',   'University of Washington Professional an...',   'University of Washington Tacoma - Tacoma...',   'University of Washington/Bothell - Bothe...',   'University of Washington/Tacoma - Profes...',   'Washington State University - Pullman, W...',   'Western Governors University (WGU) Washi...',   'Western Washington University/Bellingham...',   'Western Washington University/Everett - ...',   'Western Washington University/Kitsap - B...',   'Western Washington University/North Seat...',   'Western Washington University/Peninsula ...',   'Anvil Welding Instruction - Spokane, WA...',   'OXARC School of Welding/Pasco - Pasco, W...',   'OXARC School of Welding/Spokane - Spokan...']

            for s in school_names:
                browser.find_element_by_xpath('//*[@name="ctl00$ContentPlaceHolder1$cboProviderName"]/option[contains(text(), "'+ s +'")]').click()
                browser.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_btnSearch"]').click()
                time.sleep(3)
                print("Wait 4 seconds per school")
            
                #Select Drop Down All to Return All Results
                browser.find_element_by_xpath('//*[@name="ctl00$ContentPlaceHolder1$cboPageSize"]/option[contains(text(), "All")]').click()
                time.sleep(1)
                #print("Wait 2 seconds")
                hyperlinks = browser.find_elements_by_css_selector("div.boxinside a")
                techResults = self.find_intial_links(hyperlinks)
                techResults_all.extend(techResults)
            self.college_links = techResults_all
            return techResults_all
            
            
    def href_apprenticeship(self, browser):
        #We Only need to select all for apprenticeship programs since there are under 500 programs
        if self.type == "apprenticeship":
            try:
                browser.find_element_by_xpath('//*[@name="ctl00$ContentPlaceHolder1$cboPageSize"]/option[contains(text(), "All")]').click()
                time.sleep(4)
                print("Wait 4 seconds after select")
                hyperlinks = browser.find_elements_by_css_selector("div.boxinside a")
                techResults = self.find_intial_links(hyperlinks)
            except:
                log = open("Error_Data.txt","a")
                log.write("CareerBridgeClass.py Apprenticeship Data: Error Pulling Href Attributes from Main Page \t" + "Date: " + self.get_date() + "\n")
    
            return techResults
        
    #Format the main page links that correlate to each program
    def find_intial_links(self, hyperlinks):
        #Save hyplinks that are not in the header, first five links are for the header
        if len(hyperlinks) > 1:
            result = [{"link": category.get_attribute("href"), "program_name": category.text} for category in hyperlinks][5:]  #[15:22]
        return result
        
        
    #Format Date
    def get_date(self):
        self.now = datetime.datetime.now()
        return self.now.strftime("%Y-%m-%d %H:%M")

        
    #Check the Page Status
    def page_status(self, page, href, program):
        status = page.status_code
        soup = ""
        if status == 200:
            soup = BeautifulSoup(page.text, 'html.parser')
            #print("Downloading...")
            occupations = self.download_statewide_occupation_data(soup, href, program)
            return occupations        
        else:
            print("Page will not load")
            log = open("Error_Data.txt","a")
            log.write("CareerBridgeClass.py: Error on Page Load, Page status is " + "  " + str(status)  + "\t" + "Date: " + self.get_date() + "\n")
    
    
    def iterate_through_occupation_rows(self, row, href, program):
        pages = []
        try:
            i=0
            for r in row:
                i+=1
                col = r.findAll('td')
                career_list = []
                for d in col:
                    career_list.append(d.text.replace('\r\n', ''))
                
                occupation = career_list[0].strip()
                typical_earnings = career_list[1].strip()
                employement_openings_annual = career_list[2].strip()
                career_data = [href, program, occupation, typical_earnings, employement_openings_annual]
                pages.append(career_data)
        
        except:
            career_data = [href, program, "NULL", "NULL", "NULL"]
            pages.append(career_data)
            
        return pages
        
        
    #Download Statewide Occupation Data from Seperate URL based on Program Id
    def download_statewide_occupation_data(self, soup, href, program):
        '''Get the occupations, earnings, and openings per program based on WA State'''
        cleaned_pages = []
        #Some programs will have occupation data available, but others wont    
        try:
            body = soup.find("table", {"id": "ctl00_ContentPlaceHolder1_ctrlOccDetail_grdResults"})
         
            row = body.find_all("tr", {"class": "row"})
            altrow = body.find_all("tr", {"class": "altrow"})
            combine = []
            row_table = self.iterate_through_occupation_rows(row, href, program)
            altrow_table = self.iterate_through_occupation_rows(altrow, href, program)
            combine.extend(row_table)
            combine.extend(altrow_table)
            cleaned_pages.extend(combine)
        except:
            career_data = [href, program, "NULL", "NULL", "NULL"]
            cleaned_pages.append(career_data)
            print("No occupation data available for {0}, {1}".format(href, program))
            
        return cleaned_pages
        
        
    def merge_export_to_csv(self, result, cleaned_pages, name):
            '''Merge data from the links to data from the particular program page and export to csv'''
            try:
                df_links = pd.DataFrame.from_records(result)
                df_data = pd.DataFrame.from_records(cleaned_pages)
                df = pd.merge(df_links, df_data, on='link')
                df.to_csv(name)
                print("Merge and Export Program Details")
                
            except:
                print("Merge and Export for Programs Does Not Work")
                log = open("Error_Data.txt","a")
                log.write("CareerBridgeClass.py College Programs: Error with Merge and Export for College Programs \t" + "Date: " + self.get_date() + "\n")
            
            return df
            

    def export_career_data_to_csv(self, result, name):
            '''Iterate through the programs and pull every occupation into a dataframe for export to csv'''
            list = []
            try:
                for r in result:
                    for l in r:
                        career_data = { 'program_id': int(l[0]), 'program': l[1], 'occupation': l[2], 'typical_earnings': l[3], 'employement_openings_annual': l[4]}
                        list.append(career_data)            
                
                df = pd.DataFrame.from_records(list)
                df.to_csv(name)
                print("Export Occupation Details")
                
            except:
                print("Export for College Occupations Does Not Work")
                log = open("Error_Data.txt","a")
                log.write("CareerBridgeClass.py College Programs: Error with Export for College Occupations \t" + "Date: " + self.get_date() + "\n")
            
            return df
            
            
    #Get the address
    def get_locations(self, browser):
        #find all the Map links and grab the href
        address = ''
        href_list = []
        location = browser.find_elements_by_xpath("//*[contains(text(), 'view map')]")
        for l in location:
            href = l.get_attribute('href')
            href_list.append(href)
            address = urllib.request.unquote(href).split("q=")[1].replace('+', ' ')   
        #print("Locations")
        #print(address)
        #lat, lng, place_id = self.geocode_google(address)
        return address
        
        
    #Geocode the first 250 addresses
    def geocode_google(self, address):
        google_url = "https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}".format(address, key)
        response_geocode = requests.get(google_url).json()

        lat,lng,place_id = 0,0,"None"
        #print(response_geocode)
        
        #if results were returned take the first one
        if len(response_geocode['results']) > 0:
            r = response_geocode['results'][0]
        
            lat = r[u'geometry'][u'location'][u'lat']
            lng = r[u'geometry'][u'location'][u'lng']
            place_id = r[u'place_id']
            #print(lat, lng, place_id)
        
        return lat, lng, place_id
        
        
        
    #Details on Specific Technical College Programs 
    def download_tech_college_programs(self, result, browser):
        '''This pull the majority of the program data for the technical colleges including: award type, school aname, etp, hours, fees, tuition, website, and contact info.  This also kicks off the call to the occupation data scrapper.'''
        
        #if results are returned and the link does not contain javascript then open links in new tab
        i = 0
        cleaned_pages = []
        occupation_pages = []
        
        print("Number of program results: {0}".format( len(result)) ) 
        try:
            for r in result: #[25:45]: #[185:188]:
                if "javascript:" not in r['link']:
                    
                    #Open new tab with the hyperlink, these commands change on different OS
                    if not r['link']:
                        print("no link")
                    else:
                        i+=1
                        browser.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't') 
                        browser.get(r['link'])
                        
                        #Web Scrap the new pages per program
                        #Clean the header
                        header = browser.find_elements_by_css_selector("h2")
                        head = [h.text for h in header][0]
                        clean_head = head.splitlines()
        
                        
                        #Clean the first Program Details Page
                        program = browser.find_elements_by_css_selector("div#ctl00_ContentPlaceHolder1_pnlProgramDetails tr")
                        prog = [p.text for p in program]
                        len_text = len(prog)
    
                        
                        #The cntfld variable is added to when a field does not exist
                        #The cntfld will be subtracted from the search of the remaining fields, essentially the search space grows smaller with each missing field
                        cntfld = 0
                        program = ""
                        award_type = ""
                        school_name = ""
                        etp = prog[1].splitlines()[1]
                        website = ""
                        contact = []
                        description = ""
                        tuition=""
                        tuition_per_credit = ""
                        total_tuition= ""
                        fees = ""
                        books_material_costs= ""
                        other_costs = ""
                        location = ""
                        length_of_training = ""
                        award_type2 = ""
                        credit = ""
                        clock_hours = ""
                        evenings_weekends = ""
                        online = ""
                        accreditation = ""
                        license_req_to_work = ""
                        license_from_program  = ""
                        license_test_prep =""
                        entrance_req = ""
                        credit_hours =""
                        
                        #Check the header
                        program = clean_head[0]                
                        if 'Award type:' in clean_head[1]:
                            award_type = clean_head[1].replace("Award type: ", "")
                            school_name = clean_head[2]
                        else:
                            school_name = clean_head[1]
                            
                        #Check for variable name first if it does not exist reduce the search space by 1
                        if prog[3].splitlines()[0] == "Program website":
                            website = prog[3].splitlines()[1]
                        else:
                            cntfld += 1 
                        if prog[4 - cntfld].splitlines()[0] == "Program contact":
                            contact = prog[4 - cntfld].splitlines()[1:]
                        else:
                            cntfld += 1
                        if prog[5 - cntfld].splitlines()[0] == "Program description":
                            try: 
                                description = prog[5 - cntfld].splitlines()[1:][0]
                                description.replace("Â“CÂ”", "'")
                                description.replace("”", '"')
                                description.replace("“", '"')
                                description.replace("’", "'")
                                #print(description)
                                
                            except:
                                description = ""
                        else:
                            cntfld += 1
                            
                        #Section Financial Infromation.  
                        # This part gets messy, lot of different possible combinations for how they present data across programs
                        if prog[6 - cntfld] == "Financial Information":
                            c = 0
                        else:
                            cntfld += 1
                        
                        if prog[7 - cntfld].splitlines()[0] == 'Tuition':
                            tuition = prog[7 - cntfld].splitlines()[1]
                        elif prog[7 - cntfld].splitlines()[0] == 'Tuition per credit':
                            tuition_per_credit = prog[7 - cntfld].splitlines()[1]
                        elif prog[7 - cntfld].splitlines()[0] == 'Total program tuition':
                            total_tuition = prog[7 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1
                            
                        if prog[8 - cntfld].splitlines()[0] == 'Total program tuition':
                            total_tuition = prog[8 - cntfld].splitlines()[1]
                        elif prog[8 - cntfld].splitlines()[0] == 'Tuition per credit':
                            tuition_per_credit = prog[8 - cntfld].splitlines()[1]
                        elif prog[8 - cntfld].splitlines()[0] == 'Fees':
                            fees = prog[8 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1
                            
                        if prog[9 - cntfld].splitlines()[0] == 'Books and materials':
                            books_material_costs = prog[9 - cntfld].splitlines()[1]
                        elif prog[9 - cntfld].splitlines()[0] == 'Total program tuition':
                            total_tuition = prog[9 - cntfld].splitlines()[1]
                        elif prog[9 - cntfld].splitlines()[0] == 'Fees':
                            fees = prog[9 - cntfld].splitlines()[1]
                        elif prog[9 - cntfld].splitlines()[0] == 'Other costs':
                            other_costs = prog[9 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1
                        
                        if prog[10 - cntfld].splitlines()[0] == 'Books and materials':
                            books_material_costs = prog[10 - cntfld].splitlines()[1]
                        elif prog[10 - cntfld].splitlines()[0] == 'Fees':
                            fees = prog[10 - cntfld].splitlines()[1]
                        elif prog[10 - cntfld].splitlines()[0] == 'Other costs':
                            other_costs = prog[10 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1
                            
                        if prog[11 - cntfld].splitlines()[0] == 'Books and materials':
                            books_material_costs = prog[11 - cntfld].splitlines()[1]
                        elif prog[11 - cntfld].splitlines()[0] == 'Fees':
                            fees = prog[11 - cntfld].splitlines()[1]
                        elif prog[11 - cntfld].splitlines()[0] == 'Other costs':
                            other_costs = prog[11 - cntfld].splitlines()[1]
                        elif prog[11 - cntfld].splitlines()[0] == 'Supplies, tools, uniform':
                            supplies_costs = prog[11 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1
        
              
                        if prog[12 - cntfld].splitlines()[0] == 'Fees':
                            fees = prog[12 - cntfld].splitlines()[1]
                        elif prog[12 - cntfld].splitlines()[0] == 'Other costs':
                            other_costs = prog[12 - cntfld].splitlines()[1]
                        elif prog[12 - cntfld].splitlines()[0] == 'Supplies, tools, uniform':
                            supplies_costs = prog[12 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1
                        
             
                        if prog[13 - cntfld].splitlines()[0] == 'Other costs':
                            other_costs = prog[13 - cntfld].splitlines()[1]
                        elif prog[13 - cntfld].splitlines()[0] == 'Supplies, tools, uniform':
                            supplies_costs = prog[13 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1
                        
                        #Section program Information
                        #print(13 - cntfld)
                        if prog[15 - cntfld].splitlines()[0] == 'Length of training':
                            length_of_training = prog[15 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1                
                        #print(length_of_training)
                        
                        if prog[16 - cntfld].splitlines()[0] == 'Award type':
                            award_type2 = prog[16 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1
           
                        if prog[17 - cntfld].splitlines()[0] == 'Credits':
                            credit = prog[17 - cntfld].splitlines()[1]
                        elif prog[17 - cntfld].splitlines()[0] == 'Credit hours':
                            credit_hours = prog[17 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1
                            
                        if prog[18 - cntfld].splitlines()[0] == 'Clock hours':
                            clock_hours = prog[18 - cntfld].splitlines()[1]
                        elif prog[18 - cntfld].splitlines()[0] == 'Credit hours':
                            credit_hours = prog[18 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1
                        
                        if prog[19 - cntfld].splitlines()[0] == 'Credit hours':
                            credit_hours = prog[19 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1
                            
                        if 'Locations offered' in  prog[20 - cntfld]:
                            location = "yes"
                        else:
                            cntfld += 1
                        
                        if prog[21 - cntfld].splitlines()[0] == 'Offered evenings/weekends':
                            evenings_weekends = prog[21 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1
                  
                        if 'Offered online' in prog[22 - cntfld]:
                            online = prog[22 - cntfld].replace("Offered online" , "")
                        else:
                            cntfld += 1
                        
                        if prog[23 - cntfld].splitlines()[0] == 'Entrance requirements':
                            entrance_req = prog[23 - cntfld].splitlines()[1]
                            entrance_req.replace("Â“CÂ”", "'")
                            entrance_req.replace("”", '"')
                            entrance_req.replace("“", '"')
                            entrance_req.replace("’", "'")
                        else:
                            cntfld += 1
                            
                        if prog[24 - cntfld].splitlines()[0] == 'Certification/license required to work in this field':
                            license_req_to_work = prog[24 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1
                            
                        if prog[25 - cntfld].splitlines()[0] == 'Certification/license obtained as part of training program':
                            license_from_program = prog[25 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1
                        
                        if prog[26 - cntfld].splitlines()[0] == 'Certification/license test preparation provided':
                            license_test_prep = prog[26 - cntfld].splitlines()[1]
                        else:
                            cntfld += 1
                            
                        program_id = int(r['link'].replace('http://www.careerbridge.wa.gov/Detail_Program.aspx?program=', ''))
                        
                        
                        #Get location data from the program detail page
                        address = "None"
                        address = self.get_locations(browser)
                        
                        #Add data from page to df  
                        page_data = { 'location': location, 'link': r['link'], 'program_id': program_id, 'program': program, 'award_type': award_type, 'school_name': school_name, 'etp': etp, 'website': website, 'contact': contact, 'description': description, 'tuition': tuition, 'tuition_per_credit':tuition_per_credit, 'total_tuition':total_tuition, 'fees':fees, 'books_material_costs':books_material_costs, 'other_costs': other_costs, 'cntfld': cntfld, 'len_text': len_text, 'length_of_training': length_of_training, 'credits': credit, 'evenings_weekends': evenings_weekends, 'online_courses': online,  'clock_hours': clock_hours, 'license_req_to_work': license_req_to_work, 'license_from_program':license_from_program, 'license_test_prep': license_test_prep, 'entrance_req': entrance_req, 'address': address}
                        cleaned_pages.append(page_data)
                        
                        
                        #Request data with typical occupations per program 
                        href = r['link'].replace('http://www.careerbridge.wa.gov/Detail_Program.aspx?program=', '')
                        occupationurl = 'http://www.careerbridge.wa.gov/Detail_OccupationDetails.aspx?pid={0}'.format(href)
                        page = requests.get(occupationurl)
                        occupations = self.page_status(page, href, program)
                        occupation_pages.append(occupations)
                        
                        #Close the tab
                        browser.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'w')
            
        except ValueError:
            print("Value Error During College Program Scraping")
            log = open("Error_Data.txt","a")
            log.write("CareerBridgeClass.py College Programs: Value Error Grabing Data from College Program Pages \t" + "Date: " + self.get_date() + "\n")

        except OSError:
            print("OSError During College Program Scraping")
            log = open("Error_Data.txt","a")
            log.write("CareerBridgeClass.py College Programs: Operating System Error When Grabing Data from College Program Pages \t" + "Date: " + self.get_date() + "\n")
        
        except SystemExit:
            print("SystemExit During College Program Scraping")
            log = open("Error_Data.txt","a")
            log.write("CareerBridgeClass.py College Programs: System Exited Unexpectedly When Grabing Data from College Program Pages \t" + "Date: " + self.get_date() + "\n")
        
        except:
            print("General Error During College Program Scraping")
            log = open("Error_Data.txt","a")
            log.write("CareerBridgeClass.py College Programs: Error When Grabing Data from College Program Pages \t" + "Date: " + self.get_date() + "\n")
            
            
        try:  
            df_cleaned_pages = pd.DataFrame(cleaned_pages)
            df_occupation_pages= pd.DataFrame(occupation_pages)
            
            dir_path = os.path.dirname(os.path.realpath(__file__))
            careerBridgeClass_cleaned_pages = os.path.join(os.path.sep, dir_path, 'temp_data','CareerBridgeClass_cleaned_pages.csv')
            careerBridgeClass_occupation_pages = os.path.join(os.path.sep, dir_path, 'temp_data','CareerBridgeClass_occupation_pages.csv')
            
            df_cleaned_pages.to_csv(careerBridgeClass_cleaned_pages)
            df_occupation_pages.to_csv(careerBridgeClass_occupation_pages)
        except:
            print("Can no save temp lists into Dataframes")
            
        return cleaned_pages, occupation_pages
      
      
    #Details on Specific Apprenticeship Programs
    def download_apprenticeship_data(self, result, browser):
        '''This pull the additional apprenticeship data beyond whay is available through L&I including:  hours, fees, tuition, website, contact info, and more.  This also kicks off the call to the occupation data scrapper.'''

        #if results are returned and the link does not contain javascript then open links in new tab
        cleaned_pages = []
        print("Number of Programs {0}".format(len(result)))
        
        for r in result:
            if "javascript:" not in r['link']:
                #print( r['link'] )
                
                #Open new tab with the hyperlink, these commands change on different OS
                if not r['link']:
                    print("no link")
                else:
                   
                    browser.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 't') 
                    browser.get(r['link'])
                    
                    #Web Scrap the new pages per program
                    
                    #Clean the header
                    header = browser.find_elements_by_css_selector("h2")
                    head = [h.text for h in header][0]
                    clean_head = head.splitlines()
    
                    
                    #Clean the first Program Details Page
                    program = browser.find_elements_by_css_selector("div#ctl00_ContentPlaceHolder1_pnlProgramDetails tr")
                    prog = [p.text for p in program]
                    #print(prog)
                    len_text = len(prog)
                    print("Text Length : {0}".format(len_text))
                    
                    #The cntfld variable is added to when a field does not exist
                    #The cntfld will be subtracted from the search of the remaining fields, essentially the search space grows smaller with each missing field
                    cntfld = 0
                    
                    etp = prog[1].splitlines()[1]
                    website = ""
                    contact = []
                    description = ""
                    tuition=""
                    pay = ""
                    total_tuition= ""
                    training_length = ""
                    credit=""
                    clock_hours =""
                    credit_hours=""
                    evenings_weekends = ""
                    online = ""
                    entrance_req = ""
                    
                    #Check for variable name first if it does not exist reduce the search space by 1
                    if prog[3].splitlines()[0] == "Program website":
                        website = prog[3].splitlines()[1]
                    else:
                        cntfld += 1
                        
                    if prog[4 - cntfld].splitlines()[0] == "Program contact":
                        contact = prog[4 - cntfld].splitlines()[1:]
                    else:
                        cntfld += 1
                        
                    if prog[5 - cntfld].splitlines()[0] == "Program description":
                        #description = prog[5 - cntfld].splitlines()[1:][0]
                        
                        try: 
                                description = prog[5 - cntfld].splitlines()[1:][0]
                                description.replace("Â“CÂ”", "'")
                                description.replace("”", '"')
                                description.replace("“", '"')
                                description.replace("’", "'")
                                #print(description)
                                
                        except:
                                description = ""
                    else:
                        cntfld += 1
                    
                    if prog[7 - cntfld].splitlines()[0] == 'Tuition':
                        tuition = prog[7 - cntfld].splitlines()[1]
                    else:
                        cntfld += 1
                        
                    if prog[8 - cntfld].splitlines()[0] == 'Journey level pay':
                        pay = prog[8 - cntfld].splitlines()[1]
                    elif prog[8 - cntfld].splitlines()[0] == 'Total program tuition':
                        total_tuition = prog[8 - cntfld].splitlines()[1]
                    else:
                        cntfld += 1
    
    
    
                    if prog[10 - cntfld].splitlines()[0] == 'Length of training':
                        training_length = prog[10 - cntfld].splitlines()[1]
                    else:
                        cntfld += 1    
    
                    if prog[12 - cntfld].splitlines()[0] == 'Credits':
                        credit = prog[12 - cntfld].splitlines()[1]
                    elif prog[12 - cntfld].splitlines()[0] == 'Clock hours':
                        clock_hours = prog[12 - cntfld].splitlines()[1]
                    else:
                        cntfld += 1
                    
                    if prog[13 - cntfld].splitlines()[0] == 'Credit hours':
                        credit_hours = prog[13 - cntfld].splitlines()[1]
                    else:
                        cntfld += 1
                        
                    if prog[15 - cntfld].splitlines()[0] == 'Offered evenings/weekends':
                        evenings_weekends = prog[15 - cntfld].splitlines()[1]
                    else:
                        cntfld += 1
                        
                    #print("Offered Onlin: {0}".format(16 - cntfld))
                    if 'Offered online' in prog[16 - cntfld]:
                        online = prog[16 - cntfld].replace("Offered online" , "")
                    else:
                        cntfld += 1
                    
                    if prog[17 - cntfld].splitlines()[0] == 'Entrance requirements':
                        entrance_req = prog[17 - cntfld].splitlines()[1]
                        entrance_req.replace("Â“CÂ”", "'")
                        entrance_req.replace("”", '"')
                        entrance_req.replace("“", '"')
                        entrance_req.replace("’", "'")
                        
                        
                    else:
                        cntfld += 1
                        
                        
                        
                    if prog[18 - cntfld].splitlines()[0] == 'Certification/license required to work in this field':
                        license_req_to_work = prog[18 - cntfld].splitlines()[1]
                    else:
                        cntfld += 1
                        
                    if prog[19 - cntfld].splitlines()[0] == 'Certification/license obtained as part of training program':
                        license_from_program = prog[19 - cntfld].splitlines()[1]
                    else:
                        cntfld += 1
                    
                    if prog[20 - cntfld].splitlines()[0] == 'Certification/license test preparation provided':
                        license_test_prep = prog[20 - cntfld].splitlines()[1]
                    else:
                        cntfld += 1
                    
                    #Get location data from the program detail page
                    address = "None"
                    address = self.get_locations(browser)
                    
                    
                    
                    #Add data from page to df
                    page_data = { 'link': r['link'], 'address': address,  'position': clean_head[0], 'award_type': clean_head[1].replace("Award type: ", ""), 'school_name': clean_head[2], 'etp': etp, 'website': website, 'contact': contact, 'description': description, 'tuition': tuition, 'pay': pay, 'total_tuition': total_tuition, 'training_length': training_length, "credit": credit, "credit_hours": credit_hours, "clock_hours": clock_hours, "evenings_weekends": evenings_weekends, "online_courses": online, "entrance_req": entrance_req, "license_req_to_work": license_req_to_work, "license_from_program": license_from_program, "license_test_prep":license_test_prep, "z_Count": cntfld }
                    cleaned_pages.append(page_data)
                    
                    
                #Close the tab
                browser.find_element_by_tag_name('body').send_keys(Keys.COMMAND + 'w')
        
        return cleaned_pages



            
#Main
#Open Intial Website with Selenium and Chrome, you will need to upate this and get appropriate Linux versions for Ec2
#source http://chromedriver.storage.googleapis.com/index.html?path=2.33/

#path_to_chromedriver = r"C:\AWSRTC\chromedriver_win32_233\chromedriver.exe" 
#browser = webdriver.Chrome(executable_path = path_to_chromedriver)
#urlTechCollege = 'http://www.careerbridge.wa.gov/Search_Program.aspx?cmd=txt&adv=true&txt='
#browser.get(urlTechCollege)

##Call the HTML Scrapers
#technicalCollegeResult = CareerBridge()
#technicalCollegeResult.type = "technicalCollege"
#techResults = technicalCollegeResult.href_per_school(browser)
#cleaned_pages, occupation_pages = technicalCollegeResult.download_tech_college_programs(techResults, browser)
#
#
##Concatenate dataframes into final exports for csv
#technicalCollegeResult.merge_export_to_csv(techResults, cleaned_pages,'CareerBridge_CollegePrograms.csv')
#technicalCollegeResult.export_career_data_to_csv(occupation_pages, 'CareerBridge_CollegePrograms_Occupations.csv')




#Apprenticeship
#Open Intial Website with Selenium and Chrome, you will need to upate this and get appropriate Linux versions for Ec2
#path_to_chromedriver = r"C:\AWSRTC\chromedriver_win32_233\chromedriver.exe" 
#browser = webdriver.Chrome(executable_path = path_to_chromedriver)
#urlApprentice = 'http://www.careerbridge.wa.gov/Search_Program.aspx?cmd=saved&gsid=apprenticeship'
#browser.get(urlApprentice)
#
#apprenticeResult = CareerBridge()
#apprenticeResult.type = "apprenticeship"
#apprenticeLinks = apprenticeResult.href_apprenticeship(browser)
#
#cleanedApprenticePages = apprenticeResult.download_apprenticeship_data(apprenticeLinks, browser)
#apprenticeResult.merge_export_to_csv(apprenticeLinks, cleanedApprenticePages,'CareerBridge_ApprenticeshipNEW.csv')
#
#browser.close()