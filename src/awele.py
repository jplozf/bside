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

#===============================================================================
# Thanks to Patalou
# Code   : http://codes-sources.commentcamarche.net/source/20793-jeu-de-strategie-africain-awale
# Link   : http://pascal.libaud.free.fr
#===============================================================================

#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import copy
from random import choice

import settings

#-------------------------------------------------------------------------------
# Depth array depending of level
#-------------------------------------------------------------------------------
aDepth = [
    [0,0,1,1,3,3],
    [1,1,1,3,5,9],
    [2,2,2,4,6,10],
    [3,3,3,5,7,11],
    [4,4,4,6,9,13],
    [5,5,5,7,11,15],
    [6,6,7,9,13,19],
    [7,7,9,11,15,23],
    [8,9,11,13,17,25],
    [9,11,13,15,19,27]
    ]
    
level = 0
mw = 0

#-------------------------------------------------------------------------------
# enum()
#-------------------------------------------------------------------------------
def enum(**enums):
    return type('Enum', (), enums)

Players = enum(NONE=0, COMPUTER=1, HUMAN=2)
currentPlayer = Players.NONE

#-------------------------------------------------------------------------------
# Class Move
#-------------------------------------------------------------------------------
class Move():
    bestCell = 0
    scoreWon = 0
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self, bestCell, scoreWon):
        self.bestCell = bestCell
        self.scoreWon = scoreWon

#-------------------------------------------------------------------------------
# Class Awele
#-------------------------------------------------------------------------------
class Awele():
#-------------------------------------------------------------------------------
# __init__()
#-------------------------------------------------------------------------------
    def __init__(self):
        self.hCell = [4,4,4,4,4,4]
        self.cCell = [4,4,4,4,4,4]
        self.hScore = 0
        self.cScore = 0
        self.whoToPlay = 1
        self.theEnd = 0

#-------------------------------------------------------------------------------
# humanPlay()
#-------------------------------------------------------------------------------
def humanPlay(a, choosenCell):
    """
    Le joueur joue un coup entre 0 et 5
    Déplace les pions, change le score
    En paramètre, le plateau de jeu et la case à jouer    
    """
    computedCell = choosenCell
    seeds = a.hCell[choosenCell]
    alternateCell = 11
    minus = 0

    a.hCell[choosenCell] = 0
    while (seeds != 0):
        computedCell = computedCell + 1
        if computedCell == 12:
            computedCell = 0
        if computedCell == choosenCell:
            computedCell = computedCell + 1
        if computedCell > 5:
                a.cCell[computedCell - 6] = a.cCell[computedCell - 6] + 1
        else:
                a.hCell[computedCell] = a.hCell[computedCell] + 1
        seeds = seeds - 1

        # Vérifie la règle : enlève tout / enlève rien
        if ((computedCell > 5) and ((a.cCell[computedCell - 6] == 2) or (a.cCell[computedCell - 6] == 3))):
            while ((alternateCell != computedCell)  and (minus == 0)):
                if (a.cCell[alternateCell - 6] != 0):
                    minus = 1
                alternateCell = alternateCell - 1
            alternateCell = alternateCell - 1
            
            while ((alternateCell > 5) and (minus == 0)):
                if ((a.cCell[alternateCell - 6] != 2) and (a.cCell[alternateCell - 6] != 3)):
                    minus = 1
                alternateCell = alternateCell - 1
            
            # si minus==1, alors on peut minusr les graines gagnées
            if (minus == 1):
                while ((computedCell > 5)  and ((a.cCell[computedCell - 6] == 2) or (a.cCell[computedCell - 6] == 3))):
                    a.hScore = a.hScore + a.cCell[computedCell - 6]
                    a.cCell[computedCell - 6] = 0
                    computedCell = computedCell - 1
        
    a.whoToPlay = 2 # C'est au tour de l'autre
    
#-------------------------------------------------------------------------------
# computerPlay()
#-------------------------------------------------------------------------------
def computerPlay(a, choosenCell):
    """
    Le cpu joue un coup entre 0 et 5
    Déplace les pions, change le score
    En paramètre le plateau de jeu et la case à jouer
    """
    computedCell = choosenCell
    seeds = a.cCell[choosenCell]
    alternateCell = 11  # Servira pour la règle : enlève tout / enlève rien
    minus = 0

    a.cCell[choosenCell] = 0

    # Dépose les graines
    while (seeds != 0):
        computedCell = computedCell + 1
        if (computedCell == 12):
            computedCell = 0
        if (computedCell == choosenCell):
            computedCell = computedCell + 1
        if (computedCell > 5):
            a.hCell[computedCell - 6] = a.hCell[computedCell - 6] + 1
        else:
            a.cCell[computedCell] = a.cCell[computedCell] + 1
        seeds = seeds - 1

    # Enlève celles gagnées et augmente le score
    # Vérifie la règle : enlève tout / enlève rien
    if ((computedCell > 5) and ((a.hCell[computedCell - 6] == 2) or (a.hCell[computedCell - 6] == 3))):
        while ((alternateCell != computedCell) and (minus == 0)):
            if (a.hCell[alternateCell-6] != 0):
                minus = 1
            alternateCell = alternateCell - 1
        alternateCell = alternateCell - 1
        
        while ((alternateCell > 5) and (minus == 0)):
            if ((a.hCell[alternateCell-6] != 2) and (a.hCell[alternateCell-6] != 3)):
                minus = 1
            alternateCell = alternateCell - 1

        # si minus == 1, alors on peut minusr les graines gagnées
        if (minus == 1):
            while ((computedCell > 5) and ((a.hCell[computedCell - 6] == 2) or (a.hCell[computedCell - 6] == 3))):
                a.cScore = a.cScore + a.hCell[computedCell - 6]
                a.hCell[computedCell - 6] = 0
                computedCell = computedCell - 1

    a.whoToPlay = 1 # Au tour de l'autre

#-------------------------------------------------------------------------------
# bestMoveComputer()
#-------------------------------------------------------------------------------
def bestMoveComputer(a, depthLevel):
    """
    Cherche le meilleur coup du CPU de façon recursive
    Renvoie la case donnant le meilleur coup et le gain de score
    """
    move = Move(0, 0) # On retourne la meilleure case avec le gain
    awa = [Awele() for i in range(6)]
    choosenCell = -1
    bestWon = -36
    currentWon = 0
    give = [0, 0, 0, 0, 0, 0] # Marquera les cases qui ne givent pas de graine
    
    # Vérifie si l'adversaire est sans graines et marque les cases qui ne givent pas
    if (a.hCell[0] + a.hCell[1] + a.hCell[2] + a.hCell[3] + a.hCell[4] + a.hCell[5] == 0):
        for i in range(6):
            if (i + a.cCell[i] < 6):
                give[i] = 1
        
        if (give[0] + give[1] + give[2] + give[3] + give[4] + give[5] == 6): # Jeu fini car adversaire sans graine et on peut pas giver
            move.scoreWon = a.hScore - a.cScore
            endGame(a)
            move.bestCell = -1
            move.scoreWon = move.scoreWon + a.cScore - a.hScore;
            return move

    # Le jeu n'est pas fini
    for i in range(6):
        if ((a.cCell[i] !=0 ) and (give[i] == 0)): # give[i]=1 si adversaire sans graine et cette case ne give pas
            awa[i] = copy.deepcopy(a)
            computerPlay(awa[i], i)
            if (depthLevel == 0):
                    currentWon = a.hScore - a.cScore + awa[i].cScore - awa[i].hScore
            else:
                move = bestMovePlayer(awa[i], depthLevel - 1) # Lance la fonction récursive complémentaire
                currentWon = a.hScore - a.cScore + awa[i].cScore - awa[i].hScore - move.scoreWon
                if settings.db['AWELE_VERBOSE_MODE'] == True:
                    logMessage("Computer : Cell %d => Won %d" % (i + 7, currentWon))
            if (currentWon > bestWon):
                bestWon = currentWon
                choosenCell = i
                if settings.db['AWELE_VERBOSE_MODE'] == True:
                    logMessage("Computer : Best move %d" % (i + 7))

    move.bestCell = choosenCell
    move.scoreWon = bestWon

    return move

#-------------------------------------------------------------------------------
# bestMovePlayer()
#-------------------------------------------------------------------------------
def bestMovePlayer(a, depthLevel):
    """
    Cherche le meilleur coup du joueur de facon récursive
    Renvoie la case donnant le meilleur coup et le gain de score
    Fonction complémentaire à bestMoveComputer(...)
    """
    move = Move(0, 0)
    awa = [Awele() for i in range(6)]
    choosenCell = -1
    bestWon = -36
    currentWon = 0
    give = [0, 0, 0, 0, 0, 0]   # Marque les cases qui ne givent pas de graine
    
    # Vérifie si l'adversaire est sans graines et marque les cases qui ne givent pas
    if (a.cCell[0] + a.cCell[1] + a.cCell[2] + a.cCell[3] + a.cCell[4] + a.cCell[5] == 0):
        for i in range(6):
            if (i + a.hCell[i] < 6):
                give[i] = 1
        if (give[0] + give[1] + give[2] + give[3] + give[4] + give[5] == 6): # Jeu fini
            move.scoreWon = a.cScore - a.hScore
            endGame(a)
            move.bestCell = -1
            move.scoreWon = move.scoreWon + a.hScore - a.cScore
            return move

    for i in range(6):
        if ((a.hCell[i] != 0) and (give[i] == 0)):
            awa[i] = copy.deepcopy(a)
            humanPlay(awa[i], i)
            if (depthLevel == 0):
                currentWon = a.cScore - a.hScore + awa[i].hScore - awa[i].cScore
            else:
                move = bestMoveComputer(awa[i], depthLevel - 1)
                currentWon = a.cScore - a.hScore + awa[i].hScore - awa[i].cScore - move.scoreWon
                if settings.db['AWELE_VERBOSE_MODE'] == True:
                    logMessage("Player   : Cell %d => Won %d" % (i + 1, currentWon))
            if (currentWon > bestWon):
                bestWon = currentWon
                choosenCell = i
                if settings.db['AWELE_VERBOSE_MODE'] == True:
                    logMessage("Player   : Best move %d" % (i + 1))

    move.bestCell = choosenCell
    move.scoreWon = bestWon

    return move

#-------------------------------------------------------------------------------
# endGame()
#-------------------------------------------------------------------------------
def endGame(a):
    """
    Affecte les dernieres graines quand le jeu est fini
    """
    a.hScore = a.hScore + a.hCell[0] + a.hCell[1] + a.hCell[2] + a.hCell[3] + a.hCell[4] + a.hCell[5]
    a.cScore = a.cScore + a.cCell[0] + a.cCell[1] + a.cCell[2] + a.cCell[3] + a.cCell[4] + a.cCell[5]
    for i in range(6):
        a.hCell[i] = 0
        a.cCell[i] = 0
        
#-------------------------------------------------------------------------------
# getDepth()
#-------------------------------------------------------------------------------
def getDepth(a):
    # Calcule le nbre d'itérations en fonction du nbre total de graines
    global level
    if settings.db['AWELE_VERBOSE_MODE'] == True:
        logMessage("Level set to %d" % level)
    seeds = a.hCell[0] + a.hCell[1] + a.hCell[2] + a.hCell[3] + a.hCell[4] + a.hCell[5]
    seeds = seeds + a.cCell[0] + a.cCell[1] + a.cCell[2] + a.cCell[3] + a.cCell[4] + a.cCell[5]
    depth = aDepth[level][0]
    if (seeds < 24):
        depth = aDepth[level][1]
    if (seeds < 18):
        depth = aDepth[level][2]
    if (seeds < 12):
        depth = aDepth[level][3]
    if (seeds < 6):
        depth = aDepth[level][4]
    if (seeds < 4):  
        depth = aDepth[level][5]
        
    if settings.db['AWELE_VERBOSE_MODE'] == True:
        logMessage("Recursivity depth = %d" % depth)
    
    return depth


#-------------------------------------------------------------------------------
# displayBoard()
#-------------------------------------------------------------------------------
def displayBoard(a):
    global mw
    mw.lblAweleHomeHuman.setText(" %02d " % a.hScore)
    mw.lblAweleCase01.setText(" %02d " % a.hCell[0])
    mw.lblAweleCase02.setText(" %02d " % a.hCell[1])
    mw.lblAweleCase03.setText(" %02d " % a.hCell[2])
    mw.lblAweleCase04.setText(" %02d " % a.hCell[3])
    mw.lblAweleCase05.setText(" %02d " % a.hCell[4])
    mw.lblAweleCase06.setText(" %02d " % a.hCell[5])

    mw.lblAweleHomeComputer.setText(" %02d " % a.cScore)
    mw.lblAweleCase07.setText(" %02d " % a.cCell[0])
    mw.lblAweleCase08.setText(" %02d " % a.cCell[1])
    mw.lblAweleCase09.setText(" %02d " % a.cCell[2])
    mw.lblAweleCase10.setText(" %02d " % a.cCell[3])
    mw.lblAweleCase11.setText(" %02d " % a.cCell[4])
    mw.lblAweleCase12.setText(" %02d " % a.cCell[5])
    
    mw.lblAweleHomeHuman.repaint()
    mw.lblAweleHomeComputer.repaint()
    mw.lblAweleCase01.repaint()
    mw.lblAweleCase02.repaint()
    mw.lblAweleCase03.repaint()
    mw.lblAweleCase04.repaint()
    mw.lblAweleCase05.repaint()
    mw.lblAweleCase06.repaint()
    mw.lblAweleCase07.repaint()
    mw.lblAweleCase08.repaint()
    mw.lblAweleCase09.repaint()
    mw.lblAweleCase10.repaint()
    mw.lblAweleCase11.repaint()
    mw.lblAweleCase12.repaint()
    
    if mw.a.cScore > 24 or mw.a.hScore > 24:
        gameOver(mw)

#-------------------------------------------------------------------------------
# initFormAwele()
#-------------------------------------------------------------------------------
def initFormAwele(zmw):
    global mw
    mw = zmw
    mw.cbxAweleLevel.clear()
    level = settings.db['AWELE_LEVEL_DEFAULT']
    if settings.db['AWELE_LEVEL_SET_OPTIMIZED'] == True:
        # These levels are optimized :
        # They should fit and be convenient for most human players,
        # and the response time is good enough in highest level.
        mw.cbxAweleLevel.addItems([
            "1 - Bad",
            "2 - Low",
            "3 - Medium",
            "4 - Good",
            "5 - Very good",
            "6 - Excellent"
            ])
        if level < 1:
            mw.cbxAweleLevel.setCurrentIndex(0)
        elif level > 6:
            mw.cbxAweleLevel.setCurrentIndex(5)
        else:
            mw.cbxAweleLevel.setCurrentIndex(level - 1)
    else:
        # These levels are not optimized :
        # => Level 0 seems to be useless
        # => Levels higher than 6 are time consuming 
        mw.cbxAweleLevel.addItems([
            "0 - Idiot",
            "1 - Bad",
            "2 - Low",
            "3 - Medium",
            "4 - Good",
            "5 - Very good",
            "6 - Excellent",
            "7 - Expert",
            "8 - Genius",
            "9 - Perfect"
            ])
        if level < 0:
            mw.cbxAweleLevel.setCurrentIndex(0)
        elif level > 9:
            mw.cbxAweleLevel.setCurrentIndex(10)
        else:
            mw.cbxAweleLevel.setCurrentIndex(level)

    css1 = "QWidget {border: 2px solid gray; border-radius: 6px; background-color: %s; color: %s;}" % (settings.db['AWELE_HUMAN_COLOR_BACKGROUND'], settings.db['AWELE_HUMAN_COLOR_FOREGROUND'])
    css2 = "QWidget {border: 2px solid gray; border-radius: 6px; background-color: %s; color: %s;}" % (settings.db['AWELE_COMPUTER_COLOR_BACKGROUND'],settings.db['AWELE_COMPUTER_COLOR_FOREGROUND'])

    mw.lblAweleHomeHuman.setStyleSheet(css1)
    mw.lblAweleCase01.setStyleSheet(css1)
    mw.lblAweleCase02.setStyleSheet(css1)
    mw.lblAweleCase03.setStyleSheet(css1)
    mw.lblAweleCase04.setStyleSheet(css1)
    mw.lblAweleCase05.setStyleSheet(css1)
    mw.lblAweleCase06.setStyleSheet(css1)

    mw.lblAweleHomeComputer.setStyleSheet(css2)
    mw.lblAweleCase07.setStyleSheet(css2)
    mw.lblAweleCase08.setStyleSheet(css2)
    mw.lblAweleCase09.setStyleSheet(css2)
    mw.lblAweleCase10.setStyleSheet(css2)
    mw.lblAweleCase11.setStyleSheet(css2)
    mw.lblAweleCase12.setStyleSheet(css2)

    mw.lblAweleCase01.mousePressEvent = lambda _, mw=mw, c=1 : clickCell(mw, c)
    mw.lblAweleCase02.mousePressEvent = lambda _, mw=mw, c=2 : clickCell(mw, c)
    mw.lblAweleCase03.mousePressEvent = lambda _, mw=mw, c=3 : clickCell(mw, c)
    mw.lblAweleCase04.mousePressEvent = lambda _, mw=mw, c=4 : clickCell(mw, c)
    mw.lblAweleCase05.mousePressEvent = lambda _, mw=mw, c=5 : clickCell(mw, c)
    mw.lblAweleCase06.mousePressEvent = lambda _, mw=mw, c=6 : clickCell(mw, c)
    
    mw.a = Awele()
    displayBoard(mw.a)
    
    mw.btnAweleNew.clicked.connect(lambda _, mw=mw : startGame(mw))

#-------------------------------------------------------------------------------
# startGame()
#-------------------------------------------------------------------------------
def startGame(mw):
    initFormAwele(mw)
    global currentPlayer
    currentPlayer = choice([Players.COMPUTER, Players.HUMAN])
    mw.txtAweleConsole.setText("")
    if currentPlayer == Players.COMPUTER:
        logMessage("Computer is playing first move...")
        global level
        level = int(mw.cbxAweleLevel.currentText()[0])
        choix_cpu = bestMoveComputer(mw.a, getDepth(mw.a))
        if (choix_cpu.bestCell != -1):
            logMessage("Computer plays the cell #%d" % (choix_cpu.bestCell + 7))
            computerPlay(mw.a, choix_cpu.bestCell)
            displayBoard(mw.a)
            currentPlayer = Players.HUMAN
        else:
            currentPlayer = Players.NONE
            logMessage("Game is over")
    else:
        logMessage("Please, go ahead...")

#-------------------------------------------------------------------------------
# clickCell()
#-------------------------------------------------------------------------------
def clickCell(mw, c):
    global currentPlayer    
    if currentPlayer == Players.HUMAN:
        if (mw.a.cCell[0] + mw.a.cCell[1] + mw.a.cCell[2] + mw.a.cCell[3] + mw.a.cCell[4] + mw.a.cCell[5] == 0):
            if (c + mw.a.hCell[c - 1] < 7):
                logMessage("Please, feed me !")
                return
        if mw.a.hCell[c - 1] != 0:
            currentPlayer = Players.COMPUTER
            global level
            level = int(mw.cbxAweleLevel.currentText()[0])
            logMessage("Player plays the cell #%d" % c)
            humanPlay(mw.a, c - 1)
            displayBoard(mw.a)
            choix_cpu = bestMoveComputer(mw.a, getDepth(mw.a))
            if (choix_cpu.bestCell != -1):
                currentPlayer = Players.HUMAN
                logMessage("Computer plays the cell #%d" % (choix_cpu.bestCell + 7))
                computerPlay(mw.a, choix_cpu.bestCell)
                displayBoard(mw.a)
            else:
                gameOver(mw)
        else:
            logMessage("Can't play this cell #%d which is empty !" % c)
    elif currentPlayer == Players.COMPUTER:
        logMessage("Please, let me play !")
    else:
        logMessage("No current game, please start one...")
                
#-------------------------------------------------------------------------------
# gameOver()
#-------------------------------------------------------------------------------
def gameOver(mw):
    global currentPlayer
    currentPlayer = Players.NONE
    logMessage("Game is over")
    if mw.a.cScore == mw.a.hScore:
        logMessage("Draw by %d to %d." % (mw.a.cScore, mw.a.hScore))
    elif mw.a.cScore > mw.a.hScore:
        logMessage("Computer wins by %d to %d." % (mw.a.cScore, mw.a.hScore))
    else:
        logMessage("You win by %d to %d." % (mw.a.hScore, mw.a.cScore))

#-------------------------------------------------------------------------------
# logMessage()
#-------------------------------------------------------------------------------
def logMessage(msg):
    global mw
    mw.txtAweleConsole.append(msg)
    mw.txtAweleConsole.repaint()
    mw.lblAweleMessage.setText(msg)
    mw.lblAweleMessage.repaint()
