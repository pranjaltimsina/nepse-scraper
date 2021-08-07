from os import symlink
import sys
from time import sleep

def test_symbols():
  print("Testing symbols.py")

  try:
    from symbols import get_completed, get_symbols
    print("1/6 tests passed.")
  except:
    print("Test Failed: Could not import from symbols.py")
    sys.exit()

  try:
    symbols = get_symbols()
    print("2/6 tests passed.")
  except:
    print("\nTest Failed: Could not get symbols")
    sys.exit()


  try:
    assert(type(symbols)==list)
    print("3/6 tests passed.")
  except AssertionError:
    print(f"\nExpected symbols to be a list, not {type(symbols)}")
    sys.exit()

  try:
    assert(len(symbols)==233)
    print("4/6 tests passed.")
  except AssertionError:
    print(f"Incorrect number of symbols loaded, expected 233, got {len(symbols)}")
    sys.exit()

  try:
    completed = get_completed()
    print("5/6 tests passed.")
  except:
    print(f"Test failed: Could not get completed symbols")
    sys.exit()

  try:
    assert(type(completed)==list)
    print("6/6 tests passed.")
  except:
    print(f"Test failed: Invalid type retured by get_completed(). Expected list, got {type(completed)}")
    sys.exit()

  print("Tests passed successfully.")

if __name__ == '__main__':
  test_symbols()
