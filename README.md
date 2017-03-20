# symbtrsynthesis
This repository hosts the implementations of an adaptive synthesizer for [SymbTr](https://github.com/MTG/SymbTr) scores in MusicXML format.

The user can synthesize a SymbTr score in MusicXML format with either the theoretical intervals or according to a tuning extracted from the performed pitches of a related recording.

This repository hosts the implementation of the adaptive tuning proposed in:

_Şentürk, S., Holzapfel, A., and Serra, X. (2012). An approach for linking score and audio recordings in makam music of Turkey. In Proceedings of 2nd CompMusic Workshop, pages 95–106, Istanbul, Turkey._

If you are using this code, please cite the above paper. 

Synthesizing a score with theoretical intervals
=======
```python
from symbtrsynthesis.adaptivesynthesizer import AdaptiveSynthesizer

AdaptiveSynthesizer.synthesize(score_file, synth_type='karplus', verbose=False)
```

Synthesizing a score according to a performance
=======
```python
from symbtrsynthesis.adaptivesynthesizer import AdaptiveSynthesizer

AdaptiveSynthesizer.synthesize(
    score_file, reference=audio_file, synth_type='karplus', verbose=False)                                                   verbose=False)
```

Please refer to demo.ipynb for an interactive demo and step-by-step explanations.

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

The required packages above uses some modules in Essentia. Follow the [instructions](http://essentia.upf.edu/documentation/installing.html) to install the library. Then you should link the python bindings of Essentia in the virtual environment:

    ln -s /usr/local/lib/python2.7/dist-packages/essentia env/lib/python2.7/site-packages

Additional Code
-------
The synthesis files [synth_A_microtonal.py](https://github.com/hsercanatli/adaptivetuning/blob/master/adaptivetuning/synthesizer/synth_A_microtonal.py) and [synth_S_microtonal.py](https://github.com/hsercanatli/adaptivetuning/blob/master/adaptivetuning/synthesizer/synth_S_microtonal.py) are derived from [Martin C. Doege](https://github.com/mdoege/)'s synthesis code hosted in [PySynth](https://github.com/mdoege/PySynth/). Please see the files for more detail.

Acknowledgements
----------------
We would like to thank [Harold Hagopian](https://en.wikipedia
.org/wiki/Harold_Hagopian), the founder of [Traditional Crossroads]
(http://traditionalcrossroads.com/About-Us), for allowing us to use Tanburi Cemil Bey's performance in our demo. This work is partially supported by the European Research Council under the European Union's Seventh Framework Program, as part of the CompMusic project (ERC grant agreement 267583).

Authors
-------
Hasan Sercan Atlı	hsercanatli@gmail.com  
Sertan Şentürk		contact@sertansenturk.com
