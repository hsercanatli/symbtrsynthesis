from .. synthesizer import *
from .. musicxml_reader import read_music_xml


def synth_symbtr(musicxml_path, type='sine', out=''):
    score = read_music_xml(musicxml_path)

    if not out:
        if type == 'sine': out = musicxml_path[:-4] + "--sine.wav"
        if type == 'karplus': out = musicxml_path[:-4] + "--karplus.wav"

    if type == 'sine':
        synth_sine(score, fn=out)

    if type == 'karplus':
        synth_karplus(score, fn=out)
