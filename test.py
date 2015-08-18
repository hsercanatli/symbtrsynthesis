__author__ = 'hsercanatli'

from adaptive_tuning import AdaptiveTuning
from compmusic.extractors.makam.pitch import PitchExtractMakam
import json
import os
from tonic import TonicLastNote

def getFileNamesInDir(dir_name, ext=".mp3", skipFoldername=''):
    """

    :param dir_name:
    :param ext:
    :param skipFoldername:
    :return: returnpath = dir
             fileNames = release/songnames
    """
    names = []
    folders = []

    for (path, dirs, files) in os.walk(dir_name):
        for f in files:
            if ext in f.lower():
                if skipFoldername not in path.split(os.sep)[1:]:
                    names.append(f)
                    folders.append(path)

    returnpath = [folders[i] + '/' + names[i] for i in range(len(folders))]
    lastFolders = [folders[i].replace(dir_name, '') for i in range(len(folders))]
    fileNames = [lastFolders[i][1:] + '/' + names[i][:-len(ext)] for i in range(len(names))]

    return returnpath, fileNames
'''
ext = PitchExtractMakam()

mp3list, dump = getFileNamesInDir("/home/hsercanatli/Desktop/adaptive-test")

for element in mp3list:
    print element
    results = ext.run(element)
    pitch = json.loads(results['pitch'])

    # json file; loaded from the settings and pitch
    jsondata = json.loads(results['settings'])
    jsondata['pitch'] = pitch
    with open(element[:-4] + ".json", 'w') as f:
        json.dump(jsondata, f)

    with open(element[:-4] + ".txt", 'w') as f:
        for p in pitch:
            f.write(str(p[0]) + "\t" + str(p[1]) + "\t" + str(p[2]) + "\n")

#        f.write(str(pitch[0]))
'''

'''
pitchlist, dump = getFileNamesInDir("/home/hsercanatli/Desktop/adaptive-test", ext=".json")

for element in pitchlist:
    print element

    with open(element) as f: pitch = json.load(f)
    #with open(element[:-5] + '.txt', 'w') as f:
    #    for item in pitch['pitch']:
    #        f.write(str(item[0]) + "\t" + str(item[1]) + "\t" + str(item[2]) + "\n")
    tnc = TonicLastNote(pitch)
    tnc.compute_tonic(plot=True)
'''


adapt = AdaptiveTuning(pitch_path="/home/hsercanatli/Desktop/adaptive-test/huzzam/Usta/2-01_huzzam_taksim.json",
                       musicxml_score_path="/home/hsercanatli/Desktop/adaptive-test/huzzam/huzzam--pesrev--fahte----gazi_giray_han.xml")
adapt.adapt_score_frequencies(synth=True)