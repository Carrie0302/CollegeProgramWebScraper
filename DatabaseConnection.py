# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 10:15:47 2018

@author: carrie
"""

from sqlalchemy import create_engine
import pandas as pd



class DBConnection:
    
    def engine(self):
        
        # Connect to the database                             
        DB_URI = "mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db}"
        
        engine = create_engine(DB_URI.format(
            user = 'fill in',
            password = 'fill in' ,
            host =  'fill in', 
            port = 3306,
            db = 'fill in' ),
            connect_args = {'time_zone': '+00:00'}
          )
          
        return engine
