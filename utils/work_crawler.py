import requests
import pdb
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
        html = requests.get(url, timeout=1).content
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

def get_score_links(url):
    soup = BeautifulSoup(requests.get(url, timeout=1).content, features='lxml')
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
    soup = BeautifulSoup(requests.get(url, timeout=1).content, features='lxml')
    return soup.find("span", {"id":"sm_dl_wait"})


def get_all_pdf_links(score_links):
    pdfs = []
    for score in score_links:
        score_id = score.split('/')[-1]
        current_url = "https://imslp.org/wiki/Special:IMSLPDisclaimerAccept/" + score_id

        try:
            pdfs.append(get_pdf_link(current_url).get("data-id"))
        except:
            continue

    return pdfs

