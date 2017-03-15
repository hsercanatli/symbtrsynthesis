import os

from . synthesizer import synth_karplus, synth_sine
from . musicxml_reader import read_music_xml
from . musicxml_reader import interval_dict

from morty.converter import Converter
from predominantmelodymakam.predominantmelodymakam import \
    PredominantMelodyMakam
from pitchfilter.pitchfilter import PitchFilter
from tonicidentifier.toniclastnote import TonicLastNote
from morty.pitchdistribution import PitchDistribution
from notemodel.notemodel import NoteModel

import logging
logging.basicConfig(level=logging.WARNING)

__author__ = ['hsercanatli', 'sertansenturk']


class AdaptiveSynthesizer:
    melody_extractor = PredominantMelodyMakam()
    pitch_filter = PitchFilter()
    tonic_identifier = TonicLastNote()
    note_modeler = NoteModel()

    def __init__(self):
        pass

    @staticmethod
    def get_tonic_sym(stable_notes):
        for key, val in stable_notes.items():
            if val['theoretical_interval']['value'] == 0:
                return key

    @staticmethod
    def synthesize(musicxml_path, reference='', synth_type='karplus',
                   out='', verbose=False):
        if verbose:
            logging.basicConfig(level=logging.DEBUG)

        if not reference == '':
            assert os.path.exists(reference), 'reference should either be ' \
                                              'empty (AEU theory) or a wav ' \
                                              'file.'
        assert synth_type in ['sine', 'karplus'], 'synth_type! should ' \
                                                  'be either "sine" or ' \
                                                  '"karplus".'
        # read music score
        logging.info(u"Reading the MusicXML file: {}".format(musicxml_path))
        score = read_music_xml(musicxml_path)

        if reference == '':
            logging.info("Synthesizing the score wrt AEU theory")
            stablenotes = None
        else:
            logging.info("Synthesizing the score wrt the recording: {}".format(
                reference))

            # extract predominant melody
            logging.info("... Extracting the predominant melody")
            pitch = AdaptiveSynthesizer.melody_extractor.extract(reference)['pitch']
            pitch = AdaptiveSynthesizer.pitch_filter.run(pitch)

            # identify tonic
            logging.info("... Extracting the tonic")
            tonic = AdaptiveSynthesizer.tonic_identifier.identify(pitch)[0]

            # tuning analysis
            logging.info("... Extracting the tuning")
            pitch_distribution = PitchDistribution.from_hz_pitch(
                pitch[:, 1], ref_freq=tonic['value'])
            stablenotes = AdaptiveSynthesizer.note_modeler.calculate_notes(
                pitch_distribution, tonic['value'], score['makam'],
                min_peak_ratio=0.1)

        if not out:
            out = musicxml_path[:-4] + "--adapted_" + synth_type + ".wav"

        # synthesize
        AdaptiveSynthesizer.synth_from_tuning(score, stable_notes=stablenotes,
                                              synth_type='karplus', out=out,
                                              verbose=verbose)

    @staticmethod
    def synth_from_tuning(score, stable_notes=None,
                          synth_type='karplus', out='out.wav', verbose=False):
        assert synth_type in ['sine', 'karplus'], 'Unknown synthesis type! ' \
                                                  'Choose "sine" or "karplus"'

        # read the MusicXML score
        tonic_symbol = AdaptiveSynthesizer.get_tonic_sym(stable_notes)

        # if given, replace the note pitches wrt the tuning extracted from the
        # audio reference
        if stable_notes is not None:
            logging.info("Replacing the pitches wrt the audio tuning")
            AdaptiveSynthesizer._replace_tuning(score, stable_notes, tonic_symbol, verbose)

        # synthesize
        if synth_type == 'sine':
            synth_sine(score, fn=out, verbose=verbose)
        elif synth_type == 'karplus':
            synth_karplus(score, fn=out, verbose=verbose)

    @staticmethod
    def _replace_tuning(score, stable_notes, tonic_symbol, verbose):
        for note in score['notes']:
            note_sym = note[0]

            try:
                note[2] = stable_notes[note_sym]['stable_pitch']['value']
            except KeyError:
                if note_sym == '__':  # rest
                    pass
                else:  # tuning not available for the note symbol
                    if verbose:
                        logging.debug(u'No tuning estimation for the note {}. '
                                      u'Falling back to the theoretical (AEU) '
                                      u'interval'.format(note_sym))
                    theo_int = interval_dict[note_sym] - interval_dict[
                        tonic_symbol]
                    tonic_freq = stable_notes[tonic_symbol]['stable_pitch'][
                        'value']

                    note[2] = Converter.cent_to_hz(theo_int, tonic_freq)
