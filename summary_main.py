# -*- coding: utf-8 -*-
import json,csv,re,time,pathlib,os,sys

sys.path.append(os.getcwd())

parent_path = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(parent_path))

master_path = parent_path.parent
sys.path.append(str(master_path))

project_path = master_path.parent
sys.path.append(str(project_path))

import click
from typing import Union,List,Dict

from tqdm import tqdm
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date


from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
import asyncio
import aiohttp
import requests


from Config.setting import Info as config
from database import query as sql_query
import logging

from pyflashtext import KeywordProcessor

import tools
from stockcodes import scrapy_extract as get_stockcode_data


keyword_processor = KeywordProcessor()
keyword_processor.add_keyword('香港中央結算有限公司')

logger = logging.getLogger("summary_main_scrapy")
logger.setLevel(level=logging.INFO)

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

####----------------- Datetime setting ----------------------------------------------------####
today_payload_str = date.today().strftime('%Y%m%d')

####----------------- Website setting ----------------------------------------------------####
ccass_main_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
ccass_main_url = config.hkex_urls.main.ch# r'https://www.hkexnews.hk/sdw/search/searchsdw_c.aspx'

####----------------- Selector setting ----------------------------------------------------####
view_state_selector='<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value=".+"'
hour_check_selector='input name="txtShareholdingDate" type="text" value=".+" id'

####------------------ Extract participant list--------------------------------------

inter_p, investp_p =sql_query.get_participants(p_type='Intermediaries',db_server='pro1'),sql_query.get_participants(p_type='investp',db_server='pro1')
####------------------ Pre-setting web scraper--------------------------------------

class BaseException(Exception):
    pass

class HTTPRequestFailed(BaseException):
    pass

####------------------ Extract participant list--------------------------------------

def fetch_viewstate(scrapy_str):
    scrapy_payload_str = scrapy_str.replace('-', '/')
    viewstate_payload = {'btnSearch': ':Search', 'txtShareholdingDate': scrapy_payload_str, 'sortDirection': 'asc',
                         'sortBy': 'stockcode', 'today': today_payload_str}
    viewstate_response = requests.request('POST', ccass_main_url, headers=ccass_main_headers, data=viewstate_payload)

    _viewstate = re.findall(view_state_selector, viewstate_response.text)[0]

    viewstate = re.sub(view_state_selector[:-3], '', _viewstate)[:-1]
    logger.info(f"   Parsing View State      ---- scrapy date:  , {scrapy_str}")
    del scrapy_payload_str, viewstate_payload, viewstate_response, _viewstate
    return viewstate

def parse_hour_check(scrapy_dt, view_state, check_stockcode):
    scrapy_payload_str = scrapy_dt.strftime('%Y-%m-%d %H:%M:%S')[:10].replace('-', '/')
    check_payload = {"__VIEWSTATE": view_state, "__EVENTTARGET": 'btnSearch', 'sortDirection': 'dec',    'sortBy': 'shareholding', 'today': today_payload_str, 'txtShareholdingDate': scrapy_payload_str, 'txtStockCode': check_stockcode}
    check_response = requests.post(ccass_main_url, headers=ccass_main_headers, data=check_payload, timeout=60)
   # print(f"check response: {check_response.text}")
    __shareholdingdate_str = re.findall(hour_check_selector, check_response.text)[0]
    shareholdingdate_str = re.sub(hour_check_selector[:-6], '', __shareholdingdate_str).replace('" id', '')
    shareholdingdate_dt = datetime.strptime(shareholdingdate_str, '%Y/%m/%d')
    print(f'scrapy date: {scrapy_dt}, shareholdingdate_dt :{shareholdingdate_dt}, __shareholdingdate_str :{__shareholdingdate_str} ')
    hour_check = (shareholdingdate_dt - scrapy_dt).days  # .seconds // 3600
    del scrapy_payload_str, check_payload, check_response, __shareholdingdate_str,
    if hour_check != 0:
        logger.info(f"   Fail Hour Check         ---- scrapy date:  , {scrapy_dt},   Shareholding Date :, {shareholdingdate_dt},   Hour Check :  {hour_check}, 'days")
        return False
    else:
        logger.info(f"   Sucess Hour Check       ---- scrapy date:  , {scrapy_dt},  Shareholding Date :, {shareholdingdate_dt},   Hour Check :  {hour_check}, 'days")
        return True
    # hour_check= True if scrapy_dt in tools.trade_days_list(config.etnet_trade_days_url) else False
    # if not hour_check :
    #     logger.info( f"   Fail Hour Check         ---- scrapy date:  , {scrapy_dt} is not trade day, no further process is triggered")
    #     return hour_check
    # else:
    #     logger.info( f"   Sucess Hour Check       ---- scrapy date:  , {scrapy_dt} is trade day, go to scrap data")
    #     return hour_check

#      logger.info(f"   Fail Hour Check         ---- scrapy date:  , {scrapy_dt},   Shareholding Date :, {shareholdingdate_dt},   Hour Check :  {hour_check}, 'days")
#      return False
####------------------ Extract participant list--------------------------------------

class AsnycGrab(object):

    def __init__(self, stockcodes, scrapy_dt, view_state, max_threads):

        self.stockcodes = stockcodes
        self.view_state = view_state
        self.scrapy_dt = scrapy_dt
        self.scrapy_str = self.scrapy_dt.strftime('%Y-%m-%d %H:%M:%S')[:10]
        self.scrapy_payload_str = self.scrapy_str.replace('-', '/')
        self.results = {}
        self.max_threads = max_threads
        self.schema = 'ccass_dev'

    def __parse_results(self, html, stockcode):
        global inter_p, investp_p
        if not html: print(html)
        html = html.decode()

        try:

            Summary_soup = BeautifulSoup(html, 'html.parser')
            Summary_table_soup=Summary_soup.find(class_="ccass-search-summary-table")

            Summary_category =[i.text for i in Summary_table_soup.find_all(class_='summary-category')][:-1]
            Summary_header =[i.text for i in Summary_table_soup.find_all(class_='header')]
            Summary_values =[0 if i.text =='' else i.text for i in Summary_table_soup.find_all(class_='value')]
            Summary_total =int(re.sub(',','',Summary_table_soup.find(class_='ccass-search-remarks').find(class_='summary-value').text.strip()))

            _Summary = list(zip(Summary_header, Summary_values))[:-3]
            _Summary = [_Summary[i:i + 3] for i in range(0, len(_Summary), 3)]

            assert len(_Summary)==len(Summary_category)

            _Summary= dict(zip(Summary_category,_Summary))
            _Summary={k:{vv[0]:vv[1] for vv in v } for k,v in _Summary.items()}

            Summary_records = {'inter_holding': 0, 'consenting_holding': 0, 'nonconsenting_holding': 0,   'inter_num': 0, 'consenting_num': 0, 'nonconsenting_num': 0}
            for key ,values in _Summary.items():

                if key =='市場中介者':
                    for vk,vv in values.items():
                        if vk =='於中央結算系統的持股量':
                            Summary_records['inter_holding'] = int(vv.strip().replace(',',''))
                        elif vk== '參與者數目':
                            Summary_records['inter_num']= int(vv.strip().replace(',',''))
                        else:
                            continue
                elif key == '願意披露的投資者戶口持有人':
                    for vk, vv in values.items():
                        if vk == '於中央結算系統的持股量':
                            Summary_records['consenting_holding'] = int(vv.strip().replace(',',''))
                        elif vk =='參與者數目':
                            Summary_records['consenting_num']= int(vv.strip().replace(',',''))
                        else:
                            continue

                elif key =='不願意披露的投資者戶口持有人':
                    for vk, vv in values.items():
                        if vk == '於中央結算系統的持股量':
                            Summary_records['nonconsenting_holding'] = int(vv.strip().replace(',',''))
                        elif vk == '參與者數目':

                            Summary_records['nonconsenting_num'] = int(vv.strip().replace(',',''))
                        else:
                            continue
                else:
                    continue

            Summary_records['shareholdingdate'] = datetime(self.scrapy_dt.year, self.scrapy_dt.month, self.scrapy_dt.day, 0, 0, 0)
            Summary_records['stockcode'] =   int(stockcode)
            Summary_records['ISC']=Summary_total
            Summary_records['inter_pct']=(Summary_records['inter_holding']/Summary_records['ISC'])*100 if Summary_records['ISC'] not in [None,0] else 0
            Summary_records['consenting_pct']=(Summary_records['consenting_holding']/Summary_records['ISC'])*100 if Summary_records['ISC'] not in [None,0] else 0
            Summary_records['nonconsenting_pct']=(Summary_records['nonconsenting_holding']/Summary_records['ISC'])*100 if Summary_records['ISC'] not in [None,0] else 0
            Summary_records['CIP_pct']=Summary_records['inter_pct']+Summary_records['consenting_pct']
            Summary_records['ccass_pct']=((Summary_records['inter_holding']+Summary_records['consenting_holding']+Summary_records['nonconsenting_holding'])/Summary_records['ISC'])*100 if Summary_records['ISC'] not in [None,0] else 0
            Summary_records['non_ccass_pct']=100-Summary_records['ccass_pct']

            soup = BeautifulSoup(html, 'html.parser')
            hkex_date_soup=soup.find("#hkex_news_header_section > section > div.container.search-component > div > div.filter__inputGroup > ul > li.filter__container-input.searchDate > div > #txtShareholdingDate")
            hkex_date=hkex_date_soup.text if hkex_date_soup else ''

            participant_id= soup.find_all("td", class_="col-participant-id")
            participant_id = [i.find("div", class_="mobile-list-body").text for i in participant_id] if participant_id else []


            participant_name= soup.find_all("td", class_="col-participant-name")
            participant_name = [i.find("div", class_="mobile-list-body").text for i in participant_name] if participant_name else []

            address= soup.find_all("td", class_="col-address")
            address = [i.find("div", class_="mobile-list-body").text for i in address] if address else []

            num_holdings= soup.find_all("td", class_="col-shareholding text-right")
            num_holdings = [i.find("div", class_="mobile-list-body").text for i in num_holdings] if num_holdings else []


            __main_table = list(zip(participant_id, participant_name, address, num_holdings))


            __main_table = [[m.replace('*','').strip() if isinstance(m,str) else m for m in i ] for i in __main_table]
        #   Summary_records,Normal_records={},[]
           #
            investp__ , inter___={},{}
            for i in __main_table:


                row={ 'ccass_id':i[0], 'name_chi':i[1] , 'address':i[2],  'update_time':datetime.now()}
              #  print(row)

                keyword_found= keyword_processor.extract_keywords(row['name_chi'])

                if not keyword_found  and  row['ccass_id'] in ['',None,' ','  ','\t']:
                # if row['ccass_id'] in ['',None,' ','  ','\t']  and not re.search('香港中央結算',  row['name_chi'] ) :
                        row['p_type']= 'investp'
                        row['name_chi']=row['name_chi']#.replace('*','').strip()
                        investp__[row['name_chi']]=row
                elif not keyword_found and  row['ccass_id'] not in ['',None,' ','  ','\t']:
                # elif not re.search('香港中央結算',  row['name_chi'] ):
                        row['p_type'] ='Intermediaries'
                        row['name_chi'] = row['name_chi']#.replace('*', '').strip()
                        inter___[row['ccass_id']]=row
                else:
                    row = {'pid':16,'ccass_id': '', 'name_chi': '香港中央結算有限公司','address': '8/F TWO EXCHANGE SQUARE 8 CONNAUGHT PLACE CENTRAL HONG KONG','p_type': 'investp', 'update_time': datetime.now()}
                    investp__[row['name_chi']] = row


            update_investp, insert_investp, update_inter, insert_inter=[],[],[],[]

            for participant_id, row1 in inter___.items():
                if participant_id in inter_p:
                    row1['pid']=inter_p[participant_id]['pid']
                    update_inter.append(row1)
                else:
                    insert_inter.append(row1)

            for name_chi, row2 in investp__.items():
                if investp_p.get(name_chi) is None:
                    insert_investp.append(row2)
                else:
                    row2['pid'] = investp_p[name_chi]['pid']
                    update_investp.append(row2)

           # print(f"update investp  :{update_investp}\n\n")
            if insert_investp:
                logger.info(f"stockcode : {stockcode}")
                logger.info(f"insert investp  :{insert_investp}")
                for db_server in ['uat','pro1','pro2']:
                    sql_query.insert_participants(data=insert_investp, db_server=db_server)
           # print(f"update inter   :{update_inter}\n\n")

            if insert_inter:
                logger.info(f"stockcode : {stockcode}")
                logger.info(f"insert  inter  :{insert_inter}")
                for db_server in ['uat', 'pro1', 'pro2']:
                    sql_query.insert_participants(data=insert_inter, db_server=db_server )
            for db_server in ['uat', 'pro1', 'pro2']:
                sql_query.update_participants(data=update_investp,pid_exist=False, db_server=db_server)
                sql_query.update_participants(data=update_inter, pid_exist=True, db_server=db_server)


            investp_p= {**investp_p, **investp__}
            inter_p = {**inter_p , **inter___}


            Normal_records=[]
            for i in __main_table:
                shareholdingdate, ccass_id, stockcode, name_chi,_, holding=self.scrapy_dt,i[0],int(stockcode),i[1],i[2],i[3]
                holding=int(holding.replace(',',''))
                if ccass_id in inter_p:
                    pid= inter_p[ccass_id]['pid']
                    Normal_record={'shareholdingdate': self.scrapy_dt, 'stockcode': stockcode, 'pid': pid, 'holding': holding, 'ISC_pct': (holding / Summary_records['ISC'])*100 if Summary_records['ISC'] not in [None,0] else 0}
                    Normal_records.append(Normal_record)
                elif name_chi in investp_p:
                    pid = investp_p[name_chi]['pid']
                    Normal_record = {'shareholdingdate': self.scrapy_dt, 'stockcode': stockcode, 'pid': pid,'holding': holding, 'ISC_pct': (holding / Summary_records['ISC'])*100  if Summary_records['ISC'] not in [None,0] else 0}
                    Normal_records.append(Normal_record)
                else:
                    pass

            return Summary_records, Normal_records
        except:
            logging.error(f"error on parsing data of stockcode {stockcode},on date {self.scrapy_str}, at time :{time.time()}")
            return {},[]

    async def get_body(self, stockcode):
        payload_stock = {"__VIEWSTATE": self.view_state, "__EVENTTARGET": 'btnSearch', 'sortDirection': 'dec',   'sortBy': 'shareholding', 'today': today_payload_str,  'txtShareholdingDate': self.scrapy_payload_str, 'txtStockCode': stockcode}
        async with aiohttp.ClientSession() as session:
            async with session.post(ccass_main_url, headers=ccass_main_headers, data=payload_stock,   timeout=60) as response:
                #    if response.status == 200:
                html = await response.read()
                return response.url, html

    async def get_results(self, stockcode):
        try:
            url, html = await self.get_body(stockcode)
          #  self.__parse_results(html, stockcode)
            Summary, Main = self.__parse_results(html, stockcode)  ##Normal_info
            return Summary , Main  # ,Normal_info
        except BlockingIOError or Exception as e:
            logger.error(f'Error {e} for {stockcode}')

    async def handle_tasks(self, task_id, work_queue):
        while not work_queue.empty():
            stockcode = await work_queue.get()
            try:
              #  await self.get_results(stockcode)
                Summary, Main= await self.get_results(stockcode)  #

                if Summary:
                 #  print(Summary)
                    for db_server in ['uat','pro1','pro2']:
                        sql_query.insert_summary(data=Summary,db_server=db_server )
                if Main:
                   # print(Main)
                   for db_server in ['uat', 'pro1', 'pro2']:
                        sql_query.insert_main(data=Main,db_server=db_server )
                await asyncio.sleep(8)

            except BlockingIOError or Exception as e:
                logging.error(f'Error {e} for {stockcode}')
                await asyncio.sleep(7)
                # logging.exception('Error for {}'.format(current_url), exc_info=True)

    def eventloop(self):
        q = asyncio.Queue()
        [q.put_nowait(stockcode) for stockcode in self.stockcodes]
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
        tasks = [self.handle_tasks(task_id, q, ) for task_id in range(self.max_threads)]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()


def get_data(stockcode:Union[str,int]=None,max_requests:int=40,back_day:int=0,shareholdingdate:Union[str,datetime,date]=datetime.today().strftime('%Y-%m-%d %H:%M:%S')[:10]):
    MAX_REQUESTS = max_requests  #
    check_stockcode = str(config.parameters.main.check_stockcode)
    print(f"check code: {check_stockcode}")
    start = datetime.now()
    if isinstance(shareholdingdate,str):
        scrapy_dt = tools.convert2datetime(shareholdingdate) - relativedelta(days=back_day)
    elif isinstance(shareholdingdate,datetime):
        scrapy_dt = shareholdingdate - relativedelta(days=back_day)
    else:
        scrapy_dt = tools.date2dateime(shareholdingdate)- relativedelta(days=back_day)
    shareholdingdate_str = scrapy_dt.strftime('%Y-%m-%d')[:10]

    logging.info(f"shareholdingdate_str: {shareholdingdate_str}")
    scrapy_dt=  datetime.strptime( shareholdingdate_str + ' 00:00:00' , '%Y-%m-%d %H:%M:%S')

    view_state = fetch_viewstate(shareholdingdate_str)

    Hour_check = parse_hour_check(scrapy_dt, view_state, check_stockcode)
    print(f'Hour_check: {Hour_check}')
    if Hour_check:
        if stockcode is None:
            stockcode_list = [''.join([str(0)] * (5 - len(str(i.split('.')[0]))) + list(str(i.split('.')[0]))) for i in get_stockcode_data(run_date=shareholdingdate_str,back_day=0,exchange='HK')]
        else:
            stockcode_list=[''.join([str(0)] * (5 - len(str(stockcode))) + list(str(stockcode)))]
        if stockcode_list:
            logger.info('   Start to parse data')
            async_example = AsnycGrab(stockcode_list, scrapy_dt, view_state, MAX_REQUESTS)
            async_example.eventloop()
            del async_example, stockcode_list
        else:
            logger.warning('no stock code is provided')
    close = datetime.now()
    runtime = (close - start).seconds
    hours, remainder = divmod(runtime, 3600)
    mins, secs = divmod(remainder, 60)
    logger.info("{:02d}:{:02d}:{:02d}".format(hours, mins, secs))


def get_summary_and_main(shareholdingdate:Union[date,datetime]=date.today().strftime("%Y-%m-%d"), back_day:int=1,stockcode:Union[str,int]=None):
    start = time.time()
    get_data(stockcode=stockcode, max_requests=config.parameters.main.max_requests, shareholdingdate=shareholdingdate, back_day=back_day)  #
    for db_server in ['uat','pro1','pro2']:
        sql_query.delete_empty_participant(db_server=db_server)
    finish = time.time()
    process_time = finish - start
    print(f" processing time :{process_time / 60} mins")

@click.command()
@click.option('--shareholdingdate',default=None, help='insert shareholdingdate in either %Y-%m-%d or %Y-%m-%d %H:%M:%S format',show_default=True)
@click.option('--stockcode',default=None, help='stockcode for web-scrapy on hkex ccass webpage',show_default=True)
def run_scrapy(shareholdingdate:Union[str,datetime,date]=None,stockcode:Union[str,int]=None):
    if shareholdingdate is None:
        latest_dt=sql_query.get_main_shareholdingdate(limit=1,db_server='pro1')[0]
        today_dt=datetime.today()
        diff_day=(today_dt-latest_dt).days-1
        for i in range(diff_day,0,-1):
            get_summary_and_main(back_day=i,stockcode=stockcode)
    else:
        shareholdingdate=tools.convert2datetime(shareholdingdate)
        if shareholdingdate:
            get_summary_and_main(shareholdingdate=shareholdingdate,back_day=0,stockcode=stockcode)
        else:
            logging.error(f"shareholdingdate must be in either %Y-%m-%d or %Y-%m-%d %H:%M:%S format but got {shareholdingdate}")
            pass

if __name__ == '__main__':
    run_scrapy()
