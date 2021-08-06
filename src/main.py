import logging
logging.basicConfig(format='%(asctime)s %(levelname)s - %(message)s', level=logging.INFO, filename='logs.log')

import sys
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from symbols import get_completed, get_symbols
from get_max_page import get_max_page

def main(argv):

  try:
    symbols: list(str) = get_symbols()
    # logging.info('Symbols loaded.')
  except FileNotFoundError:
    logging.error("Symbols file not found.")
    sys.exit()

  try:
    completed = get_completed()
    for complete in completed:
      complete = complete.strip()
      try:
        symbols.remove(complete)
      except ValueError:
        logging.warning(f'Symbol {complete} not in the list of symbols')
    # logging.info('Scraped symbols list loaded.')
  except FileNotFoundError:
    logging.warning('Could not find file with symbols that have already been scraped.')

  options = Options()
  options.headless = True

  try:
    driver = webdriver.Chrome(executable_path=r'D://Dev/chromedriver.exe', options=options)
    # logging.info('Driver started.')
  except:
    logging.info('Driver start up failed')
    sys.exit()


  if (len(argv) == 1):
    symbol = argv[0]
    # logging.info(f"{symbol} recieved from argv.")
    if symbol.strip() not in symbols:
      logging.error(f"{symbol} revieved not in list of symbols.")
      sys.exit()
    else:
      # logging.info(f'{symbol} found in the list of symbols.')
      symbols = [symbol]
  else:
    symbols = symbols[:5]
    # logging.info(f"No argv supplied, {symbols} are being scraped.")

  for symbol in symbols:
    start_time = time.time()
    logging.info(f"{symbol} is being scraped.")
    try:
      driver.get(f"https://www.sharesansar.com/company/{symbol}")
      # logging.info('Successfully opened site')
    except:
      logging.error('Could not GET site.')
      continue

    try:
      price_button = driver.find_element_by_id('btn_cpricehistory')
      price_button.click()
      # logging.info('Price Button found.')
      # logging.info('Price Button Clicked.')
      time.sleep(3)
    except:
      logging.error('Price button couldn\'t be found and clicked on.')
      driver.quit()
      sys.exit()

    try:
      table = driver.find_element_by_id("myTableCPriceHistory")
      # logging.info('Table found')
    except:
        driver.quit()
        logging.error('Table not found. Driver Closed')

    header = table.text
    header = ",".join(header.split(" "))
    # logging.info('Header text scraped')

    buttons = driver.find_elements_by_class_name('paginate_button')
    max_page = get_max_page(buttons)
    logging.info(f'There are {max_page} pages for {symbol}')

    with open (f'../data/price_history/{symbol}.csv', 'w') as file:
      file.writelines([header])
      file.write("\n")

      current_page = 2
      while 1:
        # logging.info(f'Current page is {current_page}')

        try:
          buttons = driver.find_elements_by_class_name('paginate_button')
          # logging.info('Found the navigation buttons.')
        except:
          logging.error('Couldn\'t find page naviagation buttons')
          driver.quit()
          sys.exit()

        for button in buttons:
          if button.text == 'Previous' or button.text == 'Next':
            continue

          if (int(button.text) == current_page):
            button.click()
            # logging.info('Target button found and clicked.')
            time.sleep(4)
            try:
              table = driver.find_element_by_id("myTableCPriceHistory")
              table_body = table.find_element_by_tag_name("tbody")
              # logging.info('Table data found')
            except:
              logging.error('Table data not found.')
              driver.quit()
              sys.exit()

            body_text = table_body.text.replace("NO RECORD FOUND", r"\n").replace(',', "").replace(" ", ",").split(r"\n")

            file.writelines(body_text)
            file.write("\n")
            # logging.info(f'Successfully wrote page {current_page}')
            break # Stop looking at other buttons
        else:
          current_page = current_page-1
          if (current_page == max_page):
            logging.info(f'{max_page}/{max_page} pages of {symbol}have been scraped successfull in {time.time() - start_time:.2f} seconds.')
          else:
            logging.error(f'Could not scrape all pages, stopped at {current_page} after {time.time() - start_time:.2f} seconds')
          break # If all buttons have been looked at, then stop looking
        current_page+=1
      with open('../data/completed.txt', 'a') as outfile:
        outfile.writelines(f"{symbol}\n")
  driver.quit()
  logging.info('Closed driver.')

if __name__ == '__main__':
  main(sys.argv[1:])
