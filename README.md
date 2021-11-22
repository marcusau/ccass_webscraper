# Introduction
#### This project aims to  provide a web-scraping robot to extract and download the CCASS information from HKEX webpage . 
#### English:  https://www.hkexnews.hk/sdw/search/searchsdw.aspx
#### Chinese:  https://www.hkexnews.hk/sdw/search/searchsdw_c.aspx


# CCASS web-scraper module

The CCASS module is divided into two sub-modules: web-scrapper and Dayend processing
The web-scraping module is built by python3.7.9 with web-scrapping application (e.g. requests, multi-thread) and is targeted to fetch CCASS data for about ~2800 listco on daily basis in Tue-Sat for each week.


The whole module pipeline is built at sequential order. To build the module in server, you have to run the scripts at pre-defined sequences

1. Data Retrieval
2. Theme-Stock mapping
3. Natural Language Processing (NLP) application (nlp\_app)
4. web application (web)

## Module flow-chart

![](demo_configs/flow.jpg)

## Purpose
