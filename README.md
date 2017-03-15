# adaptivetuning
This repository hosts the implementations of an adaptive tuning method and a synthesizer for [SymbTr](https://github.com/MTG/SymbTr) scores in MusicXML format.

The user can synthesize a SymbTr score in MusicXML format with the theoretical intervals or according to a tuning extracted from the performed pitches of a related recording.

This repository hosts the implementation of the adaptive tuning proposed in:

_Şentürk, S., Holzapfel, A., and Serra, X. (2012). An approach for linking score and audio recordings in makam music of Turkey. In Proceedings of 2nd CompMusic Workshop, pages 95–106, Istanbul, Turkey._

If you are using this code, please cite the above paper. 

Synthesizing a score with theoretical intervals
=======
```python
from adaptivetuning.tuner.tuner import Tuner

Tuner.synthesize(score_file, synth_type='karplus', verbose=False)
```

Synthesizing a score according to a performance
=======
```python
from adaptivetuning.tuner.tuner import Tuner

Tuner.synthesize(score_file, reference=audio_file, synth_type='karplus', verbose=False)                                                   verbose=False)
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

Then you can install the rest of the dependencies:

    pip install -r requirements

Additional Code
-------
The synthesis files [synth_A_microtonal.py](https://github.com/hsercanatli/adaptivetuning/blob/master/adaptivetuning/synthesizer/synth_A_microtonal.py) and [synth_S_microtonal.py](https://github.com/hsercanatli/adaptivetuning/blob/master/adaptivetuning/synthesizer/synth_S_microtonal.py) are derived from [Martin C. Doege](https://github.com/mdoege/)'s synthesis code hosted in [PySynth](https://github.com/mdoege/PySynth/). Please see the files for more detail.

The quality of the extracted pitch track will greatly affect the synthesis. We suggest to use [predominantmelodymakam package](https://github.com/sertansenturk/predominantmelodymakam) to extract the pitch track and [pitch-post-filter](https://github.com/hsercanatli/pitch-post-filter) for post-processing (removing spurious estimations, octave correction etc.). Adaptive tuning and synthesis also needs the tonic frequency of the audio recording. For automatic tonic identification, you can use [tonicidentifier_makam](https://github.com/hsercanatli/tonicidentifier_makam). You can refer to the demo above for how to call these modules.

The suggested packages above uses some modules in Essentia. 
Follow the [instructions](http://essentia.upf.edu/documentation/installing.html) to install the library, otherwise, there would be an error for identification of the tonic from the extracted pitch.
You can synthesize the SymbTr scores with theoretical intervals without installing Essentia.
Then you should link the python bindings of Essentia in the virtual environment:

    ln -s /usr/local/lib/python2.7/dist-packages/essentia env/lib/python2.7/site-packages

Acknowledgements
----------------
We would like to thank [Harold Hagopian](https://en.wikipedia.org/wiki/Harold_Hagopian), the founder of [Traditional Crossroads](http://traditionalcrossroads.com/About-Us), for allowing us to use Tanburi Cemil Bey's performance of [Uşşak Sazsemaisi](http://musicbrainz.org/recording/f970f1e0-0be9-4914-8302-709a0eac088e) in our demos.

Authors
-------
Hasan Sercan Atlı	hsercanatli@gmail.com  
Sertan Şentürk		contact@sertansenturk.com
