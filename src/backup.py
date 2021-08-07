from shutil import copytree

def backup(src="D:/Dev/nepse-scraper/data/price_history", dest="D://Dev/stock-data/price_history"):
  copytree(src, dest)

if __name__ == "__main__":
  backup()
