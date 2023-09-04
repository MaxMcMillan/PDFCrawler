# Download (PDF) Files using Google Custom Search Engine API

## Overview

This repository contains a Python-based tool for downloading PDF files based on search queries using Google's Custom Search Engine API. The tool is configurable, allowing you to specify the number of results, maximum PDF size, and a date cutoff for the files you want to download.

## Features

- Search for PDFs based on a query string
- Download PDFs that meet specific criteria:
  - From specific domains (e.g., `.de`, `.com`)
  - Below a given file size
  - Modified after a certain date
- Save metadata about downloaded PDFs to a CSV file

## Installation

1. Clone this repository to your local machine.
2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To use the PDF Downloader, you'll need a Google API key and a Custom Search Engine ID. Once you have these:

1. Open your terminal and navigate to the directory where the script is located.
2. Run the script with the necessary command-line options:

    ```bash
    python pdf_downloader.py \
      --key YOUR_GOOGLE_API_KEY \
      --cse YOUR_CUSTOM_SEARCH_ENGINE_ID \
      --query "Your Search Query" \
      --num 100 \
      --size 10000000 \
      --cutoff_date "2023-01-01"
    ```

### Command-Line Options

- `--key`: Your Google API key (required)
- `--cse`: Your Custom Search Engine ID (required)
- `--query`: Search query for PDFs (required)
- `--num`: Number of PDFs to download (optional, default is 100)
- `--size`: Maximum size of PDFs in bytes (optional, default is 10,000,000)
- `--cutoff_date`: Only download PDFs modified after this date (optional, format: YYYY-MM-DD)


## Next Steps
- write unit tests
- improve readability, refactor `download_pdfs()`
- add functionality for multiple file types
