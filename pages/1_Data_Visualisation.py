# -*- coding: utf-8 -*-
"""
Created on Wed May 21 01:15:24 2025

@author: Alpha Sylla
"""
import sys
from pathlib import Path

current_file = Path(__file__)    # Path of the current file
base_path = current_file.parent.parent    # One level above the current module
sys.path.insert(1,base_path)

import streamlit as st
import pandas as pd
import http_verbs
import numpy as np
import altair as alt

st.set_page_config(page_title="Dataviz")
tab1, tab2 = st.tabs(["🗃 Static data","📈 Time series"])

# Definition of custom font size
st.markdown("""
<style>
.my-small-title-font {
    font-size:15px !important;
}
</style>
""", unsafe_allow_html=True)


#  streamlit "st.session_state" variable initialisation    
    
if 'api_root' not in st.session_state:
    st.session_state['api_root'] = 'https://stratview-0a6cd8d77f03.herokuapp.com/isapp/v1/resources'

    
st.sidebar.header("Narrow down the asset universe by using the filters below") 

this_key = 0    # Initialisation of the counter variable that will be used for key generation for the different widgets used


# Initialise the pre-selection selectboxes used to narrow down the search space
api_url_1 = st.session_state['api_root'] + '/fieldsearch?generic_instrument_class=cash'    # Base url for fields search

fields = http_verbs.get_request(api_url_1)
df1 = pd.DataFrame(fields)
cols = list(df1.columns)

val = np.array([[None]*100]*len(cols))   
 
for j in range(len(cols)):
    this_key +=1
    v = st.sidebar.multiselect(f'**{cols[j].capitalize()}**', df1.iloc[:,j].dropna(axis=0, how='any'), key='multiselect_'+str(this_key), placeholder='', label_visibility="visible",)
    val[j][0:len(v)] = v   
  
api_url_2 = st.session_state['api_root'] + '/static_data_class?' 

for i in range(len(val[0])):
    if val[0][i]:
        api_url_2 += f'instrument_type={val[0][i]}&'    # WATCH OUT! LEAVE NO SPACE AROUND THE EQUALITY SIGN; do instrument_type={val[0]}[i] instead of instrument_type = {val[0]}
for i in range(len(val[1])):
    if val[1][i]:
        api_url_2 += f'asset_type={val[1][i]}&'
for i in range(len(val[2])):
    if val[2][i]:
        api_url_2 += f'country={val[2][i]}&'
for i in range(len(val[3])):
    if val[3][i]:
        api_url_2 += f'sub_region={val[3][i]}&'
for i in range(len(val[4])):
    if val[4][i]:
        api_url_2 += f'region={val[4][i]}&'
for i in range(len(val[5])):
    if val[5][i]:
        api_url_2 += f'asset_class={val[5][i]}&'
for i in range(len(val[6])):
    if val[6][i]:
        api_url_2 += f'sub_asset_class={val[6][i]}&'
for i in range(len(val[7])):
    if val[7][i]:
        api_url_2 += f'ICB_supersector={val[7][i]}&'
for i in range(len(val[8])):
    if val[8][i]:
        api_url_2 += f'currency={val[8][i]}&'
for i in range(len(val[9])):
    if val[9][i]:
        api_url_2 += f'maturity={val[9][i]}&'
for i in range(len(val[10])):
    if val[10][i]:
        api_url_2 += f'rating_fitch={val[10][i]}&'
for i in range(len(val[11])):
    if val[11][i]:
        api_url_2 += f'rating_moodys={val[11][i]}&'
for i in range(len(val[12])):
    if val[12][i]:
        api_url_2 += f'rating_sp={val[12][i]}&'        
       
# Populate multiselect with the names of the pre-selected instruments        
api_url_2 = api_url_2[:-1]
preselection = http_verbs.get_request(api_url_2)
df2 = pd.DataFrame(preselection, columns=['name','ticker'])
df2.dropna(axis=0, how='any', inplace=True)   


with tab1:
    st.markdown("# Instrument characteristics")
    st.write(""" """)           
    
    this_key +=1
    selection_box = st.multiselect('**Choose a set of instruments to visualize**', df2.iloc[:,0], key='multiselect_'+str(this_key), placeholder='', label_visibility="visible")       

    # Time series data request
    st.text("")
    this_key +=1
    button = st.button("**Get instruments**", key='button_'+str(this_key))
    st.text("")

    names = []
    tickers = []

    if button:
        for item in selection_box:
            # Get names and associated tickers
            name = item
            names.append(name)
            ticker = df2.loc[df2.name == item,'ticker']
            tickers.append(ticker.iloc[0])
            mapping_table = pd.DataFrame(names, tickers)
            
        # Build url for get request to the API
        api_url_3 = st.session_state['api_root'] + '/static_data?'

        for i in range(len(tickers)):
            api_url_3 += f'ticker={tickers[i]}&'
    
        api_url_3 = api_url_3[:-1]

        try:
            # Data request and processing
            data1, data2 = http_verbs.get_request(api_url_3)
            data1 = pd.DataFrame(data1)    # cash instruments
            data2 = pd.DataFrame(data2)    # derivative instruments
            if len(data1)>0:
                data1.set_index('instrument_name', inplace=True)
                st.markdown('<p class="my-small-title-font"><b>Cash instrument characteristics </b></p>', unsafe_allow_html=True)
                st.write(data1.sort_index())   
            if len(data2)>0:
                data2.set_index('contract_label', inplace=True)    
                st.markdown('<p class="my-small-title-font"><b>Derivative contract characteristics </b></p>', unsafe_allow_html=True)
                st.write(data2.sort_index())                           
        except:
            st.markdown('<p class="my-small-title-font"><b>No historical data found for one or more of these data items</b></p>', unsafe_allow_html=True)
 

with tab2:    
    st.markdown("# Time series plot")   

    this_key +=1
    selection_box = st.multiselect('**Choose a set of instruments to visualize**', df2.iloc[:,0], key='multiselect_'+str(this_key), placeholder='', label_visibility="visible")
        
    # Date input widgets
    startDate = st.date_input('**Start date**', value=None, min_value=None, max_value=None, format="YYYY-MM-DD", label_visibility="visible")
    endDate = st.date_input('**End date**', value=None, min_value=None, max_value=None, format="YYYY-MM-DD", label_visibility="visible")

    # Time series data request
    st.text("")
    graph_option = st.radio('**Show charts**', options=['Show raw values', 'Show values rebased to 100 at start'])
    st.text("")
    draw_chart = st.button("**Get the requested data**")

    names = []
    tickers = []

    if graph_option:
        if draw_chart:
            for item in selection_box:            
                # Get names and associated tickers
                name = item
                names.append(name)
                ticker = df2.loc[df2.name == item,'ticker']
                tickers.append(ticker.iloc[0])
                mapping_table = pd.DataFrame(names, tickers)
            
            # Build url for get request to the API
            api_url_3 = st.session_state['api_root'] + '/timeseries?'

            for i in range(len(tickers)):
                api_url_3 += f'ticker={tickers[i]}&'
    
            api_url_3 = api_url_3[:-1]

            if startDate:
                api_url_3 += f'&startDate={startDate}'
            if endDate:
                api_url_3 += f'&endDate={endDate}'    
            try:
                # Data request and processing
                raw_data = http_verbs.get_request(api_url_3)
                data = raw_data['data']                
                data_type = raw_data['data_type']
                data = pd.DataFrame(data)

                if graph_option == 'Show values rebased to 100 at start': 
                    for item in data_type:
                        ticker = item[0]
                        dtp = item[1]
                        if dtp == 'level' and data[ticker].min()>0:
                            ret = data[ticker][1:]/data[ticker][0:-1].values
                            data[ticker][1:] = ret
                            data[ticker][0] = 100
                            data[ticker] = data[ticker].cumprod()
                        elif dtp == 'rate':
                            data[ticker][1:] = 1 + data[ticker][1:]/100    # watch out : rates are already expressed in percentage points
                            data[ticker][0] = 100
                            data[ticker] = data[ticker].cumprod()                            
                        elif dtp == 'annualized rate':
                            data[ticker][1:] = 1 + 1/360*data[ticker][1:]/100    # watch out : annualized rates (in percentage points) must be converted to daily
                            data[ticker][0] = 100
                            data[ticker] = data[ticker].cumprod()                                               
                        else:
                            data.drop(labels=ticker, axis=1, inplace=True)
                    data.dropna(axis=0, how='any', inplace=True)
                else:
                    data = data[data.T.isna().sum()<= len(data.columns)-2]    # I need at least a date and one observation (i.e. 2 non-NA columns) to keep a row in the dataset

                    
                dates = list(data['Date'])
                data.iloc[:,1:] = data.iloc[:,1:].round(2)
                data = data.T
                data.reset_index(inplace=True)
                col_names = ['Ticker']
                col_names.extend(dates)
                data = data.set_axis(col_names,axis=1)
                data.drop(index=0, inplace=True)

                # Show data in a table
                df = data.copy()
                final_names = data['Ticker'].apply(lambda x: mapping_table.loc[x,0]) 
                df.insert(0,'Name', final_names)
                df.set_index('Name', inplace=True)
                st.text("")
                st.text("")
                st.text("")
                st.markdown('<p class="my-small-title-font"><b>Historical levels</b></p>', unsafe_allow_html=True)
                st.write(df.sort_index())    
                
                # Show data in a chart
                data.set_index("Ticker",  inplace=True)
                data = data.T.reset_index()
                data = pd.melt(data, id_vars=["index"]).rename(
                       columns={"index": "Date", "value": "Level"})                       
                data.loc[:,'Ticker'] = data['Ticker'].apply(lambda x: mapping_table.loc[x,0])    # replace tickers by names
                data = data.rename(columns={'Ticker': 'Name'})    # Rename column name "Ticker" to "Name"
            
                # Draw graphs
                range_level = data['Level'].max() - data['Level'].min()
                scale_max = data['Level'].max()
                scale_min = data['Level'].min() - range_level/4                

                if graph_option == 'Show raw values':
                    graph_title = f'Evolution of {names[0]}'
                else:
                    graph_title = f'Rebased values of {names[0]}'
            
                if len(names)>1: 
                    if len(names)>2:
                        for i in range(1,len(names)-1) : 
                            graph_title += f', {names[i]}'
                
                        graph_title += f' and {names[-1]}'
                    else:
                        graph_title += f' and {names[1]}'                                     
                
                chart = (
                    alt.Chart(data ,   
                              title=alt.Title(
                                    f"{graph_title}"
                              ))
                    .mark_line(opacity=0.8)
                    .encode(
                        x="Date",
                        y=alt.Y("Level", scale=alt.Scale(domain=[scale_min, scale_max])),
                        color='Name' 
                    ).properties(
                              width=1200,
                              height=400
                    )
                )                                                 
                                  
                alt.data_transformers.disable_max_rows()
                st.altair_chart(chart, use_container_width=True)     
        
            except:
                st.markdown('<p class="my-small-title-font"><b>No historical data found for one or more of these data items</b></p>', unsafe_allow_html=True)        
    
    
    
