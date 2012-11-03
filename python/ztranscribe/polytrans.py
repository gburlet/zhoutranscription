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

semitones = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

def gen_midi_map():
    midi_map = {}
    oct = 0
    for i in range(88):
        semitone = semitones[i % 12]
        if semitone == 'C':
            oct += 1

        midi_map[i+21] = (semitone, oct)

    return midi_map

class PolyTrans:
    
    # map from midi number to note (pitch name and octave)
    midi_map = gen_midi_map()

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
        # access attributes of a note event (feature) in features by
        # ts: f.timestamp
        # duration: f.duration
        # MIDI notes: f.values

        # combine features with the same timestamps
        note_events = []
        for f in features:
            ts = f.timestamp.toSeconds()
            note_num = int(f.values[0])
            # if the last timestamp is equal to this timestamp, combine into a chord
            if len(note_events) > 0 and note_events[-1][0] == ts:
                note_events[-1][1].append(note_num)
            else:
                note_events.append([ts, [note_num]])

        if self._guitar:
            self._guitarify(note_events)

        print note_events

        return note_events

    def _guitarify(self, note_events):
        for i in range(len(note_events)-1,-1,-1):
            # filter pitches outside of the guitar range (standard tuning)
            # TODO: make this dynamic according to the guitar tuning
            pruned_notes = filter(lambda n: n>= 40 and n <= 88, note_events[i][1])
            if len(pruned_notes) > 0:
                # update notes with the pruned notes for the guitar
                note_events[i][1] = pruned_notes
            else:
                del note_events[i]

    def write_mei(self, note_events, output_path=None):
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
        note_container = None
        for i, note_event in enumerate(note_events):
            if i % meter_count == 0:
                measure = MeiElement('measure')
                measure.addAttribute('n', str(int(i/meter_count + 1)))
                staff = MeiElement('staff')
                staff.addAttribute('n', '1')
                layer = MeiElement('layer')
                layer.addAttribute('n', '1')
                section.addChild(measure)
                measure.addChild(staff)
                staff.addChild(layer)
                note_container = layer

            notes = note_event[1]
            if len(notes) > 1:
                chord = MeiElement('chord')
                for n in notes:
                    note = MeiElement('note')
                    note_info = PolyTrans.midi_map[n]
                    pname = note_info[0]
                    oct = note_info[1]
                    note.addAttribute('pname', pname[0])
                    note.addAttribute('oct', str(oct))
                    if len(pname) > 1 and pname[-1] == '#':
                        # there is an accidental
                        note.addAttribute('accid.ges', 's')
                    note.addAttribute('dur', str(meter_unit))
                    chord.addChild(note)
                note_container.addChild(chord)
            else:
                n = notes[0]
                note = MeiElement('note')
                note_info = PolyTrans.midi_map[n]
                pname = note_info[0]
                oct = note_info[1]
                note.addAttribute('pname', pname[0])
                note.addAttribute('oct', str(oct))
                if len(pname) > 1 and pname[-1] == '#':
                    # there is an accidental
                    note.addAttribute('accid.ges', 's')
                note.addAttribute('dur', str(meter_unit))
                note_container.addChild(note)

        if output_path is not None:
            XmlExport.meiDocumentToFile(meidoc, output_path)
        else:
            return XmlExport.meiDocumentToText(meidoc)

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
    note_events = t.transcribe(input_path)
    t.write_mei(note_events, output_path)
