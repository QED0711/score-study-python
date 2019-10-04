import requests
import pdb
import time
import pymongo
from keys import *
import pandas as pd
from urllib import parse
from bs4 import BeautifulSoup

user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1"

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
    df['work_page'] = df['Page Name'].apply(lambda x: "https://imslp.org/wiki/" + x.replace(" ", "_"))
    
    return df

def extract_composer_name(url):
    s = url.split("&")[0].split(":")[-1]
    return parse.unquote(s)
    

def get_work_pages(url):
    dfs = []
    composer = extract_composer_name(url)
    while url:
        html = requests.get(url, timeout=3, headers={"User-Agent": user_agent}).content
        time.sleep(0.5)
        table = pd.read_html(html)[0]
        dfs.append(table)
        
        soup = BeautifulSoup(html, features='lxml')
        url = get_next_page(soup)
        
    df = pd.concat(dfs)
    df['composer'] = composer
    
    return format_work_df(df).reset_index().drop("index", axis=1)



###################
# GET SCORE LINKS #
###################

def get_score_links(score_url):
    soup = BeautifulSoup(requests.get(score_url, timeout=3, headers={"User-Agent": user_agent}).content, features='lxml')
    time.sleep(0.5)
    links = soup.find_all('a', {'class': 'external text'})

    complete_scores = []

    for link in links:
        if link.text.lower().strip() in ['complete score']:
            complete_scores.append(link.get('href'))
            
    return complete_scores


#################
# GET PDF LINKS #
#################
def get_pdf_link(url):
    soup = BeautifulSoup(requests.get(url, timeout=3, headers={"User-Agent": user_agent}).content, features='lxml')
    return soup.find("span", {"id":"sm_dl_wait"})


def get_all_pdf_links(score_links):
    pdfs = []
    for score in score_links:
        score_id = score.split('/')[-1]
        current_url = "https://imslp.org/wiki/Special:IMSLPDisclaimerAccept/" + score_id

        try:
            pdfs.append(get_pdf_link(current_url).get("data-id"))
            time.sleep(0.5)
        except:
            continue

    return pdfs


################
# SAVE TO MLAB #
################

def generate_id(entry):
    # entry["_id"] = f"{entry['composer']}-{entry['work_name']}"
    entry["_id"] = f"{entry['composer']}-{entry['title']}"
    return entry

uri = f"mongodb://{mlab['username']}:{mlab['password']}@ds151076.mlab.com:51076/score-study-app"

def save_to_mlab(entry):
    
    # DB Setup
    client = pymongo.MongoClient(uri, retryWrites=retryWrites)
    db = client.get_default_database()

    works = db['works']

    # Preparing data for entry
    entry = generate_id(entry)

    try:
        works.insert(entry)
    except:
        # if there was an error on inserting, likely due to document already existing
        # update instead
        works.update({"_id": entry["_id"]}, entry)

