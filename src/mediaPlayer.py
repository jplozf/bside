#!/usr/bin/env python3
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
from PyQt5.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QMenu,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction, QWidgetAction, QInputDialog
from PyQt5.QtGui import QIcon

import sys
import os

#-------------------------------------------------------------------------------
# Class MovieWidget
#-------------------------------------------------------------------------------
class MovieWidget(QWidget):
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, parent=None):
        super(MovieWidget, self).__init__(parent)
        mini = True
        self.parent = parent
        self.isVideoAvailable = False
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.mediaPlayer.videoAvailableChanged.connect(self.videoAvailableChanged)

        videoWidget = QVideoWidget(self)
        videoWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # Context Menu
        self.customContextMenuRequested.connect(self.openContextMenu)                
        self.contextMenu = QMenu()
        
        self.openAction = self.contextMenu.addAction("Open file")
        icon = QIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton));
        self.openAction.setIcon(icon)
        
        self.urlAction = self.contextMenu.addAction("Open stream")
        icon = QIcon(self.style().standardIcon(QStyle.SP_DirLinkIcon));
        self.urlAction.setIcon(icon)

        self.playAction = self.contextMenu.addAction("Play/Pause")
        icon = QIcon(self.style().standardIcon(QStyle.SP_MediaPlay));
        self.playAction.setEnabled(False)
        self.playAction.setIcon(icon)
        
        self.closeAction = self.contextMenu.addAction("Close")
        icon = QIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton));
        self.closeAction.setEnabled(False)
        self.closeAction.setIcon(icon)
        
        self.posSlider = QSlider(Qt.Horizontal)
        self.posSlider.setRange(0, 0)
        self.posSlider.sliderMoved.connect(self.setPosition)
        self.wac=QWidgetAction(self.contextMenu)
        self.wac.setDefaultWidget(self.posSlider)        
        self.posAction=self.contextMenu.addAction(self.wac);        
        
        self.lblFile = QLabel()
        self.wal=QWidgetAction(self.contextMenu)
        self.wal.setDefaultWidget(self.lblFile)        
        self.posAction=self.contextMenu.addAction(self.wal);        

        # Control box
        self.openButton = QPushButton()
        self.openButton.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
        self.openButton.clicked.connect(self.openFile)

        self.urlButton = QPushButton()
        self.urlButton.setIcon(self.style().standardIcon(QStyle.SP_DirLinkIcon))
        self.urlButton.clicked.connect(self.openURL)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
           
        # Create layouts to place inside widget
        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(0, 0, 0, 0)
        controlLayout.addWidget(self.openButton)
        controlLayout.addWidget(self.urlButton)
        controlLayout.addWidget(self.playButton)
        controlLayout.addWidget(self.positionSlider)

        vLayout = QVBoxLayout()
        vLayout.setContentsMargins(0, 0, 0, 0)
        vLayout.addWidget(videoWidget)
        if mini != True:
            vLayout.addLayout(controlLayout)
            vLayout.addWidget(self.errorLabel)
        
        self.setLayout(vLayout)

        # Set widget to contain window contents
        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        
        self.resize(180,100)
        

#-------------------------------------------------------------------------------
# videoAvailableChanged()
#-------------------------------------------------------------------------------
    def videoAvailableChanged(self, available):
        self.isVideoAvailable = available
        print("Video available %s" % str(available))
        
#-------------------------------------------------------------------------------
# openContextMenu()
#-------------------------------------------------------------------------------
    def openContextMenu(self, position):                
        action = self.contextMenu.exec_(self.mapToGlobal(position))
        if action == self.playAction:
            self.play()
        elif action == self.openAction:
            self.openFile()
        elif action == self.urlAction:
            self.openURL()
        elif action == self.closeAction:
            self.closeFile()

#-------------------------------------------------------------------------------
# openFile()
#-------------------------------------------------------------------------------
    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Media", QDir.homePath(), "All Files (*);;Movies (*.avi *.mp4);;Music (*.mp3 *.ogg)", options = QFileDialog.DontUseNativeDialog)
        if fileName != '':            
            self.mediaSource = os.path.splitext(os.path.basename(fileName))[0]
            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(fileName)))
            self.errorLabel.setText(os.path.splitext(os.path.basename(fileName))[0])
            self.lblFile.setText(" " + self.mediaSource)
            self.playButton.setEnabled(True)
            self.playAction.setEnabled(True)
            self.closeAction.setEnabled(True)
            self.play()

#-------------------------------------------------------------------------------
# openURL()
#-------------------------------------------------------------------------------
    def openURL(self):
        url, ok = QInputDialog.getText(self, 'Open Stream', 'URL of stream :')
        if ok:
            if url != '':
                self.mediaSource = url
                self.mediaPlayer.setMedia(QMediaContent(QUrl(url)))
                self.errorLabel.setText(url)
                self.lblFile.setText(" " + url)
                self.playButton.setEnabled(True)
                self.playAction.setEnabled(True)
                self.closeAction.setEnabled(True)
                self.play()
            
#-------------------------------------------------------------------------------
# closeFile()
#-------------------------------------------------------------------------------
    def closeFile(self):
        self.pauseForce()
        self.mediaPlayer.setMedia(QMediaContent())
        self.playButton.setEnabled(False)
        self.playAction.setEnabled(False)
        self.closeAction.setEnabled(False)
        self.lblFile.setText("")

#-------------------------------------------------------------------------------
# play()
#-------------------------------------------------------------------------------
    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()
            self.parent.bigDisplay(self.mediaSource)
    
#-------------------------------------------------------------------------------
# playForce()
#-------------------------------------------------------------------------------
    def playForce(self):
        self.mediaPlayer.play()
        
#-------------------------------------------------------------------------------
# pauseForce()
#-------------------------------------------------------------------------------
    def pauseForce(self):
        self.mediaPlayer.pause()
        
#-------------------------------------------------------------------------------
# mediaStateChanged()
#-------------------------------------------------------------------------------
    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
            self.playAction.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.playAction.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            
#-------------------------------------------------------------------------------
# positionChanged()
#-------------------------------------------------------------------------------
    def positionChanged(self, position):
        self.posSlider.setValue(position)
        self.positionSlider.setValue(position)

#-------------------------------------------------------------------------------
# durationChanged()
#-------------------------------------------------------------------------------
    def durationChanged(self, duration):
        self.posSlider.setRange(0, duration)
        self.positionSlider.setRange(0, duration)

#-------------------------------------------------------------------------------
# setPosition()
#-------------------------------------------------------------------------------
    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

#-------------------------------------------------------------------------------
# handleError()
#-------------------------------------------------------------------------------
    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())

