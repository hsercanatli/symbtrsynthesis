__author__ = 'hsercanatli'

from synth_S import make_wav as synth_karplus
from synth_A import make_wav as synth_sine
from musicxml_reader import read_music_xml
from tonic import TonicLastNote
from numpy import log2

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
        self.adapted_histogram_cent_difference = {}
        self.adapted_score = {'bpm': self.score['bpm'], 'score': []}

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
            if self.score['notes'][-i][0] != '__':
                self.theoretical_tonic = self.score['notes'][-i][2]
                print self.theoretical_tonic
                break

    def adapt_score_frequencies(self, synth=True):
        self.compute_theoretical_histogram()
        self.compute_score_tonic()

        ratio = float(self.theoretical_tonic) / self.performed_tonic['estimated_tonic']

        for element in self.theoretical_histogram:
            theo_freq = self.theoretical_histogram['{0}'.format(element)][0]
            candidate = self.find_nearest(self.peaks, theo_freq / ratio)

            if (theo_freq / ratio) / 2 ** (1. / 53) <= candidate <= ((theo_freq / ratio) * 2 ** (1. / 53)):
                self.adapted_histogram['{0}'.format(element)] = int(candidate)

                cent = (log2((theo_freq / ratio) / candidate) * 1200)
                self.adapted_histogram_cent_difference['{0}'.format(element)] = cent
                print "Yes!!!", candidate, theo_freq / ratio, cent
            else:
                candidate_up = self.find_nearest(self.peaks, (theo_freq / ratio) * 2.)
                candidate_down = self.find_nearest(self.peaks, (theo_freq / ratio) / 2.)

                if ((2 * theo_freq) / ratio) / (2 ** (1. / 53)) <= candidate_up <= ((2 * theo_freq) / ratio) * (2 ** (1. / 53)):
                    cent = log2(((theo_freq * 2.) / ratio) / candidate_up) * 1200
                    self.adapted_histogram_cent_difference['{0}'.format(element)] = cent
                    print "Yes Octave up!!!", candidate_up / 2., theo_freq / ratio, cent
                    self.adapted_histogram['{0}'.format(element)] = int(candidate_up / 2.)

                elif ((theo_freq / 2.) / ratio) / (2 ** (1. / 53)) <= candidate_down <= ((theo_freq / 2.) / ratio) * (2 ** (1. / 53)):
                    cent = log2(((theo_freq / 2.) / ratio) / candidate_down) * 1200
                    self.adapted_histogram_cent_difference['{0}'.format(element)] = cent
                    print "Yes Octave down!!!", candidate_down * 2., theo_freq / ratio, ratio, theo_freq / candidate, cent
                    self.adapted_histogram['{0}'.format(element)] = int(candidate_down * 2)

                else:
                    self.adapted_histogram['{0}'.format(element)] = int(theo_freq / ratio)
                    cent = 0
                    print "No!!!", candidate, theo_freq / ratio, ratio, theo_freq / candidate, cent
                    self.adapted_histogram_cent_difference['{0}'.format(element)] = cent

        for element in self.adapted_histogram: print(element, self.theoretical_histogram['{0}'.format(element)][0],
                                                     self.adapted_histogram['{0}'.format(element)])

        for element in self.score['notes']:
            if element[0] != '__':
                element[2] = self.adapted_histogram['{0}'.format(element[0] + str(element[1]))]

        if synth: self.make_wav()
        return self.theoretical_histogram, self.adapted_histogram

    def make_wav(self):
        synth_karplus(self.score, fn=self.out_path_1)
        synth_sine(self.score, fn=self.out_path_2)
