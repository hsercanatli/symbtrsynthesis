from ..synthesizer import synth_karplus, synth_sine
from ..musicxml_reader import read_music_xml
from ..musicxml_reader import interval_dict

from ahenkidentifier.ahenkidentifier import AhenkIdentifier
from morty.converter import Converter


__author__ = ['hsercanatli', 'sertansenturk']


class Tuner:
    ahenk_identifier = AhenkIdentifier()

    def __init__(self):
        pass

    @staticmethod
    def get_tonic_sym(stable_notes):
        for key, val in stable_notes.items():
            if val['theoretical_interval']['value'] == 0:
                return key

    @staticmethod
    def adapt_score_frequencies(musicxml_path, stable_notes,
                                synth_type='karplus', out='', verbose=False):

        assert synth_type in ['sine', 'karplus'], 'Unknown synthesis type! ' \
                                                  'Choose "sine" or "karplus"'

        # read the MusicXML score
        score = read_music_xml(musicxml_path)
        tonic_symbol = Tuner.get_tonic_sym(stable_notes)

        # adapt the tuning
        for note in score['notes']:
            note_sym = note[0]

            try:
                note[2] = stable_notes[note_sym]['stable_pitch']['value']
            except KeyError:
                if note_sym == '__':  # rest
                    pass
                else:
                    if verbose:
                        print(u'No tuning estimation for the note {}. Falling '
                              u'back to the theoretical (AEU) interval'.format(
                            note_sym))
                    theo_int = interval_dict[note_sym] - interval_dict[
                        tonic_symbol]
                    tonic_freq = stable_notes[tonic_symbol]['stable_pitch'][
                        'value']

                    note[2] = Converter.cent_to_hz(theo_int, tonic_freq)

        if not out:
            out = musicxml_path[:-4] + "--adapted_" + synth_type + ".wav"

        # synthesize
        if synth_type == 'sine':
            synth_sine(score, fn=out, verbose=verbose)
        elif synth_type == 'karplus':
            synth_karplus(score, fn=out, verbose=verbose)
