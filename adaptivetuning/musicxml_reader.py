# -*- coding: utf-8 -*-

from xml.etree.ElementTree import parse
from fractions import Fraction
from morty.converter import Converter
import os
import json

# accidentals dictionary
accidental_dict = {'quarter-flat': -1, 'slash-flat': -4, 'flat': -5,
                   'double-slash-flat': -8, 'slash-quarter-sharp': +1,
                   'sharp': +4, '': +5, 'slash-sharp': +8}

# load the interval dictionary
interval_dict = json.load(open(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'data', 'note_intervals_C0.json')))

# convert to bolahenk frequency from intervals
freq_dict = {}
for key, val in interval_dict.items():
    freq_dict[key] = Converter.cent_to_hz(val - 500.0, 16.35)
freq_dict['__'] = 0  # add rest

# types dictionary
note_type_dict = {'whole': [2 ** 2, 1], 'half': [2 ** 1, 2],
                  'quarter': [2 ** 0, 4], 'eighth': [2 ** -1, 8],
                  '16th': [2 ** -2, 16], '32nd': [2 ** -3, 32],
                  '64th': [2 ** -4, 64]}


def read_music_xml(fname):
    global numerator, denominator
    notes = []

    tree = parse(fname)
    root = tree.getroot()

    bpm = float(root.find('part/measure/direction/sound').attrib['tempo'])
    divs = float(root.find('part/measure/attributes/divisions').text)
    q_note_len = 60000. / bpm

    count = 1
    for note in root.findall('part/measure/note'):
        temp_note = []

        # try-except to ignore ornamentations
        try:
            dur = note.find('duration').text

            # step and octave information
            try:
                step = note.find('pitch/step').text
                octave = note.find('pitch/octave').text
            except:
                step = '_'
                octave = '_'

            # accidental information
            try:
                acc = note.find('accidental').text
                if acc is None:
                    acc = 0
                else:
                    acc = accidental_dict["{0}".format(acc)]
            except:
                acc = 0

            # type of note
            try:
                note_type = note.find('type').text
                note_ratio = note_type_dict['{0}'.format(note_type)][0]
                note_payda = note_type_dict['{0}'.format(note_type)][1]

                # dotted notes
                try:
                    if type(note.find('dot').text):
                        pay_payda = max(
                            ((44100. * 60 * note_ratio / bpm) /
                             (int(q_note_len * float(dur) / divs) * 1e-3 *
                              44100.)),
                            ((int(q_note_len * float(dur) / divs) * 1e-3 *
                              44100.) /
                             (44100. * 60 / bpm * note_ratio))) / note_payda
                        numerator = int(Fraction(
                            pay_payda).limit_denominator(100).numerator)
                        denominator = int(Fraction(
                            pay_payda).limit_denominator(100).denominator)

                except:
                    numerator = 1
                    denominator = note_type_dict['{0}'.format(note_type)][1]

            except:
                pass

        except:
            print("ornamentation is ignored")

        note_sym = get_symbtr_note_sym(step, octave, acc)

        # freq calculations
        freq = freq_dict['{0}{1}'.format(step, octave)]
        if acc != 0:
            freq *= 2 ** (acc / 53.0)

        temp_note.append(note_sym)
        temp_note.append(acc)
        temp_note.append(freq)
        temp_note.append(numerator)
        temp_note.append(denominator)
        temp_note.append(int(q_note_len * float(dur) * 1e-3 * 44100 / divs))

        notes.append(temp_note)
        count += 1
    return {'notes': notes,
            'bpm': bpm}


def get_symbtr_note_sym(step, octave, acc):
    if acc == 0:  # natural
        acc_str = ''
    elif acc < 0:  # flat
        acc_str = 'b' + str(abs(acc))
    else:  # sharp
        acc_str = '#' + str(acc)
    note_sym = step + octave + acc_str

    return note_sym
