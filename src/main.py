import logging

import sys
import time

from multiprocessing import Pool, cpu_count, Lock

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from symbols import get_completed, get_symbols
from get_max_page import get_max_page

options = Options()
options.headless = True

def setup_logger(logger_name, log_file, level=logging.INFO, mode='a'):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
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

  try:
    driver = webdriver.Chrome(executable_path=r'D://Dev/chromedriver.exe', options=options)
    logger_v.info('Driver started.')
  except:
    logger_v.info('Driver start up failed')
    logger_c.info('Driver start up failed')
    return f"Thread {t_id}: {symbol} retured after driver start up failed."

  start_time = time.time()

  try:
    driver.get(f"https://www.sharesansar.com/company/{symbol}")
  except:
    logger_c.error('Could open site')
    logger_v.error('Could open site')
    driver.quit()
    return f"Thread {t_id}: {symbol} retured after {time.time() - start_time:.2f} seconds as the page could not be opened."

  try:
    price_button = driver.find_element_by_id('btn_cpricehistory')
    price_button.click()
    time.sleep(3)
  except:
    logger_c.error('Price button couldn\'t be found and clicked on.')
    logger_v.error('Price button couldn\'t be found and clicked on.')
    driver.quit()
    return f"Thread {t_id}: {symbol} retured after after {time.time() - start_time:.2f} seconds. Error finding and clicking price history button."

  try:
    table = driver.find_element_by_id("myTableCPriceHistory")
  except:
      logger_v.error('Table not found. Driver Closed')
      logger_c.error('Table not found. Driver Closed')
      driver.quit()
      return f"Thread {id}: {symbol} retured after {time.time() - start_time:.2f} seconds as table not found."


  header = table.text
  header = ",".join(header.split(" "))
  logger_v.info('Header text scraped.')

  try:
    buttons = driver.find_elements_by_class_name('paginate_button')
    max_page = get_max_page(buttons)
  except:
    logger_c.error('Could not find navigation buttons.')
    logger_v.error('Could not find navigation buttons.')
    driver.quit()
    return f"Thread {t_id}: {symbol} retured after {time.time() - start_time:.2f} seconds as navigation button scould not be found."

  if max_page:
    logger_c.info(f'Scraping {max_page} pages of {symbol}')
    logger_v.info(f'Scraping {max_page} pages of {symbol}')
  else:
    logger_c.warning(f'Scraping unknown number of pages of {symbol}')
    logger_v.warning(f'Scraping unknown number of pages of {symbol}')

  with open (f'../data/price_history/{symbol}.csv', 'w') as file:
    file.writelines([header])
    file.write("\n")

    current_page = 2
    while 1:
      logger_v.info(f'Scraping page {current_page}')

      try:
        buttons = driver.find_elements_by_class_name('paginate_button')
      except:
        logger_c.error('Couldn\'t find page naviagation buttons')
        logger_v.error('Couldn\'t find page naviagation buttons')
        driver.quit()
        return f"Thread {t_id}: {symbol} retured after {time.time() - start_time:.2f} seconds. Navigation button scould not be found after {current_page-1}/{max_page} pages."

      for button in buttons:
        if button.text == 'Previous' or button.text == 'Next':
          continue

        if (int(button.text) == current_page):
          button.click()
          time.sleep(4)
          try:
            table = driver.find_element_by_id("myTableCPriceHistory")
            table_body = table.find_element_by_tag_name("tbody")
          except:
            logger_c.error('Table data not found.')
            logger_v.error('Table data not found.')
            driver.quit()
            return f"Thread {t_id}: {symbol} retured after {time.time() - start_time:.2f} seconds. Table data not found after {current_page-1}/{max_page}."

          body_text = table_body.text.replace("NO RECORD FOUND", r"\n").replace(',', "").replace(" ", ",").split(r"\n")

          file.writelines(body_text)
          file.write("\n")
          logger_v.info(f'Successfully scraped page {current_page}.')
          break
      else:
        driver.quit()
        logger_v.info('Closed driver.')
        logger_c.info('Closed driver.')
        if (current_page == max_page):
          logger_c.info(f'{max_page}/{max_page} pages of {symbol} have been scraped successfull in {time.time() - start_time:.2f} seconds.')
          logger_v.info(f'{max_page}/{max_page} pages of {symbol} have been scraped successfull in {time.time() - start_time:.2f} seconds.')
          with open('../data/completed.txt', 'a') as outfile:
            outfile.writelines(f"{symbol.strip().lower()}\n")
          return f'{max_page}/{max_page} pages of {symbol} have been scraped successfull in {time.time() - start_time:.2f} seconds.'
        else:
          current_page = current_page-1
          logger_c.error(f'Could not scrape all pages of {symbol}, stopped at {current_page}/{max_page} after {time.time() - start_time:.2f} seconds')
          logger_v.error(f'Could not scrape all pages of {symbol}, stopped at {current_page}/{max_page} after {time.time() - start_time:.2f} seconds')
          if (current_page >= 0.8*max_page):
            with open('../data/completed.txt', 'a') as outfile:
              outfile.writelines(f"{symbol.strip().lower()}\n")
          return f'Could not scrape all pages of {symbol}, stopped at {current_page}/{max_page} after {time.time() - start_time:.2f} seconds'
        break # If all buttons have been looked at, then stop looking
      current_page+=1

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
    main_logger.info(result)

if __name__ == '__main__':
  main()
