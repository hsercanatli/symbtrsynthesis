__author__ = 'hsercanatli'

from numpy import log2
from .. synthesizer import *

from .. musicxml_reader import read_music_xml


class Tuner:
    def __init__(self):
        pass

    @staticmethod
    def find_nearest(array, value):
        distance = [abs(element - value) for element in array]
        idx = distance.index(min(distance))
        return array[idx]

    @staticmethod
    def compute_theoretical_histogram(score):
        theoretical_histogram = {}
        total_length = 0

        # histogram computation
        for i, x in enumerate(score['notes']):
            try:
                if not x[0] == '__':
                    theoretical_histogram['{0}'.format(str(x[0]) + str(x[1]))][1] += float(x[3]) / x[4]
                    total_length += float(x[3]) / x[4]
            except:
                if not x[0] == '__':
                    theoretical_histogram['{0}'.format(str(x[0]) + str(x[1]))] = [x[2], float(x[3] / x[4])]
                    total_length += float(x[3]) / x[4]

        # normalization
        for element in theoretical_histogram:
            theoretical_histogram['{0}'.format(element)][1] /= total_length

        return theoretical_histogram

    @staticmethod
    def compute_score_tonic(score):
        global theoretical_tonic
        for i in range(1, len(score['notes'])):
            if score['notes'][-i][0] != '__':
                theoretical_tonic = score['notes'][-i][2]
                #print theoretical_tonic
                break
        return theoretical_tonic

    def adapt_score_frequencies(self, musicxml_path, performed_tonic, stable_pitches, type='sine', out='', verbose=False):
        score = read_music_xml(musicxml_path)

        adapted_histogram = {}
        adapted_histogram_cent_difference = {}

        theoretical_histogram = self.compute_theoretical_histogram(score=score)
        theoretical_tonic = self.compute_score_tonic(score=score)

        ratio = float(theoretical_tonic) / performed_tonic

        for element in theoretical_histogram:
            theo_freq = theoretical_histogram['{0}'.format(element)][0]
            candidate = self.find_nearest(stable_pitches, theo_freq / ratio)

            if (theo_freq / ratio) / 2 ** (1. / 53) <= candidate <= ((theo_freq / ratio) * 2 ** (1. / 53)):
                adapted_histogram['{0}'.format(element)] = int(candidate)

                cent = -(log2((theo_freq / ratio) / candidate) * 1200)
                adapted_histogram_cent_difference['{0}'.format(element)] = cent
                if verbose:
                    print "Yes!!!", candidate, theo_freq / ratio, cent, element
            else:
                candidate_up = self.find_nearest(stable_pitches, (theo_freq / ratio) * 2.)
                candidate_down = self.find_nearest(stable_pitches, (theo_freq / ratio) / 2.)

                if ((2 * theo_freq) / ratio) / (2 ** (1. / 53)) <= candidate_up <= ((2 * theo_freq) / ratio) * (
                            2 ** (1. / 53)):
                    cent = -log2(((theo_freq * 2.) / ratio) / candidate_up) * 1200
                    adapted_histogram_cent_difference['{0}'.format(element)] = cent
                    if verbose:
                        print "Yes, up!!!", candidate_up / 2., theo_freq / ratio, cent, element
                    adapted_histogram['{0}'.format(element)] = int(candidate_up / 2.)

                elif ((theo_freq / 1.) / ratio) / (2 ** (1. / 53)) <= candidate_down <= ((theo_freq / 1.) / ratio) * (
                            2 ** (1. / 53)):
                    cent = -log2(((theo_freq / 2.) / ratio) / candidate_down) * 1200
                    adapted_histogram_cent_difference['{0}'.format(element)] = cent
                    if verbose:
                        print "Yes, down!!!", candidate_down * 2., theo_freq / ratio, ratio,\
                            theo_freq / candidate, cent, element
                    adapted_histogram['{0}'.format(element)] = int(candidate_down * 2)

                else:
                    adapted_histogram['{0}'.format(element)] = int(theo_freq / ratio)
                    cent = 0
                    if verbose:
                        print "No!!!", candidate, theo_freq / ratio, ratio, theo_freq / candidate, cent, element
                    adapted_histogram_cent_difference['{0}'.format(element)] = cent

        # with open(self.out_path_intonation, 'w') as f:
        #    f.write("Note" + "\t" + "Theory(Hz)" + "\t" + "Adapted(Hz)" + "\t" + "Difference(cent)" + "\n")
        #    for element in self.adapted_histogram:
        #        f.write(element + "\t" +
        #                str(int(self.theoretical_histogram['{0}'.format(element)][0] / ratio)) + "\t" +
        #                str(self.adapted_histogram['{0}'.format(element)]) + "\t" +
        #                str(self.adapted_histogram_cent_difference['{0}'.format(element)]) + "\n")

        for element in score['notes']:
            if element[0] != '__':
                element[2] = adapted_histogram['{0}'.format(element[0] + str(element[1]))]

        if not out:
            if type == 'sine': out = musicxml_path[:-4] + "--adapted_sine.wav"
            if type == 'karplus': out = musicxml_path[:-4] + "--adapted_karplus.wav"

        self.make_wav(score=score, type=type, fn=out, verbose=verbose)

        return theoretical_histogram, adapted_histogram

    @staticmethod
    def make_wav(score, fn, type, verbose=False):

        if type == 'sine':
            synth_sine(score, fn=fn, verbose=verbose)

        if type == 'karplus':
            synth_karplus(score, fn=fn, verbose=verbose)
