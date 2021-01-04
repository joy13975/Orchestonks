from time import time, sleep
import math

import sounddevice as sd
import numpy as np
from enum import IntEnum, auto

from notes import note_to_freq


class ToneStatus(IntEnum):
    Inactive = 0
    Active = 1
    Dead = 2


class Tone:
    def __init__(self, freq, volume, duration):
        self.freq = freq
        self.volume = volume  # 0~1
        self.duration = duration  # ms
        self.status = ToneStatus.Inactive
        self._start_time = -1

    def start(self):
        if self.status >= ToneStatus.Active:
            return
        self.status = ToneStatus.Active
        self._start_time = time()

    def check_expired(self):
        if self.duration == -1 or self._start_time == -1:
            return
        if (time() - self._start_time) * 1000 >= self.duration:
            self.status = ToneStatus.Dead

    def sample(self):
        return self.freq, self.volume, int(self.status)


class TonePlayer:
    def __init__(self):
        self.chunk_size = 512
        self.fs = 2048*10
        sd.default.samplerate = self.fs
        self.tones = dict()
        self.sample_i = 0

    def _sample_callback(self, out_data, frame_count, time_info, status):
        end = self.sample_i + frame_count
        out_data[:] = self._mix_samples(
            self.sample_i, end).reshape(frame_count, 1)
        self.sample_i = end

    def __enter__(self):
        self.stream = sd.OutputStream(channels=1,
                                      blocksize=self.chunk_size,
                                      callback=self._sample_callback)
        self.stream.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stream.close()

    def _logistic(self, x, k=1, x0=1, L=1):
        return L/(1+(np.exp(-k*(x - x0))))

    def _mix_samples(self, i, j):
        self.tones = {k: v for k, v in self.tones.items()
                      if not v.status == ToneStatus.Dead}
        if self.tones:
            for t in self.tones.values():
                t.check_expired()
            freq, volume, status = \
                [np.asmatrix(a) for a in
                 zip(*(t.sample() for t in self.tones.values()))]
            sines = np.asmatrix(
                np.sin((freq / self.fs).T * 2.0 * np.pi * np.arange(i, j)))
            # Multiply by envelop based on tone status:
            #   Inactive -> Fade In
            #   Active -> Identity
            #   Dead -> Fade Out
            k = (6*np.pi)/self.chunk_size
            x0 = self.chunk_size / 2
            fade_in = self._logistic(np.arange(j-i), x0=x0, k=k)
            identity = np.ones(j-i)
            fade_out = self._logistic(np.arange(j-i), x0=x0, k=-k)
            fade_mat = np.asmatrix([fade_in, identity, fade_out])
            fade_mask = np.asmatrix(np.diag(np.ones(3)))[status.A1]
            samples = (volume * (np.multiply(fade_mask*fade_mat, sines))).A1
            for t in self.tones.values():
                t.start()
        else:
            samples = np.array([0.0]*(j-i))
        return samples

    def play(self, freq, duration=-1, volume=0.5):
        if isinstance(freq, str):
            freq = note_to_freq(freq)
        tone = Tone(freq, volume, duration)
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
