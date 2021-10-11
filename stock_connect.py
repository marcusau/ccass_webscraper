# -*- coding: utf-8 -*-
import json,csv,re,time,pathlib,os,sys

sys.path.append(os.getcwd())

parent_path = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(parent_path))

master_path = parent_path.parent
sys.path.append(str(master_path))

project_path = master_path.parent
sys.path.append(str(project_path))

from tqdm import tqdm
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date

from typing import List,Union,Dict

import requests
from bs4 import BeautifulSoup

import logging,click

import unicodedata


from database import query as sql_query
from Config.setting import Info as config
import tools



logger = logging.getLogger("stock_connect_scrapy")
logger.setLevel(level=logging.DEBUG)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# FileHandler
file_handler = logging.FileHandler(config.log_file_path)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# StreamHandler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

#### Define gloabal variables
today_str= date.today().strftime('%Y%m%d')

connect_config=config.hkex_urls.stock_connect
urls={'hk':connect_config.hk,'sh':connect_config.sh,'sz':connect_config.sz}

#### Define selectors ------------------
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
view_state_selector = "form#form1 > input#__VIEWSTATE"
event_validation_selector="form#form1 > input#__EVENTVALIDATION"
shareholdingdate_selector = "#pnlResult h2.ccass-heading > span"
stockcodes_selector = "div.ccass-search-result > #pnlResult > div.search-details-table-container.table-mobile-list-container > #mutualmarket-result > tbody > tr > td.col-stock-code > div.mobile-list-body"
shareholding_selector = "div.ccass-search-result > #pnlResult > div.search-details-table-container.table-mobile-list-container > #mutualmarket-result > tbody > tr > td.col-shareholding > div.mobile-list-body"
ISC_selector = "div.ccass-search-result > #pnlResult > div.search-details-table-container.table-mobile-list-container > #mutualmarket-result > tbody > tr > td.col-shareholding-percent > div.mobile-list-body"

####------------------------------------------------------------------------------------

def get_viewstate(region:str, payload_viewstate):
    url=urls.get(region,None)
    if url is None:
        logger.info(f"incorrect region: {region}")
        view_state, event_validation = None, None
    else:
        response_viewstate = requests.request("POST", url, headers=headers, data=payload_viewstate, params= {"t":region})

        if response_viewstate.status_code != 200:
            view_state, event_validation =None, None
            logger.error('Error on scrapying viewstate. region: ', region,' url:', url, ' error code:', response_viewstate.status_code)

        else:
            soup_viewstate = BeautifulSoup(response_viewstate.text.encode('utf8'), 'html.parser')
            view_state= soup_viewstate.select(view_state_selector)[0].get('value')
            event_validation = soup_viewstate.select(event_validation_selector)[0].get('value')
    return view_state ,event_validation



def scrap_single_exchange(region:str, payload_data):
    url = urls.get(region, None)
    shareholdingdate_web, stockcodes, shareholding,ISC_pct= None, None,None,None
    if url is None:
        logger.error(f"incorrect region: {region}")
    else:
        response_data = requests.request("POST", url, data=payload_data, headers=headers, params= {"t":region})
        if response_data.status_code != 200:
            logger.error(f"Error on scrapying data.  region: , {region}, url: {url}, ' error code:{response_data.status_code}")
            return shareholdingdate_web, stockcodes, shareholding, ISC_pct
        else:
            soup_data = BeautifulSoup(response_data.text.encode('utf8'), 'html.parser')
            shareholdingdate_web = datetime.strptime( re.sub('Shareholding Date: ', '', soup_data.select(shareholdingdate_selector)[0].text),  '%Y/%m/%d')
            stockcodes = [int(re.sub("\n|\r|\s\s|,", "", c.text)) for c in soup_data.select(stockcodes_selector)]
            shareholding = [int(re.sub("\n|\r|\s\s|,", "", c.text)) for c in soup_data.select(shareholding_selector)]
            ISC_pct = [re.sub("\n|\r|\s\s|,|\\%|\s", "", c.text) for c in soup_data.select(ISC_selector)]
            ISC_pct = [float(isc) if isc is not '' else 0 for isc in ISC_pct]
            assert len(stockcodes) == len(shareholding)
            return shareholdingdate_web,stockcodes,shareholding,ISC_pct

def scrapy_extract(run_date:Union[str,datetime,date]=date.today(),back_day:Union[int,str]=1,exchange:str='HK'):
    exchange=exchange.lower()
    run_date=datetime.strptime(run_date,'%Y-%m-%d') if isinstance(run_date,str) else run_date
    shareholdingdate = run_date - timedelta(days=back_day)
    shareholdingdate_str =  shareholdingdate.strftime('%Y-%m-%d')[:10].replace('-', '/')

    logger.info(f"shareholdingdate :{shareholdingdate}")
    try:
        payload_viewstate = {'btnSearch': ':Search', 'txtShareholdingDate': shareholdingdate_str, 'sortDirection': 'asc', 'sortBy': 'stockcode', 'today': today_str}
        view_state, event_validation = get_viewstate(exchange, payload_viewstate)

        payload_data = {"__VIEWSTATE": view_state, "__EVENTVALIDATION": event_validation, "btnSearch": 'Search','sortDirection': 'asc', 'sortBy': 'stockcode', 'today': today_str, 'txtShareholdingDate': shareholdingdate_str}
        shareholdingdate_web ,stockcodes, shareholding ,ISC_pct= scrap_single_exchange(exchange, payload_data)

        return {'shareholdingdate':shareholdingdate_web,"stockcode":stockcodes, "shareholding":shareholding,'ISC_pct':ISC_pct}
    except Exception as e1:
        logger.error(f"Error:, {e1}, 'region:  {exchange},   'shareholding date: {shareholdingdate_str}")
        return  {'shareholdingdate':[],"stockcode":[], "shareholding":[],'ISC_pct':[]}


def transform(scrapy_data:Dict,run_date:Union[str,datetime,date]=date.today(),back_day:Union[int,str]=1,exchange:str='HK')->Dict:

    run_date=datetime.strptime(run_date,'%Y-%m-%d') if isinstance(run_date,str) else run_date
    shareholdingdate = run_date - timedelta(days=back_day)
    shareholdingdate_str = shareholdingdate.strftime('%Y-%m-%d')[:10].replace('-', '/')

    shareholdingdate_web,stockcodes,shareholding,ISC_pct=scrapy_data.get('shareholdingdate'),scrapy_data.get('stockcode'),scrapy_data.get('shareholding'),scrapy_data.get('ISC_pct')
    if shareholdingdate_web is None:
        logger.warning( f'Scrapy Error:,  shareholdingdate: {shareholdingdate_str} is different from response date : {shareholdingdate_web}')
        return {}
    else:
        shareholdingdate_web_str = shareholdingdate_web.strftime('%Y-%m-%d 00:00:00')[:10].replace('-', '/')

        if shareholdingdate_str != shareholdingdate_web_str :
            logger.warning(f'Scrapy Error:, shareholdingdate: {shareholdingdate_str} is different from response date : {shareholdingdate_web_str}')
            return {}
        else:
            records = list(zip([shareholdingdate_web] * len(stockcodes),  stockcodes, [exchange.upper()]* len(stockcodes), shareholding,ISC_pct))
            logger.info(f"Success scrapy  ',region: {exchange}, '   ShareholdingDate: {shareholdingdate_web},    Numbers of records: {len(records)}")

            return {f"{i[1]}.{i[2]}":i for i in records}


def load(transform_output:Dict,to_db:bool=False,db_server:str='uat')->Dict:
    if transform_output:
        if to_db:
            sql_query.insert_stock_connect([v for k,v in transform_output.items()],db_server=db_server)
        return transform_output
    else:
        return {}

def get_stockconnect(run_date:Union[str,datetime,date]=date.today(),back_day:Union[int,str]=1,to_db:bool=True):
    data_output={}
    for exchange in tqdm(urls.keys(),desc='scrapy stock-connect'):
        scrapy_data = scrapy_extract(run_date=run_date, back_day=back_day, exchange=exchange)
        transform_output = transform(scrapy_data=scrapy_data, run_date=run_date, back_day=back_day, exchange=exchange)
        if transform_output:
            data_output={**data_output,**transform_output}
            for db_server in ['uat', 'pro1', 'pro2']:
                load(data_output,to_db=to_db,db_server=db_server)






@click.command()
@click.option("--shareholdingdate",default=None,help='Please insert shareholdingdate at format of either %Y-%m-%d %H:%M:%S or %Y-%m-%d')
@click.option("--to_db",default=True,help='Please type either True or False')
def run_scrapy(shareholdingdate:Union[str,datetime,date]=None,to_db:bool=True):
    if shareholdingdate is None:
        latest_dt = sql_query.get_stock_connect_date(1,db_server='pro1')[0]
        today_dt = datetime.today()
        diff_dt = (today_dt - latest_dt).days
        for i in range(diff_dt, 0, -1):
            if i > 0:
                get_stockconnect(run_date=date.today().strftime("%Y-%m-%d"), back_day=i, to_db=to_db)

    else:
        shareholdingdate=tools.convert2datetime(shareholdingdate)
        if shareholdingdate:
            get_stockconnect(run_date=shareholdingdate,back_day=0,to_db=to_db)
        else:
            logging.error(f"shareholdingdate is wrong format :{shareholdingdate}")
            pass

if __name__=='__main__':
    run_scrapy()



