import pandas as pd

from work_crawler import get_work_pages, get_score_links, get_all_pdf_links

class CrawlPipeline():

    def __init__(self, composer_chart):
        self.composer_chart = composer_chart

    def _create_works_df(self):
        self.works_df = get_work_pages(self.composer_chart)[["Page Name", "Year", "composer", "link"]]
        self.works_df['pdfs'] = None

    def get_work_pdfs(self):
        for i, row in self.works_df.iterrows():
            scores = get_score_links(row['link'])
            pdfs = get_all_pdf_links(scores)
            row.pdfs = pdfs if len(pdfs) > 0 else None
            
            if i > 5: 
                return

    def save_to_mlab(self):

