# -*- coding: utf-8 -*-
import json,csv,re,time,pathlib,os,sys

sys.path.append(os.getcwd())

parent_path = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(parent_path))

master_path = parent_path.parent
sys.path.append(str(master_path))

project_path = master_path.parent
sys.path.append(str(project_path))

from typing import Dict,List,Tuple,Union,Optional
import unicodedata

import requests,click
from bs4 import BeautifulSoup

from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from datetime import datetime,date,timedelta

import logging

import tools
from Config.setting import Info as config
from database import query as sql_query

urls={'eng':config.hkex_urls.stocks.eng,'chi':config.hkex_urls.stocks.chi}

logger = logging.getLogger("stockcode_scrapy")
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


def Ashare_decode(name:str,stockcode:Union[str,int],ccass_id:Union[str,int],lang:str):
    if lang in ['eng','Eng','ENG']:
        name = re.sub('\(A\s\\#\d+\)|\(A\\#\d+\)|\(\\#\d+\)|\(A\\#\s\d+\)', '', name).strip()
        stockcode = re.sub('A|\(|\)|\\#|\s', '', stockcode)
        exchange= 'SH' if (stockcode.startswith('6') or stockcode.startswith('3')) else 'SZ'
        return {str(int(ccass_id)):{'stockcode':stockcode,'exchange':exchange,'ccass_id':ccass_id,f'name_{lang}':unicodedata.normalize('NFKD', name)}}
    else:
        return {str(int(ccass_id)): {'stockcode': None, 'exchange': 'CH', 'ccass_id': ccass_id,    f'name_{lang}': unicodedata.normalize('NFKD', name)}}

def HKshare_decode(name:str,ccass_id:Union[str,int],lang:str):
    stockcode,exchange  = ccass_id,'HK'
    return {str(int(ccass_id)):{'stockcode':stockcode,'exchange':exchange,'ccass_id':ccass_id,f'name_{lang}':unicodedata.normalize('NFKD', name)}}


def extract_single_lang(shareholdingdate:date,lang:str):

    shareholdingdate_str = shareholdingdate.strftime('%Y%m%d')
    url = urls.get(lang.lower(), None)
    if url is None:
        logger.info(f"error : lang: {lang},  url: None,  shareholdingdate : {shareholdingdate_str}")
        return None
    else:
        url=url.format(shareholdingdate_str)
        resp=requests.get(url)

        status_code=resp.status_code
        if status_code !=200:
            logger.info(f"error :{status_code} ,lang: {lang},shareholdingdate :{shareholdingdate}, url : {url}")
            return None
        else:
            url_content = resp.content.decode('utf-8', 'ignore')
            soup = BeautifulSoup(url_content, 'html.parser')
            trs = soup.find('tbody').find_all('tr')
            if not trs:
                logger.info(f"error :no data from html ,lang: {lang},shareholdingdate :{shareholdingdate}, url : {url}")
                return None
            else:
                data = {}
                for tr in tqdm(trs,desc=f"fetch data , lang: {lang},  data: {shareholdingdate}, url: {url}"):
                    row=[re.sub('\n|\r|\t','',td.text.strip()) for td in tr.find_all('td')]
                    if len(row)==2:
                        stock_ccass_id,stock_name=row[0],row[1]
                        if lang in ['chi','Chi','CHI']:
                            A_share =re.search('9\d\d\d\d|7\d\d\d\d|3\d\d\d\d',stock_ccass_id)
                        else:
                            A_share=re.search('\(A\s\\#\d+\)|\(A\\#\d+\)|\(\\#\d+\)|\(A\\#\s\d+\)',stock_name)
                        if A_share:
                            stockcode=A_share.group(0)
                            record=Ashare_decode(stock_name,stockcode,stock_ccass_id,lang=lang)
                        else:
                            record = HKshare_decode(stock_name,stock_ccass_id,lang=lang)
                        data.update(record)
                    else:
                        pass

                return data



def scrapy_extract(run_date:Union[datetime,date,str],back_day:int=1, exchange:Union[str,None]='HK')->Dict:
    run_date=datetime.strptime(run_date,'%Y-%m-%d') if isinstance(run_date,str) else run_date
    shareholdingdate = run_date - timedelta(days=back_day)
    logger.info(f"shareholdingdate :{shareholdingdate},  ")

    chi_data=extract_single_lang(lang='chi',shareholdingdate=shareholdingdate)
    eng_data=extract_single_lang(lang='eng',shareholdingdate=shareholdingdate)
    if not eng_data or not chi_data:
        logger.info(f"eng data: {eng_data} and chi data : {chi_data}")
        return {}
    else:
        total_data=eng_data.copy()
        for stock_ccass_id, d in total_data.items():
            d['name_chi']=chi_data.get(stock_ccass_id, )['name_chi'] if chi_data.get(stock_ccass_id,None) else ''
            d['listing'] = 'Y'
            d['update_time'] = datetime.now()

        total_data = {str(int(stock_d['stockcode'])) + '.' + stock_d['exchange'].upper(): stock_d for stockcode, stock_d in total_data.items()}
        if exchange:
            total_data = {stockcode: stock_d for stockcode, stock_d in total_data.items() if stock_d['exchange'].upper() == exchange.upper()}
        return total_data


def sql_extract(exchange:str=None,db_server:str='pro1')->Dict:
    return  sql_query.get_stocks(exchange=exchange,db_server=db_server) if exchange else sql_query.get_stocks(db_server=db_server)


def transform(scrapy_data:Dict,sql_data:Dict)->Dict:
    if scrapy_data and sql_data:
        obsolete_data={stockcode:d for stockcode, d in sql_data.items() if scrapy_data.get(str(stockcode),None) is None}
        new_data = {stockcode: d for stockcode, d in scrapy_data.items() if  sql_data.get(str(stockcode), None) is None}
        update_data = {stockcode: d for stockcode, d in scrapy_data.items() if  sql_data.get(str(stockcode), None) is not None}

        return {'obsolete': obsolete_data,'new':new_data,"update":update_data}
    else:
        return {'obsolete':{}, 'new':{}, "update": {}}

def load(transform_output:Dict,to_db:bool=False,db_server:str='uat'):
    obsolete_stocks,new_stocks,update_stocks=transform_output['obsolete'],transform_output['new'],transform_output['update']
    if obsolete_stocks:
        for stockcode,d in obsolete_stocks.items():
            d['listing']='N'
        logger.info(f"there are {len(obsolete_stocks)} obsolete stocks ")
        if to_db:
            sql_query.update_stocks(data=[d for stockcode,d in obsolete_stocks.items()],db_server=db_server)

    else:
        logger.info(f"no obsolete stocks ")

    if new_stocks:
        for stockcode,d in new_stocks.items():
            d['listing']='Y'
        logger.info(f"there are {len(new_stocks)} new stocks")
        if to_db:
            sql_query.insert_stocks(data=[d for stockcode, d in new_stocks.items()],db_server=db_server)

    else:
        logger.info(f"no new stocks")
    if update_stocks:
        for stockcode,d in new_stocks.items():
            d['listing']='Y'
        logger.info(f"there are {len(update_stocks)} updated stocks ")
        if to_db:
            sql_query.update_stocks(data=[d for stockcode, d in update_stocks.items()],db_server=db_server)



def get_stockcodes(run_date:Union[datetime,date,str]=(date.today()-timedelta(days=1)).strftime('%Y-%m-%d'),back_day:int=0,exchange:str=None,to_db:bool=True):
    scrapy_data = scrapy_extract(run_date=run_date, back_day=back_day, exchange=exchange)
    sql_data = sql_extract(exchange=exchange,db_server='pro1')
    transform_output = transform(scrapy_data=scrapy_data, sql_data=sql_data)
    for db_server in ['uat','pro1','pro2']:
        load(transform_output=transform_output, to_db=to_db,db_server=db_server)


@click.command()
@click.option("--shareholdingdate",default=None,help='Please insert shareholdingdate at format of either %Y-%m-%d %H:%M:%S or %Y-%m-%d',show_default=True)
@click.option("--exchange",default=None,help='Please insert exchange, must be in HK, SH or SZ',show_default=True)
@click.option("--to_db",default=True,help='Please type True or False',show_default=True)
def run_scrapy(shareholdingdate:Union[str,datetime,date]=None,exchange:str=None,to_db:bool=config.parameters.stocks.to_db):
    if shareholdingdate is None:
        get_stockcodes(run_date=date.today().strftime("%Y-%m-%d"),back_day=config.parameters.stocks.backtract_day,exchange=exchange,to_db=to_db)
    else:
        shareholdingdate_=tools.convert2datetime(shareholdingdate)
        if shareholdingdate_ :
            get_stockcodes(run_date=shareholdingdate_,back_day=0,exchange=exchange,to_db=to_db)
        else:
            logging.error(f"shareholdingdate is wrong format :{shareholdingdate_}")
            pass


if __name__=='__main__':
    run_scrapy()
