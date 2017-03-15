# -*- coding: utf-8 -*-

from xml.etree.ElementTree import parse
from fractions import Fraction
from morty.converter import Converter
import os
import json
import warnings

# accidentals dictionary
_accidental_dict = {'quarter-flat': -1, 'slash-flat': -4, 'flat': -5,
                    'double-slash-flat': -8, 'slash-quarter-sharp': +1,
                    'sharp': +4, '': +5, 'slash-sharp': +8}

# load the interval dictionary
_interval_dict = json.load(open(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'data', 'note_intervals_C0.json')))

# convert to bolahenk frequency from intervals
_freq_dict = {}
for key, val in _interval_dict.items():
    _freq_dict[key] = Converter.cent_to_hz(val - 500.0, 16.35)
_freq_dict['__'] = 0  # add rest

# types dictionary
_note_type_dict = {'whole': [2 ** 2, 1], 'half': [2 ** 1, 2],
                   'quarter': [2 ** 0, 4], 'eighth': [2 ** -1, 8],
                   '16th': [2 ** -2, 16], '32nd': [2 ** -3, 32],
                   '64th': [2 ** -4, 64]}

# makam dictionary
_makam_dict = json.load(open(os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'data', 'makam.json')))


def read_music_xml(fname):
    global numerator, denominator
    notes = []

    tree = parse(fname)
    root = tree.getroot()

    bpm = float(root.find('part/measure/direction/sound').attrib['tempo'])
    divs = float(root.find('part/measure/attributes/divisions').text)
    q_note_len = 60000. / bpm

    makam = _get_makam(root)

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
                    acc = _accidental_dict["{0}".format(acc)]
            except:
                acc = 0

            # type of note
            try:
                note_type = note.find('type').text
                note_ratio = _note_type_dict['{0}'.format(note_type)][0]
                note_payda = _note_type_dict['{0}'.format(note_type)][1]

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
                    denominator = _note_type_dict['{0}'.format(note_type)][1]

            except:
                pass

        except:
            print("ornamentation is ignored")

        note_sym = _get_symbtr_note_sym(step, octave, acc)

        # freq calculations
        freq = _freq_dict['{0}{1}'.format(step, octave)]
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
    return {'notes': notes, 'bpm': bpm, 'makam': makam}


def _get_makam(root):
    if root.find('part/measure/direction/direction-type/words').text:
        # the information is stored in the form below:
        # "Makam: [makam], Form: [form], Usul: [usul] "
        cultural_info = root.find(
            'part/measure/direction/direction-type/words').text

        attributes = []
        for info in cultural_info.split(","):
            attributes.append(''.join(info.split(": ")[1]).strip())

        makam, form, usul = attributes
    else:
        warnings.warn("Makam information does not exist.")
        makam = ''

    return _get_makam_slug(makam)


def _get_symbtr_note_sym(step, octave, acc):
    if acc == 0:  # natural
        acc_str = ''
    elif acc < 0:  # flat
        acc_str = 'b' + str(abs(acc))
    else:  # sharp
        acc_str = '#' + str(acc)
    note_sym = step + octave + acc_str

    return note_sym


def _get_makam_slug(makam_mu2_name):
    for makam_slug, makam_val in _makam_dict.items():
        if makam_val['mu2_name'] == makam_mu2_name:
            return makam_slug
