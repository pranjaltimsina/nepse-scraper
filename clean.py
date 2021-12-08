from os import listdir
import regex
import re

files = listdir('./data/price_history')

for file in files:
  PATH = f"./data/price_history/{file}"

  fin = open(PATH, "rt")
  # lines = fin.readlines()
  data = fin.read()

  fin.close()
  # first = lines[0]
  # for i, line in enumerate(lines):
  #   splits = re.split(',', line, 2)
  #   split = splits[2]
  #   splits[2] = regex.sub(r'(?<!\.00|\d\.\d\d),', '', split)
  #   lines[i] = ','.join(splits)
  data = data.replace("S.N.,Date,OpenHighLowLtp%ChangeQtyTurnover", "S.N.,Date,Open,High,Low,Ltp,%Change,Qty,Turnover")
  fin = open(PATH, "wt")
  fin.write(data)
  fin.close()

