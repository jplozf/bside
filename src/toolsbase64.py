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
import base64
import hashlib 
import re
import random

import utils

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------
ONE = 1
TWO = 2
ENCODE = 0
DECODE = 1

#-------------------------------------------------------------------------------
# doBase64()
#-------------------------------------------------------------------------------
def doBase64(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1
    if way == ENCODE:
        message = srcText.toPlainText()
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')    
        dstText.setPlainText(base64_message)
    else:
        base64_message = srcText.toPlainText()
        base64_bytes = base64_message.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')
        dstText.setPlainText(message)       

#-------------------------------------------------------------------------------
# doROT13()
#-------------------------------------------------------------------------------
def doROT13(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    

    rot13trans = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', 
       'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm')
    message = srcText.toPlainText()
    dstText.setPlainText(message.translate(rot13trans))
    
#-------------------------------------------------------------------------------
# doLeet()
#-------------------------------------------------------------------------------
def doLeet(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    

    leet = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', 
       '4bcd3f6h1jklmn0pqr57uvwxyz4bcd3f6h1jklmn0pqr57uvwxyz')
    message = srcText.toPlainText()
    dstText.setPlainText(message.translate(leet))
    
#-------------------------------------------------------------------------------
# doClever()
#-------------------------------------------------------------------------------
def doClever(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    

    message = srcText.toPlainText()
    clever = ""
    words = re.findall('\w+', message)
    for word in words:
        clever = clever + scramble(word) + " "
    
    dstText.setPlainText(clever)
    
#-------------------------------------------------------------------------------
# scramble()
#-------------------------------------------------------------------------------
def scramble(word):
    if len(word)>3:
        shStr = list(word[1:-1])
        random.shuffle(shStr)
        sword = word[0] + "".join(shStr) + word[-1]
    else:
        sword = word
    return sword

#-------------------------------------------------------------------------------
# doNTLM()
#-------------------------------------------------------------------------------
def doNTLM(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('md4', message.encode('utf-16le')).hexdigest())


#-------------------------------------------------------------------------------
# doSha3_256()
#-------------------------------------------------------------------------------
def doSha3_256(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('sha3_256', message.encode('utf-16le')).hexdigest())

#-------------------------------------------------------------------------------
# doBlake2b()
#-------------------------------------------------------------------------------
def doBlake2b(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('blake2b', message.encode('utf-16le')).hexdigest())

#-------------------------------------------------------------------------------
# doSha256()
#-------------------------------------------------------------------------------
def doSha256(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('sha256', message.encode('utf-16le')).hexdigest())

#-------------------------------------------------------------------------------
# doBlake2s()
#-------------------------------------------------------------------------------
def doBlake2s(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('blake2s', message.encode('utf-16le')).hexdigest())

#-------------------------------------------------------------------------------
# doShake_256()
#-------------------------------------------------------------------------------
def doShake_256(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('shake_256', message.encode('utf-16le')).hexdigest())

#-------------------------------------------------------------------------------
# doSha3_224()
#-------------------------------------------------------------------------------
def doSha3_224(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('sha3_224', message.encode('utf-16le')).hexdigest())

#-------------------------------------------------------------------------------
# doSha3_512()
#-------------------------------------------------------------------------------
def doSha3_512(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('sha3_512', message.encode('utf-16le')).hexdigest())

#-------------------------------------------------------------------------------
# doSha1()
#-------------------------------------------------------------------------------
def doSha1(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('sha1', message.encode('utf-16le')).hexdigest())

#-------------------------------------------------------------------------------
# doMd5()
#-------------------------------------------------------------------------------
def doMd5(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('md5', message.encode('utf-16le')).hexdigest())

#-------------------------------------------------------------------------------
# doSha384()
#-------------------------------------------------------------------------------
def doSha384(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('sha384', message.encode('utf-16le')).hexdigest())

#-------------------------------------------------------------------------------
# doSha224()
#-------------------------------------------------------------------------------
def doSha224(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('sha224', message.encode('utf-16le')).hexdigest())

#-------------------------------------------------------------------------------
# doSha512()
#-------------------------------------------------------------------------------
def doSha512(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('sha512', message.encode('utf-16le')).hexdigest())

#-------------------------------------------------------------------------------
# doShake_128()
#-------------------------------------------------------------------------------
def doShake_128(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('shake_128', message.encode('utf-16le')).hexdigest())

#-------------------------------------------------------------------------------
# doSha3_384()
#-------------------------------------------------------------------------------
def doSha3_384(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('sha3_384', message.encode('utf-16le')).hexdigest())

#-------------------------------------------------------------------------------
# doMd4()
#-------------------------------------------------------------------------------
def doMd4(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('md4', message.encode('utf-16le')).hexdigest())

#-------------------------------------------------------------------------------
# doSm3()
#-------------------------------------------------------------------------------
def doSm3(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('sm3', message.encode('utf-16le')).hexdigest())
    
#-------------------------------------------------------------------------------
# doRipemd160()
#-------------------------------------------------------------------------------
def doRipemd160(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('ripemd160', message.encode('utf-16le')).hexdigest())
    
#-------------------------------------------------------------------------------
# doWhirlpool()
#-------------------------------------------------------------------------------
def doWhirlpool(mw, fromText, way):
    if fromText == ONE:
        srcText = mw.txtBase64_1
        dstText = mw.txtBase64_2
    else:
        srcText = mw.txtBase64_2
        dstText = mw.txtBase64_1    
    message = srcText.toPlainText()
    dstText.setPlainText(hashlib.new('whirlpool', message.encode('utf-16le')).hexdigest())
    
algos = [
    ['Base64', True, lambda mw, fromText, way : doBase64(mw, fromText, way)],
    ['ROT13', True, lambda mw, fromText, way : doROT13(mw, fromText, way)],
    ['1337', False, lambda mw, fromText, way : doLeet(mw, fromText, way)],
    ['Clever', False, lambda mw, fromText, way : doClever(mw, fromText, way)],
    ['NTLM', False, lambda mw, fromText, way : doNTLM(mw, fromText, way)],    
    ['md4', False, lambda mw, fromText, way : doMd4(mw, fromText, way)],
    ['md5', False, lambda mw, fromText, way : doMd5(mw, fromText, way)],    
    ['sm3', False, lambda mw, fromText, way : doSm3(mw, fromText, way)],
    ['sha1', False, lambda mw, fromText, way : doSha1(mw, fromText, way)],    
    ['sha224', False, lambda mw, fromText, way : doSha224(mw, fromText, way)],    
    ['sha256', False, lambda mw, fromText, way : doSha256(mw, fromText, way)],    
    ['sha384', False, lambda mw, fromText, way : doSha384(mw, fromText, way)],    
    ['sha512', False, lambda mw, fromText, way : doSha512(mw, fromText, way)],    
    ['blake2b', False, lambda mw, fromText, way : doBlake2b(mw, fromText, way)],    
    ['blake2s', False, lambda mw, fromText, way : doBlake2s(mw, fromText, way)],    
    ['sha3_224', False, lambda mw, fromText, way : doSha3_224(mw, fromText, way)],    
    ['sha3_384', False, lambda mw, fromText, way : doSha3_384(mw, fromText, way)],
    ['sha3_256', False, lambda mw, fromText, way : doSha3_256(mw, fromText, way)],    
    ['sha3_512', False, lambda mw, fromText, way : doSha3_512(mw, fromText, way)],    
#   ['shake_128', False, lambda mw, fromText, way : doShake_128(mw, fromText, way)],    
#   ['shake_256', False, lambda mw, fromText, way : doShake_256(mw, fromText, way)],    
    ['ripemd160', False, lambda mw, fromText, way : doRipemd160(mw, fromText, way)],
    ['whirlpool', False, lambda mw, fromText, way : doWhirlpool(mw, fromText, way)]
]

#-------------------------------------------------------------------------------
# initBase64()
#-------------------------------------------------------------------------------
def initBase64(mw):
    mw.btnEncode_1_to_2.clicked.connect(lambda _, mw=mw : doEncode(mw, ONE))
    mw.btnDecode_1_to_2.clicked.connect(lambda _, mw=mw : doDecode(mw, ONE))
    mw.btnEncode_2_to_1.clicked.connect(lambda _, mw=mw : doEncode(mw, TWO))
    mw.btnDecode_2_to_1.clicked.connect(lambda _, mw=mw : doDecode(mw, TWO))
    mw.txtBase64_1.textChanged.connect(lambda mw=mw : computeSizeText(mw, ONE))
    mw.txtBase64_2.textChanged.connect(lambda mw=mw : computeSizeText(mw, TWO))
    mw.cbxCodec.currentIndexChanged.connect(lambda _, mw=mw : onCodecChanged(mw))
    mw.btnBase64Copy_1.clicked.connect(lambda _, mw=mw : doCopy(mw, ONE))
    mw.btnBase64Paste_1.clicked.connect(lambda _, mw=mw : doPaste(mw, ONE))
    mw.btnBase64Clear_1.clicked.connect(lambda _, mw=mw : doClear(mw, ONE))
    mw.btnBase64Copy_2.clicked.connect(lambda _, mw=mw : doCopy(mw, TWO))
    mw.btnBase64Paste_2.clicked.connect(lambda _, mw=mw : doPaste(mw, TWO))
    mw.btnBase64Clear_2.clicked.connect(lambda _, mw=mw : doClear(mw, TWO))
    
    for algo in algos:
        mw.cbxCodec.addItem(algo[0])
    
    mw.txtBase64_1.setPlainText("")
    mw.txtBase64_2.setPlainText("")
    
#-------------------------------------------------------------------------------
# doEncode()
#-------------------------------------------------------------------------------
def doEncode(mw, fromText):
    for algo in algos:
        if algo[0] == mw.cbxCodec.currentText():
            algo[2](mw, fromText, ENCODE)
    
#-------------------------------------------------------------------------------
# doDecode()
#-------------------------------------------------------------------------------
def doDecode(mw, fromText):
    for algo in algos:
        if algo[0] == mw.cbxCodec.currentText():
            algo[2](mw, fromText, DECODE)

#-------------------------------------------------------------------------------
# computeSizeText()
#-------------------------------------------------------------------------------
def computeSizeText(mw, src):
    if src == ONE:
        srcText = mw.txtBase64_1
        srcLabel = mw.lblSizeText_1
    else:
        srcText = mw.txtBase64_2
        srcLabel = mw.lblSizeText_2
        
    textLength = len(srcText.toPlainText())        
    srcLabel.setText("%d (%s)" % (textLength, utils.getHumanSize(textLength)))

#-------------------------------------------------------------------------------
# onCodecChanged()
#-------------------------------------------------------------------------------
def onCodecChanged(mw):
    for algo in algos:
        if algo[0] == mw.cbxCodec.currentText():
            if algo[1] == True:
                mw.btnEncode_1_to_2.setEnabled(True)
                mw.btnDecode_1_to_2.setEnabled(True)
                mw.btnEncode_2_to_1.setEnabled(True)
                mw.btnDecode_2_to_1.setEnabled(True)
            else:
                mw.btnEncode_1_to_2.setEnabled(True)
                mw.btnDecode_1_to_2.setEnabled(False)
                mw.btnEncode_2_to_1.setEnabled(True)
                mw.btnDecode_2_to_1.setEnabled(False)

#-------------------------------------------------------------------------------
# doCopy()
#-------------------------------------------------------------------------------
def doCopy(mw, src):
    if src == ONE:
        QApplication.clipboard().setText(mw.txtBase64_1.toPlainText())
    else:
        QApplication.clipboard().setText(mw.txtBase64_2.toPlainText())
    mw.showMessage("Pasted to clipboard")

#-------------------------------------------------------------------------------
# doPaste()
#-------------------------------------------------------------------------------
def doPaste(mw, src):    
    clipboard = QApplication.clipboard().text()
    if src == ONE:
        mw.txtBase64_1.appendPlainText(clipboard)
    else:
        mw.txtBase64_2.appendPlainText(clipboard)
    mw.showMessage("Pasted from clipboard")

#-------------------------------------------------------------------------------
# doClear()
#-------------------------------------------------------------------------------
def doClear(mw, src):
    if src == ONE:
        mw.txtBase64_1.setPlainText("")
    else:
        mw.txtBase64_2.setPlainText("")
    mw.showMessage("Text field cleared")
    
"""
http://www.robertecker.com/hp/research/leet-converter.php?lang=en
abcdefghijklmnopqrstuvwxyz
4bcd3f6h1jklmn0pqr57uvwxyz
    leet = str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', 
       '4bcd3f6h1jklmn0pqr57uvwxyz4bcd3f6h1jklmn0pqr57uvwxyz')

"""    