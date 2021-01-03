from time import time, sleep

import sounddevice as sd
import numpy as np

from notes import note_to_freq


class TonePlayer:
    class Tone:
        def __init__(self, freq, volume, duration):
            self.freq = freq
            self.volume = volume  # 0~1
            self.start_time = -1
            self.duration = duration  # ms
            self.sample_included = False

        def expired(self):
            if self.duration == -1 or self.start_time == -1:
                return False
            return (time() - self.start_time) * 1000 >= self.duration

        def sample(self):
            self.sample_included = True
            return self.freq, self.volume

    def __init__(self):
        self.chunk_size = 512
        self.fs = 2048*10
        sd.default.samplerate = self.fs
        self.tones = dict()
        self.sample_i = 0

    def _sample_callback(self, out_data, frame_count, time_info, status):
        keys = list(self.tones.keys())
        for k in keys:
            if self.tones[k].expired():
                del self.tones[k]
        end = self.sample_i + frame_count
        out_data[:] = self._gen_samples(
            self.sample_i, end).reshape(frame_count, 1)
        self.sample_i = end
        now = time()
        for t in self.tones.values():
            if t.start_time == -1:
                t.start_time = now

    def __enter__(self):
        self.stream = sd.OutputStream(channels=1,
                                      blocksize=self.chunk_size,
                                      callback=self._sample_callback)
        self.stream.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.close()

    def _gen_samples(self, i, j):
        if self.tones:
            freq, volume = zip(*(t.sample()
                                 for t in self.tones.values()))
            freq = np.asmatrix(freq)
            volume = np.asmatrix(volume)
            sines = np.asmatrix(
                np.sin((freq / self.fs).T * 2.0 * np.pi * np.arange(i, j)))
            samples = (volume * sines).A1
        else:
            samples = np.array([0.0]*(j-i))
        return samples

    def play(self, freq, duration=-1, volume=0.5):
        if isinstance(freq, str):
            freq = note_to_freq(freq)
        tone = self.Tone(freq, volume, duration)
        tone_id = id(tone)
        self.tones[tone_id] = tone
        return tone_id

    def stop(self, tone_id=-1):
        if tone_id == -1:
            self.tones.clear()
        elif tone_id in self.tones:
            del self.tones[tone_id]

    def test(self):
        octave = 4
        notes = [f'c{octave}', f'e{octave}', f'g{octave}', f'c{octave+1}']
        duration = 4000
        n = 2 * len(notes)
        interval = (duration / n) / 1000
        for i, note in enumerate(notes + notes[::-1]):
            d = duration * (n - i)/n
            p.play(note_to_freq(note), d)
            sleep(interval)


if __name__ == "__main__":
    with TonePlayer() as p:
        p.test()
        import code
        code.interact(local={**locals(), **globals()})
