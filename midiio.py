from __future__ import division
import os
from pretty_midi import PrettyMIDI, Instrument
from pretty_midi import Note as MidiNote

from frettableserver.resources.score.scoreevent import Note


class MidiIO(object):
    """
    This class forms an abstraction around the python-midi module
    """

    DEFAULT_TEMPO = 120
    DEFAULT_PPQ = 480
    DEFAULT_VELOCITY = 100

    def __init__(self, path):
        """
        Initialize the MIDI reader/writer.

        PARAMETERS:
        path (string) path to read/write the MIDI file
        """
        self._path = path

    def write_midi(self, score_events, midi_program, pitch_low_passband=0, pitch_high_passband=127, time_offset=0.0):
        """
        Given a sequence of NoteEvents, calculate the MIDI ticks for each note and write these to a MIDI file.

        PARAMETERS:
            score_events (list): list of ScoreEvents
            midi_program (int): MIDI program to use for the MIDI track
            pitch_low_passband (int): discard any pitches with midi numbers less than this bound
            pitch_high_passband (int): discard any pitches with midi numbers greater than this bound
            time_offset (float): amount of time (s) to delay MIDI note events
        """

        midi = PrettyMIDI(resolution=MidiIO.DEFAULT_PPQ, initial_tempo=MidiIO.DEFAULT_TEMPO)
        instr = Instrument(program=midi_program)
        for n in score_events:
            if pitch_low_passband <= n.midi_number <= pitch_high_passband:
                note = MidiNote(
                    velocity=MidiIO.DEFAULT_VELOCITY, pitch=n.midi_number,
                    start=(n.onset_ts + time_offset), end=(n.offset_ts + time_offset)
                )
                instr.notes.append(note)
        midi.instruments.append(instr)
        midi.remove_invalid_notes()

        directory = os.path.split(self._path)[0]
        if not os.path.exists(directory):
            os.makedirs(directory)
        midi.write(self._path)
