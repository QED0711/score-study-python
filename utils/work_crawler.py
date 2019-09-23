import requests
import pandas as pd
from urllib import parse
from bs4 import BeautifulSoup

#################
# GET NEXT PAGE #
#################

def get_next_page(current_soup):
    
    links = current_soup.findAll('a', {"class":"categorypaginglink"})
    for link in links:
        if link.text == "next 200":
            return "https://imslp.org/" + link.get("href")
        
    return None

##################
# GET WORK PAGES #
##################

def format_work_df(df):
    df['link'] = df['Page Name'].apply(lambda x: "https://imslp.org/wiki/" + x.replace(" ", "_"))
    
    return df

def extract_composer_name(url):
    s = url.split("&")[0].split(":")[-1]
    return parse.unquote(s)
    

def get_work_pages(url):
    dfs = []
    composer = extract_composer_name(url)
    while url:
        html = requests.get(url).content
        table = pd.read_html(html)[0]
        dfs.append(table)
        
        soup = BeautifulSoup(html)
        url = get_next_page(soup)
        
    df = pd.concat(dfs)
    df['composer'] = composer
    
    return format_work_df(df).reset_index().drop("index", axis=1)