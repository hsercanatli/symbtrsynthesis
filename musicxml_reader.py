# -*- coding: utf-8 -*-
__author__ = 'hsercanatli'

from xml.etree.ElementTree import parse
from fractions import Fraction

# accidentals dictionary
accidental_dict = {'quarter-flat': -1, 'slash-flat': -4, 'flat': -5, 'double-slash-flat': -8,
                   'slash-quarter-sharp': +1, 'sharp': +4, '': +5, 'slash-sharp': +8}

# frequency dictionary
freq_dict = {'__': 0, 'G3': 196, 'A3': 220, 'B3': 247, 'C4': 262, 'D4': 294, 'E4': 330,
             'F4': 349, 'G4': 392, 'A4': 440, 'B4': 493, 'C5': 523, 'D5': 587,
             'E5': 659, 'F5': 698, 'G5': 783, 'A5': 880, 'B5': 988, 'C6': 1046,
             'D6': 1174, 'E6': 1318, 'F6': 1396, 'G6': 1566, 'B6': 1976, 'C7': 2092}

# types dictionary
note_type_dict = {'whole': [2 ** 2, 1], 'half': [2 ** 1, 2], 'quarter': [2 ** 0, 4],
                  'eighth': [2 ** -1, 8], '16th': [2 ** -2, 16], '32nd': [2 ** -3, 32],
                  '64th': [2 ** -4, 64]}


def read_music_xml(fname):
    global pay, payda
    notes = []

    tree = parse(fname)
    root = tree.getroot()

    bpm = float(root.find('part/measure/direction/sound').attrib['tempo'])
    divs = float(root.find('part/measure/attributes/divisions').text)
    q_note_len = 60000. / bpm

    count = 1
    for note in root.findall('part/measure/note'):
        temp_note = []
        dur = note.find('duration').text

        # step and octave information
        try:
            step = note.find('pitch/step').text
            octave = note.find('pitch/octave').text
        except:
            step = '_'
            octave = '_'

        # accidentals information
        try:
            acc = note.find('accidental').text
            if type(acc) is type(None): acc = 0
            else: acc = accidental_dict["{0}".format(acc)]
        except: acc = 0

        # type of note
        try:
            note_type = note.find('type').text
            note_ratio = note_type_dict['{0}'.format(note_type)][0]
            note_payda = note_type_dict['{0}'.format(note_type)][1]
            # dotted notes
            try:
                if type(note.find('dot').text):
                    pay_payda = max(
                        ((44100. * 60 * note_ratio / bpm) / (int(q_note_len * float(dur) / divs) * 1e-3 * 44100.)),
                        ((int(q_note_len * float(dur) / divs) * 1e-3 * 44100.) /
                         (44100. * 60 / bpm * note_ratio))) / note_payda
                    pay = int(Fraction(pay_payda).limit_denominator(100).numerator)
                    payda = int(Fraction(pay_payda).limit_denominator(100).denominator)

            except:
                pay = 1
                payda = note_type_dict['{0}'.format(note_type)][1]

        except: pass

        # freq calculations
        freq = freq_dict['{0}'.format(step + octave)]
        if acc != 0: freq *= 2 ** (acc / 53.0)

        temp_note.append(step + octave)
        temp_note.append(acc)
        temp_note.append(int(freq))
        temp_note.append(pay)
        temp_note.append(payda)
        temp_note.append(int(q_note_len * float(dur) * 1e-3 * 44100 / divs))

        notes.append(temp_note)
        count += 1
    return {'notes': notes, 'bpm': bpm}
