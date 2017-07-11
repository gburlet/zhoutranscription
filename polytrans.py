import os
import argparse
import numpy as np
import vamp

from librosa import load
from scoreevent import Note
from midiio import MidiIO

# set up command line argument structure
parser = argparse.ArgumentParser(description='Estimate the pitches in an audio file.')
parser.add_argument('filein', help='input file')
parser.add_argument('fileout', help='output file')
parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true')


class PolyTrans(object):
    def __init__(self, step_size=441, hop_size=441):
        self._step_size = step_size
        self._hop_size = hop_size

    def transcribe(self, audio_path):
        if not os.path.exists(audio_path):
            raise ValueError('Invalid audio path')

        x, fs = load(audio_path, mono=True)

        notes = vamp.collect(x, fs, "qm-vamp-plugins:qm-transcription", output="transcription")['list']
        # access attributes of a note event by:
        # ts: f.timestamp
        # duration: f.duration
        # MIDI notes: f.values

        return notes

    def write_midi(self, notes, output_path):
        note_events = []
        for n in notes:
            midi_num = int(n['values'][0])+1 # everything is transposed a semitone down in the vamp plugin, who knows why
            pname, oct = Note.midi_to_pitch(midi_num)
            onset_ts = float(n['timestamp'])
            offset_ts = onset_ts + float(n['duration'])
            note_event = Note(pname, oct, onset_ts=onset_ts, offset_ts=offset_ts)
            note_events.append(note_event)
        song_notes = sorted(note_events, key=lambda x: x.onset_ts)

        m = MidiIO(output_path)
        m.write_midi(song_notes, 25)

if __name__ == '__main__':
    # parse command line arguments
    args = parser.parse_args()

    input_path = args.filein
    if not os.path.exists(input_path):
        raise ValueError('The input file does not exist')

    output_path = args.fileout

    # check file extensions are correct for this type of conversion
    _, output_ext = os.path.splitext(output_path)
    if output_ext != '.mid':
        raise ValueError('Ouput path must have the file extension .mid')

    t = PolyTrans()
    note_events = t.transcribe(input_path)
    t.write_midi(note_events, output_path)
