#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#                                                       ____      _     _      
#                                                      | __ ) ___(_) __| | ___ 
#                                                      |  _ \/ __| |/ _` |/ _ \
#                                                      | |_) \__ \ | (_| |  __/
#                                                      |____/|___/_|\__,_|\___|
#                         
#============================================================(C) JPL 2019=======

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
import random

#-------------------------------------------------------------------------------
# Class Lorem
#-------------------------------------------------------------------------------
class Lorem():
    WORDS = ("adipisci aliquam amet consectetur dolor dolore dolorem eius est et"
             "incidunt ipsum labore magnam modi neque non numquam porro quaerat qui"
             "quia quisquam sed sit tempora ut velit voluptatem").split()
                      
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, wsep=' ', ssep=' ', psep='\n\n',
                 srange=(4, 8), prange=(5, 10), trange=(3, 6),
                 words=None):
        self._wsep = wsep
        self._ssep = ssep
        self._psep = psep
        self._srange = srange
        self._prange = prange
        self._trange = trange
        if words:
            self._words = words
        else:
            self._words = self.WORDS

#-------------------------------------------------------------------------------
# sentence()
#-------------------------------------------------------------------------------
    def sentence(self):
        n = random.randint(*self._srange)
        s = self._wsep.join(self._word() for _ in range(n))
        return s[0].upper() + s[1:] + '.'

#-------------------------------------------------------------------------------
# paragraph()
#-------------------------------------------------------------------------------
    def paragraph(self):
        n = random.randint(*self._prange)
        p = self._ssep.join(self.sentence() for _ in range(n))
        return p

#-------------------------------------------------------------------------------
# text()
#-------------------------------------------------------------------------------
    def text(self):
        n = random.randint(*self._trange)
        t = self._psep.join(self.paragraph() for _ in range(n))
        return t

#-------------------------------------------------------------------------------
# _word()
#-------------------------------------------------------------------------------
    def _word(self):
        return random.choice(self._words)         