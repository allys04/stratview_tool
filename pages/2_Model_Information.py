# -*- coding: utf-8 -*-
"""
Created on Wed May 21 01:28:42 2025

@author: Alpha Sylla
"""

import streamlit as st
import pandas as pd
import http_verbs
import numpy as np
from datetime import datetime
import altair as alt


st.set_page_config(page_title="Stratinfo")
tab1, tab2, tab3 = st.tabs(["🗃 Static data & parameters", "📈 Backtested performance", "📈 Live performance"])

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
    st.session_state['api_root'] = 'https://stratview-api-0373e4642705.herokuapp.com/isapp/v1/resources'

if 'persist' not in st.session_state:
    st.session_state['persist'] = 0

def persist_results():

    st.session_state['persist'] = 1 

    
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
    st.markdown("# Strategy characteristics & parameters")
    st.write(
        """This demo illustrates a combination of plotting and animation with
    Streamlit. We're generating a bunch of random numbers in a loop for around
    5 seconds. Enjoy!"""
    )           
    
    this_key += 1
    selection_box = st.multiselect('**Choose a set of strategies to visualize**', df2.iloc[:,0], key='multiselect_'+str(this_key), placeholder='', label_visibility="visible")       

    # Time series data request
    st.text("")
    this_key += 1
    button = st.button("**Retrieve strategy details**", key='button_'+str(this_key))
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
        api_url_3 = st.session_state['api_root'] + '/static_strategy_data?'

        for i in range(len(tickers)):
            api_url_3 += f'ticker={tickers[i]}&'
    
        api_url_3 = api_url_3[:-1]

        try:
            # Data request and processing
            data1, data2 = http_verbs.get_request(api_url_3)
            if len(data1)>0:
                data1 = pd.DataFrame(data1)
                data1.set_index('instrument_name', inplace=True)
                st.markdown('<p class="my-small-title-font"><b>General strategy characteristics </b></p>', unsafe_allow_html=True)
                st.write(data1.sort_index())   
            if len(data2)>0:
                data2 = pd.DataFrame(data2)
                data2.set_index('strategy_label', inplace=True)    
                st.markdown('<p class="my-small-title-font"><b>Strategy specific characteristics & parameters </b></p>', unsafe_allow_html=True)
                st.write(data2.sort_index()) 
        except:
            st.markdown('<p class="my-small-title-font"><b>No historical data found for one or more of these data items</b></p>', unsafe_allow_html=True)
            
            
with tab2:    
    st.markdown("# Performance and diagnostics")   

    this_key += 1
    selection_box = st.multiselect('**Choose a set of strategies to visualize**', df2.iloc[:,0], key='multiselect_'+str(this_key), placeholder='', label_visibility="visible")
        
    # Date input widgets
    startDate = st.date_input('**Start date**', value=None, min_value=None, max_value=None, format="YYYY-MM-DD", label_visibility="visible")
    endDate = st.date_input('**End date**', value=None, min_value=None, max_value=None, format="YYYY-MM-DD", label_visibility="visible")
    
    # target risk and hurdle rate
    scale_risk = st.slider("**Enter target annualised risk in basis points**", min_value=10.00, max_value=1000.00, value=100.00, step = 5.00 )
    hurdle_rate = st.slider("**Enter hurdle rate for Sharpe ratio calculation**", min_value=-0.02, max_value=0.10, value=0.000, step = 0.005 )
    
    # Benchmark index
    this_key += 1
    benchmark = st.multiselect('**Choose a benchmark index for relative performance visualisation and beta calculation**', df2.iloc[:,0], key='multiselect_'+str(this_key), placeholder='', label_visibility="visible")    
        
    # Time series data request
    st.text("")
    this_key += 1
    show_results = st.button("**Show results**", key='button_'+str(this_key), on_click=persist_results, args=[])
    st.text("")
    
    # asset universe
    names = []
    tickers = []
    assets = selection_box
    if benchmark:
        assets.extend(benchmark)  
        
    if st.session_state['persist'] == 1:    
        for item in assets:            
            # get names and associated tickers
            name = item
            names.append(name)
            ticker = df2.loc[df2.name == item,'ticker']
            tickers.append(ticker.iloc[0])
            
        mapping_table = pd.DataFrame(names, tickers)    # mapping table between names and corresponding tickers
                        
        # Build url for strategy parameters retrieval to the API
        api_url_3 = st.session_state['api_root'] + '/static_strategy_data?'

        for i in range(len(tickers)):
            api_url_3 += f'ticker={tickers[i]}&'
        
        api_url_3 = api_url_3[:-1]          
            
        # Build url for time series data request to the API
        api_url_4 = st.session_state['api_root'] + '/timeseries?'

        for i in range(len(tickers)):
            api_url_4 += f'ticker={tickers[i]}&'
    
        api_url_4 = api_url_4[:-1]        

        if startDate:
            api_url_4 += f'&startDate={startDate}'
        if endDate:
            api_url_4 += f'&endDate={endDate}'    
        try:
            
            # Time series data retrieval and processing
            data = http_verbs.get_request(api_url_4)
            data = pd.DataFrame(data) 
            data.dropna(axis=0, how = 'any', inplace=True)    # on dates where at least one data is missing, delete everything
            
            dates = list(data['Date'])
            col_names = ['Code']
            col_names.extend(dates)     

            # strategy risk budget request
            data1, data2 = http_verbs.get_request(api_url_3)
            data2 = pd.DataFrame(data2)
            data2 = data2[['strategy_code', 'risk_alloc']]    # getting risk budget used for backtesting for strategies, returns nothing for the benchmark asset even if it is present in the assets list             
            risk_budget = []
            for i in range(len(tickers)):
                risk_budget.extend(data2.loc[data2.strategy_code == tickers[i],'risk_alloc'])
            
            n = len(risk_budget)
            nobs = len(data) - 1
            risk_budget = np.repeat(risk_budget, nobs)    # Create a dataframe where risk_budgets are repeated as many times as the number of observations
            risk_budget = risk_budget.reshape((n,nobs))    
            risk_budget = pd.DataFrame(risk_budget).astype(float)
            risk_budget = risk_budget.T
            
            # time interval between successive data points       
            dates_conv = [datetime.strptime(x, '%Y-%m-%d').date() for x in dates]    # Conversion of string into python datetime format
            df_dates = pd.DataFrame(dates_conv)    # time interval between successive dates in terms f timedelta, e.g. datetime.timedelta(days=7) for a 7 days interval
            df_dates.dropna(axis=0, how='any', inplace=True)            
            timestep = np.mean([len(pd.bdate_range(df_dates.iloc[i,0], df_dates.iloc[i+1,0], inclusive='left')) for i in range(len(df_dates)-1)])    # average time interval in number of business days
            d = np.round(260/np.round(timestep)) 

            # strategy returns                 
            ret = data.copy()
            ret.iloc[0,1:] = 0
            if benchmark:
                risk_budget[:,4] = 100   # extend by arbitrarily assigning a 100 bps risk alloc to the benchmark asset, that will be corrected just below
                
            ret.iloc[1:,1:] = (data.iloc[1:,1:].values/data.iloc[0:-1,1:].values -1)*(scale_risk/risk_budget)
            data.iloc[1:,1:] = 1 + ret.iloc[1:,1:].values
            data.iloc[0,1:] = 100
            data.iloc[:,1:] = data.iloc[:,1:].cumprod() 
            
            if benchmark:
                re_scale = (scale_risk / 10000) / (np.nanstd(ret.iloc[:,-1]) * np.sqrt(d))    # scale_risk is annualised and expressed in basis points, hence the "np.sqrt(d)" and "/10000" 
                ret.iloc[:,-1] = ret.iloc[:,-1]*re_scale
                data.iloc[1:,-1] = 1 + ret.iloc[1:,-1].values
                data.iloc[:,-1] = data.iloc[:,-1].cumprod()   
                              
            ret.iloc[:,1:] = ret.iloc[:,1:] * 10000    # expressing returns in bps
            ret.replace(to_replace=0, value=np.nan, inplace=True)    # Replacing '0' by 'nan' : '0' means no data (not a trading day, or release day, etc) in general
            #df_dates.dropna(axis=0, how='any', inplace=True)    # Now delete dates where at least one data item has an 'nan' : this may significantly impact some metrics
            ret = ret.T
            ret.reset_index(inplace=True)
            ret = ret.set_axis(col_names,axis=1)
            ret.drop(index=0, inplace=True)                         
       
            # Metrics computation
            # mean return
            ret_mean = ret.iloc[:,2:].mean(axis=1, skipna=True)
            ret_mean = ret_mean.reset_index().iloc[:,1]   # indices start at 1, this causes an issue below with df = pd.DataFrame(metrics_dict) -> reset_index() to start at 0       
            # median return
            ret_median = ret.iloc[:,2:].median(axis=1, skipna=True)
            ret_median = ret_median.reset_index().iloc[:,1] 
            # standard deviation of returns
            ret_std = ret.iloc[:,2:].std(axis=1, skipna=True, ddof=0) * np.sqrt(d)
            ret_std = ret_std.reset_index().iloc[:,1]
            # information ratio
            ret_ir = ret_mean.iloc[:].values / ret_std.iloc[:].values * d
            # sharpe ratio
            ret_sharpe = (ret_mean.iloc[:].values * d - hurdle_rate * 10000) / (ret_std.iloc[:].values)
            # Hurst exponent
            hurst_lags = range(2, 202)    # calculate standard deviation of differenced series using various lags
            ncols = len(data.columns) - 1
            hurst = [None]*ncols
            for j in range(ncols):
                logdata = np.log(data.iloc[:, j+1])
                tau = [np.nanstd(np.subtract(logdata.iloc[lag:].values, logdata.iloc[:-lag].values)) for lag in hurst_lags]    # standard deviation of log level differences at various lags
                m = np.polyfit(np.log(hurst_lags), np.log(tau), 1)    # calculate slope of log-log regression: log(tau) = p + m*log(lag)
                hurst[j] = m[0]    # calculate Hurst as twice the slope of log-log plot             
            hurst_exp = pd.DataFrame(hurst)
            # max drawdown
            running_max = data.iloc[:,1:].cummax()
            mdd = ((running_max - data.iloc[:,1:]) / running_max).abs().max()    # mdd(i.e. "max drawdown") = max(t>0) DDt = max(t>0){Abs(running_max(t) - Xt)/running_max(t)}  
            mdd = mdd.reset_index().iloc[:,1] * 10000    # expressed in basis points           
            # value-at-risk
            ret_VaR = ret.iloc[:,2:].quantile(0.05, axis=1)
            ret_VaR = ret_VaR.reset_index().iloc[:,1]
            # conditional value-at-risk
            y = []
            for j in range(len(tickers)):
                y.append(np.where(ret.iloc[j,2:] <= ret_VaR.iloc[j], 1.0, 0.0))
                   
            y = pd.DataFrame(np.squeeze(y)) 
            z = ret.iloc[:,2:].reset_index()
            del z['index']
            n,p = z.shape
            z = z.set_axis(range(0,p), axis=1)
            y = y.to_numpy().reshape(z.shape)    # make y the same shape as z
            y = pd.DataFrame(y)    # Make y a dataframe for element-wise multiplication with z ( a dataframe as well)
            a = pd.DataFrame((y.mul(z, axis=1)))
            b = pd.DataFrame(y.sum(axis=1)).T
            ret_CVaR = a.sum(axis=1)/b
            ret_CVaR = ret_CVaR.T.iloc[:,0]  
            # overall beta, up beta and down beta
            # overall beta
            if benchmark:
                ret_all = ret.iloc[:,2:].T
                beta = pd.DataFrame([None]*ncols)    
                covMat = ret_all.cov()           
                beta = covMat.iloc[:,-1]/covMat.iloc[-1,-1]    # benchmark returns are last column of ret.T, so pair-wise covariances with bench are in the last column of this cov mat
                beta = beta.to_numpy()
                # up beta
                ret_up = ret_all.loc[ret_all.iloc[:,-1]>0]
                up_beta = pd.DataFrame([None]*ncols)    
                covMat = ret_up.cov()           
                up_beta = covMat.iloc[:,-1]/covMat.iloc[-1,-1]    
                up_beta = up_beta.to_numpy()            
                # down beta
                ret_down = ret_all.loc[ret_all.iloc[:,-1]<0]
                down_beta = pd.DataFrame([None]*ncols)    
                covMat = ret_down.cov()           
                down_beta = covMat.iloc[:,-1]/covMat.iloc[-1,-1]    
                down_beta = down_beta.to_numpy()    
           
            # Re-arrange levels for display    
            data = data.T
            data.reset_index(inplace=True)
            data = data.set_axis(col_names,axis=1)
            data.drop(index=0, inplace=True)               
        
            # Show cum. return index, single return and metrics data in tables
            df = data.copy()
            df.insert(0,'Name', names)
            df.set_index('Name', inplace=True)
            del df['Code']
            df = df.astype(float).round(2)
            st.markdown('<p class="my-small-title-font"><b>Cumulative return index</b></p>', unsafe_allow_html=True)
            st.write(df)   
            
            df = ret.copy() 
            df.insert(0,'Name', names)
            df.set_index('Name', inplace=True)
            del df['Code']
            df = df.astype(float).round(2)
            st.markdown('<p class="my-small-title-font"><b>Returns (in basis points)</b></p>', unsafe_allow_html=True)
            st.write(df)                         
            
            if benchmark:
                metrics_dict = {'mean': ret_mean, 'median' : ret_median, 'std' : ret_std, 'ir' : ret_ir, 'sharpe' : ret_sharpe, 
                               'hurst': hurst, 'max drawdown' : mdd, 'VaR' : ret_VaR, 'CVaR' : ret_CVaR, 'beta': beta, 'up_beta': up_beta, 'down_beta': down_beta}
                
                df = pd.DataFrame(metrics_dict)
                df = df.set_axis(['mean','median', 'std','info ratio', 'sharpe', 'hurst', 'max DD', 'VaR', 'CVaR', 'beta', 'up beta' , 'down beta'], axis=1)
                
            else:
                metrics_dict = {'mean': ret_mean, 'median' : ret_median, 'std' : ret_std, 'ir' : ret_ir, 'sharpe' : ret_sharpe, 
                               'hurst': hurst, 'max drawdown' : mdd, 'VaR' : ret_VaR, 'CVaR' : ret_CVaR}

                df = pd.DataFrame(metrics_dict)
                df = df.set_axis(['mean','median', 'std','info ratio', 'sharpe', 'hurst', 'max DD', 'VaR', 'CVaR'], axis=1)                
                    

            df.insert(0,'Name', names)
            df.set_index('Name', inplace=True)
            df = df.astype(float).round(2)
            st.markdown('<p class="my-small-title-font"><b>Performance metrics</b></p>', unsafe_allow_html=True)
            st.write(df) 
            
            # Show level data in a chart
            data.set_index("Code",  inplace=True)
            data = data.T.reset_index()
            data = pd.melt(data, id_vars=["index"]).rename(columns={"index": "Date", "value": "Level"})                       
            data.loc[:,'Code'] = data['Code'].apply(lambda x: mapping_table.loc[x,0])    # replace tickers by names
            data = data.rename(columns={"Code": "Name"})    # and rename column from 'Code' to 'Name' 
            
            # Draw graphs            
            range_level = data['Level'].max() - data['Level'].min()
            scale_max = data['Level'].max()
            scale_min = data['Level'].min() - range_level/4
           
            graph_title = f'Cumulative performance of {names[0]}'

            if len(names)>1: 
                if len(names)>2:
                    for i in range(1,len(names)-1) : 
                        graph_title += f', {names[i]}'
                
                    graph_title += f' and {names[-1]}'
                else:
                    graph_title += f' and {names[1]}'
            
            chart_perf = (
                alt.Chart(data ,   
                          title=alt.Title(
                              f"{graph_title}"
                          ))
                .mark_line(opacity=0.8)
                .encode(
                    x="Date",
                    y=alt.Y("Level", scale=alt.Scale(domain=[scale_min, scale_max])),
                    color="Name",
                ).properties(
                          width=800,
                          height=400
                )
            )                    
           
            this_key += 1        
            st.altair_chart(chart_perf, use_container_width=True, key='altair_chart_'+str(this_key))   
 
            # Bring up position weights over time
            st.markdown('<p class="my-small-title-font"><b>Visualise the evolution of position weights over time</b></p>', unsafe_allow_html=True)
            if benchmark:
                choice = st.radio(label='Visualise position weights over time', options=names[:-1], horizontal=True, label_visibility="hidden")    # take out benchmark name when it is present
            else:
                choice = st.radio(label='Visualise position weights over time', options=names, horizontal=True, label_visibility="hidden")
            
            st.text("")
            this_key += 1
            show_weights = st.button("**Bring up the position weights**", key='button_'+str(this_key))    
            st.text("")
            
            if show_weights:
                for i in range(len(mapping_table)):
                    if mapping_table.iloc[i,0] == choice:
                        strat_code = mapping_table.index[i]
                        break
                
                api_url_5 = st.session_state['api_root'] + '/strategy_historical_position_weights?'
                api_url_5 += f'strat_code={strat_code}'     

                if startDate:
                    api_url_5 += f'&startDate={startDate}'
                if endDate:
                    api_url_5 += f'&endDate={endDate}'    

                data_pos = http_verbs.get_request(api_url_5)                               
                data_pos = pd.DataFrame(data_pos) 
                dates_pos = data_pos.date
                cols = ['ticker']
                cols.extend(dates_pos)            
                data_pos = data_pos.T
                data_pos.drop('date', axis=0, inplace=True)
                data_pos = data_pos.reset_index()
                data_pos = data_pos.set_axis(cols, axis=1)
                
                # re-scale weights to match target risk budget supplied in the frontend
                
                rb = data2.loc[data2.strategy_code == strat_code,'risk_alloc'].astype(float)   # Remember 'data2' above had strategy risk budgets (originally used to generate backtest weights)
                scale = scale_risk/rb
                data_pos.iloc[:,1:] = data_pos.iloc[:,1:].astype(float) * scale.iloc[0] 
                
                # Build url to request underlying instrument's static data to the API
                api_url_6 = st.session_state['api_root'] + '/static_data?'

                for i in range(len(data_pos)):
                    api_url_6 += f'ticker={data_pos.loc[i,"ticker"]}&'
    
                api_url_6 = api_url_6[:-1]

                data3, data4 = http_verbs.get_request(api_url_6)
                data3 = pd.DataFrame(data3)
                data4 = pd.DataFrame(data4)            
            
                pos_name = []
                pos_currency = []                
            
                for i in range(len(data_pos)):
                    if len(data3)>0:
                        if data_pos.loc[i,'ticker'] in data3.loc['instrument_ticker']:
                            undl_name = data3.loc[data3.instrument_ticker == data_pos.loc[i,'ticker'], 'instrument_name']
                            undl_currency = data3.loc[data3.instrument_ticker == data_pos.loc[i,'ticker'], 'currency']                    
                        elif len(data4)>0:
                            undl_name = data4.loc[data4.contract_code == data_pos.loc[i,'ticker'], 'contract_label']
                            undl_currency = data4.loc[data4.contract_code == data_pos.loc[i,'ticker'], 'invoice_currency']                                                    
                    else:                    
                        undl_name = data4.loc[data4.contract_code == data_pos.loc[i,'ticker'], 'contract_label']
                        undl_currency = data4.loc[data4.contract_code == data_pos.loc[i,'ticker'], 'invoice_currency']                    
                               
                    pos_name.append(list(undl_name))
                    pos_currency.append(list(undl_currency))                       
                
                # Show positions in a tabel
                data_pos.insert(0, 'Name', pd.DataFrame(pos_name))
                data_pos.insert(2, 'currency', pd.DataFrame(pos_currency))
                data_pos.set_index('Name', inplace=True)
                
                st.text("")
                st.write(data_pos)
            
                # chart the weights
                data_pos = data_pos.T
                data_pos.drop(index=['ticker','currency'], axis=0, inplace=True)
                data_pos = data_pos.reset_index()
                data_pos = pd.melt(data_pos, id_vars=["index"]).rename(columns={"index": "Date", "value": "weights"})                       
                
                st.text("")
                
                chart_weights = (
                    alt.Chart(data_pos ,   
                              title=alt.Title(
                                  ""
                              ))
                    .mark_line(opacity=0.9)
                    .encode(
                        x="Date",
                        y="weights",
                        color="Name",
                    ).properties(
                              width=1200,
                              height=400
                    )
                )  

                this_key += 1
                alt.data_transformers.disable_max_rows()
                st.altair_chart(chart_weights, use_container_width=True, key='altair_chart_'+str(this_key)) 


#*************************************************************************************************************************************************************************
# For reference:              
                # Example with data points marked as "points" and addition of a subtitle
                #chart = (
                #    alt.Chart(data ,   
                #          title=alt.Title(
                #                f"{graph_title} ",
                #                subtitle="this is a subtitle")
                #    .mark_point(opacity=0.8)    # Notice : "mark_point()" here in lieu of mark_line() as before
                #    .encode(
                #        x="Date",
                #        y="Level",
                #        color="Ticker",
                #    )
                #)          
        
        
                # Example with curves with colored areas and addition of a subtitle
                #chart = (
                #    alt.Chart(data ,   
                #          title=alt.Title(
                #                f"{graph_title} ",
                #                subtitle="this is a subtitle")
                #    .mark_area(opacity=0.8)
                #    .encode(
                #        x="Date:T",
                #        y=alt.Y("Level:Q", stack=None),
                #        color="Instrument:N",
                #    )
                #)  

#*************************************************************************************************************************************************************************
   
        
        except:
            st.markdown('<p class="my-small-title-font"><b>An error occurred when processing the data</b></p>', unsafe_allow_html=True)    

 
            