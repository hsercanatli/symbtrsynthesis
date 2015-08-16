# -*- coding: utf-8 -*-
__author__ = 'hsercanatli'

from numpy import delete
from numpy import log2
from numpy import arange
from numpy import histogram
from numpy import sum
from numpy import median
from numpy import where
from pypeaks import Data
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter

class Histogram(object):
    def __init__(self, data, post_filter=True, freq_limit=False, bottom_limit=64, upper_limit=1024):
        # inputs
        self.pitch = data['pitch']

        self.post_filter = post_filter
        self.freq_limit = freq_limit
        self.bottom_limit = bottom_limit
        self.upper_limit = upper_limit

        # outputs
        self.pitch_chunks = {}
        self.normal_histogram = {}

    def energy_filter(self, threshold=0.002):
        """
        checks the saliences
        """
        for element in self.pitch:
            if element[2] <= threshold and element[1] != 0:
                element[1] = 0
                element[2] = 0

    def decompose_into_chunks(self, bottom_limit=0.8, upper_limit=1.2):
        """
        decomposes the given pitch track into the chunks.
        """
        pitch_chunks = []
        temp_pitch = [self.pitch[0]]

        # starts at the first sample
        for i in range(1, len(self.pitch) - 1):
            # separation of the zero chunks
            if self.pitch[i][1] == 0:
                if self.pitch[i + 1][1] == 0:
                    temp_pitch.append(self.pitch[i + 1])

                else:
                    temp_pitch.append(self.pitch[i])
                    pitch_chunks.append(temp_pitch)
                    temp_pitch = []
            # non-zero chunks
            else:
                interval = float(self.pitch[i + 1][1]) / float(self.pitch[i][1])
                if bottom_limit < interval < upper_limit:
                    temp_pitch.append(self.pitch[i])
                else:
                    temp_pitch.append(self.pitch[i])
                    pitch_chunks.append(temp_pitch)
                    temp_pitch = []
        pitch_chunks.append(temp_pitch)

        if self.post_filter:
            self.post_filter_chunks(pitch_chunks, chunk_limit=60, freq_limit=self.freq_limit)
        else:
            self.pitch_chunks = pitch_chunks

    def post_filter_chunks(self, pitch_chunks, chunk_limit=60, freq_limit=True):
        """
        Postfilter for the pitchChunks
        deletes the zero chunks
        deletes the chunks smaller than 60 samples(default)
        """
        # deleting Zero chunks
        zero_chunks = [i for i in range(0, len(pitch_chunks)) if pitch_chunks[i][0][1] == 0]
        pitch_chunks = delete(pitch_chunks, zero_chunks)

        # deleting small Chunks
        small_chunks = [i for i in range(0, len(pitch_chunks)) if len(pitch_chunks[i]) <= chunk_limit]
        pitch_chunks = delete(pitch_chunks, small_chunks)

        # frequency limit
        if freq_limit:
            limit_chunks = [i for i in range(0, len(pitch_chunks)) if pitch_chunks[i][0][1] >= self.upper_limit or
                            pitch_chunks[i][0][1] <= self.bottom_limit]
            pitch_chunks = delete(pitch_chunks, limit_chunks)

        self.pitch_chunks = pitch_chunks

    def recompose_chunks(self):
        """
        recomposes the given pitch chunks as a new pitch track
        """
        self.pitch = [self.pitch_chunks[i][j] for i in range(len(self.pitch_chunks))
                      for j in range(len(self.pitch_chunks[i]))]

    def compute_histogram(self, times=1):
        """
        Computes the histogram for given pitch track
        """
        global min_logf0
        self.energy_filter()

        self.decompose_into_chunks()
        self.recompose_chunks()

        self.decompose_into_chunks(bottom_limit=0.965, upper_limit=1.035)
        self.recompose_chunks()

        pitch = [sample[1] for sample in self.pitch]

        # log2 of pitch track
        log_pitch = log2(pitch)

        # calculating the bins in 4 octave range...
        max_logf0 = max(log_pitch)
        if max_logf0 > 5:
            min_logf0 = max_logf0 - 4.
        else:
            print '!!!PROBLEM!!!\nCheck the given audio recording. Range is lower than 4 octave'

        # 1/3 holderian comma in 4 octave
        step_no = 4 * 53 * 3 * times
        edges = (arange(step_no + 1) * (1. / (3 * times * 53.))) + min_logf0
        # pitch histogram
        hist = histogram(log_pitch, edges)[0]
        # normalization of the histogram
        hist = [float(hist[i]) / sum(hist) for i in range(len(hist))]
        # edges calculation
        edges = [2 ** ((edges[i] + edges[i + 1]) / 2.) for i in range(len(edges) - 1)]

        self.normal_histogram = {'bins': edges, 'hist': hist}


class TonicLastNote(Histogram, Data):
    def __init__(self, data):
        self.counter = 0
        self.data = data

        # getting histograms 3 times more resolution
        Histogram.__init__(self, data, post_filter=True, freq_limit=True, bottom_limit=64, upper_limit=1024)
        self.compute_histogram(times=3)

        # getting histogram peaks with pypeaks library
        Data.__init__(self, self.normal_histogram['bins'], self.normal_histogram['hist'], smoothness=3)
        self.get_peaks(method='slope')

        self.peaks_list = self.peaks["peaks"][0]
        self.tonic = 0
        self.time_interval = None

    @staticmethod
    def find_nearest(array, value):
        distance = [abs(element - value) for element in array]
        idx = distance.index(min(distance))
        return array[idx]

    def compute_tonic(self, plot=False):
        """
        plot function
        """
        global last_note
        while self.tonic is 0:
            self.counter += 1
            last_chunk = [element[1] for element in self.pitch_chunks[-self.counter]]

            last_note = median(last_chunk)
            self.peaks_list = sorted(self.peaks_list, key=lambda x: abs(last_note - x))

            for j in range(len(self.peaks_list)):
                tonic_candidate = float(self.peaks_list[j])

                if (tonic_candidate / (2 ** (2. / 53))) <= last_note <= (tonic_candidate * (2 ** (2. / 53))):
                    self.tonic = {"estimated_tonic": tonic_candidate,
                                  "time_interval": [self.pitch_chunks[-self.counter][0][0],
                                                    self.pitch_chunks[-self.counter][-1][0]]}
                    print "Tonic=", self.tonic
                    break

                elif last_note >= tonic_candidate or last_note <= tonic_candidate:
                    if last_note <= tonic_candidate:
                        times = round(tonic_candidate / last_note)

                        if (tonic_candidate / (2 ** (2. / 53))) <= (last_note * times) \
                                <= (tonic_candidate * (2 ** (2. / 53))) and times < 3:
                            self.tonic = {"estimated_tonic": tonic_candidate,
                                          "time_interval": [self.pitch_chunks[-self.counter][0][0],
                                                            self.pitch_chunks[-self.counter][-1][0]]}
                            print "Tonic=", self.tonic
                            break

                    else:
                        times = round(last_note / tonic_candidate)

                        if (tonic_candidate / (2 ** (2. / 53))) <= (last_note / times) \
                                <= (tonic_candidate * (2 ** (2. / 53))) and times < 3:
                            self.tonic = {"estimated_tonic": tonic_candidate,
                                          "time_interval": [self.pitch_chunks[-self.counter][0][0],
                                                            self.pitch_chunks[-self.counter][-1][0]]}
                            print "Tonic=", self.tonic
                            break

        # octave correction
        temp_tonic = self.tonic['estimated_tonic'] / 2
        temp_candidate = self.find_nearest(self.peaks_list, temp_tonic)
        temp_candidate_ind = [i for i, x in enumerate(self.peaks['peaks'][0]) if x == temp_candidate]
        temp_candidate_occurence = self.peaks["peaks"][1][temp_candidate_ind[0]]

        tonic_ind = [i for i, x in enumerate(self.peaks['peaks'][0]) if x == self.tonic['estimated_tonic']]
        tonic_occurrence = self.peaks["peaks"][1][tonic_ind[0]]

        if (temp_candidate / (2 ** (1. / 53))) <= temp_tonic <= (temp_candidate * (2 ** (1. / 53))):
            if self.tonic['estimated_tonic'] >= 400:
                print "OCTAVE CORRECTED!!!!"
                self.tonic = {"estimated_tonic": temp_candidate,
                              "time_interval": [self.pitch_chunks[-self.counter][0][0],
                                                self.pitch_chunks[-self.counter][-1][0]]}

            if tonic_occurrence <= temp_candidate_occurence:
                print "OCTAVE CORRECTED!!!!"

                self.tonic = {"estimated_tonic": temp_candidate,
                              "time_interval": [self.pitch_chunks[-self.counter][0][0],
                                                self.pitch_chunks[-self.counter][-1][0]]}
                print self.tonic
        else: print "No octave correction!!!"

        if plot:
            self.plot_tonic()
            print last_note
            print self.tonic
            print sorted(self.peaks_list)
            plt.show()

        return self.tonic

    def plot_tonic(self):
        fig, (ax1, ax2, ax3) = plt.subplots(3, num=None, figsize=(18, 8), dpi=80)
        plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0, hspace=0.4)

        # plot title
        ax1.set_title('Recording Histogram')
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('Frequency of occurrence')
        # log scaling the x axis
        ax1.set_xscale('log', basex=2, nonposx='clip')
        ax1.xaxis.set_major_formatter(FormatStrFormatter('%d'))
        # recording histogram
        ax1.plot(self.x, self.y, label='SongHist', ls='-', c='b', lw='1.5')
        # peaks
        ax1.plot(self.peaks['peaks'][0], self.peaks['peaks'][1], 'cD', ms=6, c='r')
        # tonic
        ax1.plot(self.tonic['estimated_tonic'],
                 self.y[where(self.x == self.tonic['estimated_tonic'])[0]], 'cD', ms=10)

        # pitch track histogram
        ax2.plot([element[0] for element in self.data["pitch"]], [element[1] for element in self.data["pitch"]],
                 ls='-', c='r', lw='0.8')
        ax2.vlines([element[0][0] for element in self.pitch_chunks], 0,
                   max([element[1]] for element in self.data["pitch"]))
        ax2.set_xlabel('Time (secs)')
        ax2.set_ylabel('Frequency (Hz)')

        ax3.plot([element[0] for element in self.pitch_chunks[-self.counter]],
                 [element[1] for element in self.pitch_chunks[-self.counter]])
        ax3.set_title("Last Chunk")
        ax3.set_xlabel('Time (secs)')
        ax3.set_ylabel('Frequency (Hz)')
        plt.show()
