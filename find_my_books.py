import pandas as pd
import requests
import re
import json
import logging

# Description: From a provided export of a goodreads library in .csv format, search for ebook availability in specific
# online libraries. Those results are provided in a supplementary .csv file.

# USER PARAMETERS
GOODREADS_LIBRARY_EXPORT_FILE_PATH = "test_library.csv"
OUTPUT_FILE_PATH = "test_output.csv"
# GOODREADS_LIBRARY_EXPORT_FILE_PATH = "goodreads_library_export.csv"
# OUTPUT_FILE_PATH = "output.csv"
LOGGING_LEVEL = logging.DEBUG

# SCRIPT


def get_book_address_in_library(book_infos: pd.Series, lib: dict):
    # Returns the url of the book if it is found, None otherwise.
    logging.debug("get_book_address_in_library()")
    logging.debug(f"\tLibrary: {lib['name']}")
    logging.debug(f"\tBook: {book_infos['Author']}, \"{book_infos['Title']}\"")

    url = lib["url"]
    url = url.replace("{AUTHOR}", book_infos["Author"].replace(" ", "+"))
    url = url.replace("{TITLE}", book_infos["Title"].replace(" ", "+"))
    # Some websites need a more realistic header. TODO: Investigate exactly what part of the header is required.
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
              'Accept-Language': 'en-US,en;q=0.5',
              'Accept-Encoding': 'gzip, deflate, br',
              'Upgrade-Insecure-Requests': '1',
              'Sec-Fetch-Dest': 'document',
              'Sec-Fetch-Mode': 'navigate',
              'Sec-Fetch-Site': 'none',
              'Sec-Fetch-User': '?1',
              'Connection': 'keep-alive'}
    logging.debug(f"\tURL: {url}")

    # Using a GET is a waste of download. However, not all websites provide Content-Length with HEAD, and some do not
    # answer to HEAD at all.
    # TODO: Figure out way to check libraries with smaller footprint. Idea: pretend to be mobile, very small screen, etc.
    response = requests.get(url, headers=headers)
    nb_bytes = len(response.content)

    logging.debug(f"\tContent size: {nb_bytes} bytes (threshold: {lib['response_size_threshold']} bytes)")

    if response:
        if nb_bytes < lib["response_size_threshold"]:
            return ""
        else:
            return url
    else:
        logging.warning(f"An error has occured. Response status code: {response.status_code}")

if __name__=='__main__':
    # 1) Read Goodreads library .csv
    # 2) Keep only books with "Exclusive shelf" = "to-read"
    # 3) Keep only columns "Title", "Author".
    # 4) Search for books available on Banq (Overdrive)
    # 5) Search for books available on quebec.pretsnumerique.ca
    # 6) Search for books available on Kobo plus
    # 7) Put results together in output .csv

    logging.basicConfig(level=LOGGING_LEVEL)

    logging.info("Where can I rent ebooks that I have on my Goodreads to-read shelf?")
    logging.info("\tScript developed by Jonathan Larochelle, June 2022\n")
    logging.info("Starting script ...")
    logging.info("1) Loading Goodreads library")
    logging.info(f"\tGoodreads Export file: {GOODREADS_LIBRARY_EXPORT_FILE_PATH}")

    df = pd.read_csv(GOODREADS_LIBRARY_EXPORT_FILE_PATH, header=0, usecols=["Title", "Author", "Exclusive Shelf"])
    df = df[df["Exclusive Shelf"] == "to-read"]
    df = df.reset_index()
    df.drop("Exclusive Shelf", axis=1, inplace=True)
    re_remove_parenthesis = "\(.*\)|\s-\s.*"
    df["Title"] = df["Title"].apply(lambda x: re.sub(re_remove_parenthesis, "", x))
    re_remove_colon = ":.+"
    df["Title"] = df["Title"].apply(lambda x: re.sub(re_remove_colon, "", x))
    nb_books = df.shape[0]
    logging.info(f"\tFound {nb_books} books in to-read shelf.")

    logging.info("2) Searching in libraries")
    with open("libraries.json") as f:
        libraries = json.load(f)["libraries"]
        for library in libraries:
            if library["name"] in ["BANQ (Overdrive)", "Ville de Québec (Prêt Numérique)"]:
                continue
            df[library["name"]] = df.apply(lambda x: get_book_address_in_library(x, library), axis="columns")

    logging.info("5) Producing output file")
    df.to_csv(OUTPUT_FILE_PATH)
    logging.info(f"\tResults output to {OUTPUT_FILE_PATH}")

    logging.info("Script execution successfully completed.")