from hashlib import new
from http import client
from tokenize import Name
from typing import Final
from unittest.util import strclass
from wave import _wave_params
from gridfs import Database
from nbformat import write
import streamlit as st
import pandas as pd
from pandas import DataFrame
import numpy as np
import pymongo
from pymongo import MongoClient
import csv
from decouple import config
import altair as alt

st.set_page_config( #Changes the webpage to "Wide" in streamlit
    layout="wide"
)

hide_table_row_index = """ 
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """ #HTTP language that tells the "hide_table_row_index" to return nothing on the tables index

st.markdown(hide_table_row_index, unsafe_allow_html=True) #enables all tables displayed on streamlit to have no index

client = MongoClient(config("MONGOCLIENT")) #Accesses mongoDb database using the config "MONGOCLIENT"
database = client["Database"] #goes into the database folder
db1 = database["Apartment Information"] #goes into the apartment information folder
db2 = database["Machine Learning Output"] #goes into the machine learning output folder

cursor1 = db1.find() #places a cursor for apartment information
cursor2 = db2.find() #places a cursor for machine learning output

db_list1 = list(cursor1) #creates a list for the first cursor
db_list2 = list(cursor2) #creates a list for the second cursor
    
df_1 = pd.DataFrame(db_list1) #creates a dataframe for the first list
df_2 = pd.DataFrame(db_list2) #creates a dataframe for the second list

del df_1['_id'] #deletes the coulum with the Ids in the first dataframe
del df_2['_id'] #deletes the coulum with the Ids in the second dataframe

u = df_1.select_dtypes(object) #chagnes the lanuguae on the coulums to remove any bugs
df_1[u.columns] = u.apply(
    lambda x: x.str.encode('ascii', 'ignore').str.decode('ascii'))

u = df_2.select_dtypes(object) #chagnes the lanuguae on the coulums to remove any bugs
df_2[u.columns] = u.apply(
    lambda x: x.str.encode('ascii', 'ignore').str.decode('ascii'))

st.write("""
# Assessment Realtors
##### Welcome, we are AssessmentRealtors.com 
To begin please answer the questions on the sidebar located on the left side of the screen and set your aparment specifications.
Or type the name of a specific apartment in the serch bar below.
""") #writes a welcome and a few set of instructions for the user

st.markdown("---") #creates a line in the website to separate the welcome message and information from the apartment search

st.sidebar.header('Apartment Specifications') #creates a sidebar on the website with the name apartment specifications

Cost = float(st.sidebar.number_input (
    "Enter the max Monthly Rent:", min_value=0, max_value=2000, step=50
)) #User input for the cost from 0 to 2000 with a step of 50

NumberofBedRooms = str(st.sidebar.selectbox(
    "Enter your desired number of Bedrooms and Bathrooms:", ("1", "2", "3", "4")
)) #User input for the number of bedrooms and bathrooms

Distance = float(st.sidebar.selectbox(
    "How far away would you like to live(In miles):", ("2.5", "5", "7.5", "10", "12.5", "15")
)) #User input for how far away they would like to be from Texas A&M

df_3 = pd.merge(df_1, df_2, left_on='Name', right_on='Name', how='left') #Merges the Apartments Information CSV file and the Machine Learning Output CSV file

Final = df_3[df_3['Monthly Rent'].astype(float) <= Cost] #Creates a new dataframe Final that factors out the unwanted apartments based on the user input desired monthly rent

Final = Final[Final['Number of Bedrooms/Bathrooms'] <= NumberofBedRooms] #Factors out the unwanted apartments based on the user input desired number of bedrooms and bathrooms

Final = Final[Final['Distance to Texas A&M University (miles)'].astype(float) <= Distance] #Factors out the unwanted apartments based on the user input desired distance to Texas A&M

Final = Final.sort_values(by=['Average Review Score'],ascending=False) #Sorts the Final dataframe based on the Average Review Score ascending

apartment_search = st.text_input("Enter the name of a apartment (case sensative):", "") #Creates a search bar for the apartment individual search to work

apartment_name = df_3['Name'].eq(apartment_search).any() #Checks if the input apartment name is in the dataframe contianing everything

if apartment_search == "": #Checks if the apartment search is empty and returns nothing
    st.write('')

elif apartment_name == False: #Checks if the apartment exists in the CSV file and returns a message
    st.write('Apartment does not exist.')

else: #If non of the conditions are met above then it gives the user the searched apartment information
    Monthly_Rent = float(df_3.loc[df_3["Name"] == apartment_search, "Monthly Rent"]) #takes the name and matches it to the monthly rent in the CSV file and places it into a variable

    DistanceToCampus = float(df_3.loc[df_3["Name"] == apartment_search, "Distance to Texas A&M University (miles)"]) #takes the name and matches it to the Distance to Texas A&M in the CSV file and places it into a variable

    Address = df_3.loc[df_3["Name"].str.contains(apartment_search), "Address"].item() #takes the name and matches it to the address in the CSV file and places it into a variable

    AverageReviewScore = float(df_3.loc[df_3["Name"] == apartment_search, "Average Review Score"]) #takes the name and matches it to the average review score in the CSV file and places it into a variable

    AverageReviewScore = str(round(AverageReviewScore, 2)) #rounds the average review score to 2 decimal places

    Pros = df_3.loc[df_3["Name"].str.contains(apartment_search), "Pro"].item() #grabs the list of pros and matches them to the apartmnet selected
    Pros = Pros.split(",") #splits the list of pros with commas

    Cons = df_3.loc[df_3["Name"].str.contains(apartment_search), "Con"].item() #grabs the list of cons and matches them to the apartmnet selected
    Cons = Cons.split(",") #splits the list of pros with commas

    data = {'Pros':[Pros],'Cons': [Cons]} #creates a table with the pros and cons and titales them respectivly
    PCTable = pd.DataFrame(data) #creates a varibale named PCTable and equals it to the data dataframe trough pandas
    PCTable = PCTable.explode(['Pros','Cons']) #changes the table from a 2x2 to a dataframe with how ever many cons and pros by 2 so #ofprosandconsx2

    st.write(f'The Apartment you have Chosen is: {apartment_search}.') #outputs a message to the user containing the selected apartment
    st.write(f'The Monthly Rent is ${Monthly_Rent} for {NumberofBedRooms} bathrooms and {NumberofBedRooms} bedrooms.') #outputs a message to the user containing the monthly rent and the number of bedrooms and bathrooms
    st.write(f'The location of the apartment is {Address}, which is {DistanceToCampus} miles away from Texas A&M University.') #outputs a message to the user containing the address and the distance to TexasA&M
    st.write(F'The Average Review Score for {apartment_search} is {AverageReviewScore} on a scale from 1 to 10.') #outputs a message to the user containing the name of the apartment and the average review score
    st.table(PCTable) #displays the table of pros and cons

    AllAverageReviewScores = df_3.loc[df_3["Name"] == apartment_search] #grabs the row that the selected apartment is in

    for i in range(6): #deletes the first 6 columns of the table
        del AllAverageReviewScores[AllAverageReviewScores.columns.values[0]] 

    AllAverageReviewScores = AllAverageReviewScores.iloc[: , :-3] #deletes the last 3 columns of the table

    AllAverageReviewScores = AllAverageReviewScores.T.stack().reset_index(name='val') #changes the table to be vertical instead of horizontal and adds the columns level_0, level_1, and val

    del AllAverageReviewScores["level_1"] #delets the column named level_1

    AllAverageReviewScores.rename( #changes the column name from level_0 to Date and val to Average Review Score
    columns={"level_0":"Date","val":"Average Review Score"} , inplace=True)

    AllAverageReviewScores['Date'] =  pd.date_range(start='2015-01-01', end='2022-04-01', periods=88) # generate a date range to be used as the x axis
    df_melted = pd.melt(AllAverageReviewScores,id_vars=['Date'], value_name='Average Review Score') #formats the dataframe
    c = alt.Chart(df_melted, title='Average Review Score Over Time').mark_line().encode( #creates the chart using altair
        x='Date', y='Average Review Score')

    st.altair_chart(c, use_container_width=True) #presets the chart to the user

st.markdown("---") #creates a line in the website to separate the apartment search and list of apartments with user constraints

if Final.empty: #checks if the constraints and list is empty
    st.write('Nothing has been selected or there are no apartments that fall under those constraints.')

else: #if its not empty present the list to the user
    st.table(Final['Name']) #shows a table to the user containing the list of most suitable apartments for the user given his/her constraints

    st.markdown("---") #creates a line in the website to separate the apartment list and information of the selected apartment from the list created

    dropdown = st.selectbox('Pick your Apartment from the list above', Final["Name"]) #creates a dropdown box for the user to select his/her apartment from the list created

    Monthly_Rent = float(Final.loc[Final["Name"] == dropdown, "Monthly Rent"]) #takes the name and matches it to the monthly rent in the CSV file and places it into a variable

    DistanceToCampus = float(Final.loc[Final["Name"] == dropdown, "Distance to Texas A&M University (miles)"]) #takes the name and matches it to the Distance to Texas A&M in the CSV file and places it into a variable

    Address = Final.loc[Final["Name"].str.contains(dropdown), "Address"].item() #takes the name and matches it to the address in the CSV file and places it into a variable

    AverageReviewScore = float(Final.loc[Final["Name"] == dropdown, "Average Review Score"]) #takes the name and matches it to the average review score in the CSV file and places it into a variable

    AverageReviewScore = str(round(AverageReviewScore, 2)) #rounds the average review score to 2 decimal places

    Pros = Final.loc[Final["Name"].str.contains(dropdown), "Pro"].item() #grabs the list of pros and matches them to the apartmnet selected
    Pros = Pros.split(",") #splits the list of pros with commas

    Cons = Final.loc[Final["Name"].str.contains(dropdown), "Con"].item() #grabs the list of cons and matches them to the apartmnet selected
    Cons = Cons.split(",") #splits the list of cons with commas

    data = {'Pros':[Pros],'Cons': [Cons]} #creates a table with the pros and cons and titales them respectivly
    PCTable = pd.DataFrame(data) #creates a varibale named PCTable and equals it to the data dataframe trough pandas
    PCTable = PCTable.explode(['Pros','Cons']) #changes the table from a 2x2 to a dataframe with how ever many cons and pros by 2 so #ofprosandconsx2

    st.write(f'The Apartment you have Chosen is: {dropdown}.') #outputs a message to the user containing the selected apartment
    st.write(f'The Monthly Rent is ${Monthly_Rent} for {NumberofBedRooms} bathrooms and {NumberofBedRooms} bedrooms.') #outputs a message to the user containing the monthly rent and the number of bedrooms and bathrooms
    st.write(f'The location of the apartment is {Address}, which is {DistanceToCampus} miles away from Texas A&M University.') #outputs a message to the user containing the address and the distance to TexasA&M
    st.write(F'The Average Review Score for {dropdown} is {AverageReviewScore} on a scale from 1 to 10.') #outputs a message to the user containing the name of the apartment and the average review score
    st.table(PCTable) #displays the table of pros and cons

    AllAverageReviewScores = Final.loc[Final["Name"] == dropdown] #grabs the row that the selected apartment is in

    for i in range(6): #deletes the first 6 columns of the table
        del AllAverageReviewScores[AllAverageReviewScores.columns.values[0]]

    AllAverageReviewScores = AllAverageReviewScores.iloc[: , :-3] #deletes the last 3 columns of the table

    AllAverageReviewScores = AllAverageReviewScores.T.stack().reset_index(name='val') #changes the table to be vertical instead of horizontal and adds the columns level_0, level_1, and val

    del AllAverageReviewScores["level_1"] #delets the column named level_1

    AllAverageReviewScores.rename( #changes the column name from level_0 to Date and val to Average Review Score
    columns={"level_0":"Date","val":"Average Review Score"} , inplace=True)

    AllAverageReviewScores['Date'] =  pd.date_range(start='2015-01-01', end='2022-04-01', periods=88) # generate a date range to be used as the x axis
    df_melted = pd.melt(AllAverageReviewScores,id_vars=['Date'], value_name='Average Review Score') #formats the dataframe
    c = alt.Chart(df_melted, title='Average Review Score Over Time').mark_line().encode( #creates the chart using altair
        x='Date', y='Average Review Score')

    st.altair_chart(c, use_container_width=True) #presets the chart to the user
