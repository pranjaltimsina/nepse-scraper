import logging

import sys
import time
import requests

from multiprocessing import Pool, cpu_count, Lock

from symbols import get_completed, get_symbols

def setup_logger(logger_name, log_file, level=logging.INFO, mode='a'):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    fileHandler = logging.FileHandler(log_file, mode=mode)
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)

def scrape(symbol):
  setup_logger('compact_log', f'../logs/t{symbol[0]}_c.log', mode='w')
  setup_logger('verbose_log', f'../logs/t{symbol[0]}_v.log', mode='w')
  logger_c = logging.getLogger('compact_log')
  logger_v = logging.getLogger('verbose_log')

  t_id, symbol = symbol

  start_time = time.time()

  try:
    response = requests.get(f"https://www.sharesansar.com/company-chart/history?symbol={symbol}&resolution=1D&from=300000000&to={int(start_time)}")
    if (response.status_code == 200):
      with open (f'../data/price_history/{symbol}.json', 'wb') as file:
        file.write(response.content)
    else:
      logger_c.error(f'Request failed with status {response.status_code}.')
      logger_v.error(f'Request failed with status {response.status_code}.')
      return 0, f"Thread {t_id}: {symbol} returned after {time.time() - start_time:.2f} seconds as the request failed with status {response.status_code}."
  except:
    logger_c.error('Could not get the response.')
    logger_v.error('Could not get the response.')
    return 0, f"Thread {t_id}: {symbol} returned after {time.time() - start_time:.2f} seconds as the request failed."

def init_child(lock_):
  global lock
  lock = lock_

def main():
  setup_logger('main_log', '../logs/main.log')
  main_logger = logging.getLogger('main_log')

  try:
    symbols: list(str) = get_symbols()
    main_logger.info('Symbols loaded.')
  except FileNotFoundError:
    main_logger.error("Symbols file not found.")
    sys.exit()

  try:
    completed = get_completed()
    for complete in completed:
      complete = complete.strip()
      try:
        symbols.remove(complete)
      except ValueError:
        main_logger.warning(f'Symbol {complete} not in the list of symbols')
    main_logger.info('Scraped symbols list loaded.')
  except FileNotFoundError:
    main_logger.warning('Could not find file with symbols that have already been scraped.')

  lock = Lock()
  pool_size = cpu_count()

  symbols = symbols[:pool_size]

  main_logger.info(f"{symbols} will be scraped.")

  new_symbols = []
  for i, symbol in enumerate(symbols):
    new_symbols.append((i, symbol))

  with Pool(pool_size, initializer=init_child, initargs=(lock,)) as pool:
    results = pool.map(scrape, new_symbols)

  for result in results:
    if result[0]:
      main_logger.info(f"Success! {result[1]}")
    else:
      main_logger.info(f"Failure! {result[1]}")

if __name__ == '__main__':
  main()
