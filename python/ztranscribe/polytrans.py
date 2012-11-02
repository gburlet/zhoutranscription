import os
import argparse
import numpy as np
from scikits.audiolab import wavread
from ztranscribe.transcribe import Transcription, FeatureList, Feature, RealTime
from pymei import MeiDocument, MeiElement, XmlExport

# set up command line argument structure
parser = argparse.ArgumentParser(description='Estimate the pitches in an audio file.')
parser.add_argument('filein', help='input file')
parser.add_argument('fileout', help='output file')
parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')

class PolyTrans:

    def __init__(self, guitar=True, step_size=441, hop_size=441):
        self._guitar = guitar
        self._step_size = step_size
        self._hop_size = hop_size

    def transcribe(self, audio_path):
        if not os.path.exists(audio_path):
            raise ValueError('Invalid audio path')

        x, fs, _ = wavread(audio_path)

        # make x mono if stereo
        if x.ndim > 1:
            _, n_channels = x.shape
            x = x.sum(axis=1)/n_channels

        t = Transcription(fs)
        t.initialise(1, self._step_size, self._hop_size)

        t.inputAudio(x)
        features = t.getRemainingFeatures()[0]

        return features

    def write_mei(self, features, output_path=None):
        # begin constructing mei document
        meidoc = MeiDocument()
        mei = MeiElement('mei')
        meidoc.setRootElement(mei)
        mei_head = MeiElement('meiHead')
        mei.addChild(mei_head)

        music = MeiElement('music')
        body = MeiElement('body')
        mdiv = MeiElement('mdiv')
        score = MeiElement('score')
        score_def = MeiElement('scoreDef')

        # assume 4/4 time signature
        meter_count = 4
        meter_unit = 4
        score_def.addAttribute('meter.count', str(meter_count))
        score_def.addAttribute('meter.unit', str(meter_unit))
        
        staff_def = MeiElement('staffDef')
        staff_def.addAttribute('n', '1')
        staff_def.addAttribute('label.full', 'Electric Guitar')
        staff_def.addAttribute('clef.shape', 'TAB')

        instr_def = MeiElement('instrDef')
        instr_def.addAttribute('n', 'Electric_Guitar')
        instr_def.addAttribute('midi.channel', '1')
        instr_def.addAttribute('midi.instrnum', '28')

        mei.addChild(music)
        music.addChild(body)
        body.addChild(mdiv)
        mdiv.addChild(score)
        score.addChild(score_def)
        score_def.addChild(staff_def)
        staff_def.addChild(instr_def)

        section = MeiElement('section')
        score.addChild(section)
        # another score def
        score_def = MeiElement('scoreDef')
        score_def.addAttribute('meter.count', str(meter_count))
        score_def.addAttribute('meter.unit', str(meter_unit))
        section.addChild(score_def)
        
        # start writing pitches to file
        for f in features:
            print "ts: ", f.timestamp
            print "duration: ", f.duration
            print "MIDI: ", f.values

        if self._guitar:
            self._guitarify(meidoc)

    def _guitarify(self, meidoc):
        pass

if __name__ == '__main__':
    # parse command line arguments
    args = parser.parse_args()

    input_path = args.filein
    if not os.path.exists(input_path):
        raise ValueError('The input file does not exist')

    output_path = args.fileout

    # check file extensions are correct for this type of conversion
    _, input_ext = os.path.splitext(input_path)
    if input_ext != '.wav':
        raise ValueError('Input path must be a wav file')
    _, output_ext = os.path.splitext(output_path)
    if output_ext != '.mei':
        raise ValueError('Ouput path must have the file extension .mei')

    t = PolyTrans(guitar=True)
    features = t.transcribe(input_path)
    t.write_mei(features, output_path)
