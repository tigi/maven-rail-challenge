import dash_leaflet as dl
import dash_leaflet.express as dlx
import pandas as pd
from dash import Dash, html, State,dcc
#from dash import dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from dash_extensions.javascript import assign
import dash_ag_grid as dag
#som graphs would probably be better with plotly express but stick with one lib
import plotly.graph_objects as go


import sys
import os
def resource_path(relative_path):

# get absolute path to resource
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

import assets.ed_functions as edf
import assets.ed_prepare_data as edpd



routes = edpd.read_routes_csv()
stations_dict = edpd.read_stations_csv()
geojson = dlx.dicts_to_geojson([{**c, **dict(tooltip=c['station'])} for c in stations_dict])
point_to_layer = assign("function(feature, latlng, context) {return L.circleMarker(latlng);}")
#read all raildata into pandas df
df_raildata = pd.read_csv ('railway-cleaned-v12.csv')
df_raildata_sorted = df_raildata.sort_values(['Departure Datetime', 'Departure Station','Arrival Destination'])
#lineup some lists to fill dropdowns without recalculating
months = df_raildata_sorted['Month Name'].unique().tolist()
stations_departure = df_raildata_sorted['Departure Station'].unique().tolist()
stations_departure.sort()
stations_arrival = df_raildata_sorted['Arrival Destination'].unique().tolist()
stations_arrival.sort()
treintje =  'assets/train-orange.svg'


##PREPARE DATAFRAMES##

##moneyrelated, month is grouped by month, nomonth is grouped without month
#money is about revenue, rides etc => df_money_month en df_money_nomonth #
df_money_month, df_money_nomonth = edpd.create_df_money(df_raildata_sorted)
#status is about delays, cancellations and reasons
df_delays_month, df_delays_nomonth = edpd.create_df_delays(df_raildata_sorted)
#heat is about popular days, time of days to travel
df_heat_month, df_heat_nomonth = edpd.create_df_heat(df_raildata_sorted)


#columdefinition for the ag-grid table #
money_raildata_columdefs = [
    { 'field': 'Route' },
    { 'field': 'transactions', 'headerName': 'Transactions'},
    { 'field': 'total_revenue_gbp', 'headerName': 'Revenue (£)'},   
    { 'field': 'missed_revenue_gbp', 'headerName': 'Refunds (£)' },   
]






#create a list with from,to lat,lon to draw lines on the map
#based on filtering (or not)

def create_polylines_routes(dataframe):
    #dataframe is moneny_railday_general_nomonth or a filtered version of a dataframe after callback
    #to avoid duplicates(because month can be a column) polylines is generated from the distinct values of Route
    input_routes = dataframe["Route"].unique()
    polylines_routes = []
    #loop list with routes
    for route in input_routes:
        #split route       
        #find coordinates
        #add to polylines
        route_names = route.split(' - ')
        dep_coordinates = edf.get_lat_lon(stations_dict,route_names[0])
        dest_coordinates = edf.get_lat_lon(stations_dict,route_names[1])
        route = [dep_coordinates,dest_coordinates]   
        polylines_routes.append(route)  

    return polylines_routes



create_polylines_routes(df_money_nomonth)







    
app = Dash(external_stylesheets=[
     dbc.themes.CYBORG
])

app.layout =  dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Img(id="logo", src=treintje, style={"width":"80px", "height":"80px"}),
            ],width=1),
        dbc.Col([ 
            dcc.Dropdown(
                id = "select_month", options= [{'label': 'All', 'value': None}] +[
                    {'label': i, 'value': i} for i in months
                    ],
                                        placeholder='Select month')
            ], width = 2),
        dbc.Col([ dcc.Dropdown(
            id = "select_departure_station", options= [{'label': 'All', 'value': None}] +[
                {'label': i, 'value': i} for i in stations_departure],
                                    placeholder='Select departure')
            
            
            ,], width=2),
        dbc.Col([ 
            dcc.Dropdown(
                id = "select_destination_station", options= [{'label': 'All', 'value': None}] +[
                    {'label': i, 'value': i} for i in stations_arrival
                    ],
                                        placeholder='Select destination')
            ], width=2),


        dbc.Col([
            dbc.Button('Reset Filters', id='reset-button'),
            
            
html.Div(
    [
        
        dbc.Button("Show map", id="open-lg", className="me-auto d-grid gap-2", style={'marginLeft':'1rem'}, n_clicks=0),
        

        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Your selected routes")),
                dbc.ModalBody(
                    [
                        dl.Map([
                            dl.TileLayer(),
                            #draw dottes
                            dl.GeoJSON(data=geojson,  pointToLayer=point_to_layer),
                            #draw routes
                            dl.Polyline(color="#333333",weight=2, positions=create_polylines_routes(df_money_nomonth), id='position-data')
                        ],id="routemap", center=[53.7, -1.5], zoom=7 ,  style={'height': '800px', 'width':'400'})
                    ]
                ),
            ],
            id="modal-lg",
            size="lg",
            is_open=False,
        ),

    ],
)
            
            
            
            
            ], width=5, style=edf.header_buttons()),
        
        ], style = edf.style_row1()),
    
    dbc.Row([
        html.H1(children="Summary",style=edf.style_h1()),
        dbc.Col([ 
            dbc.Row([
                dbc.Col([ 
                    html.Div(id="total_transactions", children=edf.DataCard(df_money_nomonth,"Transactions","transactions", "sum", df_money_nomonth,df_money_month,df_delays_nomonth,df_delays_month)),
                    ], width = 6),
                dbc.Col([ 
                    html.Div(id="total_revenue", children=edf.DataCard(df_money_nomonth,"Netto Revenue","netto_revenue_gbp", "sum",  df_money_nomonth,df_money_month,df_delays_nomonth,df_delays_month)),
                    ], width = 6),
                ],style = edf.style_row()),
            # dash_table.DataTable(df_money_month.to_dict('records'), [{"name": i, "id": i} for i in df_money_month.columns]),
            
            html.H2(children="Route(s) details",style=edf.style_h2()),
            html.P(children="The information below is sorted on transactions. Click on a table header to sort on another value."),
            
            dag.AgGrid(
                 id="table_summarized_1",
                 columnDefs= money_raildata_columdefs,
                 rowData= df_money_nomonth.to_dict('records'),
                 className="ag-theme-alpine-dark",
                 columnSize="sizeToFit",
             ),
            

            
            
            
            
            ], width=6),
        dbc.Col([
            
            dbc.Row([
                dbc.Col([ 
                    html.Div(id="total_trainrides", children=edf.DataCard(df_delays_nomonth,"Rides","Rides", "sum",  df_money_nomonth,df_money_month,df_delays_nomonth,df_delays_month)),
                    ], width = 6),
                dbc.Col([ 
                    html.Div(id="total_intime", children=edf.DataCard(df_delays_nomonth,"On time","On time", "sum",  df_money_nomonth,df_money_month,df_delays_nomonth,df_delays_month)),
                    ], width = 6),
                ],style = edf.style_row()),

            
            
            dbc.Row([
                html.H2(children="Train not in time analysis",style=edf.style_h2()),
                
                dbc.Col([
                    html.Div(id="total_delayed", children=edf.DataCard(df_delays_nomonth,"Delayed","Delayed", "sum", df_money_nomonth,df_money_month,df_delays_nomonth,df_delays_month))
                    ],width=6),
                dbc.Col([
                    html.Div(id="total_cancelled", children=edf.DataCard(df_delays_nomonth,"Cancelled","Cancelled", "sum",  df_money_nomonth,df_money_month,df_delays_nomonth,df_delays_month))
                    ],width=6)
            ],style = edf.style_row()),
            dbc.Row([
                html.H3(children="Why?",style=edf.style_h3()),
                
                dbc.Col([
                    dcc.Graph(id = 'bar_chart_notintime',figure=edf.bar_chart_notintime(df_delays_nomonth)),
                    ],width=12)
                ],style = edf.style_row()),
            

            

            ], width=6)
    
    
       ],style = edf.style_row()),
    
    dbc.Row([
            html.H2(children="Busy times",style=edf.style_h2()),
            dcc.Graph(id = 'heatmap',figure=edf.heatmap_busiest(df_heat_nomonth))
        ],style = edf.style_row())


    

],fluid=False)




# Store default values for filters
default_values = {
    'select_departure_station': None,
    'select_destination_station': None,
    'select_month': None
}

# RESET FILTERS HANDLING #

@app.callback(
    Output('select_departure_station', 'value'),
    Output('select_destination_station', 'value'),
    Output('select_month', 'value'),
    Input('reset-button', 'n_clicks'),
    prevent_initial_call=True
)

def reset_filters(n_clicks):
    if n_clicks:
        return default_values['select_departure_station'],default_values['select_destination_station'],default_values['select_month']
    return Dash.no_update

# FILTERING & UPDATING SCREEN HANDLING #

@app.callback(
    Output(component_id='total_transactions', component_property='children'),
    Output(component_id='total_revenue', component_property='children'),
    Output(component_id='total_trainrides', component_property='children'),
    Output(component_id='total_intime', component_property='children'),
    Output(component_id='total_delayed', component_property='children'),
    Output(component_id='total_cancelled', component_property='children'),
    Output(component_id = 'table_summarized_1',component_property='rowData'),
    Output(component_id = 'position-data',component_property='positions'),
    Output(component_id='bar_chart_notintime', component_property='figure'),
    Output(component_id='heatmap', component_property='figure'),
    Input(component_id='select_month', component_property='value'),
    Input(component_id='select_departure_station', component_property='value'),
    Input(component_id='select_destination_station', component_property='value'),
    prevent_initial_call=True
)

def update_output_div(select_month,select_departure_station,select_destination_station):
      
    
    # construct the 'where clause' for the dataframes
    # still not sure if it makes much difference to do it in fewer
    # lines and conditionally replace dataframes and in where clause later
    # probably less prone to errors but is it faster?
    
    used_filters_incl_month=[]
    used_filters_excl_month=[]
    

    filtered = False
    
    if select_month != None:
         used_filters_incl_month.append("(replace_df['Month Name']==select_month)")
         
         filtered = True
    
    
    if select_departure_station != None:
         used_filters_incl_month.append("(replace_df['Departure Station']==select_departure_station)")
         used_filters_excl_month.append("(replace_df['Departure Station']==select_departure_station)")
         filtered = True

    
    if select_destination_station != None:
         used_filters_incl_month.append("(replace_df['Arrival Destination']==select_destination_station)") 
         used_filters_excl_month.append("(replace_df['Arrival Destination']==select_destination_station)") 
         filtered = True
    
          
    #just initialize and filter them all, more kiss than adding a lot of logic.
    
    #nomonth data
    filtered_df = df_money_nomonth
    filtered_sr = df_delays_nomonth
    filtered_he = df_heat_nomonth
    #monthdata
    filtered_df_m = df_money_month
    filtered_sr_m = df_delays_month
    filtered_he_m = df_heat_month
    #summary tables for previous month data
    money_to_sum = df_money_month
    delay_to_sum = df_delays_month
  

    
    if filtered == True: 
        
        #convert the list with filters into a where clause
        #SYNTAX: filtered_df['Month Name']==select_month

        filter2use_incl_month = "&".join(used_filters_incl_month)
        filter2use_excl_month = "&".join(used_filters_excl_month)

        
        if select_month != None:         
            #filter all the frames with Month Name in them => all the filters
            #money with month data
            df_money_m = filter2use_incl_month.replace("replace_df", "filtered_df_m")
            filtered_df_m = filtered_df_m[eval(df_money_m)]
            #delays with month data
            df_delays_m = filter2use_incl_month.replace("replace_df", "filtered_sr_m")
            filtered_sr_m = filtered_sr_m[eval(df_delays_m)]
            #delays with month data
            df_heat_m = filter2use_incl_month.replace("replace_df", "filtered_he_m")
            filtered_he_m = filtered_he_m[eval(df_heat_m)]
            
            
            if select_departure_station != None or select_destination_station != None:
                #these 2 df's are needed to calculate previous month values if 
                #a month is selected and/of departure or destination
                #you should add extra columns with previous month values(shift?), more straighforward
            
            
                #money_to_sum = df with all months + other filters
                df_m_s = filter2use_excl_month.replace("replace_df", "money_to_sum ")
                money_to_sum = money_to_sum [eval(df_m_s)]                    
                #delay_to_sum = df with all months + other filters
                df_d_s = filter2use_excl_month.replace("replace_df", "delay_to_sum ")
                delay_to_sum = delay_to_sum[eval(df_d_s)]
            
            
            
            
        elif select_departure_station != None or select_destination_station != None:
            #filter all the frames with Month Name in them => all the filters
            #money with month data
            df_money_m = filter2use_incl_month.replace("replace_df", "filtered_df_m")
            filtered_df_m = filtered_df_m[eval(df_money_m)]
            #delays with month data
            df_delays_m = filter2use_incl_month.replace("replace_df", "filtered_sr_m")
            filtered_sr_m = filtered_sr_m[eval(df_delays_m)]
            #delays with month data
            df_heat_m = filter2use_incl_month.replace("replace_df", "filtered_he_m")
            filtered_he_m = filtered_he_m[eval(df_heat_m)]
            #update the df's without Month data too
            df_money_nm = filter2use_excl_month.replace("replace_df", "filtered_df")
            filtered_df = filtered_df[eval(df_money_nm)]
            #delays without month data
            df_delays_nm = filter2use_excl_month.replace("replace_df", "filtered_sr")
            filtered_sr = filtered_sr[eval(df_delays_nm)]
            #delays without month data
            df_heat_nm = filter2use_excl_month.replace("replace_df", "filtered_he")
            filtered_he = filtered_he[eval(df_heat_nm)]

           

    #define output, the order is different from the output because of the params for the DataCard
    
    #in the end the datacard needs all data since the context is triggered in the card and 
    #is decided upon true/false month selected.
    
    if select_month != None:
        
        transactions = edf.DataCard(filtered_df_m,"Transactions","transactions", "sum", filtered_df,filtered_df_m,filtered_sr,filtered_sr_m,money_to_sum = money_to_sum, delay_to_sum = delay_to_sum)
        revenue = edf.DataCard(filtered_df_m,"Netto Revenue","netto_revenue_gbp", "sum", filtered_df,filtered_df_m,filtered_sr,filtered_sr_m,money_to_sum = money_to_sum, delay_to_sum = delay_to_sum)
        delayed = edf.DataCard(filtered_sr_m,"Delayed","Delayed", "sum", filtered_df,filtered_df_m,filtered_sr,filtered_sr_m,money_to_sum = money_to_sum, delay_to_sum = delay_to_sum)
        cancelled = edf.DataCard(filtered_sr_m,"Cancelled","Cancelled", "sum",  filtered_df,filtered_df_m,filtered_sr,filtered_sr_m,money_to_sum = money_to_sum, delay_to_sum = delay_to_sum)
        rides = edf.DataCard(filtered_sr_m ,"Rides","Rides", "sum", filtered_df,filtered_df_m,filtered_sr,filtered_sr_m,money_to_sum = money_to_sum, delay_to_sum = delay_to_sum)
        intime = edf.DataCard(filtered_sr_m ,"On time","On time", "sum", filtered_df,filtered_df_m,filtered_sr,filtered_sr_m,money_to_sum = money_to_sum, delay_to_sum = delay_to_sum)   
        
                 
 
    else:
       
        transactions = edf.DataCard(filtered_df,"Transactions","transactions", "sum", filtered_df,filtered_df_m,filtered_sr,filtered_sr_m)
        revenue = edf.DataCard(filtered_df,"Netto Revenue","netto_revenue_gbp", "sum", filtered_df,filtered_df_m,filtered_sr,filtered_sr_m)
        delayed = edf.DataCard(filtered_sr,"Delayed","Delayed", "sum",filtered_df,filtered_df_m,filtered_sr,filtered_sr_m)
        cancelled = edf.DataCard(filtered_sr,"Cancelled","Cancelled", "sum", filtered_df,filtered_df_m,filtered_sr,filtered_sr_m)
        rides = edf.DataCard(filtered_sr ,"Rides","Rides", "sum", filtered_df,filtered_df_m,filtered_sr,filtered_sr_m)
        intime = edf.DataCard(filtered_sr ,"On time","On time", "sum", filtered_df,filtered_df_m,filtered_sr,filtered_sr_m)  


    
    
    
    if select_month != None:
        barchartime = edf.bar_chart_notintime(filtered_sr_m,True)
        heatmap = edf.heatmap_busiest(filtered_he_m,True)
        output3 = filtered_df_m.to_dict('records')
        output_positions = create_polylines_routes(filtered_df_m)
    else:
        barchartime = edf.bar_chart_notintime(filtered_sr)
        heatmap = edf.heatmap_busiest(filtered_he)
        output3 = filtered_df.to_dict('records')
        output_positions = create_polylines_routes(filtered_df)
        

    


    
    return transactions,revenue,rides, intime, delayed, cancelled, output3,output_positions,barchartime,heatmap

# MODAL MAP OPEN/CLOSE HANDLING

def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

app.callback(
    Output("modal-lg", "is_open"),
    Input("open-lg", "n_clicks"),
    State("modal-lg", "is_open"),
)(toggle_modal)



if __name__ == '__main__':
    app.run_server()