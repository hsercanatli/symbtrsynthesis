# adaptivetuning
This repository hosts the implementations of an adaptive tuning method and a synthesizer for [SymbTr](https://github.com/MTG/SymbTr) scores in MusicXML format.

The user can synthesize a SymbTr score in MusicXML format with the theoretical intervals or according to a tuning extracted from the performed pitches of a related recording.

This repository hosts the implementation of the adaptive tuning proposed in:

_Şentürk, S., Holzapfel, A., and Serra, X. (2012). An approach for linking score and audio recordings in makam music of Turkey. In Proceedings of 2nd CompMusic Workshop, pages 95–106, Istanbul, Turkey._

If you are using this code, please cite the above paper. 

Synthesizing a score with theoretical intervals
=======
```python
from adaptivetuning.synthesizer.synth_symbtr import synth_symbtr

synth_symbtr(musicxml_path="sampledata/saba--ornek_oz--sofyan--2--ruhi_ayangil/saba--ornek_oz--sofyan--2--ruhi_ayangil.xml",
             out='out.wav', type='karplus', verbose=False)

synth_symbtr(musicxml_path="sampledata/saba--ornek_oz--sofyan--2--ruhi_ayangil/saba--ornek_oz--sofyan--2--ruhi_ayangil.xml",
             out='out.wav', type='sine', verbose=True, out='out.wav')
```

Synthesizing a score according to a performance
=======
```python
import json

from pitchfilter.pitchfilter import PitchPostFilter
from tonicidentifier.tonicidentifier import TonicLastNote
from adaptivetuning.tuner.tuner import Tuner
from adaptivetuning.synthesizer.synth_symbtr import synth_symbtr

# load extracted pitch of a related recording of the selected SymbTr for adaptive tuning
# You can use predominantmelodymakam (https://github.com/sertansenturk/predominantmelodymakam) to compute the pitch track
pitch = json.load(open("sampledata/huseyni--sazsemaisi--aksaksemai----tatyos_efendi/8b8d697b-cad9-446e-ad19-5e85a36aa253.json", 'r'))['pitch']

# Post process the pitch track to get rid of spurious pitch estimations and correct octave errors
flt = PitchPostFilter()
pitch = flt.run(pitch)

# identify the tonic for the related recording of SymbTr
tnc = TonicLastNote()
tonic, pitch, pitch_chunks, pitch_distribution, stable_pitches = tnc.identify(pitch)

# Adapt the tuning and synthesizing the SymbTr
tuner = Tuner()
theoretical_histogram, adapted_histogram = tuner.adapt_score_frequencies(musicxml_path="sampledata/huseyni--sazsemaisi--aksaksemai----tatyos_efendi/huseyni--sazsemaisi--aksaksemai----tatyos_efendi.xml",
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
Follow the [instructions](http://essentia.upf.edu/documentation/installing.html) to install the library, otherwise, there would be an error for identification of the tonic from the extracted pitch.
You can synthesize the SymbTr scores with theoretical intervals without installing Essentia.
Then you should link the python bindings of Essentia in the virtual environment:

    ln -s /usr/local/lib/python2.7/dist-packages/essentia env/lib/python2.7/site-packages

Then you can install the rest of the dependencies:

    pip install -r requirements

Additional Code
-------
The synthesis files [synth_A_microtonal.py](https://github.com/hsercanatli/adaptivetuning/blob/master/adaptivetuning/synthesizer/synth_A_microtonal.py) and [synth_S_microtonal.py](https://github.com/hsercanatli/adaptivetuning/blob/master/adaptivetuning/synthesizer/synth_S_microtonal.py) are derived from [Martin C. Doege](https://github.com/mdoege/)'s synthesis code hosted in [PySynth](https://github.com/mdoege/PySynth/). Please see the files for more detail.

Authors
-------
Hasan Sercan Atlı	hsercanatli@gmail.com  
Sertan Şentürk		contact@sertansenturk.com
