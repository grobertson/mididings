# -*- coding: utf-8 -*-
#
# mididings
#
# Copyright (C) 2008  Dominic Sacré  <dominic.sacre@gmx.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#

import _mididings


class Types:
    NOTEON      = 1 << 0
    NOTEOFF     = 1 << 1
    NOTE        = NOTEON | NOTEOFF
    CONTROLLER  = 1 << 2
    PITCHBEND   = 1 << 3
    PGMCHANGE   = 1 << 4


PORT      = -1
CHANNEL   = -2
# generic
DATA1     = -3
DATA2     = -4
# note
NOTE      = -3
VELOCITY  = -4
# controller
PARAM     = -3
VALUE     = -4
# program change
PROGRAM   = -4


class _MidiEventEx(_mididings.MidiEvent):
    def make_get_set(typ, data):
        def getter(self):
            if not self.type & typ:
                print "midi event attribute error"
            return getattr(self, data)

        def setter(self, value):
            if not self.type & typ:
                print "midi event attribute error"
            setattr(self, data, value)

        return (getter, setter)

    note     = property(*make_get_set(Types.NOTE, 'data1'))
    velocity = property(*make_get_set(Types.NOTE, 'data2'))
    param    = property(*make_get_set(Types.CONTROLLER, 'data1'))
    value    = property(*make_get_set(Types.CONTROLLER | Types.PITCHBEND | Types.PGMCHANGE, 'data2'))