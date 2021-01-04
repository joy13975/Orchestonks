import sys
import csv
from time import sleep
from datetime import datetime

import numpy as np

from notes import note_to_freq
from tone_player import TonePlayer

def main(file=''):
    assert file
    with open(file, 'r') as f:
        data = list(csv.reader(f, delimiter=','))
    with TonePlayer() as tp:
        mat = np.asmatrix(data[1:])
        # time_vals = [datetime.strptime('-'.join(row.A1), r'%Y%m%d-%H%M%S') for row in mat[:,2:4]]
        open_vals, high_vals, low_vals, close_vals, vol_vals = np.asarray(mat[:,4:9].T.astype(float))
        # pitch = 100.0 * (close_vals - open_vals) / close_vals
        pitch = 100 * (close_vals - open_vals) / open_vals
        duration = (close_vals - open_vals) / (high_vals - low_vals)
        
        base_freq = note_to_freq('c4')
        max_pitch = max(abs(pitch))
        pitch_factor = 12 * 4  # 1 octaves = 12 notes
        
        interval = 100
        max_vol = max(vol_vals)
        vol_cap = 1
        
        for i, (p, d, v) in enumerate(zip(pitch, duration, vol_vals)):
            h = round(pitch_factor * p / max_pitch)
            freq = base_freq * (2.0 ** (h/12))
            sound_vol = np.clip(v / (max_vol/2), 0, vol_cap)
            print(f'i={i}, p={p:.4f}, d={d:.2f} h={h}, freq={freq:.2f}, sound_vol={sound_vol:.4f}')
            tp.play(freq, duration=interval*8*d, volume=sound_vol)
            sleep(interval/1000)

if __name__ == "__main__":
    main(**dict(v.split('=') for v in sys.argv[1:]))