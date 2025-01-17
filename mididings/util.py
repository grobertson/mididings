# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008-2014  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import mididings.misc as _misc
import mididings.constants as _constants
import mididings.setup as _setup

import sys as _sys


_NOTE_NUMBERS = {
    'c':   0,
    'c#':  1, 'db':  1,
    'd':   2,
    'd#':  3, 'eb':  3,
    'e':   4,
    'f':   5,
    'f#':  6, 'gb':  6,
    'g':   7,
    'g#':  8, 'ab':  8,
    'a':   9,
    'a#': 10, 'bb': 10,
    'b':  11,
}

_NOTE_NAMES = {
     0: 'c',
     1: 'c#',
     2: 'd',
     3: 'd#',
     4: 'e',
     5: 'f',
     6: 'f#',
     7: 'g',
     8: 'g#',
     9: 'a',
    10: 'a#',
    11: 'b',
}

_CONTROLLER_NAMES = {
     0: 'Bank select (MSB)',
     1: 'Modulation',
     6: 'Data entry (MSB)',
     7: 'Volume',
    10: 'Pan',
    11: 'Expression',
    32: 'Bank select (LSB)',
    38: 'Data entry (LSB)',
    64: 'Sustain',
    65: 'Portamento',
    66: 'Sostenuto',
    67: 'Soft pedal',
    68: 'Legato pedal',
    98: 'NRPN (LSB)',
    99: 'NRPN (MSB)',
   100: 'RPN (LSB)',
   101: 'RPN (MSB)',
   121: 'Reset all controllers',
   123: 'All notes off',
}


def note_number(note, allow_end=False):
    """
    note_number(note)

    Convert note name to note number.

    :param note:
        any valid :ref:`note description <notes>` (name or number).
    :return:
        MIDI note number.
    """
    if isinstance(note, int):
        r = note
    elif isinstance(note, str):
        note = note.lower()
        # find first digit
        for i in range(len(note)):
            if note[i].isdigit() or note[i] == '-':
                break
        try:
            name = note[:i]
            octave = int(note[i:])
            r = (_NOTE_NUMBERS[name] +
                    (octave + _setup.get_config('octave_offset')) * 12)
        except Exception:
            raise ValueError("invalid note name '%s'" % note)
    else:
        raise TypeError("note must be an integer or string")

    end = 128 if not allow_end else 129
    if not (0 <= r < end):
        raise ValueError("note number %d is out of range" % r)
    return r


def note_limit(note):
    return note_number(note, allow_end=True)


def note_range(notes):
    """
    Convert note range to note numbers.

    :param notes:
        any valid :ref:`note range <notes>`
        (names or numbers, tuple or string).
        If this is a single note, the range containing only that note is
        returned.
    :return:
        tuple of two MIDI note numbers.
    """
    try:
        # single note
        n = note_number(notes)
        return (n, n + 1)
    except Exception:
        try:
            if isinstance(notes, tuple):
                # tuple of note numbers
                return note_limit(notes[0]), note_limit(notes[1])
            elif isinstance(notes, str):
                # note range string
                nn = notes.split(':', 1)
                lower = note_limit(nn[0]) if nn[0] else 0
                upper = note_limit(nn[1]) if nn[1] else 0
                return lower, upper
            else:
                raise TypeError("note range must be a tuple"
                                " of integers or a string")
        except (ValueError, IndexError):
            raise ValueError("invalid note range %r" % notes)


def note_name(note):
    """
    Get note name from note number.

    :param note:
        a MIDI note number.
    :return:
        note name as a string.
    """
    if not isinstance(note, int):
        raise TypeError("note must be an integer")
    return _NOTE_NAMES[note % 12] + str(
                (note // 12) - _setup.get_config('octave_offset'))


def tonic_note_number(key):
    return _NOTE_NUMBERS[key]


def controller_name(ctrl):
    """
    Get controller description.
    """
    if ctrl in _CONTROLLER_NAMES:
        return _CONTROLLER_NAMES[ctrl]
    else:
        return None


def event_type(type):
    if type not in _constants._EVENT_TYPES:
        raise ValueError("invalid event type %r" % type)
    return type


def port_number(port):
    """
    Convert port description to port number.

    :param port:
        a :ref:`port name <ports>` or number.
    :return:
        the port's number.
    """
    if isinstance(port, int):
        if actual(port) < 0:
            raise ValueError("invalid port number %d" % port)
        return port
    elif isinstance(port, str):
        in_ports = _setup._in_portnames
        out_ports = _setup._out_portnames

        if (port in in_ports and port in out_ports and
                in_ports.index(port) != out_ports.index(port)):
            raise ValueError("port name '%s' is ambiguous" % port)
        elif port in in_ports:
            return offset(in_ports.index(port))
        elif port in out_ports:
            return offset(out_ports.index(port))
        else:
            raise ValueError("invalid port name '%s'" % port)
    else:
        raise TypeError("port must be an integer or string")


def channel_number(channel):
    if not isinstance(channel, int):
        raise TypeError("channel must be an integer")
    if not (0 <= actual(channel) < 16):
        raise ValueError("channel number %d is out of range" % channel)
    return channel


def program_number(program):
    if not isinstance(program, int):
        raise TypeError("program must be an integer")
    if not (0 <= actual(program) < 128):
        raise ValueError("program number %d is out of range" % program)
    return program


def ctrl_number(ctrl):
    if not isinstance(ctrl, int):
        raise TypeError("controller must be an integer")
    if not (0 <= ctrl < 128):
        raise ValueError("controller number %d is out of range" % ctrl)
    return ctrl


def ctrl_value(value, allow_end=False):
    if not isinstance(value, int):
        raise TypeError("controller value must be an integer")
    end = 128 if not allow_end else 129
    if not (0 <= value < end):
        raise ValueError("controller value %d is out of range" % value)
    return value

def ctrl_limit(value):
    return ctrl_value(value, allow_end=True)

def ctrl_range(value):
    try:
        n = ctrl_value(value)
        return (n, n + 1)
    except Exception:
        if isinstance(value, tuple) and len(value) == 2:
            return (ctrl_limit(value[0]), ctrl_limit(value[1]))
    raise ValueError("invalid controller value range %r" % value)


def velocity_value(velocity, allow_end=False):
    if not isinstance(velocity, int):
        raise TypeError("velocity must be an integer")
    end = 128 if not allow_end else 129
    if not (0 <= velocity < end):
        raise ValueError("velocity %d is out of range" % velocity)
    return velocity

def velocity_limit(velocity):
    return velocity_value(velocity, allow_end=True)

def velocity_range(velocity):
    try:
        n = velocity_value(velocity)
        return (n, n + 1)
    except Exception:
        if isinstance(velocity, tuple) and len(velocity) == 2:
            return (velocity_limit(velocity[0]), velocity_limit(velocity[1]))
    raise ValueError("invalid velocity range %r" % velocity)


def scene_number(scene):
    if not isinstance(scene, int):
        raise TypeError("scene number must be an integer")
    if actual(scene) < 0:
        raise ValueError("scene number %d is out of range" % scene)
    return scene


def subscene_number(subscene):
    if not isinstance(subscene, int):
        raise TypeError("subscene number must be an integer")
    if actual(subscene) < 0:
        raise ValueError("subscene number %d is out of range" % subscene)
    return subscene


def sysex_to_bytearray(sysex):
    if isinstance(sysex, str):
        if sysex.startswith('F0') or sysex.startswith('f0'):
            if len(sysex) < 3 or sysex[2] not in ', \f\n\r\t\v':
                return bytearray(int(sysex[i:i+2], 16)
                                 for i in range(0, len(sysex), 2))
            else:
                return bytearray(int(x, 16) for x in sysex.split(sysex[2]))
        else:
            return bytearray(map(ord, sysex))
    elif isinstance(sysex, bytearray):
        return sysex
    else:
        return bytearray(sysex)


def sysex_data(sysex, allow_partial=False):
    sysex = sysex_to_bytearray(sysex)
    if len(sysex) < 2:
        raise ValueError("sysex too short")
    elif sysex[0] != 0xf0:
        raise ValueError("sysex doesn't start with F0")
    elif sysex[-1] != 0xf7 and not allow_partial:
        raise ValueError("sysex doesn't end with F7")
    else:
        for c in sysex[1:-1]:
            if c > 0x7f:
                raise ValueError("sysex data byte %#x is out of range" % c)
    return sysex


def sysex_manufacturer(manufacturer):
    if not _misc.issequence(manufacturer, True):
        manufacturer = [manufacturer]
    manid = sysex_to_bytearray(manufacturer)
    if len(manid) not in (1, 3):
        raise ValueError("manufacturer id must be either one or three bytes")
    elif len(manid) == 3 and manid[0] != 0x00:
        raise ValueError("three-byte manufacturer id must start with 0x00")
    else:
        for c in manid:
            if c > 0x7f:
                raise ValueError("manufacturer id byte %#x is out of range" % c)
    return manid



class NoDataOffset(int):
    """
    An integer type that's unaffected by data offset conversions.
    """
    def __new__(cls, value):
        return int.__new__(cls, value)
    def __repr__(self):
        return 'NoDataOffset(%d)' % int(self)
    def __str__(self):
        return 'NoDataOffset(%d)' % int(self)


def offset(n):
    """
    Add current data offset.
    """
    return n + _setup.get_config('data_offset')


def actual(n):
    """
    Subtract current data offset to get the "real" value used on the C++ side.
    """
    if isinstance(n, NoDataOffset):
        return int(n)
    else:
        return n - _setup.get_config('data_offset')



# define wrappers around parameter check functions that will also accept
# event attribute references
def _allow_event_attribute(f):
    def func(first, *args, **kwargs):
        if isinstance(first, _constants._EventAttribute):
            return first
        else:
            return f(first, *args, **kwargs)
    return func

port_number_ref     = _allow_event_attribute(port_number)
channel_number_ref  = _allow_event_attribute(channel_number)
note_number_ref     = _allow_event_attribute(note_number)
velocity_value_ref  = _allow_event_attribute(velocity_value)
ctrl_number_ref     = _allow_event_attribute(ctrl_number)
ctrl_value_ref      = _allow_event_attribute(ctrl_value)
program_number_ref  = _allow_event_attribute(program_number)
scene_number_ref    = _allow_event_attribute(scene_number)
subscene_number_ref = _allow_event_attribute(subscene_number)
actual_ref          = _allow_event_attribute(actual)
