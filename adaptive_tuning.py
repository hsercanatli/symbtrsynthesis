__author__ = 'hsercanatli'

from synth_S import make_wav as synth_karplus
from synth_A import make_wav as synth_sine
from musicxml_reader import read_music_xml
from tonic import TonicLastNote

import json


class AdaptiveTuning:
    def __init__(self, pitch_path, musicxml_score_path):
        # reading pitch and music-xml score
        with open(pitch_path) as f: self.pitch = json.load(f)
        self.score = read_music_xml(musicxml_score_path)

        # tonic identification
        tonic_identifier = TonicLastNote(self.pitch)
        self.performed_tonic = tonic_identifier.compute_tonic()
        self.peaks = tonic_identifier.peaks_list

        self.theoretical_histogram = {}
        self.theoretical_tonic = 0
        self.theoretical_pitches = {}
        self.adapted_histogram = {}

        self.out_path_1 = musicxml_score_path[:-4] + "-out1.wav"
        self.out_path_2 = musicxml_score_path[:-4] + "-out2.wav"

    @staticmethod
    def find_nearest(array, value):
        distance = [abs(element - value) for element in array]
        idx = distance.index(min(distance))
        return array[idx]

    def compute_theoretical_histogram(self):
        total_length = 0
        # histogram computation
        for i, x in enumerate(self.score['notes']):
            try:
                if not x[0] == '__':
                    self.theoretical_histogram['{0}'.format(str(x[0]) + str(x[1]))][1] += float(x[3]) / x[4]
                    total_length += float(x[3]) / x[4]
            except:
                if not x[0] == '__':
                    self.theoretical_histogram['{0}'.format(str(x[0]) + str(x[1]))] = [x[2], float(x[3] / x[4])]
                    total_length += float(x[3]) / x[4]
        # normalization
        for element in self.theoretical_histogram: self.theoretical_histogram['{0}'.format(element)][1] /= total_length

    def compute_score_tonic(self):
        for i in range(1, len(self.score['notes'])):
            if self.score['notes'][-i] != '__':
                self.theoretical_tonic = self.score['notes'][-i][2]
                print self.score['notes'][-i]
                break

    def adapt_score_frequencies(self, synth=True):
        self.compute_theoretical_histogram()
        self.compute_score_tonic()

        ratio = float(self.theoretical_tonic) / self.performed_tonic['estimated_tonic']

        for element in self.theoretical_histogram:
            theo_freq = self.theoretical_histogram['{0}'.format(element)][0]
            candidate = self.find_nearest(self.peaks, theo_freq / ratio)

            if (theo_freq / ratio) / 2 ** (3. / 53) <= candidate <= ((theo_freq / ratio) * 2 ** (3. / 53)):
                self.adapted_histogram['{0}'.format(element)] = int(candidate)
                print "Yes!!!", candidate, theo_freq / ratio, ratio, theo_freq / candidate
            else:
                self.adapted_histogram['{0}'.format(element)] = int(theo_freq / ratio)
                print "No!!!", candidate, theo_freq / ratio, ratio, theo_freq / candidate

        for element in self.adapted_histogram: print(element, self.adapted_histogram['{0}'.format(element)])
        for element in self.score['notes']:
            if element[0] != '__':
                element[2] = self.adapted_histogram['{0}'.format(element[0] + str(element[1]))]

        if synth: self.make_wav()

    def make_wav(self):
        synth_karplus(self.score, fn=self.out_path_1)
        synth_sine(self.score, fn=self.out_path_2)
