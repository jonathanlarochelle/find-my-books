# FindMyBooks
Ever found yourself in front of a 100+ books to-read list on Goodreads, without knowing which one is available from your local library?
FindMyBooks allows you to where all of those books are available.

## Getting started
To use the tool, first clone this repository.
Then, download your goodreads library ([link](https://www.goodreads.com/review/import)).
```Python
python find_my_books MY_GOODREADS_LIBRARY.csv
```
You will then find a MY_GOODREADS_LIBRARY_OUTPUT.csv document with columns for each target library, with url if the book was found in the library.
A detailed list of supported command line arguments can be found below in the Configuration section.

## Features
- Import a list of books from Goodreads
- Find out in which library your books are available

## Configuration
### Goodreads library file
Mandatory, string path to the goodreads library file.
Example:
```Python
python find_my_books MY_GOODREADS_LIBRARY.csv
```

### Output file
Optional, path to desired output file to be created.
Default: Goodreads library file with "_output" suffix.
Example:
```Python
python find_my_books MY_GOODREADS_LIBRARY.csv -o OUTPUT_FILE.csv
```

## Contributing
### New libraries
Everyone is encourage to add libraries via the libraries.json file. Please create one PR with all the libraries you wish to add.
### New features
New features are always welcome. If the feature is substantial, please create an issue first, so that it can be discussed. If the feature is minor, you can directly create a PR and we'll look at it.

## Licensing
The code in this project is licensed under MIT license.