import sys
sys.path.append("./utils/")
sys.path.append("./json/")

import warnings
warnings.filterwarnings("ignore")

from work_crawler import save_to_mlab
from keys import *
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
import pdb
import json
import os



#################
# GET COMPOSERS #
#################

for root, dirs, files in os.walk("./json"):
    composers = [file.split(".")[0] for file in files]

###########
# HELPERS #
###########


def is_bytes(resp):
    try:
        resp.content.decode()
        return True
    except:
        return False

def json_range(composers, start=None, stop=None):
    start_index = 0
    stop_index = -1
    
    if start:
        start_index = composers.index(start)
        
    if stop:
        stop_index = composers.index(stop) + 1
        
    return composers[start_index:stop_index]


#####################
# PROCESS COMPOSERS #
#####################


class ProcessComposer():

    def __init__(self, composer):
        composer_json = self._get_json(composer)
        self._create_composer_df(composer_json)

    def _get_json(self, composer):
        with open(f"./json/{composer}.json", "r") as file:
            composer_json = json.load(file)
        return composer_json

    def _create_composer_df(self, composer_json):
        composer_df = pd.DataFrame(composer_json)
        composer_df['score_ids'] = composer_df.scores.apply(
            lambda score_lst: [int(x.split("/")[-1]) for x in score_lst])
        self.composer_df = composer_df

    def _process_work(self, work):
        pdfs = []
        for score_id in work.score_ids:
            resp = requests.get(
                f"https://imslp.org/wiki/Special:IMSLPDisclaimerAccept/{score_id}", headers={"X-Forwarded-For": "24.18.100.31"})
            try:
                soup = BeautifulSoup(resp.content)
                pdfs.append(
                    soup.find("span", {"id": "sm_dl_wait"}).get("data-id"))
            except:
                time.sleep(sleep_time)
                continue

            time.sleep(sleep_time)

        return pdfs

    def _save_work(self, work_dict):
        save_to_mlab(work_dict)

    def run_work_retrieval(self, start=0, stop=-1, log=False):
        for i, row in self.composer_df[start:stop].iterrows():
            pdfs = self._process_work(row)
            row_dict = row.to_dict()

            row_dict["pdfs"] = pdfs
            if len(pdfs) > 0:
                self._save_work(row_dict)


if __name__ == "__main__":
    import gc

    composers = sorted(composers)

    try:
        start = sys.argv[1]
    except:
        start = None
    try:
        stop = sys.argv[2]
    except:
        stop = None

    composers = json_range(composers, start, stop)

    for composer in composers:
        import gc
        
        cp = ProcessComposer(composer)
        cp.run_work_retrieval()
        cp = None
        gc.collect()
