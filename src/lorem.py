#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===============================================================================
#                                                       ____      _     _      
#                                                      | __ ) ___(_) __| | ___ 
#                                                      |  _ \/ __| |/ _` |/ _ \
#                                                      | |_) \__ \ | (_| |  __/
#                                                      |____/|___/_|\__,_|\___|
#                         
#============================================================(C) JPL 2020=======

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import random

#-------------------------------------------------------------------------------
# initFormLorem()
#-------------------------------------------------------------------------------
def initFormLorem(mw):
    mw.txtLorem.setPlainText("")
    mw.txtLorem.setReadOnly(True)
    
    mw.cbxLorem.addItem("Lorem Ipsum")
    mw.cbxLorem.addItem("Hacker News")
    mw.cbxLorem.addItem("Hexadecimal")
    
    mw.cbxLorem.addItem("UUID")
    
    mw.cbxLorem.addItem("Private/Public Keys")
    
    # https://strm.sh/post/bitcoin-address-generation/ 
    # https://www.freecodecamp.org/news/how-to-create-a-bitcoin-wallet-address-from-a-private-key-eca3ddd9c05f/
    mw.cbxLorem.addItem("Bitcoin Address")  
    
    mw.btnLoremText.clicked.connect(lambda _, mw=mw : doLoremText(mw))
    mw.btnLoremParagraph.clicked.connect(lambda _, mw=mw : doLoremParagraph(mw))
    mw.btnLoremSentence.clicked.connect(lambda _, mw=mw : doLoremSentence(mw))
    mw.btnLoremCopy.clicked.connect(lambda _, mw=mw : doLoremCopy(mw))

#-------------------------------------------------------------------------------
# doLoremText()
#-------------------------------------------------------------------------------
def doLoremText(mw):
    txt = Lorem()
    mw.txtLorem.setPlainText(txt.text())
                           
#-------------------------------------------------------------------------------
# doLoremParagraph()
#-------------------------------------------------------------------------------
def doLoremParagraph(mw):
    txt = Lorem()
    mw.txtLorem.setPlainText(txt.paragraph())

#-------------------------------------------------------------------------------
# doLoremSentence()
#-------------------------------------------------------------------------------
def doLoremSentence(mw):
    txt = Lorem()
    mw.txtLorem.setPlainText(txt.sentence())

#-------------------------------------------------------------------------------
# copyNameToClipboard()
#-------------------------------------------------------------------------------
def doLoremCopy(mw):
    QApplication.clipboard().setText(mw.txtLorem.toPlainText())
    mw.showMessage("Copy Lorem Ipsum to clipboard")

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
    
"""
from Crypto.PublicKey import RSA
key = RSA.generate(1024) # or 2048
f = open("private.pem", "wb")
f.write(key.exportKey('PEM'))
f.close()

pubkey = key.publickey()
f = open("public.pem", "wb")
f.write(pubkey.exportKey('OpenSSH'))
f.close()

-- OR --

from os import chmod
from Crypto.PublicKey import RSA

key = RSA.generate(2048)
with open("/tmp/private.key", 'wb') as content_file:
    chmod("/tmp/private.key", 0600)
    content_file.write(key.exportKey('PEM'))
pubkey = key.publickey()
with open("/tmp/public.key", 'wb') as content_file:
    content_file.write(pubkey.exportKey('OpenSSH'))
"""    