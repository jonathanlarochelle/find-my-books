# -*- coding: utf-8 -*-

# import built-in modules
import re
import json
import logging
import argparse
import csv

# import third-party modules
import requests


APP_DESCRIPTION = "Parse a Goodreads books list to find in which library they are available."
SUPPORTED_LIBRARIES_FILE = "libraries.json"
REQUEST_HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                   'Accept-Language': 'en-US,en;q=0.5',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Upgrade-Insecure-Requests': '1',
                   'Sec-Fetch-Dest': 'document',
                   'Sec-Fetch-Mode': 'navigate',
                   'Sec-Fetch-Site': 'none',
                   'Sec-Fetch-User': '?1',
                   'Connection': 'keep-alive'}


def parse_argv() -> dict:
    """
    Parse command-line arguments into a dict.
    """
    arg_parser = argparse.ArgumentParser(description=APP_DESCRIPTION)
    arg_parser.add_argument("goodreads_library", type=str,
                            help="Goodreads library .csv file")
    arg_parser.add_argument("-o", "--output", type=str, required=False,
                            dest="output",
                            help="output .csv file")
    arg_parser.add_argument("-d", "--debug", action="store_true", required=False, default=False,
                            help="display debug logging lines")
    args = arg_parser.parse_args()
    args_dict = vars(args)
    return args_dict


def get_book_search_url(book_title: str, book_author: str, url_template: str) -> str:
    """
    Replace {TITLE} and {AUTHOR} in url_template by book_title and book_author respectively.
    """
    # Remove parenthesis and colon in book title to facilitate search.
    re_remove_parenthesis = "\(.*\)|\s-\s.*"
    book_title = re.sub(re_remove_parenthesis, "", book_title)
    re_remove_colon = ":.+"
    book_title = re.sub(re_remove_colon, "", book_title)

    url = url_template.replace("{AUTHOR}", book_author.replace(" ", "+"))
    url = url.replace("{TITLE}", book_title.replace(" ", "+"))
    return url


# Script starts here
if __name__ == '__main__':
    # Parse command line arguments
    args = parse_argv()
    goodreads_library_file_path = args["goodreads_library"]
    if args["output"]:
        output_file_path = args["output"]
    else:
        output_file_path = goodreads_library_file_path.replace(".csv", "_output.csv")

    # Set-up logging
    if args["debug"]:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    logging.basicConfig(level=logging_level)

    logging.info("FindMyBooks")
    logging.info(f"\tGoodreads library file path: {goodreads_library_file_path}")
    logging.info(f"\tOutput file path: {output_file_path}")

    # Load Goodreads library file
    books_to_check = list()
    with open(goodreads_library_file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)

        # Consider only "to-read" books
        for book in reader:
            if book["Exclusive Shelf"] == "to-read":
                books_to_check.append({"title": book["Title"],
                                       "author": book["Author"]})
        logging.info(f"\tFound {len(books_to_check)} books in to-read shelf.")

    # Load supported libraries from json config file
    with open(SUPPORTED_LIBRARIES_FILE) as f:
        supported_libraries = json.load(f)["libraries"]
    logging.info(f"\tFound {len(supported_libraries)} supported libraries.")

    for id, book in enumerate(books_to_check):
        logging.debug(f"\tBook: {book['author']}, \"{book['title']}\"")

        for lib in supported_libraries:
            books_to_check[id][lib["name"]] = ""
            logging.debug(f"\tLibrary: {lib['name']} ({lib['response_length_threshold']} bytes response length threshold)")
            url = get_book_search_url(book["title"], book["author"], lib["url"])
            logging.debug(f"\tURL: {url}")

            # Using a GET is a waste of download. However, not all websites provide Content-Length with HEAD,
            # and some do not answer to HEAD at all.
            # TODO: Figure out way to check libraries with smaller footprint. Idea: pretend to be mobile, very small screen, etc.
            # REQUEST_HEADERS is used because some websites require a "realistic" header to answer the request.
            # TODO: Figure out what is the minimal header required.
            response = requests.get(url, headers=REQUEST_HEADERS)
            if response:
                response_content_length = len(response.content)
                logging.debug(f"\tContent size: {response_content_length} bytes")
                if response_content_length > lib["response_length_threshold"]:
                    books_to_check[id][lib["name"]] = url

    # Create output file
    with open(output_file_path, "w", newline="") as csvfile:
        fieldnames = books_to_check[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for book in books_to_check:
            writer.writerow(book)
    logging.info(f"\tResults written to output file {output_file_path}")

    logging.info("Script execution successfully completed.")
