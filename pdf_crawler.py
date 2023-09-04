from googleapiclient.discovery import build
import requests
import csv
import os
from datetime import datetime
from email.utils import parsedate_to_datetime

class PDFDownloader:
    def __init__(self, api_key, cse_id, num_results=100, max_size=10000000, cutoff_date=None, csv_file='crawled_pdfs.csv'):
        self.api_key = api_key
        self.cse_id = cse_id
        self.num_results = num_results
        self.max_size = max_size
        self.cutoff_date = datetime.timestamp(cutoff_date) if cutoff_date else None
        self.csv_file = csv_file
        self.service = build("customsearch", "v1", developerKey=api_key)
        self.init_csv()

    def init_csv(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["URL", "Filename"])

    def search_pdfs(self, query):
        all_items, start_index = [], 1
        while len(all_items) < self.num_results:
            try:
                res = self.service.cse().list(q=query, cx=self.cse_id, num=10, start=start_index).execute()
                all_items.extend(res['items'])
                start_index += 10
            except Exception as e:
                print(f"Error fetching search results: {e}")
                break
        return all_items[:self.num_results]

    def download_pdfs(self, items):
        if not os.path.exists('out'): os.makedirs('out')
        
        for item in items:
            pdf_url = item['link']
            filename = os.path.join('out', pdf_url.split('/')[-1])
            try:
                response = requests.head(pdf_url)
            except requests.exceptions.RequestException:
                print(f"Error fetching {pdf_url}. Skipping.")
                continue

            if response.headers.get('Content-Type') != 'application/pdf':
                print(f"{pdf_url} is not a valid PDF. Skipping.")
                continue

            if self.cutoff_date:
                try:
                    last_modified = datetime.timestamp(parsedate_to_datetime(response.headers.get('Last-Modified', '')))
                    if last_modified < self.cutoff_date:
                        print(f"{pdf_url} is older than the cutoff date. Skipping.")
                        continue
                except:
                    pass

            size = int(response.headers.get('Content-Length', 0))
            if self.max_size and size > self.max_size:
                print(f"{pdf_url} is too large. Skipping.")
                continue

            try:
                r = requests.get(pdf_url)
                with open(filename, 'wb') as f:
                    f.write(r.content)
                with open(self.csv_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([pdf_url, filename])
                print(f"{filename} downloaded")
            except requests.exceptions.RequestException:
                print(f"Error downloading {pdf_url}. Skipping.")

if __name__ == "__main__":
    # ... (Argument Parsing here)
    from optparse import OptionParser
    from datetime import datetime
    parser = OptionParser()
    parser.add_option("-k", "--key", dest="api_key", help="Google API key")
    parser.add_option("-c", "--cse", dest="cse_id", help="Custom Search Engine ID")
    parser.add_option("-q", "--query", dest="query", help="Search query")
    parser.add_option("-n", "--num", dest="num_results", type="int", help="Number of PDFs")
    parser.add_option("-s", "--size", dest="max_size", type="int", help="Maximum size of PDFs in bytes")
    parser.add_option("--cutoff_date", dest="cutoff_date", help="Only download PDFs modified after this date (format: YYYY-MM-DD)")

    (options, args) = parser.parse_args()

    # Convert cutoff_date to datetime object if it's not None
    if options.cutoff_date:
        try:
            options.cutoff_date = datetime.strptime(options.cutoff_date, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format for cutoff_date. Use YYYY-MM-DD.")
            exit(1)

    # Constructing the query with multiple terms
    if options.query:
        search_terms = options.query.split(',')
        query = " OR ".join([f"{term} filetype:pdf" for term in search_terms])
    else:
        print("Query is required.")
        exit(1)


    # Make sure to replace the cutoff_date with a string in 'YYYY-MM-DD' format or None
    downloader = PDFDownloader(api_key=options.api_key, cse_id=options.cse_id, num_results=options.num_results, max_size=options.max_size, cutoff_date=options.cutoff_date)
    search_results = downloader.search_pdfs(query)
    downloader.download_pdfs(search_results)
    print("All PDFs downloaded.")