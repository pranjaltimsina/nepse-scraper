def get_max_page(buttons):
  max_v = 1
  for button in buttons:
    value = button.text
    try:
      value = int(value)
    except:
      continue
    if (value > max_v):
      max_v = value
  return max_v
