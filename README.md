Polyphonic Transcription
------------------------

Polyphonic transcription algorithm by Ruohua Zhou, Josh Reiss (2009). Ported from Vamp plugin to standalone application with python bindings.

Author: Gregory Burlet

Installation
------------
`make`

Python Installation
-------------------
Dependencies:
Boost.NumPy (https://github.com/ndarray/Boost.NumPy)
install using `scons & scons install`
The boost/numpy headers will be installed to `/usr/local/include`
The boost/numpy dynamic library will be installed to `/usr/local/lib` 

Now compile the dynamic library with the polyphonic transcription code:
```
make dylib
cd python
python setup.py build
sudo python setup.py install
```
The dynamic library will be installed in `/usr/local/lib`
