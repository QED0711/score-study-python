import sys
sys.path.append('./utils')
import pdb

import pandas as pd

from crawl_pipeline import CrawlPipeline
from work_crawler import get_work_pages, get_score_links, get_all_pdf_links, save_to_mlab
from mlab_db import get_composers

if __name__ == '__main__':
    composers = get_composers()
    urls = [c['composer_url'] for c in composers if not c.get('visited')] 
    for url in urls:
        cp = CrawlPipeline(url)
        cp.get_work_pdfs(max_scores=None) # set max_scores to set limit