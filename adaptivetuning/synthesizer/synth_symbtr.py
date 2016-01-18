from .. synthesizer import *
from .. musicxml_reader import read_music_xml


def synth_symbtr(musicxml_path):
    score = read_music_xml(musicxml_path)

    synth_karplus(score, fn=musicxml_path[:-4] + "--karplus.wav")
    synth_sine(score, fn=musicxml_path[:-4] + "--sine.wav")
