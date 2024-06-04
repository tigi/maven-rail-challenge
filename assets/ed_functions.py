# -*- coding: utf-8 -*-
"""
Created on Thu May 23 11:00:06 2024

@author: vraag
"""

import dash_bootstrap_components as dbc
from dash import Dash, html, State,dcc
import pandas as pd
import plotly.graph_objects as go

#order_month = ['Jan','Feb','Mar','Apr']
#order_day = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']


def get_lat_lon(stationlist, cityname): 
    citynamefind = list(filter(lambda coord: coord['station'] == cityname, stationlist))    
    lat = citynamefind[0]['lat']
    lon = citynamefind[0]['lon']
    listcoordinates = [lat,lon]  
    return listcoordinates

def DataCard(dataframe, title, field, todo, df_money_nm,df_money_m,df_delay_nm,df_delay_m, money_to_sum = None, delay_to_sum = None):
    #yes I know the switch/match statement but somehow I never got it working in this
    #combi of spider & python although it should work

    #dataframe is the frame initially to proces
    # _nm => no month column
    # _m => month column
    # to_sum are used for previous values
    #if money_to_sum is not None:
        #print(money_to_sum.head())
    #if delay_to_sum is not None:
        #print(delay_to_sum.head())
    
    #check if dataframe contains the Month Name column.
    #this is not the way to do it.
    #if yes, add context value to card
    #if no, add sparkle line month results to card

     
    if 'Month Name' in dataframe:
         ## if month name in dataframe, this means a month name was selected and one
         ## should be returned if you ask for the distinct month names in the dataframe
         
         #return value selected_month is a list
         selected_month = dataframe['Month Name'].unique()
         #print(selected_month)

         if field in ('transactions','netto_revenue_gbp'):
               output_context = previous_month_context(money_to_sum, field,  selected_month)
         elif field in('Rides','On time','Cancelled','Delayed'):
               output_context = previous_month_context(delay_to_sum, field,  selected_month)
         else:
               output_context = ["some context this is"]

    else:
         if field in ('transactions','netto_revenue_gbp'):
             output_context = create_mom_sparline(df_money_m,field)
         elif field in('Rides','On time','Cancelled','Delayed'):
             output_context = create_mom_sparline(df_delay_m,field)
         else:
             output_context = ["some sparkline this is"]

        
 
    
    #create the core value of card.
    if todo == "sum":
        #moneycards get pound sign
        if field in ("total_revenue_gbp","missed_revenue_gbp","netto_revenue_gbp"):
            output_value = '£ ' + str(dataframe.sum()[field])
        elif field in ("On time"):
            #calcullate percentage of total

            fieldsum = dataframe.sum()[field]
            totalsum = dataframe.sum()['Rides']
            percentage = round( 100 * fieldsum/totalsum,1)
            output_value = str(f"{percentage} %")
        else:

            output_value = str(dataframe.sum()[field])
             
    if todo == "count":
        output_value = str(dataframe.count()[field])
        
    data_card = dbc.Card(
        dbc.CardBody(
        [
            html.H4(f"{title}", style=style_h4()),
            html.H2(f"{output_value}"
            ),
            html.Div(output_context[0])
        ]
        ),
        style=style_datacard(),
    )
    return data_card




def previous_month_context(dataframe,field,selected_value):
    
    
    
    
    
    #we did this before
    outputCardtmp = []
    #you could make this into one thing, the arrow images
    image_up_red = 'assets/up-red.svg'
    image_up_white = 'assets/up-white.svg'
    image_down_white = 'assets/down-white.svg'
    image_down_red = 'assets/down-red.svg'
    
    #check the index of the month (should include year too but hey, can't have it all)
    #if index 0, there will be no context
    
    #this is all not efficient but the result come out in random order, with this list they will be ordered.
    order_month = ['Jan','Feb','Mar','Apr']
    
    selected_value_index = order_month.index(selected_value)
    
    if selected_value_index > 0:
        #there will be previous month data
        pm = order_month[selected_value_index-1]
        cm = order_month[selected_value_index]
        
        if field in ('On time'):
            alldata = dataframe.groupby(['Month Name']).agg(
                value = (field, 'sum'),
                rides= ('Rides',sum)
            ).reset_index()
        else:
            alldata = dataframe.groupby(['Month Name']).agg(
                value = (field, 'sum')
            ).reset_index()
              

        # Create a dummy df with the required list and the col name to sort on
        dummy = pd.Series(order_month, name = 'Month Name').to_frame()

        # Use left merge on the dummy to return a sorted df
        sorted_df = pd.merge(dummy, alldata, on = 'Month Name', how = 'left')
        print(sorted_df.head())

        #get month value for previous month pm
        pm_value = sorted_df[sorted_df['Month Name']== pm]['value'].item()
        #current month value, maybe an extra column is better?
        cm_value = sorted_df[sorted_df['Month Name']== selected_value[0]]['value'].item() 

        #compare and set image
        
        if pm_value < cm_value:
            show_image = image_up_white
            if field in ('Delayed', 'Cancelled'):
                show_image = image_up_red
            
        else:
            show_image = image_down_red
            if field in ('Delayed', 'Cancelled'):
                show_image = image_down_white
        
        #on time should only show the percentage previous month and not a percentage change over percentages.
        if field not in ('On time'):
            percentage_mom = str(mom_perc_change(pm_value,cm_value)) + '% '
        else:
            ##percentage last month instead of mom percentage
            percentage_mom = ''
            percentage_cm = 100* sorted_df[sorted_df['Month Name']== selected_value[0]]['value'].item()/sorted_df[sorted_df['Month Name']== selected_value[0]]['rides'].item() 
            percentage_pm = 100 * pm_value / sorted_df[sorted_df['Month Name']== pm]['rides'].item()
            pm_value = str(round(percentage_pm,1)) + '%'
            if percentage_cm > percentage_pm:
                show_image = image_up_white
            else:
                show_image = image_down_red
            
            
            
            
       
        #print(sorted_df)
        outputCardtmp.append(html.P(children=[
            html.Img(src=show_image, style=def_png()),
            html.Span(f"  {percentage_mom} (pm: {pm_value})")
            
            
            ]))
                                    
                                    
               
    
    else:
        #no context data available
        outputCardtmp.append(html.P(children="No context data available"))
    
    

    
    #get index of selected value in order_month and previous month
    
    

    
    
    return outputCardtmp

def create_mom_sparline(dataframe,field):
    outputCardtmp = []
    # sparkleline = sum field per month in dataframe
    
        
    alldata = dataframe.groupby(['Month Name']).agg(
        value = (field, 'sum')
        ).reset_index()
    
    #this is all not efficient but the result come out in random order
    order_month = ['Jan','Feb','Mar','Apr']
    # Create a dummy df with the required list and the col name to sort on
    dummy = pd.Series(order_month, name = 'Month Name').to_frame()

    # Use left merge on the dummy to return a sorted df
    sorted_df = pd.merge(dummy, alldata, on = 'Month Name', how = 'left')

    #print(alldata.columns)
    #print(alldata.head())
    fig = go.Figure(data=go.Scatter(x=sorted_df['Month Name'], y=sorted_df['value'],
                                    line = dict(color='rgba(255,255,255,.7)', width=2, dash='dot')))  
    
    fig.update_layout(
    
        autosize=False,
        width=250,
        height=100,
        showlegend=False,
        plot_bgcolor="#282828",
        paper_bgcolor="#282828",
        font=dict(color= 'white'),
        margin=dict(t=10,l=10,b=10,r=10)
    
    )
    
    fig.update_xaxes(showgrid=False, zeroline=False,visible=False, showticklabels=False)
    fig.update_yaxes(showgrid=False, zeroline=False,visible=False, showticklabels=False)
    
    
    
    outputCardtmp.append(dcc.Graph(id = 'sparkle_'+field,figure=fig))

    
    return outputCardtmp



def mom_perc_change(old_value, new_value):
    
    percentage = 0
    # = 100*(new-old)/old
    
    if old_value > 0:
        percentage = 100 * ((new_value - old_value)/old_value)
        
    
    return round(percentage,1)


def bar_chart_notintime(dataframe,monthindex:bool()=False):   
    
        
    #monthindex is input/output by month or not
    if monthindex:
        meltids = ['Month Name','Departure Station','Arrival Destination']
    else:
        meltids = ['Departure Station','Arrival Destination','Cancelled','Delayed']
        
    meltcols = ['Signal failure','Staffing','Technical issues','Traffic','Weather']
    
    alldata = dataframe.melt(id_vars=meltids, value_vars=meltcols,var_name="reason")
    
    #(alldata.head())
     
    
    bar_chart_notintime= go.Figure(go.Bar(
            x=alldata['value'],
            y=alldata['reason'],
            marker_color='#336699',
            orientation='h')
)
    bar_chart_notintime.update_layout(
        showlegend=False,
        plot_bgcolor="black",
        paper_bgcolor="black",
        font=dict(color= 'white'),
        margin=dict(t=10,l=10,b=10,r=10)
    
    )
    bar_chart_notintime.update_xaxes(showgrid=False, zeroline=False)
    bar_chart_notintime.update_yaxes(showgrid=False, zeroline=False)
    
    
    
    return  bar_chart_notintime


def heatmap_busiest(dataframe,monthindex:bool()=False):
    
    if monthindex:
        alldata = dataframe.groupby(['Month Name', 'Day Name', 'Departure timeslot']).agg(
            total = ('timeslot', 'sum')).reset_index()
    else:
        alldata = dataframe.groupby(['Day Name', 'Departure timeslot']).agg(
            total = ('timeslot', 'sum')).reset_index()
    
    
    order_day = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    
    # Create a dummy df with the required list and the col name to sort on
    dummy = pd.Series(order_day, name = 'Day Name').to_frame()

    # Use left merge on the dummy to return a sorted df
    sorted_df = pd.merge(dummy, alldata, on = 'Day Name', how = 'left')
    

    
    heatmap = go.Figure(data=go.Heatmap(
                   z=alldata['total'],
                   #pity you can't define a gradient like in css.
                   colorscale=[[0.0, "rgba(0,0,0,1)"],
                               [0.1111111111111111, "rgba(51,102,153,.2)"],
                               [0.2222222222222222, "rgba(51,102,153,.4)"],
                               [0.3333333333333333, "rgba(51,102,153,.6)"],
                               [0.4444444444444444, "rgba(51,102,153,.8)"],
                               [0.5555555555555556, "rgba(51,102,153,1)"],
                               [0.6666666666666666, "rgba(255, 165, 0,.4)"],
                               [0.7777777777777778, "rgba(255, 165, 0,.6)"],
                               [0.8888888888888888, "rgba(255, 165, 0,.8)"],
                               [1.0, "rgba(255, 165, 0,1)"]],
                   x=sorted_df['Day Name'],
                   y=sorted_df['Departure timeslot'],
                   
                   ))   
    heatmap.update_layout(
    
    autosize=False,
    width=800,
    height=800,
    showlegend=False,
    plot_bgcolor="#282828",
    paper_bgcolor="#282828",
    font=dict(color= 'white'),
    margin=dict(t=10,l=10,b=10,r=10)
    
    )
    
    heatmap.update_xaxes(showgrid=False, zeroline=False)
    heatmap.update_yaxes(showgrid=False, zeroline=False)
    
   # disable the modebar for such a small plot
    heatmap.show(config=dict(displayModeBar=False))
    
    
    return heatmap






#UI should be separate .py, some generic functions and styledefinitions, somehow /assets/custom.css
#stopped loading, this is faster than solving the local problem

def style_h1():
    layout_style={'fontSize': '2.5rem',
                  'marginBottom':'1.8rem',
                  'color': 'rgba(255, 165, 0,1)'}
    return layout_style
def style_h2():
    layout_style={'fontSize': '2rem',
                  'marginBottom':'1.8rem',
                  'color': 'rgba(255, 165, 0,1)'}
    return layout_style

def style_h3():
    layout_style={'fontSize': '1.5rem'}
    return layout_style

def style_h4():
    layout_style={'fontSize': '1rem',
                  'textAlign': 'center'}
    return layout_style



def style_datacard():
    
    layout_style={'textAlign': 'center'}
    return layout_style

def style_row():
    layout_style={'marginBottom': '3rem'}
    return layout_style
#row1 is the headerrow with filters and buttons
def style_row1():
    layout_style={'marginBottom': '1rem', 'marginTop': '1rem', 'backgroundColor': '#3d3d3d' , 'padding':'1rem','alignItems': 'center' }
    return layout_style
def max_width():
    layout_style={'width': '100%' }
    return layout_style
#style for up/down images
def def_png():
    layout_style={'width': '20px' , 'height': '20px'}
    return layout_style

def header_buttons():
    layout_style={'display': 'flex', 'justifyContent': 'flex-end' }
    return layout_style