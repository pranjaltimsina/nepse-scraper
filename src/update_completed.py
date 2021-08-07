from os import listdir, write

files = listdir('../data/price_history')

files = [f"{file[:-4]}\n" for file in files]
print(files)

with open('../data/completed.txt', 'w') as write_file:
  write_file.writelines(files)


