# -*- coding: utf-8 -*-
"""
Created on Fri May 31 10:32:24 2024

@author: vraag
"""
##READ DATAFILES##

# get temp working directory

import os
import csv



def read_routes_csv():
    os.chdir('d:\\Studie\\data-maven\\maven-train-challenge\\UK+Train+Rides\\') 
    # read csv with station data into file to a list of dictionaries, lat, long as str.
    with open("routes.csv", "r") as f_csv:
        reader = csv.DictReader(f_csv)
        data = [row for row in reader]
        routes = {r["Route"]: [{k : v} for k, v in r.items() if "Route" not in k] for r in data}
    return routes


def read_stations_csv():
    os.chdir('d:\\Studie\\data-maven\\maven-train-challenge\\UK+Train+Rides\\') 
    with open('stations.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        stations_dict = [row for row in csv_reader]
    return stations_dict


##PREPARE DATAFRAMES##

def create_df_money(dataframe):
    ##the money df is used to show revenue, refunds, tickettypes etc##
    ##all the filtering depends on the with and without month grouping##
    ##better one call and return 2 dfs##
    
    
    df_money_month = dataframe.groupby(['Month Name','Departure Station', 'Arrival Destination']).agg(
        transactions= ('Transaction ID','count'), 
        total_revenue_gbp = ('Revenue', 'sum'), 
        missed_revenue_gbp = ('Missed Revenue', 'sum'), 
        netto_revenue_gbp = ('Netto Revenue', 'sum'), 
        ticket_class_standard = ('Ticket Class Standard', 'sum'), 
        ticket_class_first_class = ('Ticket Class First Class', 'sum'),
        ticket_type_advance = ('Ticket Type Advance', 'sum'),
        ticket_type_anytime = ('Ticket Type Anytime', 'sum'),
        ticket_type_off_peak = ('Ticket Type Off-Peak', 'sum'),
        railcard_adult = ('Railcard Adult', 'sum'),
        railcard_disabled = ('Railcard Disabled', 'sum'),
        railcard_none = ('Railcard None', 'sum'),
        railcard_senior = ('Railcard Senior', 'sum'),
        payment_contactless = ('Payment Contactless', 'sum'),
        payment_credit_card = ('Payment Credit Card', 'sum'),
        payment_debit_card = ('Payment Debit Card', 'sum')
    ).reset_index()

    df_money_month['Route'] = df_money_month['Departure Station'] + " - " + df_money_month['Arrival Destination']
    df_money_month = df_money_month.sort_values(by='transactions', ascending=False).reset_index()

    ##rename columns if needed, this saves a stepp##
    ##don't forget to adjust the nomonth code if you do so##
    
    ##another grouping to get rid of the month name, this df is input for the dashboard without filtering##
    
    
    df_money_nomonth = df_money_month.groupby(['Departure Station', 'Arrival Destination']).agg(
         transactions= ('transactions','sum'), 
         total_revenue_gbp = ('total_revenue_gbp', 'sum'), 
         missed_revenue_gbp = ('missed_revenue_gbp', 'sum'), 
         netto_revenue_gbp = ('netto_revenue_gbp', 'sum'), 
         ticket_class_standard = ('ticket_class_standard', 'sum'), 
         ticket_class_first_class = ('ticket_class_first_class', 'sum'),
         ticket_type_advance = ('ticket_type_advance', 'sum'),
         ticket_type_anytime = ('ticket_type_anytime', 'sum'),
         ticket_type_off_peak = ('ticket_type_off_peak', 'sum'),
         railcard_adult = ('railcard_adult', 'sum'),
         railcard_disabled = ('railcard_adult', 'sum'),
         railcard_none = ('railcard_none', 'sum'),
         railcard_senior = ('railcard_senior', 'sum'),
         payment_contactless = ('payment_contactless', 'sum'),
         payment_credit_card = ('payment_credit_card', 'sum'),
         payment_debit_card = ('payment_debit_card', 'sum'),
         Route =  ('Route', 'max')
     ).reset_index()   
    
    df_money_nomonth = df_money_nomonth.sort_values(by='transactions', ascending=False).reset_index()
    
    
    return df_money_month, df_money_nomonth



def create_df_delays(dataframe):
    ##the delay df is used to show delay,cancellation and reasons to be cheerfull##
    ##all the filtering depends on the with and without month grouping##
    
    ##create groupting with monthdata and departure time, they are separate rides and can have a diffreent status.
    ## , as_index=False in groupby keeps the columns out of the index
    df_delay_month = dataframe.groupby(['Month Name','Departure Station', 'Arrival Destination', 'Departure Datetime'], as_index=False).agg(
        status_ontime = ('Status On Time', 'max'),
        status_delayed = ('Status Delayed', 'max'),
        status_cancelled = ('Status Cancelled', 'max'),
        status_delaysignalfailure = ('Delay Signal Failure', 'max'),
        status_delaystaffing= ('Delay Staffing', 'max'),
        status_delaytechnical= ('Delay Technical Issue', 'max'),
        status_delaytraffic= ('Delay Traffic', 'max'),
        status_delayweather= ('Delay Weather', 'max')
        )
    df_delay_month['trainrides'] = df_delay_month['status_ontime'] +  df_delay_month['status_delayed'] +  df_delay_month['status_cancelled']


    df_delay_month.reset_index()

    
    #df_delay_month = dataframe[pd.DataFrame(np.sort(dataframe[['Month Name','Departure Station', 'Arrival Destination', 'Departure Datetime']].values,1)).duplicated()]
    #if you drop duplicates than you can just use one groupby, but how.

        
    df_delay_month2 = df_delay_month.groupby(['Month Name','Departure Station', 'Arrival Destination'], as_index=False).agg(
        status_ontime = ('status_ontime', 'sum'),
        status_delayed = ('status_delayed', 'sum'),
        status_cancelled = ('status_cancelled', 'sum'),
        status_delaysignalfailure = ('status_delaysignalfailure', 'sum'),
        status_delaystaffing= ('status_delaystaffing', 'sum'),
        status_delaytechnical= ('status_delaytechnical', 'sum'),
        status_delaytraffic= ('status_delaytraffic', 'sum'),
        status_delayweather= ('status_delayweather', 'sum'),
        trainrides =  ('trainrides', 'sum')
        )
    #df_delay_month2['trainrides'] = df_delay_month2['status_ontime'] +  df_delay_month2['status_delayed'] +  df_delay_month2['status_cancelled']

    #volgende poging, verwijderen complete combi van key voor duplicate values voor reis.
    #df[pd.DataFrame(np.sort(df[['Name1','Name2']].values,1)).duplicated()]

    df_delay_month2.reset_index()
    
    ##create the grouping without month
    
    df_delay_nomonth = df_delay_month.groupby(['Departure Station', 'Arrival Destination']).agg(
        status_ontime = ('status_ontime', 'sum'),
        status_delayed = ('status_delayed', 'sum'),
        status_cancelled = ('status_cancelled', 'sum'),    
        status_delaysignalfailure = ('status_delaysignalfailure', 'sum'),
        status_delaystaffing= ('status_delaystaffing', 'sum'),
        status_delaytechnical= ('status_delaytechnical', 'sum'),
        status_delaytraffic= ('status_delaytraffic', 'sum'),
        status_delayweather= ('status_delayweather', 'sum'),
        trainrides = ('trainrides', 'sum')
        ).reset_index()

    
    ##rename columns definitive##
    renamecols = {'status_ontime':'On time', 'status_delayed': 'Delayed', 'status_cancelled': 'Cancelled',
                  'status_delaysignalfailure': 'Signal failure', 'status_delaystaffing': 'Staffing',
                  'status_delaytechnical': 'Technical issues', 'status_delaytraffic':'Traffic',
                  'status_delayweather': 'Weather', 'trainrides': 'Rides'}
    
   
    df_delay_month2.rename(columns=renamecols,  inplace = True)
    df_delay_nomonth.rename(columns=renamecols,  inplace = True)   
    
    
    return df_delay_month2, df_delay_nomonth


def create_df_heat(dataframe):
    
    
    df_heat_month = dataframe.groupby(['Month Name','Departure Station', 'Arrival Destination','Day Name','Departure timeslot']).agg(
        timeslot= ('Departure timeslot','count'), 
        ).reset_index()


    df_heat_nomonth = dataframe.groupby(['Departure Station', 'Arrival Destination','Day Name','Departure timeslot']).agg(
        timeslot= ('Departure timeslot','count'), 
        ).reset_index()
    
    
    return df_heat_month, df_heat_nomonth
    