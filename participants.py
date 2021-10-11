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

import requests,click
from bs4 import BeautifulSoup

from dateutil.relativedelta import relativedelta
from tqdm import tqdm
from datetime import datetime,date,timedelta
import logging

import unicodedata

from database import query as sql_query
from Config.setting import Info as config
import tools


logger = logging.getLogger("participants_scrapy")
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


urls={'chi':config.hkex_urls.participants.chi,'eng':config.hkex_urls.participants.eng}


def extract_single_lang(lang:str,scrap_date:Union[date,datetime]):
    scrap_date_str=scrap_date.strftime('%Y%m%d')
    url=urls.get(lang.lower(),None)


    if url is None:
        logger.info(f"error : lang: {lang},  url: None,  scrapy_date : {scrap_date_str}")
        return None
    else:
        url=url.format(scrap_date_str)
        resp=requests.get(url)
        status_code=resp.status_code
        if status_code != 200:
            logger.info(f"error :{status_code} from url : {url}")
            return None
        else:
            data = {}
            url_content=resp.content.decode('utf-8', 'ignore')
            soup=BeautifulSoup(url_content,'html.parser')
            trs= soup.find('tbody').find_all('tr')
            if trs:
                for tr in tqdm(trs,desc=f"fetch data from html of {lang} url : {url}"):
                    tds=tr.find_all('td')
                    if tds:
                        row=[td.text.strip() for td in tds]
                        if len(row)==2:
                            ParticipantID, Participant_Name =row[0],row[1]
                            data[ParticipantID]= unicodedata.normalize('NFKD', Participant_Name)
                        else:
                            logger.info(f"row error: {row}")
                            pass
                return data
            else:
                logger.info(f"error in url : {url}, html :  {soup.text}")
                return None


def scrapy_extract(run_date:Union[datetime,date,str],back_day:int=1)->Dict:
    run_date=datetime.strptime(run_date,'%Y-%m-%d') if isinstance(run_date,str) else run_date
    scrapy_date = run_date - timedelta(days=back_day)
    logger.info(f"scrapy date :{scrapy_date},  ")

    chi_data=extract_single_lang(lang='chi',scrap_date=scrapy_date)
    eng_data=extract_single_lang(lang='eng',scrap_date=scrapy_date)
    if eng_data and chi_data:
        return {id_ if id_ is not '' else config.abbv.participant.ccass_id: {'ccass_id':id_ if id_ is not '' else config.abbv.participant.ccass_id,'name_eng':eng,'name_chi':chi_data.get(id_,''),'p_type':'Intermediaries','update_time':datetime.now()} for id_, eng in eng_data.items()}
    else:
        logger.info(f"eng data: {eng_data} and chi data : {chi_data}")
        return {}


#@task(name='participant sql extraction')
def sql_extract( db_server:str='pro1'):
    return sql_query.get_participants(p_type='Intermediaries',db_server=db_server)

#@task(name='participants transformation')
def transform(scrapy_data:Dict,sql_data:Dict):

    if scrapy_data   and sql_data:

        update_data, new_data={},{}
        for ccass_id, d in scrapy_data.items():

            if d['name_chi'] =='香港中央結算有限公司':
                pass#d['pid'],d['p_type']=16,'investp'

               # update_data[16] = d
            else:
                old_d=sql_data.get(ccass_id, None)
                if old_d:
                    d['pid'] = old_d['pid']
                    update_data[ccass_id] = d
                else:
                    new_data[ccass_id] = d
        logger.info(f" news :{len(new_data)},  update : {len(update_data)}")
        return {"update":update_data,"new":new_data}
    else:
        return  {"update":{},"new":{}}

#@task(name='participant load to db')
def load(transform_output:Dict,to_db:bool=False,db_server:str='uat'):#

    update_data, new_data=transform_output.get('update'), transform_output.get('new')
    if new_data and to_db:
        sql_query.insert_participants(data=[d for ccass_id, d in new_data.items()],db_server=db_server)
    if update_data and to_db:
        sql_query.update_participants(data=[d for ccass_id, d in update_data.items()],db_server=db_server)

#

def get_participants(run_date:Union[datetime,date,str]=date.today().strftime("%Y-%m-%d"),back_day:int=0,to_db:bool=True):
        scrapy_data = scrapy_extract(run_date=run_date,back_day=back_day )
        sql_data = sql_extract(db_server='pro1')
        transform_output=transform(scrapy_data=scrapy_data,sql_data=sql_data)
        for db_server in ['uat','pro1','pro2']:
            load( transform_output=transform_output,to_db=to_db,db_server=db_server)



@click.command()
@click.option("--shareholdingdate",default=None,help='Please insert shareholdingdate at format of either %Y-%m-%d %H:%M:%S or %Y-%m-%d',show_default=True)
@click.option("--to_db",default=True,help='Please type either True or False',show_default=True)
def run_scrapy(shareholdingdate:Union[str,datetime,date]=None,to_db:bool=True):
    if shareholdingdate is None:
       get_participants(back_day=0,to_db=to_db)
    else:
        shareholdingdate=tools.convert2datetime(shareholdingdate)
        if shareholdingdate:
            get_participants(run_date=shareholdingdate,back_day=0, to_db=to_db)
        else:
            logging.error(f"shareholdingdate is wrong format :{shareholdingdate}")
            pass



if __name__=='__main__':
    run_scrapy()

