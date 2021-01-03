import re
import math

A4 = 440
C0 = A4*math.pow(2, -4.75)

notes = 'CDEFGAB'
scale = ['C', 'SC', 'D', 'SD', 'E', 'F', 'SF', 'G', 'SG', 'A', 'SA', 'B']

def note_to_freq(note):
    note = note.upper()
    match = re.match(r'^([SF])?([A-G])(\d+)$', note)
    assert match is not None
    sharpflat, note_name, octave = match.groups()
    octave = int(octave)
    # Regularize notes to sharp only
    note_index = notes.index(note_name)
    if sharpflat == 'F':
        note_index -= 1
        sharpflat = '' if note_name in 'CF' else 'S'
    elif sharpflat is None:
        sharpflat = ''
    scale_index = scale.index(sharpflat + notes[note_index])
    return C0*math.pow(2, octave + (scale_index / 12))