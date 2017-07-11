from __future__ import division
from abc import ABCMeta, abstractmethod

import numpy as np


class ScoreEvent(object):
    """
    An abstract class representing a score event
    """
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        """
        Parameters:
            kwargs, named arguments:
                onset_ts (float): onset timestamp (seconds)
                onset_tick (int): onset MIDI tick
                offset_ts (float): offset timestamp (seconds)
                offset_tick (int): offset MIDI tick
        """

        # onset timestamp
        self.onset_ts = kwargs.get('onset_ts')
        self.onset_tick = kwargs.get('onset_tick')
        # offset timestamp
        self.offset_ts = kwargs.get('offset_ts')
        self.offset_tick = kwargs.get('offset_tick')

    @property
    def duration(self):
        if self.offset_ts and self.onset_ts:
            return self.offset_ts - self.onset_ts


class Note(ScoreEvent):
    """
    Represents a note with pitch and optionally timing information
    """

    pitch_classes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

    def __init__(self, pname, octave, id=None, **kwargs):
        """
        Parameters:
            id (String): id of the xml element this note originates from
            pname (String): pitch name
            octave (int): octave number
            id (String): note identifier
        """

        super(Note, self).__init__(**kwargs)

        # pitch class
        if pname.upper() in Note.pitch_classes:
            self.__pname = pname.upper()
        elif pname[-1] == 'b':
            # there's a flat, convert it to a sharp
            i = Note.pitch_classes.index(pname[:-1])
            self.__pname = Note.pitch_classes[(i-1) % len(Note.pitch_classes)]
        else:
            raise ValueError('Invalid pitch name')

        # octave
        self.__oct = octave

        # midi
        self.__midi_number = Note.pitch_to_midi(pname, octave)

        self.id = id

    @staticmethod
    def midi_to_pitch(midi_number):
        """
        Convert midi number to pitch name and octave

        Parameters:
            midi_number (int): midi number in [0, 127]

        Return:
            pname (String): pitch name
            oct (int): octave
        """

        if not 0 <= midi_number <= 127:
            raise ValueError("midi number must be in [0,127]")

        num_chroma = len(Note.pitch_classes)

        pname = Note.pitch_classes[midi_number % 12]
        octave = int(midi_number / num_chroma) - 1

        return pname, octave

    @staticmethod
    def pitch_to_midi(pname, octave):
        """
        Converts pitch name and octave to MIDI number

        Parameters:
            pname (String): pitch name
            octave (int): octave number

        Returns:
            midi_number (int): MIDI number in [0,127]
        """

        p_ind = Note.pitch_classes.index(pname)
        num_chroma = len(Note.pitch_classes)

        midi = (octave + 1) * num_chroma + p_ind

        return midi if 0 <= midi <= 127 else None

    @staticmethod
    def midi_to_freq(m):
        """
        Converts midi number to frequency (A4 relative)

        Parameters:
            m (int): midi number
        """

        return 2**((m-69)/12.)*440

    @property
    def midi_number(self):
        return self.__midi_number

    @midi_number.setter
    def midi_number(self, midi_number):
        if not 0 <= midi_number <= 127:
            raise ValueError("MIDI number must be in [0,127]")
        self.__midi_number = midi_number
        pname, octave = Note.midi_to_pitch(midi_number)
        self.__pname = pname
        self.__oct = octave

    @property
    def pname(self):
        return self.__pname

    @pname.setter
    def pname(self, pname):
        if pname not in Note.pitch_classes:
            raise ValueError("Note pitch must be a valid pitch class")
        self.__pname = pname
        self.__midi_number = Note.pitch_to_midi(pname, self.__oct)

    @property
    def oct(self):
        return self.__oct

    @oct.setter
    def oct(self, octave):
        if octave < 0:
            raise ValueError("Octave number must be greater than 0")
        self.__oct = octave
        self.__midi_number = Note.pitch_to_midi(self.__pname, octave)

    @property
    def frequency(self):
        # returns frequency of note in Hz
        return Note.midi_to_freq(self.__midi_number)

    def __add__(self, step):
        """
        Add an integer number of semitones to the note
        """

        num_chroma = len(Note.pitch_classes)
        step_up = True
        if step < 0:
            step_up = False

        note = Note(self.pname, self.oct, id=self.id)
        p_ind = Note.pitch_classes.index(self.pname)
        new_p_ind = (p_ind + step) % num_chroma

        note.pname = Note.pitch_classes[new_p_ind]
        oct_diff = int(step / 12)

        note.oct = self.oct + oct_diff

        if oct_diff == 0:
            if step_up:
                if new_p_ind >= 0 and new_p_ind < p_ind:
                    note.oct += 1
            else:
                if new_p_ind > p_ind and new_p_ind < num_chroma:
                    note.oct -= 1

        return note

    def __sub__(self, step):
        """
        Subtract an integer number of semitones to the note
        """

        return self.__add__(-step)

    def __eq__(self, other_note):
        return self.pname == other_note.pname and self.oct == other_note.oct

    def __lt__(self, other_note):
        return self.oct < other_note.oct or (self.oct == other_note.oct and Note.pitch_classes.index(self.pname) < Note.pitch_classes.index(other_note.pname))

    def __le__(self, other_note):
        return self.__lt__(other_note) or self.__eq__(other_note)

    def __gt__(self, other_note):
        return self.oct > other_note.oct or (self.oct == other_note.oct and Note.pitch_classes.index(self.pname) > Note.pitch_classes.index(other_note.pname))

    def __ge__(self, other_note):
        return self.__gt__(other_note) or self.__eq__(other_note)

    def __str__(self):
        note_str = "<%s%d [midi: %d]" % (self.pname, self.oct, self.midi_number)
        if self.onset_ts and self.offset_ts:
            note_str += " @ (%.2fs, %.2fs)" % (self.onset_ts, self.offset_ts)
        note_str += ">"
        return note_str

    def __repr__(self):
        return self.__str__()
