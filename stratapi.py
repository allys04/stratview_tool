# -*- coding: utf-8 -*-#
"""
Created on Thu May  1 01:04:16 2025

@author: Alpha Sylla
"""

from fastapi import FastAPI, Query
import sqlite3
from typing import Annotated
import pandas as pd
import numpy as np
import json

app = FastAPI()


@app.get('/')
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for reading archived data.</p>'''

def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.get('/isapp/v1/resources/taxonomy')
def taxonomy_request():
    
    """

    Returns
    -------
    TYPE
        dataframe.

    """  

    database = './stratdata.db'
    conn = sqlite3.connect(database)    
    cursor = conn.cursor()

    cursor.execute("SELECT GROUP_CONCAT(name, ',') FROM pragma_table_info('taxonomy');")    # get all column names as a list of one tuple
    cols = [item for item in cursor.fetchall()[0]]    
    cols = cols[0].split(',')    # get all column names in a list
    results = cursor.execute('SELECT * FROM taxonomy').fetchall()
    results = pd.DataFrame(np.squeeze(results), columns = cols)

    return results


@app.get('/isapp/v1/resources/fieldsearch')
def field_request(generic_instrument_class: str | None = None):
    
    """
    Parameters
    ----------
    generic_instrument_class : str|None
        security class : cash or derivatives.
        
    Returns
    -------
    TYPE
        dataframe.

    """  

    database = './stratdata.db'
    conn = sqlite3.connect(database)    
    cursor = conn.cursor()   
        
    cursor.execute("SELECT GROUP_CONCAT(name, ',') FROM pragma_table_info('search_fields');")    # get all column names as a list of one tuple
    cols = [item for item in cursor.fetchall()[0]]    
    cols = cols[0].split(',')    # get all column names in a list    

    fields = cursor.execute('SELECT * FROM search_fields').fetchall()
    fields = pd.DataFrame(np.squeeze(fields), columns = cols)      

    for item in cols:
        if generic_instrument_class == item :
            qstr = ''
            for field in fields[item]:
                if field is not None:
                    qstr += f'{field},'  
                    
            qstr = qstr[:-1]
            results = cursor.execute(f'SELECT {qstr} FROM taxonomy').fetchall()
            c = [y for y in fields[item].tolist() if y is not None]
            results = pd.DataFrame(np.squeeze(results), columns = c)  
            break       

    return results


@app.get('/isapp/v1/resources/static_data_class') 
def static_data_class_request(instrument_type: Annotated[list[str] | None, Query()] = None, asset_type: Annotated[list[str] | None, Query()] = None, 
                              country: Annotated[list[str] | None, Query()] = None, sub_region: Annotated[list[str] | None, Query()] = None, 
                              region: Annotated[list[str] | None, Query()] = None, asset_class: Annotated[list[str] | None, Query()] = None, 
                              sub_asset_class: Annotated[list[str] | None, Query()] = None, ICB_supersector: Annotated[list[str] | None, Query()] = None, 
                              currency: Annotated[list[str] | None, Query()] = None, maturity: Annotated[list[str] | None, Query()] = None, 
                              rating_fitch: Annotated[list[str] | None, Query()] = None, rating_moodys: Annotated[list[str] | None, Query()] = None, 
                              rating_sp: Annotated[list[str] | None, Query()] = None):    
    
    """
    
    Parameters
    ----------
    search_criteria : str|None
        list of criteria to combine for static data search.

    Returns
    -------
    TYPE
        DataFrame.

    """       
    
    
    database = './stratdata.db'
    conn = sqlite3.connect(database)    
    cursor = conn.cursor()
            
    query = 'CREATE TEMPORARY TABLE request_table_derivatives AS SELECT * FROM cash_instruments FULL JOIN derivative_instruments \
                ON cash_instruments.instrument_ticker = derivative_instruments.undl_ticker'
               
    cursor.execute(query)
    conn.commit()         

    # set instrument_type to 'financial_asset' and asset_type to 'future' for all derivative (i.e.future) contracts
    cursor.execute("UPDATE request_table_derivatives SET instrument_type = 'financial_asset' WHERE contract_code IS NOT NULL;")
    conn.commit()
    cursor.execute("UPDATE request_table_derivatives SET asset_type = 'future' WHERE contract_code IS NOT NULL;")
    conn.commit()
    
    # Run 3 requests, each for table cash_instruments and the two request tables above obtained from JOIN operations    
    to_filter = []
    
    qstr = ''
   
    if instrument_type is not None:
        subqstr = ''
        for i in range(len(instrument_type)):           
            subqstr += 'instrument_type=? OR '   
            to_filter.append(instrument_type[i])
        qstr += f'({subqstr[:-4]}) AND '
        
    if asset_type is not None:
        subqstr = ''
        for i in range(len(asset_type)):           
            subqstr += 'asset_type=? OR '    
            to_filter.append(asset_type[i])            
        qstr += f'({subqstr[:-4]}) AND '  
        
    if country is not None:
        subqstr = ''
        for i in range(len(country)):           
            subqstr += 'country=? OR '    
            to_filter.append(country[i])                
        qstr += f'({subqstr[:-4]}) AND '        
        
    if sub_region is not None:
        subqstr = ''
        for i in range(len(sub_region)):           
            subqstr += 'sub_region=? OR ' 
            to_filter.append(sub_region[i])              
        qstr += f'({subqstr[:-4]}) AND '      
        
    if region is not None:
        subqstr = ''
        for i in range(len(region)):           
            subqstr += 'region=? OR '    
            to_filter.append(region[i])              
        qstr += f'({subqstr[:-4]}) AND '        
        
    if asset_class is not None:
        subqstr = ''
        for i in range(len(asset_class)):           
            subqstr += 'asset_class=? OR ' 
            to_filter.append(asset_class[i])             
        qstr += f'({subqstr[:-4]}) AND '      
        
    if sub_asset_class is not None:
        subqstr = ''
        for i in range(len(sub_asset_class)):           
            subqstr += 'sub_asset_class=? OR '  
            to_filter.append(sub_asset_class[i])              
        qstr += f'({subqstr[:-4]}) AND '          
        
    if ICB_supersector is not None:
        subqstr = ''
        for i in range(len(ICB_supersector)):           
            subqstr += 'ICB_supersector=? OR '  
            to_filter.append(ICB_supersector[i])             
        qstr += f'({subqstr[:-4]}) AND '

    if currency is not None:
        subqstr = ''
        for i in range(len(currency)):           
            subqstr += 'currency=? OR '   
            to_filter.append(currency[i])             
        qstr += f'({subqstr[:-4]}) AND '

    if maturity is not None:
        subqstr = ''
        for i in range(len(maturity)):           
            subqstr += 'maturity=? OR '  
            to_filter.append(maturity[i])             
        qstr += f'({subqstr[:-4]}) AND '

    if rating_fitch is not None:
        subqstr = ''
        for i in range(len(rating_fitch)):           
           subqstr += 'rating_fitch=? OR '    
           to_filter.append(rating_fitch[i])            
        qstr += f'({subqstr[:-4]}) AND '

    if rating_moodys is not None:
        subqstr = ''
        for i in range(len(rating_moodys)):           
           subqstr += 'rating_moodys=? OR '  
           to_filter.append(rating_moodys[i])            
        qstr += f'({subqstr[:-4]}) AND '

    if rating_sp:
        subqstr = ''
        for i in range(len(rating_sp)):           
           subqstr += 'rating_sp=? OR '   
           to_filter.append(rating_sp[i])            
        qstr += f'({subqstr[:-4]}) AND ' 

     
    qstr = qstr[:-5]
    query_00 = 'CREATE TEMPORARY TABLE response_table_10 AS SELECT instrument_name, instrument_ticker FROM cash_instruments'
    query_01 = 'CREATE TEMPORARY TABLE response_table_11 AS SELECT contract_label, contract_code FROM request_table_derivatives'    
    query_10 = f'CREATE TEMPORARY TABLE response_table_10 AS SELECT instrument_name, instrument_ticker FROM cash_instruments WHERE {qstr}'
    query_11 = f'CREATE TEMPORARY TABLE response_table_11 AS SELECT contract_label, contract_code FROM request_table_derivatives WHERE {qstr}'
    
    if to_filter == []:        
        cursor.execute(query_00, to_filter)
        conn.commit()
        cursor.execute(query_01, to_filter)
        conn.commit()          
    else :            
        cursor.execute(query_10, to_filter)
        conn.commit()            
        cursor.execute(query_11, to_filter)
        conn.commit()     
    
    # Rename columns to same names across all 3 tables to allow UNION operation    
    query_200 = 'ALTER TABLE response_table_10 ' \
               'RENAME COLUMN instrument_name to name'           
 
    query_201 = 'ALTER TABLE response_table_10 ' \
               'RENAME COLUMN instrument_ticker to ticker'   
 
    query_210 = 'ALTER TABLE response_table_11 ' \
               'RENAME COLUMN contract_label to name'
               
    query_211 = 'ALTER TABLE response_table_11 ' \
               'RENAME COLUMN contract_code to ticker'               
                        
    cursor.execute(query_200)
    conn.commit()
    cursor.execute(query_201)
    conn.commit()    
    cursor.execute(query_210)
    conn.commit()    
    cursor.execute(query_211)
    conn.commit()      
     
    # Now run UNION operation between the 3 (properly renamed) response tables         
    query_3 = 'CREATE TEMPORARY TABLE response_table_2 AS' \
              ' SELECT * FROM response_table_10' \
              ' UNION'\
              ' SELECT * FROM  response_table_11'
        
    cursor.execute(query_3).fetchall()
    conn.commit()
    results = cursor.execute('SELECT * FROM response_table_2').fetchall()
    results = pd.DataFrame(results, columns = ['name','ticker'])
         
    
    return results



@app.get('/isapp/v1/resources/static_data')
def static_data_request(ticker: Annotated[list[str] | None, Query()] = None):
    """

    Parameters
    ----------
    ticker : str|None
        list of instrument or contract tickers.

    Returns
    -------
    TYPE
        DataFrame.

    """

    if not (ticker):
        return page_not_found(404) 

    database = './stratdata.db'
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    # Get column names from cash_instruments and derivative_instruments tables
    cursor.execute("SELECT GROUP_CONCAT(name, ',') FROM pragma_table_info('cash_instruments');")    # get all column names as a list of one tuple
    cols_0 = [item for item in cursor.fetchall()[0]]    
    cols_0 = cols_0[0].split(',')    # get all column names in a list    
    
    cursor.execute("SELECT GROUP_CONCAT(name, ',') FROM pragma_table_info('derivative_instruments');")    # get all column names as a list of one tuple
    cols_1 = [item for item in cursor.fetchall()[0]]    
    cols_1 = cols_1[0].split(',')    # get all column names in a list      

    # Combine all tickers
    to_filter=[]
    qstr_0 = 'SELECT * FROM cash_instruments WHERE '
    qstr_1 = 'SELECT * FROM derivative_instruments WHERE '
    if ticker:
        for i in range(0,len(ticker)):
            qstr_0 += ' instrument_ticker = ? OR'
            qstr_1 += ' contract_code = ? OR'
            to_filter.append(ticker[i]) 
         
        qstr_0 = qstr_0[:-3]
        qstr_1 = qstr_1[:-3]
        
        query_0 = f'SELECT * FROM ({qstr_0}) WHERE instrument_ticker IS NOT NULL' 
        query_1 = f'SELECT * FROM ({qstr_1}) WHERE contract_code IS NOT NULL'
        
        query_0 = qstr_0 
        query_1 = qstr_1

    # run the data requests
    results_0 = cursor.execute(query_0, to_filter).fetchall()
    conn.commit()
    results_1 = cursor.execute(query_1, to_filter).fetchall()           
    conn.commit()         

    df0 = pd.DataFrame(results_0, columns = cols_0).astype(str)
    df1 = pd.DataFrame(results_1, columns = cols_1).astype(str)
    
    return df0, df1


@app.get('/isapp/v1/resources/static_strategy_data')
def static_strategy_data_request(ticker: Annotated[list[str] | None, Query()] = None):
    """

    Parameters
    ----------
    ticker : str|None
        list of instrument or contract tickers.

    Returns
    -------
    TYPE
        DataFrame.

    """

    if not (ticker):
        return page_not_found(404) 

    database = './stratdata.db'
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    # Get column names from cash_instruments and derivative_instruments tables
    cursor.execute("SELECT GROUP_CONCAT(name, ',') FROM pragma_table_info('cash_instruments');")    # get all column names as a list of one tuple
    cols_0 = [item for item in cursor.fetchall()[0]]    
    cols_0 = cols_0[0].split(',')    # get all column names in a list    
    
    cursor.execute("SELECT GROUP_CONCAT(name, ',') FROM pragma_table_info('strategy_params');")    # get all column names as a list of one tuple
    cols_1 = [item for item in cursor.fetchall()[0]]    
    cols_1 = cols_1[0].split(',')    # get all column names in a list      

    # Combine all tickers
    to_filter=[]
    qstr_0 = 'SELECT * FROM cash_instruments WHERE '
    qstr_1 = 'SELECT * FROM strategy_params WHERE '
    if ticker:
        for i in range(0,len(ticker)):
            qstr_0 += ' instrument_ticker = ? OR'
            qstr_1 += ' strategy_code = ? OR'
            to_filter.append(ticker[i]) 
         
        qstr_0 = qstr_0[:-3]
        qstr_1 = qstr_1[:-3]
        
        query_0 = f'SELECT * FROM ({qstr_0}) AND instrument_ticker IS NOT NULL' 
        query_1 = f'SELECT * FROM ({qstr_1}) AND strategy_code IS NOT NULL'
        
        query_0 = qstr_0 
        query_1 = qstr_1

    # run the data requests
    results_0 = cursor.execute(query_0, to_filter).fetchall()
    conn.commit()
    results_1 = cursor.execute(query_1, to_filter).fetchall()           
    conn.commit()         

    df0 = pd.DataFrame(results_0, columns = cols_0).astype(str)
    df1 = pd.DataFrame(results_1, columns = cols_1).astype(str)
    
    return df0, df1


@app.get('/isapp/v1/resources/timeseries')
def timeseries_request(ticker: Annotated[list[str] | None, Query()] = None, startDate: str | None = None, endDate: str | None = None):
    """

    Parameters
    ----------
    ticker : str|None
        Instrument ticker.
    startDate : str|None
        Start date of requested time series.
    endDate : str|None
        End date of requested time series.

    Returns
    -------
    TYPE
        Float.

    """


    database = './stratdata.db'
    conn = sqlite3.connect(database)
    
    # first retrieve the names of all existing table ending with '_timeseries' keyword
    query_0 = 'SELECT name FROM sqlite_master WHERE type="table" ORDER BY name ASC'
    df = pd.read_sql_query(query_0,conn)
    tables = df.to_numpy()
    tables = [z for z in [y[0] for y in tables if len(y[0])>11] if z[-11:] =='_timeseries' ]    # list of tables with name ending with '_timeseries'

    # Join all the selected tables
    # start by stacking all the dates present in all the tables...
    qstr_1 = 'CREATE TEMPORARY TABLE date_table AS SELECT Date FROM ('
    for i in range(len(tables)): 
        qstr_1 += f'SELECT Date FROM {tables[i]} UNION '
        
    query_1 = qstr_1[:-7] + ')'
    cursor = conn.cursor()
    cursor.execute(query_1)
    conn.commit()    
    
    cursor.execute('ALTER TABLE date_table RENAME COLUMN Date to bulkDate;')
    
    # ...then proceed with joining the tables to get one big request table    
    if len(tables)==1:
        qstr_2 = f'CREATE TEMPORARY TABLE request_table_1 AS SELECT * FROM date_table FULL JOIN {tables[0]} ON date_table.bulkDate = {tables[0]}.Date'
    elif len(tables)>1:
        qstr_2 = f'CREATE TEMPORARY TABLE request_table AS SELECT * FROM date_table FULL JOIN {tables[0]} ON date_table.bulkDate = {tables[0]}.Date' 
        for i in range(1,len(tables)):
            qstr_2 += f' FULL JOIN {tables[i]} ON date_table.bulkDate = {tables[i]}.Date'
    
    query_2 = qstr_2
    cursor.execute(query_2)
    conn.commit()
    
    # Different commits with the view to sorting the rows of the request table by increasing dates   
    query_3 = 'CREATE TEMPORARY TABLE request_table_TEMP AS ' \
                  'SELECT * FROM (SELECT ROW_NUMBER() OVER (ORDER BY bulkDate ASC) as date_index, * FROM request_table);'     
                                   
    cursor.execute(query_3)
    conn.commit()                  
         
    cursor.execute('DROP TABLE IF EXISTS request_table;')    # drop the original table
    conn.commit() 
        
    cursor.execute('ALTER TABLE request_table_TEMP DROP COLUMN date_index;')    # drop column 'date_index' from temporary table
    conn.commit()     
       
    cursor.execute('ALTER TABLE request_table_TEMP RENAME TO request_table;')    # drop column 'date_index' from temporary table
    conn.commit()         
    
    # Combine all tickers for joint request
    if ticker:
        tickers=''
        for i in range(0,len(ticker)):
            tickers += f'{ticker[i]},' 
        tickers = tickers[:-1]
        query_4 = f'SELECT bulkDate, {tickers} FROM request_table WHERE'
    else: 
        query_4 = "SELECT * FROM request_table WHERE"

    # Create filter from start and end dates        
    to_filter = []
    
    if startDate:
        query_4 += ' bulkDate>=? AND'
        to_filter.append(startDate)
    if endDate:
        query_4 += ' bulkDate<=? AND'
        to_filter.append(endDate)
    if not (ticker or startDate or endDate):
        return page_not_found(404)    
    
    query_4 = query_4[:-4] + ';'
    
    results = {'data' :[], 'data_type':[]}
    results['data'] = cursor.execute(query_4, to_filter).fetchall()
    cols = ['Date'] + ticker
    results['data'] = pd.DataFrame(np.squeeze(results['data']), columns = cols)
    cursor.execute('DROP TABLE request_table')
    conn.commit()
      
    # Request the data type ("level","rate", "ratio")
    qstr_3 = ''
    qstr_4 = ''
    to_filter=[]
    if ticker:
        for i in range(0,len(ticker)):
            qstr_3 += ' instrument_ticker = ? OR'
            qstr_4 += ' contract_code = ? OR'
            to_filter.append(ticker[i]) 
    
    qstr_3 = qstr_3[:-3]
    qstr_4 = qstr_4[:-3]
    query_50 = f'SELECT instrument_ticker, timeseries_data_type FROM cash_instruments WHERE {qstr_3} '    
    query_51 = f'SELECT contract_code, price_data_type FROM derivative_instruments WHERE {qstr_4} '
    
    res_0 = cursor.execute(query_50, to_filter).fetchall()
    res_1 = cursor.execute(query_51, to_filter).fetchall()
    conn.commit()      
    
    #n,p = len(res_0),len(res_1)
    if len(res_0)>0:
        #for i in range(n):
            results['data_type'].extend(list(res_0))
    if len(res_1):  
        #for j in range(p):       
            results['data_type'].extend(list(res_1))         
    
    return results



@app.get('/isapp/v1/resources/strategy_historical_position_weights')
def historical_pos_weights_request(strat_code: str | None = None, startDate: str | None = None, endDate: str | None = None):
    """

    Parameters
    ----------
    strat_code : str|None
        strategy code.
    startDate : str|None
        Start date of requested time series.
    endDate : str|None
        End date of requested time series.

    Returns
    -------
    TYPE
        Float.

    """


    database = './stratdata.db'
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    query_0 = f'SELECT Date, {strat_code} FROM strategy_positions WHERE'
    
    # Create filter from start and end dates        
    to_filter = []
    
    if startDate:
        query_0 += ' Date>=? AND'
        to_filter.append(startDate)
    if endDate:
        query_0 += ' Date<=? AND'
        to_filter.append(endDate)
    if not (strat_code or startDate or endDate):
        return page_not_found(404)    
    
    query_0 = query_0[:-4] + ';'
    
    res = cursor.execute(query_0, to_filter).fetchall()
    conn.commit()    

    res = pd.DataFrame(np.array(res))
    res.dropna(axis=0,how='any', inplace=True)
    cnames = list(json.loads(res.iloc[0,1]).keys())    # de-jasonify to get a dictionary, then get the keys of the dictionary, and transform to list            
    res.iloc[:,1] = res.iloc[:,1].apply(lambda x : list(json.loads(x).values()))
    res = res.reset_index()
    del res['index']    # Delete the former index which is now a new column
    p,n = len(cnames),len(res)
    M = np.repeat([None]*n, p)
    results = pd.DataFrame(M.reshape((n,p)))
    results = results.set_axis(cnames, axis=1)
    
    for i in range(n):
        results.loc[i,:] = res.iloc[i,1] 
    
    results.insert(0, 'date', res.iloc[:,0])
    
    return results
