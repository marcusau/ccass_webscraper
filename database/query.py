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
from dataclasses import dataclass, asdict

from datetime import datetime, date
from tqdm import tqdm

import mysql.connector

from Config.setting import Info as config

##############---------------------------------------------------------------------------------------------------------------------------

@dataclass
class db_configs:
    host: str
    port : Union[str,int]
    user : str
    password: str
    database:str
    use_unicode: bool = True
    get_warnings: bool = True

@dataclass
class DB_Servers:
    uat: db_configs
    pro1 :db_configs
    pro2: db_configs

uat_conf, pro1_conf, pro2_conf = db_configs(host=config.db.UAT.host,port=int(config.db.UAT.port), user=config.db.UAT.user, password=config.db.UAT.password,database=config.db.UAT.schema), \
                                        db_configs(host=config.db.prod_1.host,port=int(config.db.prod_1.port), user=config.db.prod_1.user, password=config.db.prod_1.password,database=config.db.prod_1.schema), \
                                        db_configs(host=config.db.prod_2.host,port=int(config.db.prod_2.port), user=config.db.prod_2.user, password=config.db.prod_2.password,database=config.db.prod_2.schema)

db_servers=DB_Servers(uat=uat_conf,pro1=pro1_conf,pro2=pro2_conf)
db_tables=config.db.tables

##############---------------------------------------------------------------------------------------------------------------------------

def insert_stocks(data:List[Dict],db_server:str='uat'):
    db_choices=asdict(db_servers)
    db_chosen=db_choices.get(db_server)
    if db_chosen is None:
        print(f'db server :{db_server} is wrong, please choose uat, pro1 or pro2')
        pass
    else:
        db = mysql.connector.connect(**db_chosen)  #mysql.connector.connect(**config)
        cursor = db.cursor(dictionary=True)
        data=  [(d['stockcode'],  d['exchange'],  d['ccass_id'],  d['name_eng'],  d['name_chi'], d['listing'], d['update_time']) for d in tqdm(data,desc='insert stocks in db')]

    # uat_db,pro1_db,pro2_db = mysql.connector.connect(**asdict(db_servers.uat)),mysql.connector.connect(**asdict(db_servers.pro1)),mysql.connector.connect(**asdict(db_servers.pro2))
    # uat_cur, pro1_cur,pro2_cur= uat_db.cursor(),pro1_db.cursor(),pro2_db.cursor()

        stmt_insert = f"INSERT INTO  {db_tables.stocks} (stockcode,exchange,ccass_id,name_eng,name_chi,listing,update_time) VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE name_eng=name_eng, name_chi=name_chi, listing=listing, update_time=update_time;  "
    #
    # uat_cur.executemany(stmt_insert, data), pro1_cur.executemany(stmt_insert, data), pro2_cur.executemany(stmt_insert, data)
    # uat_db.commit(), pro1_db.commit(), pro2_db.commit()
    # uat_cur.close(), pro1_cur.close(),pro2_cur.close()
    # uat_db.close() pro1_db.close(), pro2_db.close()
        cursor.executemany(stmt_insert, data)
        db.commit()
        cursor.close()
        db.close()

def get_stocks(limit:Union[int,str,None]=None, exchange:str=None,db_server:str='uat'):

    db_choices=asdict(db_servers)
    db_chosen=db_choices.get(db_server)
    if db_chosen is None:
        print(f'db server :{db_server} is wrong, please choose uat, pro1 or pro2')
        return {}
    else:
        db = mysql.connector.connect(**db_chosen)  #mysql.connector.connect(**config)
        cursor = db.cursor(dictionary=True)

        stmt_select = f"select * from  {db_tables.stocks} "
        if exchange:
            stmt_select = f"{stmt_select} where {db_tables.stocks}.exchange='{exchange.upper()}'"
        stmt_select=f"{stmt_select} order by stockcode, exchange  "
        if limit:
            stmt_select = f"{stmt_select} limit {limit} "

        cursor.execute(stmt_select)
        records={f"{str(d['stockcode'])}.{d['exchange']}": d for d in tqdm(cursor.fetchall(),desc=f"fetch stock data from db")}
        cursor.close()
        db.close()
        return records

def update_stocks(data:List[Dict],db_server:str='uat'):
    db_choices=asdict(db_servers)
    db_chosen=db_choices.get(db_server)
    if db_chosen is None:
        print(f'db server :{db_server} is wrong, please choose uat, pro1 or pro2')
        pass
    else:
        db = mysql.connector.connect(**db_chosen)  #mysql.connector.connect(**config)
        cursor = db.cursor(dictionary=True)
        data=  [( str(d['ccass_id']), unicodedata.normalize('NFKD', str(d['name_eng'])), unicodedata.normalize( 'NFKD',str(d['name_chi'])),  d['listing'] , d['update_time'] , str(d['stockcode']),  str(d['exchange']) ) for d in tqdm(data,desc=f' updating stock in db')]
        # db = mysql.connector.connect(**config)
        # cursor = db.cursor()
        stmt_udpate= f"UPDATE {db_tables.stocks} SET ccass_id=%s , name_eng=%s , name_chi=%s , listing=%s , update_time=%s WHERE stockcode=%s and exchange=%s"
        cursor.executemany( stmt_udpate,data)
        cursor.close()
        db.commit()
        db.close()

# ###--------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_participants(limit:Union[int,str,None]=None,p_type:Union[int,str,None]=None,db_server:str='uat'):
    db_choices=asdict(db_servers)
    db_chosen=db_choices.get(db_server)
    if db_chosen is None:
        print(f'db server :{db_server} is wrong, please choose uat, pro1 or pro2')
        return {}
    else:

        db=mysql.connector.connect(**db_chosen)
    # db = mysql.connector.connect(**config)
        cursor = db.cursor(dictionary=True)
        stmt_select = f"select * from  {db_tables.participants} "

        if p_type:
            stmt_select=stmt_select+ f"where p_type='{p_type}'"

        stmt_select=stmt_select+f" order by pid"
        if limit:
            stmt_select = stmt_select +f"limit {limit} "

        stmt_select = stmt_select + f"; "
        cursor.execute(stmt_select)
        if p_type=='Intermediaries':
            records={f"{str(d['ccass_id'])}": d for d in tqdm(cursor.fetchall(),desc=f"fetch participants from db")}
        elif  p_type=='investp':
            records = {f"{str(d['name_chi'])}": d for d in tqdm(cursor.fetchall(), desc=f"fetch participants from db")}
        else:
            records = {f"{int(d['pid'])}": d for d in tqdm(cursor.fetchall(), desc=f"fetch participants from db")}
        cursor.close()
        db.close()
        return records


def insert_participants(data,db_server:str='uat'):
    db_choices=asdict(db_servers)
    db_chosen=db_choices.get(db_server)
    if db_chosen is None:
        print(f'db server :{db_server} is wrong, please choose uat, pro1 or pro2')
        pass
    else:

        db=mysql.connector.connect(**db_chosen)
        cursor = db.cursor()
        data=  [(d['ccass_id'], d.get('name_eng',None),   d.get('name_chi',None), d.get('address',None), d['p_type'], d['update_time']) for d in data]

        stmt_insert = f"INSERT INTO  {db_tables.participants} (ccass_id, name_eng, name_chi,address, p_type, update_time) VALUES (%s, %s, %s, %s,%s,  %s) ON DUPLICATE KEY UPDATE  name_chi=name_chi ,address=address, update_time=update_time  "
        cursor.executemany(stmt_insert, data)

        db.commit()
        cursor.close()
        db.close()

def update_participants(data,pid_exist:bool=True,db_server:str='uat'):


    if pid_exist:
        data=  [(d['ccass_id'],d.get('name_eng',None),   d.get('name_chi',None), d.get('address',None),  d['update_time'],  int(d['pid']) ) for d in data]
    else:
        data =  [(d['ccass_id'], d.get('name_eng',None),  d.get('address',None),  d['update_time'] , d.get('name_chi', None)) for d in data]

    db_choices=asdict(db_servers)
    db_chosen=db_choices.get(db_server)
    if db_chosen is None:
        print(f'db server :{db_server} is wrong, please choose uat, pro1 or pro2')
        pass
    else:

        db = mysql.connector.connect(**db_chosen)
        cursor = db.cursor()
        if pid_exist:
            stmt_udpate= f"update  {db_tables.participants} SET ccass_id= %s,name_eng= %s,  name_chi= %s, address= %s,update_time=%s WHERE pid= %s ;"
        else:
            stmt_udpate = f"update  {db_tables.participants} SET ccass_id= %s, name_eng= %s,  address= %s, update_time=%s WHERE name_chi= %s ;"
        cursor.executemany( stmt_udpate,data)
        cursor.close()
        db.commit()
        db.close()

def delete_empty_participant(db_server:str='uat'):
    db_choices=asdict(db_servers)
    db_chosen=db_choices.get(db_server)
    if db_chosen is None:
        print(f'db server :{db_server} is wrong, please choose uat, pro1 or pro2')
        pass
    else:
        db = mysql.connector.connect(**db_chosen)
        cursor = db.cursor()

        delete_p_type, delete_name_chi,delete_non_pid='Intermediaries','香港中央結算有限公司',16

        stmt_delete = f"delete FROM  {db_tables.participants} where p_type='{delete_p_type}' and name_chi='{delete_name_chi}' and pid not in ({delete_non_pid}); "
        cursor.execute(stmt_delete)

        db.commit()

        cursor.close()
        db.close()

# ##----------------------------------------------------------------------------------------------------------

def get_stock_connect_date(limit:Union[int,str,None]=None,db_server:str='uat'):

    db_choices=asdict(db_servers)
    db_chosen=db_choices.get(db_server)
    if db_chosen is None:
        print(f'db server :{db_server} is wrong, please choose uat, pro1 or pro2')
        return []
    else:
        db = mysql.connector.connect(**db_chosen)
        cursor = db.cursor(dictionary=True)
        stmt_select = f"select distinct shareholdingdate from {db_tables.stock_connect} "

        stmt_select=stmt_select+f" order by shareholdingdate desc "
        if limit:
            stmt_select = stmt_select +f" limit {limit} "


        cursor.execute(stmt_select)
        records=[d['shareholdingdate'] for d in tqdm(cursor.fetchall(),desc=f"fetch stock_ connect shareholdingdate from db ")]
        cursor.close()
        db.close()
        return records

def insert_stock_connect(data:List[Tuple],db_server:str='uat'):
    db_choices=asdict(db_servers)
    db_chosen=db_choices.get(db_server)
    if db_chosen is None:
        print(f'db server :{db_server} is wrong, please choose uat, pro1 or pro2')
        pass
    else:
    #    db = mysql.connector.connect(**config)
        db = mysql.connector.connect(**db_chosen)
        cursor = db.cursor()

        stmt_insert = f"INSERT INTO  {db_tables.stock_connect} (shareholdingdate, stockcode, exchange,holding,ISC_pct) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE shareholdingdate=shareholdingdate, stockcode=stockcode, exchange=exchange, ISC_pct=ISC_pct;  "
        cursor.executemany(stmt_insert, data)

        db.commit()
        cursor.close()
        db.close()

#
# #####-------------------------------------------------------------------------------------------------------------------------------

def insert_summary(data:Dict,db_server:str='uat'):

    db_choices=asdict(db_servers)
    db_chosen=db_choices.get(db_server)
    if db_chosen is None:
        print(f'db server :{db_server} is wrong, please choose uat, pro1 or pro2')
        pass
    else:
    #    db = mysql.connector.connect(**config)
        db = mysql.connector.connect(**db_chosen)
        data_=  [(data['shareholdingdate'], data['stockcode'], data['inter_holding'], data['consenting_holding'], data['nonconsenting_holding'], data['inter_num'], data['consenting_num'], data['nonconsenting_num'], data['ISC']  ,data['inter_pct'] ,  data['consenting_pct'] ,data['nonconsenting_pct'], data['CIP_pct'], data['ccass_pct'],data['non_ccass_pct'])]

        cursor = db.cursor()

        stmt_insert = f"INSERT INTO  {db_tables.summary} (shareholdingdate , stockcode , inter_holding , consenting_holding , nonconsenting_holding , inter_num , consenting_num , nonconsenting_num , ISC   , inter_pct  ,  consenting_pct  , nonconsenting_pct , CIP_pct , ccass_pct , non_ccass_pct ) VALUES (%s, %s, %s, %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE shareholdingdate=shareholdingdate, stockcode=stockcode "
        cursor.executemany(stmt_insert, data_)

        db.commit()

        cursor.close()
        db.close()

#
# #####-------------------------------------------------------------------------------------

def get_main_shareholdingdate(limit:int=None,db_server:str='uat'):
    db_choices=asdict(db_servers)
    db_chosen=db_choices.get(db_server)
    if db_chosen is None:
        print(f'db server :{db_server} is wrong, please choose uat, pro1 or pro2')
        return []
    else:
        db = mysql.connector.connect(**db_chosen)## mysql.connector.connect(**config)
        cursor = db.cursor(dictionary=True)
        stmt_select = f"SELECT distinct shareholdingdate FROM {db_tables.main}  order by shareholdingdate desc  "
        if limit:
            stmt_select = stmt_select + f" limit {limit} "
        cursor.execute(stmt_select)
        records = [i['shareholdingdate'] for i in cursor.fetchall()]
        cursor.close()
        db.close()
        return records


def insert_main(data:List[Dict],db_server:str='uat'):
    db_choices=asdict(db_servers)
    db_chosen=db_choices.get(db_server)
    if db_chosen is None:
        print(f'db server :{db_server} is wrong, please choose uat, pro1 or pro2')
        pass
    else:
    #    db = mysql.connector.connect(**config)
        db = mysql.connector.connect(**db_chosen)
        data_=  [(d['shareholdingdate'],d['stockcode'], d['pid'], d['holding'], d['ISC_pct']) for d in data]
       # db = mysql.connector.connect(**config)
        cursor = db.cursor()

        stmt_insert = f"INSERT INTO {db_tables.main} ( shareholdingdate,stockcode, pid, holding, ISC_pct  ) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE shareholdingdate=shareholdingdate, stockcode=stockcode, pid=pid;  "
        cursor.executemany(stmt_insert, data_)

        db.commit()

        cursor.close()
        db.close()

