from http import client
from typing import Final
from unittest.util import strclass
from gridfs import Database
from nbformat import write
import streamlit as st
import pandas as pd
from pandas import DataFrame
import numpy as np
#import pymongo
#from pymongo import MongoClient
import csv

st.set_page_config(
    layout="wide"
)
#heroku config:set MONGODB_URI="mongodb+srv://jorgecantu33:cantu33@cistus.qmxcz.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = MongoClient("mongodb+srv://jorgecantu33:cantu33@cistus.qmxcz.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
database = client["Database"]
db1 = database["Apartment Information"]
db2 = database["Machine Learning Output"]

cursor1 = db1.find()
cursor2 = db2.find()

db_list1 = list(cursor1)
db_list2 = list(cursor2)
    
df_1 = pd.DataFrame(db_list1)
df_2 = pd.DataFrame(db_list2)

del df_1['_id']
del df_2['_id']

u = df_1.select_dtypes(object)
df_1[u.columns] = u.apply(
    lambda x: x.str.encode('ascii', 'ignore').str.decode('ascii'))

u = df_2.select_dtypes(object)
df_2[u.columns] = u.apply(
    lambda x: x.str.encode('ascii', 'ignore').str.decode('ascii'))

st.write("""
# Assessment Realtors
##### Welcome, we are AssessmentRealtors.com 
To begin please answer the questions on the sidebar located on the left side of the screen and set your aparment specifications.
Or type the name of a specific apartment in the serch bar below.
""")

st.markdown("---")

st.sidebar.header('Apartment Specifications')

Cost = str(st.sidebar.number_input (
    "Enter the max Monthly Rent:", min_value=0, max_value=2000, step=50
))

NumberofBedRooms = str(st.sidebar.selectbox(
    "Enter your desired number of Bedrooms and Bathrooms:", ("1", "2", "3", "4")
))

Distance = float(st.sidebar.selectbox(
    "How far away would you like to live(In miles):", ("2.5", "5", "7.5", "10", "12.5", "15")
))

#df_1 = pd.read_csv(r"C:\Users\Jorge Cantu\Downloads\SampleUpdated.csv",encoding='latin1')

#df_2 = pd.read_csv(r"C:\Users\Jorge Cantu\Downloads\ML_Output.csv",encoding='latin1')

df_3 = pd.merge(df_1, df_2, left_on='Name', right_on='Name', how='left')

Final = df_3[df_3['Monthly Rent'] <= Cost]

Final = Final[Final['Number of Bedrooms'] <= NumberofBedRooms]

Final = Final[Final['Distance to Texas A&M University (miles)'].astype(float) <= Distance]

Final = Final.sort_values(by=['Average Review Score'],ascending=False)

apartment_search = st.text_input("Enter the name of a apartment:", "")

if apartment_search:
    Monthly_Rent = int(df_3.loc[df_3["Name"] == apartment_search, "Monthly Rent"])

    DistanceToCampus = float(df_3.loc[df_3["Name"] == apartment_search, "Distance to Texas A&M University (miles)"])

    Address = df_3.loc[df_3["Name"].str.contains(apartment_search), "Location"].item()

    AverageReviewScore = DistanceToCampus = float(df_3.loc[df_3["Name"] == apartment_search, "Average Review Score"])

    st.write(f'The Apartment you have Chosen is: {apartment_search}.')
    st.write(f'The Monthly Rent is ${Monthly_Rent} for {NumberofBedRooms} bathrooms and {NumberofBedRooms} bedrooms.')
    st.write(f'The location of the apartment is {Address}, which is {DistanceToCampus} miles away from Texas A&M University.')
    st.write(F'The Average Review Score for {apartment_search} is {AverageReviewScore} on a scale from 1 to 10.')

st.markdown("---")

if Final.empty:
    st.write('Nothing has been selected or there are no apartments that fall under those constraints.')

else:
    st.dataframe(Final)

    st.markdown("---")

    dropdown = st.selectbox('Pick your Apartment from the list above', Final["Name"])

    Monthly_Rent = int(Final.loc[Final["Name"] == dropdown, "Monthly Rent"])

    DistanceToCampus = float(Final.loc[Final["Name"] == dropdown, "Distance to Texas A&M University (miles)"])

    Address = Final.loc[Final["Name"].str.contains(dropdown), "Location"].item()

    AverageReviewScore = DistanceToCampus = float(Final.loc[Final["Name"] == dropdown, "Average Review Score"])

    st.write(f'The Apartment you have Chosen is: {dropdown}.')
    st.write(f'The Monthly Rent is ${Monthly_Rent} for {NumberofBedRooms} bathrooms and {NumberofBedRooms} bedrooms.')
    st.write(f'The location of the apartment is {Address}, which is {DistanceToCampus} miles away from Texas A&M University.')
    st.write(F'The Average Review Score for {dropdown} is {AverageReviewScore} on a scale from 1 to 10.')



