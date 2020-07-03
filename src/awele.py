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

import settings

# tab_profondeur = [[0 for x in range(6)] for y in range(10)] # [10][6]
tab_profondeur = [
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


#-------------------------------------------------------------------------------
# Class Case_Retour
#-------------------------------------------------------------------------------
class Case_Retour():
    case_meilleure = 0
    gain_score = 0

#-------------------------------------------------------------------------------
# Class Awele
#-------------------------------------------------------------------------------
class Awele():
#-------------------------------------------------------------------------------
# initFormAwele()
#-------------------------------------------------------------------------------
    def __init__(self):
        self.difficulte = mw.cbxAweleLevel.currentIndex()
        self.case_moi = [4,4,4,4,4,4]
        self.case_cpu = [4,4,4,4,4,4]
        self.score_moi = 0
        self.score_cpu = 0
        self.tour_jeu = 1
        self.fini = 0

#-------------------------------------------------------------------------------
# lanceJeu()
#-------------------------------------------------------------------------------
def lanceJeu(a):
    nbre_graine = 0
    profondeur = 0
    choix_cpu = Case_Retour()

    global tab_profondeur

    afficher(a)

    if a.fini == 0:
        nbre_graine = a.case_moi[0] + a.case_moi[1] + a.case_moi[2] + a.case_moi[3] + a.case_moi[4] + a.case_moi[5]
        nbre_graine = nbre_graine  + a.case_cpu[0] + a.case_cpu[1] + a.case_cpu[2] + a.case_cpu[3] + a.case_cpu[4] + a.case_cpu[5]
        profondeur = tab_profondeur[a.difficulte][0]
        if (nbre_graine < 24):
            profondeur=tab_profondeur[a.difficulte][1]
        if (nbre_graine < 18):
            profondeur=tab_profondeur[a.difficulte][2]
        if (nbre_graine < 12):
            profondeur=tab_profondeur[a.difficulte][3]
        if (nbre_graine < 6):
            profondeur=tab_profondeur[a.difficulte][4]
        if (nbre_graine < 4):
            profondeur=tab_profondeur[a.difficulte][5]

        choix_cpu = meilleure_case_cpu(a, profondeur)

        if choix_cpu.case_meilleure != -1:
            cpu_joue(a,choix_cpu.case_meilleure)
            afficher(a)
        else:
            a.fini = 1

def joueurJoue(a, case_choisie):
    case_gene = case_choisie
    nb_graine = a.case_moi[case_choisie]
    case_bis = 11
    enleve = 0

    a.case_moi[case_choisie] = 0
    
"""
// Le joueur joue un coup entre 0 et 5
// D�place les pions, change le score
// En param�tre, le plateau de jeu et la case � jouer
//*****************************************
void joueur_joue(awale* a,int case_choisie)
//*****************************************
{
	int case_gene=case_choisie;
	int nb_graine=a->case_moi[case_choisie]; // Nombre de graines dans la case � jouer
	int case_bis=11; // Servira pour la r�gle : enl�ve tt enl�ve rien
	int enleve=0;


	a->case_moi[case_choisie]=0; // Case � jouer remise � 0

	//D�pose les graines
	while(nb_graine!=0)
	{
		case_gene++;
		if (case_gene==12) case_gene=0;
  		if (case_gene==case_choisie) case_gene++; // On est dans la case � jouer, on passe � la suivante
		if (case_gene>5)
			a->case_cpu[case_gene-6]++;
		else
			a->case_moi[case_gene]++;
		nb_graine--;
	}

	// V�rifie la r�gle : enl�ve tt enl�ve rien
	if ((case_gene>5)&&((a->case_cpu[case_gene-6]==2)||(a->case_cpu[case_gene-6]==3)))
	{
		while ((case_bis!=case_gene)&&(enleve==0))
		{
			if (a->case_cpu[case_bis-6]!=0) enleve=1;
			case_bis--;
		}
		case_bis--;
		while ((case_bis>5)&&(enleve==0))
		{
			if ((a->case_cpu[case_bis-6]!=2)&&(a->case_cpu[case_bis-6]!=3)) enleve=1;
			case_bis--;
		}
		// si enleve==1, alors on peut enlever les graines gagn�es
		if (enleve==1)
			while ((case_gene>5)&&((a->case_cpu[case_gene-6]==2)||(a->case_cpu[case_gene-6]==3)))
			{
				a->score_moi+=a->case_cpu[case_gene-6];
				a->case_cpu[case_gene-6]=0;
				case_gene--;
			}
	}
	a->tour_jeu=2; // C'est au tour de l'autre
}
"""

#-------------------------------------------------------------------------------
# afficher()
#-------------------------------------------------------------------------------
def afficher(a):
    mw.lblAweleHomeHuman.setText("%02d" % a.score_moi)
    mw.lblAweleCase01.setText("%02d" % a.case_moi[0])
    mw.lblAweleCase02.setText("%02d" % a.case_moi[1])
    mw.lblAweleCase03.setText("%02d" % a.case_moi[2])
    mw.lblAweleCase04.setText("%02d" % a.case_moi[3])
    mw.lblAweleCase05.setText("%02d" % a.case_moi[4])
    mw.lblAweleCase06.setText("%02d" % a.case_moi[5])

    mw.lblAweleHomeComputer.setText("%02d" % a.score_cpu)
    mw.lblAweleCase07.setText("%02d" % a.case_cpu[0])
    mw.lblAweleCase08.setText("%02d" % a.case_cpu[1])
    mw.lblAweleCase09.setText("%02d" % a.case_cpu[2])
    mw.lblAweleCase10.setText("%02d" % a.case_cpu[3])
    mw.lblAweleCase11.setText("%02d" % a.case_cpu[4])
    mw.lblAweleCase12.setText("%02d" % a.case_cpu[5])

#-------------------------------------------------------------------------------
# initFormAwele()
#-------------------------------------------------------------------------------
def initFormAwele(mw):
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

    mw.cbxAweleLevel.setCurrentIndex(settings.db['AWELE_LEVEL_DEFAULT'])

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

    mw.lblAweleCase01.mousePressEvent = lambda _, mw=mw, c=1 : clickCase(mw, c)
    mw.lblAweleCase02.mousePressEvent = lambda _, mw=mw, c=2 : clickCase(mw, c)
    mw.lblAweleCase03.mousePressEvent = lambda _, mw=mw, c=3 : clickCase(mw, c)
    mw.lblAweleCase04.mousePressEvent = lambda _, mw=mw, c=4 : clickCase(mw, c)
    mw.lblAweleCase05.mousePressEvent = lambda _, mw=mw, c=5 : clickCase(mw, c)
    mw.lblAweleCase06.mousePressEvent = lambda _, mw=mw, c=6 : clickCase(mw, c)


def clickCase(mw, c):
    mw.showMessage("Clicked the cell #%d" % c)
    # joueurJoue(a, c-1)

    """
    mw.btnDisassemble.clicked.connect(lambda : disassembleFile(mw))
    mw.btnBrowseSourceFile.clicked.connect(lambda: browseSourceFile(mw))
    mw.btnCopyDis.clicked.connect(lambda: copyDisToClipboard(mw))
    """