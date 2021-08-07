import logging
# logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', level=logging.INFO, filename='logs.log')

import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from symbols import get_completed, get_symbols
from get_max_page import get_max_page

def setup_logger(logger_name, log_file, level=logging.INFO):
    l = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='a')
    fileHandler.setFormatter(formatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)

    l.setLevel(level)
    l.addHandler(fileHandler)
    l.addHandler(streamHandler)

def main(argv):
  setup_logger('compact_log', './compact.log')
  setup_logger('verbose_log', './verbose.log')
  logger_c = logging.getLogger('compact_log')
  logger_v = logging.getLogger('verbose_log')

  try:
    symbols: list(str) = get_symbols()
    logger_v.info('Symbols loaded.')
  except FileNotFoundError:
    logger_v.error("Symbols file not found.")
    logger_c.error("Symbols file not found.")
    sys.exit()

  try:
    completed = get_completed()
    for complete in completed:
      complete = complete.strip()
      try:
        symbols.remove(complete)
      except ValueError:
        logger_c.warning(f'Symbol {complete} not in the list of symbols')
        logger_v.warning(f'Symbol {complete} not in the list of symbols')
    logger_v.info('Scraped symbols list loaded.')
  except FileNotFoundError:
    logger_c.warning('Could not find file with symbols that have already been scraped.')
    logger_v.warning('Could not find file with symbols that have already been scraped.')

  options = Options()
  options.headless = True

  try:
    driver = webdriver.Chrome(executable_path=r'D://Dev/chromedriver.exe', options=options)
    logger_v.info('Driver started.')
  except:
    logger_v.info('Driver start up failed')
    logger_c.info('Driver start up failed')
    sys.exit()

  if (len(argv) == 1):
    symbol = argv[0]
    logger_v.info(f"{symbol} recieved from argv.")
    if symbol.strip() not in symbols:
      logger_c.error(f"{symbol} revieved not in list of symbols.")
      logger_v.error(f"{symbol} revieved not in list of symbols.")
      sys.exit()
    else:
      logger_v.info(f'{symbol} found in the list of symbols.')
      symbols = [symbol]
  else:
    symbols = symbols[:5]
    logger_v.info(f"No argv supplied, {symbols} are being scraped.")

  for symbol in symbols:
    start_time = time.time()
    logger_c.info(f"{symbol} is being scraped.")
    logger_v.info(f"{symbol} is being scraped.")
    try:
      driver.get(f"https://www.sharesansar.com/company/{symbol}")
      logger_v.info('Successfully opened site')
    except:
      logger_c.error('Could not GET site.')
      logger_v.error('Could not GET site.')
      continue

    try:
      price_button = driver.find_element_by_id('btn_cpricehistory')
      price_button.click()
      logger_v.info('Price Button  found and clicked on.')
      time.sleep(3)
    except:
      logger_c.error('Price button couldn\'t be found and clicked on.')
      logger_v.error('Price button couldn\'t be found and clicked on.')
      driver.quit()
      sys.exit()

    try:
      table = driver.find_element_by_id("myTableCPriceHistory")
      logger_v.info('Table found')
    except:
        driver.quit()
        logger_v.error('Table not found. Driver Closed')
        logger_c.error('Table not found. Driver Closed')

    header = table.text
    header = ",".join(header.split(" "))
    logger_v.info('Header text scraped')

    buttons = driver.find_elements_by_class_name('paginate_button')
    max_page = get_max_page(buttons)
    logger_c.info(f'There are {max_page} pages for {symbol}')
    logger_v.info(f'There are {max_page} pages for {symbol}')

    with open (f'../data/price_history/{symbol}.csv', 'w') as file:
      file.writelines([header])
      file.write("\n")

      current_page = 2
      while 1:
        logger_v.info(f'Current page is {current_page}')

        try:
          buttons = driver.find_elements_by_class_name('paginate_button')
          logger_v.info('Found the navigation buttons.')
        except:
          logger_c.error('Couldn\'t find page naviagation buttons')
          logger_v.error('Couldn\'t find page naviagation buttons')
          driver.quit()
          sys.exit()

        for button in buttons:
          if button.text == 'Previous' or button.text == 'Next':
            continue

          if (int(button.text) == current_page):
            button.click()
            logger_v.info('Target button found and clicked.')
            time.sleep(4)
            try:
              table = driver.find_element_by_id("myTableCPriceHistory")
              table_body = table.find_element_by_tag_name("tbody")
              logger_v.info('Table data found')
            except:
              logger_c.error('Table data not found.')
              logger_v.error('Table data not found.')
              driver.quit()
              sys.exit()

            body_text = table_body.text.replace("NO RECORD FOUND", r"\n").replace(',', "").replace(" ", ",").split(r"\n")

            file.writelines(body_text)
            file.write("\n")
            logger_v.info(f'Successfully wrote page {current_page}')
            break # Stop looking at other buttons
        else:
          current_page = current_page-1
          if (current_page == max_page):
            logger_c.info(f'{max_page}/{max_page} pages of {symbol}have been scraped successfull in {time.time() - start_time:.2f} seconds.')
            logger_v.info(f'{max_page}/{max_page} pages of {symbol}have been scraped successfull in {time.time() - start_time:.2f} seconds.')
          else:
            logger_v.error(f'Could not scrape all pages, stopped at {current_page} after {time.time() - start_time:.2f} seconds')
            logger_v.error(f'Could not scrape all pages, stopped at {current_page} after {time.time() - start_time:.2f} seconds')
          break # If all buttons have been looked at, then stop looking
        current_page+=1
      with open('../data/completed.txt', 'a') as outfile:
        outfile.writelines(f"{symbol.strip().lower()}\n")

  driver.quit()
  logger_v.info('Closed driver.')
  logger_c.info('Closed driver.')

if __name__ == '__main__':
  main(sys.argv[1:])
