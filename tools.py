# -*- coding: utf-8 -*-
import json,csv,re,time,pathlib,os,sys

sys.path.append(os.getcwd())

parent_path = pathlib.Path(__file__).parent.absolute()
sys.path.append(str(parent_path))

master_path = parent_path.parent
sys.path.append(str(master_path))

project_path = master_path.parent
sys.path.append(str(project_path))

from typing import Union,List,Dict

from tqdm import tqdm
import time
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date

import requests
####------------------------------------------------------------------------------------

def myTimer(func):
    def wrapper(*args, **kargs):
      t1 = time.time()
      result = func(*args, **kargs)
      t2 = time.time() - t1
      print('Execution Time (function : {}) : {} sec'.format(func.__name__, t2))
      return result

    return wrapper

def trade_days_list(trade_day_url:str):
    resp= requests.get(trade_day_url)
    decode_resp=resp.text.split('\n')[-1].split(',')[-1]
    trade_days_timestamps=[int(s)/1000 for s in decode_resp.split('|')]
    trade_days_dt=[datetime.fromtimestamp(s) for s in trade_days_timestamps]
    return trade_days_dt

def date2dateime(dt:date):
    return datetime(year=dt.year, month=dt.month, day=dt.day, hour=0,    minute=0, second=0)

def convert2datetime(shareholdingdate:Union[date,datetime,str])->Union[datetime,None]:
    if isinstance(shareholdingdate,datetime):
        return shareholdingdate
    elif isinstance(shareholdingdate,date):
        return date2dateime(shareholdingdate)
    elif isinstance(shareholdingdate,str) and len(shareholdingdate) in [10,19]:
        return datetime.fromisoformat(shareholdingdate)
    else:
        return None

def datetime2date(dt:datetime):
    return date.fromisoformat(dt.strftime('%Y-%m-%d %H:%M:%S')[:10])

def convert2date(shareholdingdate:str)->Union[date,None]:

    if len(shareholdingdate)==10:
        return date.fromisoformat(shareholdingdate)

    elif len(shareholdingdate)==19:
        dt= datetime.fromisoformat(shareholdingdate)
        return datetime2date(dt)
    else:
        print(f' wrong format of shareholdingdate: {shareholdingdate}')
        return None


# if __name__=="__main__":
#    print(convert2datetime('2021-10-09'))