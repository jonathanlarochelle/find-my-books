import pandas as pd
import requests
import re
import time

# update_sources_list.py
# Author: Jonathan Larochelle
# Date of creation: 25.06.2022

# Description: From a provided export of a goodreads library in .csv format, search for ebook availability in specific
# online libraries. Those results are provided in a supplementary .csv file.

# USER PARAMETERS
# GOODREADS_LIBRARY_EXPORT_FILE_PATH = "test_library.csv"
# OUTPUT_FILE_PATH = "test_output.csv"
GOODREADS_LIBRARY_EXPORT_FILE_PATH = "goodreads_library_export.csv"
OUTPUT_FILE_PATH = "output.csv"

# SCRIPT


def add_links(source: str, row):
    """
    source: One of ["banq.overdrive.com", "quebec.pretnumerique.ca", "Kobo Plus", "Stadtbibliothek Freiburg", "Onleihe Freiburg", "UB Freiburg"]
    """
    if source == "banq.overdrive.com":
        url = f"https://banq.overdrive.com/search/title?query={row['Title'].replace(' ', '+')}" \
              f"&creator={row['Author'].replace(' ', '+')}&mediaType=ebook&sortBy=newlyadded"
        headers = {}
        not_found_str = "Results-noResultsHeading"
    elif source == "quebec.pretnumerique.ca":
        url = f"https://quebec.pretnumerique.ca/resources?utf8=%E2%9C%93&keywords={row['Title'].replace(' ', '+')}" \
              f"&author={row['Author'].replace(' ', '+')}&narrator=&publisher=&collection_title=&issued_on_range=&language=" \
              f"&audience=&category_standard=thema&category=&nature=ebook&medium="
        headers = {}
        not_found_str = "Aucune entrée trouvée"
    elif source == "Kobo Plus":
        url = f"https://www.kobo.com/ca/en/search?query=query&fcmedia=Book~BookSubscription&nd=true&ac=1" \
              f"&ac.author={row['Author'].replace(' ', '+')}&ac.title={row['Title'].replace(' ', '+')}" \
              f"&sort=PublicationDateDesc&sortchange=1"
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
        not_found_str = "search-zero-results"
    elif source == "Stadtbibliothek Freiburg":
        pass
    elif source == "Onleihe Freiburg":
        pass
    elif source == "UB Freiburg":
        pass

    print(f"\tRow {row['index']}: {row['Author']}, \"{row['Title']}\"")
    # print(f"\t\tUrl: {url}")

    pre = time.perf_counter()
    response = requests.get(url, headers=headers)
    post = time.perf_counter()
    # print(f"\t\tRequest time: {post-pre}")

    nb_bytes = len(response.content)
    # print(f"\t\tNb of bytes: {nb_bytes}")

    if response:
        if not_found_str in response.text:
                print("\t\tBook not found.")
                return ""
        else:
            print("\t\tBook found!")
            return url
    else:
        print(f"An error has occured. Response status code: {response.status_code}")

# 1) Read Goodreads library .csv
# 2) Keep only books with "Exclusive shelf" = "to-read"
# 3) Keep only columns "Title", "Author".
# 4) Search for books available on Banq (Overdrive)
# 5) Search for books available on quebec.pretsnumerique.ca
# 6) Search for books available on Kobo plus
# 7) Put results together in output .csv

print("Where can I rent ebooks that I have on my Goodreads to-read shelf?")
print("\tScript developed by Jonathan Larochelle, June 2022\n")
print("Starting script ...")
print("1) Loading Goodreads library")
print(f"\tGoodreads Export file: {GOODREADS_LIBRARY_EXPORT_FILE_PATH}")

df = pd.read_csv(GOODREADS_LIBRARY_EXPORT_FILE_PATH, header=0, usecols=["Title", "Author", "Exclusive Shelf"])
df = df[df["Exclusive Shelf"]=="to-read"]
df = df.reset_index()
df.drop("Exclusive Shelf", axis=1, inplace=True)
re_remove_parenthesis = "\(.*\)|\s-\s.*"
df["Title"] = df["Title"].apply(lambda x: re.sub(re_remove_parenthesis, "", x))
re_remove_colon = ":.+"
df["Title"] = df["Title"].apply(lambda x: re.sub(re_remove_colon, "", x))
nb_books = df.shape[0]
print(f"\tFound {nb_books} books in to-read shelf.")

print("2) Searching on banq.overdrive.com")
df["banq.overdrive.com"] = df.apply(lambda x: add_links("banq.overdrive.com", x), axis="columns")

print("3) Searching on quebec.pretnumerique.ca")
df["quebec.pretnumerique.ca"] = df.apply(lambda x: add_links("quebec.pretnumerique.ca", x), axis="columns")

print("4) Searching on Kobo plus")
df["kobo_plus"] = df.apply(lambda x: add_links("Kobo Plus", x), axis="columns")

print("5) Producing output file")
df.to_csv(OUTPUT_FILE_PATH)
print(f"\tResults output to {OUTPUT_FILE_PATH}")

print("Script execution successfully completed.")