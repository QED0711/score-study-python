import pandas as pd
import concurrent.futures
from work_crawler import get_work_pages, get_score_links, get_all_pdf_links, save_to_mlab

import signal

################
# SIGNAL SETUP #
################

def handler(signum, frame):
    raise RuntimeError

signal.signal(signal.SIGALRM, handler)

class CrawlPipeline():

    def __init__(self, composer_chart):
        self.composer_chart = composer_chart
        self._create_works_df()

    def _create_works_df(self):
        self.works_df = get_work_pages(self.composer_chart)[["Page Name", "Year", "composer", "work_page"]]
        self.works_df['pdfs'] = None
        self.works_df.columns = ["work_name", "year", 'composer', 'work_page', 'pdfs']

    def get_work_pdfs(self, max_scores=None, save=True):
        for i, row in self.works_df.iterrows():
            print(i)
            scores = get_score_links(row['work_page'])
            pdfs = get_all_pdf_links(scores)
            row.pdfs = pdfs if len(pdfs) > 0 else None
            
            if save and row.pdfs:
                try:
                    signal.alarm(5)
                    save_to_mlab(row.to_dict())
                    signal.alarm(0)
                except:
                    print('skipping')
                    signal.alarm(0)

            if max_scores:
                if i > max_scores: 
                    return
    
    # def _run_threaded_crawler(self, link):
    #     scores = get_score_links(link)
    #     pdfs = get_all_pdf_links(scores)
    #     print(link)
    #     print(scores)
    #     print(pdfs)

    # def threaded_get_pdfs(self, threads=1):
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
    #         executor.map(self._run_threaded_crawler, self.works_df.link)

