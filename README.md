Project: Automated Web Scraping College Apprenticeship and Occupation Data
Written by Carrie Schaden
Jan, 2018

## Project Background
This project includes web scrapers that pull publicly available information about apprentice and college programs from a variety of government and college websites.  The program then identifies the related occupation code for each school and apprentice program and pushes that data to a database

# Codebase
The program is built in Python 3.5.  Some of the web scrapers use Selenium and chromedriver to interact with javascript based website filters and buttons. Some of the web scrpaers just use requests and BeutifulSoup to make simpler calls to download spreadsheets hosted on government websites.  Data coming from the different webscrapers is matched between different the sources to identify the occupation associated with each program and then filtered to select only contstruciton related occupations and programs.  Projects are geocoded using Google Map's Place API, which converts the user-inputted address into the various location fields. 

## Process to match Program Data to the Labor and Industries list:
First we check the L & I website for any construction related programs that are active. Soc codes are in the L & I data. Nonactive programs are excluded from the list. Then we match the L & I programs to Career Bridge to grab additional contextual data like program length, description, and more.

## Process to tag SOC Codes to the College Programs:
First the scraper checks the “Performance Results” Tab for the school and follow the “View statewide earnings and employment trends for jobs related to programs of this type.” link to get the occupations related to the program.  The occupations names are matched to a SOC Lookup Table to match the SOC code to the occupations listed. Then for the remaining unmatched programs we run the programs through a key word list to SOC lookup.

