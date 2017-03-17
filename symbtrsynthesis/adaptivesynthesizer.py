import os

from .synthesizer.synth_S_microtonal import make_wav as synth_karplus
from .synthesizer.synth_A_microtonal import make_wav as synth_sine

from .musicxmlreader import read_music_xml
from .musicxmlreader import interval_dict
from .reader import MusicXMLReader

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
    reader = MusicXMLReader()
    melody_extractor = PredominantMelodyMakam()
    pitch_filter = PitchFilter()
    tonic_identifier = TonicLastNote()
    note_modeler = NoteModel()

    def __init__(self):
        pass

    @staticmethod
    def synthesize(musicxml_path, ref_rec='', synth_type='karplus',
                   out='', verbose=False):
        if verbose:
            logging.basicConfig(level=logging.DEBUG)

        if not ref_rec == '':
            assert os.path.exists(ref_rec), 'reference should either be ' \
                                            'empty (AEU theory) or a wav ' \
                                            'file.'
        assert synth_type in ['sine', 'karplus'], 'synth_type! should ' \
                                                  'be either "sine" or ' \
                                                  '"karplus".'
        # read music score
        logging.info(u"Reading the MusicXML file: {}".format(musicxml_path))
        (measures, makam, usul, form, time_sigs, keysig, work_title, composer,
         lyricist, bpm, tnc_sym) = AdaptiveSynthesizer.reader.read(
            musicxml_path)

        if ref_rec == '':
            logging.info("Synthesizing the score wrt AEU theory")
            stablenotes = None
        else:  # audio recording as the reference
            logging.info("Synthesizing the score wrt the recording: {}".format(
                ref_rec))
            stablenotes = AdaptiveSynthesizer._extract_tuning_from_recording(
                ref_rec, makam)

        if not out:
            out = musicxml_path[:-4] + "--adapted_" + synth_type + ".wav"

        # synthesize
        AdaptiveSynthesizer.synth_from_tuning(
            measures, bpm, stable_notes=stablenotes, synth_type=synth_type,
            out=out,
            verbose=verbose)

    @staticmethod
    def _extract_tuning_from_recording(reference, makam):
        # extract predominant melody
        logging.info("... Extracting the predominant melody")
        pitch = AdaptiveSynthesizer.melody_extractor.extract(reference)[
            'pitch']
        pitch = AdaptiveSynthesizer.pitch_filter.run(pitch)
        # identify tonic
        logging.info("... Extracting the tonic")
        tonic = AdaptiveSynthesizer.tonic_identifier.identify(pitch)[0]
        # tuning analysis
        logging.info("... Extracting the tuning")
        pitch_distribution = PitchDistribution.from_hz_pitch(
            pitch[:, 1], ref_freq=tonic['value'])
        stablenotes = AdaptiveSynthesizer.note_modeler.calculate_notes(
            pitch_distribution, tonic['value'], makam,
            min_peak_ratio=0.1)
        return stablenotes

    @staticmethod
    def synth_from_tuning(measures, bpm, stable_notes=None,
                          synth_type='karplus', out='out.wav', verbose=False):
        assert synth_type in ['sine', 'karplus'], 'Unknown synthesis type! ' \
                                                  'Choose "sine" or "karplus"'

        # if given, replace the note pitches wrt the tuning extracted from the
        # audio reference
        score = AdaptiveSynthesizer._get_notes_from_measures(measures)

        if stable_notes is not None:
            logging.info("Replacing the pitches wrt the audio tuning")
            AdaptiveSynthesizer._replace_tuning(score, stable_notes, verbose)

        # synthesize
        if synth_type == 'sine':
            synth_sine(score, bpm, fn=out, verbose=verbose)
        elif synth_type == 'karplus':
            synth_karplus(score, bpm, fn=out, verbose=verbose)

    @staticmethod
    def _replace_tuning(score, stable_notes, verbose, tnc_sym):
        for note in score:
            note_sym = note[0].upper() + str(note[1])

            try:
                note[11] = stable_notes[note_sym]['stable_pitch']['value']
            except KeyError:
                if note_sym == u'r':  # rest
                    pass
                else:  # tuning not available for the note symbol
                    if verbose:
                        logging.debug(u'No tuning estimation for the note {}. '
                                      u'Falling back to the theoretical (AEU) '
                                      u'interval'.format(note_sym))
                    theo_int = interval_dict[note_sym] - interval_dict[tnc_sym]
                    tonic_freq = stable_notes[tnc_sym]['stable_pitch']['value']

                    note[11] = Converter.cent_to_hz(theo_int, tonic_freq)

    @staticmethod
    def _get_notes_from_measures(measures):
        notes = []
        for measure in measures:
            for note in measure:
                notes.append(note)
        return notes
