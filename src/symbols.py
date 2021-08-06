import csv

"""
  Returns the symbols from a file

  Position arguments:
    file_path: str -- Path to symbols (default: ./data/names.csv)

  Returns:
    symbols: list(str) -- List of the symbols
"""
def get_symbols(file_path: str='../data/names.csv'):
  symbols: list(str) = []

  with open (file_path, 'r') as symbols_file:
    csv_reader = csv.reader(symbols_file, delimiter=',')
    for row in csv_reader:
      symbols.append(row[1].lower().strip())

  return symbols

"""
  Returns the symbols which have already been scraped

  Position arguments:
    file_path: str -- Path to symbols (default: ./data/names.csv)

  Returns:
    symbols: list(str) -- List of the symbols
"""
def get_completed(file_path: str='../data/completed.txt'):
  with open(file_path, 'r') as symbols_file:
    return symbols_file.readlines()
