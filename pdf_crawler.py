from googleapiclient.discovery import build
import requests
from optparse import OptionParser
from datetime import datetime
from email.utils import parsedate_to_datetime
import csv
import os
from urllib.parse import urlparse

class PDFDownloader:
    def __init__(self, api_key, cse_id, query, num_results=100, max_size=10000000, cutoff_date=None, csv_file='crawled_pdfs.csv'):
        self.api_key = api_key
        self.cse_id = cse_id
        self.query = query
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

    def search_pdfs(self):
        return self.search_pdfs_until_goal(self.query, self.num_results)

    def is_valid_domain(self, pdf_url, allowed_tlds):
        parsed_url = urlparse(pdf_url)
        domain = parsed_url.netloc
        return any(domain.endswith(tld) for tld in allowed_tlds)

    def is_valid_pdf(self, response):
        return response.headers.get('Content-Type') == 'application/pdf'

    def is_below_max_size(self, response):
        size = int(response.headers.get('Content-Length', 0))
        return self.max_size is None or size <= self.max_size

    def is_newer_than_cutoff(self, last_modified_unix):
        return self.cutoff_date is None or last_modified_unix >= self.cutoff_date

    def download_single_pdf(self, pdf_url, formatted_date):
        try:
            r = requests.get(pdf_url)
            filename = os.path.join('out', f"{formatted_date}_{pdf_url.split('/')[-1]}")
            with open(filename, 'wb') as f:
                f.write(r.content)
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([pdf_url, filename])
            print(f"{filename} downloaded")
            return True
        except requests.exceptions.RequestException:
            print(f"Error downloading {pdf_url}. Skipping.")
            return False

    def search_pdfs_until_goal(self, query, goal):
        all_items, start_index = [], 1
        while len(all_items) < goal:
            try:
                res = self.service.cse().list(q=query, cx=self.cse_id, num=10, start=start_index).execute()
                if 'items' not in res:
                    break  # No more search results
                all_items.extend(res['items'])
                start_index += 10
            except Exception as e:
                print(f"Error fetching search results: {e}")
                break
        return all_items

    def download_pdfs(self):
        saved_count, skipped_count, successful_downloads = 0, 0, 0
        allowed_tlds = ['.de']
        items = self.search_pdfs()

        if not os.path.exists('out'): os.makedirs('out')

        while successful_downloads < self.num_results:
            for item in items:
                if successful_downloads >= self.num_results:
                    break
                
                pdf_url = item['link']

                if not self.is_valid_domain(pdf_url, allowed_tlds):
                    print(f"{pdf_url} is not from an allowed domain. Skipping.")
                    skipped_count += 1
                    continue

                try:
                    response = requests.head(pdf_url)
                except requests.exceptions.RequestException:
                    print(f"Error fetching {pdf_url}. Skipping.")
                    skipped_count += 1
                    continue

                if not self.is_valid_pdf(response):
                    print(f"{pdf_url} is not a valid PDF. Skipping.")
                    skipped_count += 1
                    continue

                last_modified = parsedate_to_datetime(response.headers.get('Last-Modified', ''))
                last_modified_unix = datetime.timestamp(last_modified)

                if not self.is_newer_than_cutoff(last_modified_unix):
                    print(f"{pdf_url} is older than the cutoff date. Skipping.")
                    skipped_count += 1
                    continue

                if not self.is_below_max_size(response):
                    print(f"{pdf_url} is too large. Skipping.")
                    skipped_count += 1
                    continue

                formatted_date = last_modified.strftime("%Y%m%d")
                if self.download_single_pdf(pdf_url, formatted_date):
                    successful_downloads += 1
                    saved_count += 1
                else:
                    skipped_count += 1

            if successful_downloads < self.num_results:
                new_items = self.search_pdfs_until_goal(self.query, self.num_results - successful_downloads)
                if not new_items:
                    break  # No more search results available
                items = new_items  # Replace old items with newly fetched items

        print(f"Total PDFs saved: {saved_count}")
        print(f"Total PDFs skipped: {skipped_count}")


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-k", "--key", dest="api_key", help="Google API key")
    parser.add_option("-c", "--cse", dest="cse_id", help="Custom Search Engine ID")
    parser.add_option("-q", "--query", dest="query", help="Search query")
    parser.add_option("-n", "--num", dest="num_results", type="int", help="Number of PDFs")
    parser.add_option("-s", "--size", dest="max_size", type="int", help="Maximum size of PDFs in bytes")
    parser.add_option("--cutoff_date", dest="cutoff_date", help="Only download PDFs modified after this date (format: YYYY-MM-DD)")

    (options, args) = parser.parse_args()

    if options.cutoff_date:
        try:
            options.cutoff_date = datetime.strptime(options.cutoff_date, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format for cutoff_date. Use YYYY-MM-DD.")
            exit(1)

    downloader = PDFDownloader(api_key=options.api_key, cse_id=options.cse_id, query=options.query, num_results=options.num_results, max_size=options.max_size, cutoff_date=options.cutoff_date)
    downloader.download_pdfs()
    print("All PDFs downloaded.")
