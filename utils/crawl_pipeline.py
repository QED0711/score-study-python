import pandas as pd
import concurrent.futures
from work_crawler import get_work_pages, get_score_links, get_all_pdf_links

class CrawlPipeline():

    def __init__(self, composer_chart):
        self.composer_chart = composer_chart

    def _create_works_df(self):
        self.works_df = get_work_pages(self.composer_chart)[["Page Name", "Year", "composer", "link"]]
        self.works_df['pdfs'] = None

    def get_work_pdfs(self, max_scores=None):
        for i, row in self.works_df.iterrows():
            scores = get_score_links(row['link'])
            pdfs = get_all_pdf_links(scores)
            row.pdfs = pdfs if len(pdfs) > 0 else None
            
            if max_scores:
                if i > max_scores: 
                    return

    def _run_threaded_crawler(self, link):
        scores = get_score_links(link)
        pdfs = get_all_pdf_links(scores)
        print(link)
        print(scores)
        print(pdfs)

    def threaded_get_pdfs(self, threads=1):
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self._run_threaded_crawler, self.works_df.link)

    def save_to_mlab(self):
        pass
