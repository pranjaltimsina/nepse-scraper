from os import listdir, write

def update_completed():
  files = listdir('../data/price_history')

  files = [f"{file[:-5]}\n" for file in files]
  # print(files)

  with open('../data/completed.txt', 'w') as write_file:
    write_file.writelines(files)


if __name__ == "__main__":
  update_completed()
