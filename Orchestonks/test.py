import sys
import csv

from tone_player import TonePlayer

def main(file=''):
    assert file
    with open(file, 'r') as f:
        data = list(csv.reader(f, delimiter=','))
    with TonePlayer() as tp:
        import code
        code.interact(local={**locals(), **globals()})

if __name__ == "__main__":
    main(**dict(v.split('=') for v in sys.argv[1:]))