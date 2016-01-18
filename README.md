# adaptivetuning
This repository hosts the implementations of an adaptive tuning method and a synthesizer for [SymbTr](https://github.com/MTG/SymbTr) scores.

The user can synthesize a score w.r.t. the performed pitches of a related recording or the user can directly synthesize a SymbTr score with the theoretical intervals.

Usage of synthesizing a score with theoretical intervals
=======
```python
from adaptivetuning.synthesizer.synth_symbtr import synth_symbtr

# This function synthesizes the score according to the theoretical intervals.
# It takes a time w.r.t. the length of given SymbTr. 
# If you want to observe the status of the process, give "verbose" flag as true.
# Possible synth types are 'sine' and 'karplus' 
# 'Sine' option takes less time.

synth_symbtr(musicxml_path="sampledata/saba--ornek_oz--sofyan--2--ruhi_ayangil/saba--ornek_oz--sofyan--2--ruhi_ayangil.xml",
             type='karplus', verbose=False)

synth_symbtr(musicxml_path="sampledata/saba--ornek_oz--sofyan--2--ruhi_ayangil/saba--ornek_oz--sofyan--2--ruhi_ayangil.xml",
             type='sine', verbose=True, out='out.wav')
```

Usage of synthesizing a score with performed intervals
=======
```python
import json

from pitchfilter.pitchfilter import PitchPostFilter
from tonic_identifier.tonic_identifier import TonicLastNote
from adaptivetuning.tuner.tuner import Tuner
from adaptivetuning.synthesizer.synth_symbtr import synth_symbtr

# loading extracted pitch of a related recording of the selected SymbTr for adaptive tuning
pitch = json.load(open("sampledata/huseyni--sazsemaisi--aksaksemai----tatyos_efendi/8b8d697b-cad9-446e-ad19-5e85a36aa253.json", 'r'))['pitch']

# Post process the pitch track to get rid of spurious pitch estimations and correct octave errors
flt = PitchPostFilter()
pitch = flt.run(pitch)

# identification of the tonic for the related recording of SymbTr

tnc = TonicLastNote()
tonic, pitch, pitch_chunks, pitch_distribution, stable_pitches = tnc.identify(pitch)

# Adapting the tuning and synthesizing the SymbTr
# This part synthesizes the score according to the related audio recording. 
# Extracted stable pitches are used as reference in synth function.
# It takes a time w.r.t. the length of given SymbTr. If you want to obseve the status of the process, give "verbose" flag as true.
# Possible synth types are 'sine' and 'karplus' 'Sine' option takes less time.

adapt = Tuner()
theoretical_histogram, adapted_histogram = adapt.adapt_score_frequencies(musicxml_path="sampledata/huseyni--sazsemaisi--aksaksemai----tatyos_efendi/huseyni--sazsemaisi--aksaksemai----tatyos_efendi.xml",
                                                                         performed_tonic=tonic['value'],
                                                                         stable_pitches=stable_pitches,
                                                                         type='karplus',
                                                                         verbose=False)
```

Please refer to demo.ipynb for an interactive demo.

Installation
============

If you want to install the repository, it is recommended to install the package and dependencies into a virtualenv. In the terminal, do the following:

    virtualenv env
    source env/bin/activate
    python setup.py install

If you want to be able to edit files and have the changes be reflected, then install the repo like this instead

    pip install -e .

The tonic identifier algorithm uses some modules in Essentia. 
Follow the [instructions](essentia.upf.edu/documentation/installing.html) to install the library, otherwise, there would be an error for identification of the tonic from the extracted pitch.
You can synthesize the SymbTr scores with theoretical intervals without installing Essentia.
Then you should link the python bindings of Essentia in the virtual environment:

    ln -s /usr/local/lib/python2.7/dist-packages/essentia env/lib/python2.7/site-packages

Then you can install the rest of the dependencies:

    pip install -r requirements

Authors
-------
Hasan Sercan Atlı	hsercanatli@gmail.com  
Sertan Şentürk		contact@sertansenturk.com
