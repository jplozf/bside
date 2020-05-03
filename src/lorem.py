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
import os
import binascii
import uuid
from Crypto.PublicKey import RSA

import bitcoin

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
    mw.cbxLorem.addItem("Bitcoin Address")  
    # https://strm.sh/post/bitcoin-address-generation/ 
    # https://www.freecodecamp.org/news/how-to-create-a-bitcoin-wallet-address-from-a-private-key-eca3ddd9c05f/
    
    mw.btnLoremGenerate.clicked.connect(lambda _, mw=mw : doLoremGenerate(mw))
    mw.btnLoremCopy.clicked.connect(lambda _, mw=mw : doLoremCopy(mw))
    mw.cbxLorem.currentIndexChanged.connect(lambda _, mw=mw : onLoremChanged(mw))
    mw.cbxLorem.setCurrentIndex(0)
    mw.chkLoremText.setChecked(True)
    
#-------------------------------------------------------------------------------
# doLoremText()
#-------------------------------------------------------------------------------
def doLoremGenerate(mw):
    if mw.cbxLorem.currentText() == "Lorem Ipsum" or mw.cbxLorem.currentText() == "Hacker News":
        if mw.cbxLorem.currentText() == "Lorem Ipsum":
            txt = Lorem()
        elif mw.cbxLorem.currentText() == "Hacker News":
            txt = Hacker()
        if mw.chkLoremText.isChecked() == True:
            mw.txtLorem.setPlainText(txt.text())
        elif mw.chkLoremParagraph.isChecked() == True:
            mw.txtLorem.setPlainText(txt.paragraph())
        elif mw.chkLoremSentence.isChecked() == True:
            mw.txtLorem.setPlainText(txt.sentence())
    elif mw.cbxLorem.currentText() == "Hexadecimal":
        mw.txtLorem.setPlainText(genHexa(mw))
    elif mw.cbxLorem.currentText() == "UUID":
        mw.txtLorem.setPlainText(genUUID(mw))
    elif mw.cbxLorem.currentText() == "Private/Public Keys":
        mw.txtLorem.setPlainText(genRSAKeys(mw))
    elif mw.cbxLorem.currentText() == "Bitcoin Address":
        mw.txtLorem.setPlainText(genBitcoinAddress(mw))
                           
#-------------------------------------------------------------------------------
# copyNameToClipboard()
#-------------------------------------------------------------------------------
def doLoremCopy(mw):
    QApplication.clipboard().setText(mw.txtLorem.toPlainText())
    mw.showMessage("Copy to clipboard")
    
#-------------------------------------------------------------------------------
# genHexa()
#-------------------------------------------------------------------------------
def genHexa(mw):    
    return binascii.b2a_hex(os.urandom(mw.spnLoremNumber.value())).decode("utf-8") 

#-------------------------------------------------------------------------------
# genUUID()
#-------------------------------------------------------------------------------
def genUUID(mw):
    uuids = ""
    for i in range(mw.spnLoremNumber.value()):
        id = uuid.uuid4()
        uuids = uuids + str(id) + "\n"
    return uuids

#-------------------------------------------------------------------------------
# genRSAKeys()
#-------------------------------------------------------------------------------
def genRSAKeys(mw):
    # key = RSA.generate(2048)
    # f = open("private.pem", "wb")
    # f.write(key.exportKey('PEM'))
    # f.close()
    # pubkey = key.publickey()
    # f = open("public.pem", "wb")
    # f.write(pubkey.exportKey('OpenSSH'))
    # f.close()
    rsa = ""
    for i in range(mw.spnLoremNumber.value()):
        key = RSA.generate(2048)
        rsa = rsa + key.exportKey('PEM').decode("utf-8") + "\n"
        pubkey = key.publickey()
        # rsa = rsa + pubkey.exportKey('OpenSSH').decode("utf-8") + "\n"
        rsa = rsa + pubkey.exportKey('PEM').decode("utf-8") + "\n\n"
    return rsa
    
#-------------------------------------------------------------------------------
# genBitcoinAddress()
#-------------------------------------------------------------------------------
def genBitcoinAddress(mw):    
    bitcoins = ""
    for _ in range(mw.spnLoremNumber.value()):
        randomBytes = os.urandom(32)
        bitcoins = bitcoins + "Bitcoin Address : " + bitcoin.getPublicKey(randomBytes) + "\n"
        bitcoins = bitcoins + "Private Key     : " + bitcoin.getWif(randomBytes) + "\n\n"
    return bitcoins

#-------------------------------------------------------------------------------
# onLoremChanged()
#-------------------------------------------------------------------------------
def onLoremChanged(mw):
    if mw.cbxLorem.currentText() == "Lorem Ipsum":
        mw.chkLoremText.setEnabled(True)
        mw.chkLoremParagraph.setEnabled(True)
        mw.chkLoremSentence.setEnabled(True)
        mw.spnLoremNumber.setEnabled(False)
        mw.spnLoremNumber.setValue(0)
    elif mw.cbxLorem.currentText() == "Hacker News":
        mw.chkLoremText.setEnabled(True)
        mw.chkLoremParagraph.setEnabled(True)
        mw.chkLoremSentence.setEnabled(True)
        mw.spnLoremNumber.setEnabled(False)
        mw.spnLoremNumber.setValue(0)
    elif mw.cbxLorem.currentText() == "Hexadecimal":
        mw.chkLoremText.setEnabled(False)
        mw.chkLoremParagraph.setEnabled(False)
        mw.chkLoremSentence.setEnabled(False)
        mw.spnLoremNumber.setEnabled(True)
        mw.spnLoremNumber.setValue(512)
    elif mw.cbxLorem.currentText() == "UUID":
        mw.chkLoremText.setEnabled(False)
        mw.chkLoremParagraph.setEnabled(False)
        mw.chkLoremSentence.setEnabled(False)
        mw.spnLoremNumber.setEnabled(True)
        mw.spnLoremNumber.setValue(10)
    elif mw.cbxLorem.currentText() == "Private/Public Keys":
        mw.chkLoremText.setEnabled(False)
        mw.chkLoremParagraph.setEnabled(False)
        mw.chkLoremSentence.setEnabled(False)
        mw.spnLoremNumber.setEnabled(True)
        mw.spnLoremNumber.setValue(10)
    elif mw.cbxLorem.currentText() == "Bitcoin Address":
        mw.chkLoremText.setEnabled(False)
        mw.chkLoremParagraph.setEnabled(False)
        mw.chkLoremSentence.setEnabled(False)
        mw.spnLoremNumber.setEnabled(True)
        mw.spnLoremNumber.setValue(10)
        
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
   
#-------------------------------------------------------------------------------
# Class Hacker
#-------------------------------------------------------------------------------
class Hacker():    
    WORDS = ("""
        *.*
        access
        ack
        admin
        afk
        alloc
        ascii
        back_door
        ban
        bang
        big-endian
        bin
        bit
        blob
        boolean
        break
        brute_force
        bubble_sort
        buffer
        bytes
        cache
        cd
        char
        chown
        class
        client
        clock
        concurrently
        continue
        cookie
        crypto
        css
        ctl-c
        d00dz
        daemon
        data
        database
        ddos
        deadlock
        default
        Dennis_Ritchie
        dereference
        dir
        do
        Donald_Knuth
        double
        echo
        else
        emacs
        eof
        epoch
        error
        exception
        fail
        false
        fatal
        file
        finally
        firewall
        flood
        flush
        foad
        folder
        foo
        foo_bar
        fopen
        for
        fork
        fork_bomb
        form
        format
        frack
        function
        gc
        gcc
        giga
        gnu
        gobble
        grep
        gurfle
        hack_the_mainframe
        hash
        headers
        hello_world
        hexadecimal
        highjack
        html
        if
        ifdef
        I'm_compiling
        I'm_sorry_Dave,_I'm_afraid_I_can't_do_that
        in
        infinite_loop
        injection
        int
        interpreter
        ip
        irc
        it's_a_feature
        James_T._Kirk
        java
        keyboard
        kilo
        L0phtCrack
        leapfrog
        leet
        Leslie_Lamport
        less
        lib
        Linus_Torvalds
        linux
        long
        loop
        machine_code
        mailbomb
        mainframe
        malloc
        man_pages
        memory_leak
        mountain_dew
        mouse
        mutex
        nak
        new
        null
        over
        overflow
        packet
        password
        perl
        php
        piggyback
        port
        pragma
        private
        protected
        protocol
        public
        pwned
        python
        race_condition
        rainbow_table
        recursively
        red_bull
        regex
        rm_-rf
        root
        rsa
        salt
        script_kiddies
        segfault
        select
        semaphore
        server
        shell
        small_values
        snarf
        sniffer
        socket
        spoof
        sql
        ssh
        stack
        Starcraft
        stdio.h
        strlen
        sudo
        suitably
        syn
        system
        table
        tarball
        tcp
        tera
        terminal
        thread
        throw
        todo
        trace
        Trojan_horse
        true
        try_catch
        tunnel
        unix
        var
        vi
        virus
        void
        wabbit
        wannabee
        warez
        watchdog
        while
        win
        windows
        wombat
        worm
        xml
        xss
        x-window
    """).split()    
    
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
        return random.choice(self._words).replace("_", " ")
    
    
