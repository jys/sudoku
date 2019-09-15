#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2019 LATEJCON"
__license__ = "GNU AGPL"
__version__ = "2.0.1"

import sys
from os import path
from re import match
import codecs
import glob
from SudokuPdfDoc import SudokuPdfDoc
from SudokuValeurs import SudokuValeurs
from SudokuVejrification import SudokuVejrification
from SudokuMejthodes import SudokuMejthodes

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (u"""© l'ATEJCON.  
Le sudoku anthropomorphique est un programme qui essaie de rejsoudre une grille
de sudoku comme le ferait un humain et qui explique dans un document PDF, 
à chaque ejtape, les prejmisses, son raisonnement et ses dejductions.
Le document rejsultat est <rejpertoire>/sudokuSolution-<lig1>.pdf

usage   : %s <lig1,lig2,lig3,lig4,lig5,lig6,lig7,lig8,lig9> 
usage   : %s <fichier problehme> 
example : %s 000008109,230670008,090000000,408001900,300000005,009300702,000000090,500093086,906400000
example : %s Boa/sudoku/donnees/sudoku000008109.txt
example : %s "Boa/sudoku/donnees/sudoku*.txt"
"""%(script, script, script, script, script))

def main():
    try:
        if len(sys.argv) < 2 : raise Exception()
        lignes = sys.argv[1]
        sudoku(lignes)
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            print (exc)
            print ("******************************")
            raise
        sys.exit()

def sudoku(lignes):
    # lignes ou fichier ?
    formatLignes = u'[0-9]{9},[0-9]{9},[0-9]{9},[0-9]{9},[0-9]{9},[0-9]{9},[0-9]{9},[0-9]{9},[0-9]{9}'
    if match(formatLignes, lignes) != None: 
        # la grille a ejtej fournie en ligne
        rejpertoire = path.abspath(path.curdir)
        resoudSudoku(lignes, rejpertoire)
    else:
        # c'est une spejcification de fichiers
        nomsFichiers = glob.glob(lignes)
        if len(nomsFichiers) == 0: raise Exception('ERREUR : %s fichier inconnu'%(lignes))
        for nomFichier in nomsFichiers:
            #print ('**** %s'%(nomFichier))       
            fichierEntreje = codecs.open(nomFichier, 'r', 'utf-8')
            lignes = fichierEntreje.readline()
            fichierEntreje.close()
            lignes = lignes.strip()
            if match(formatLignes, lignes) == None: raise Exception('ERREUR : %s mauvais format dans fichier'%(nomFichier))
            rejpertoire = path.dirname(path.abspath(nomFichier))
            resoudSudoku(lignes, rejpertoire)    
    
# numejrotation des 81 cellules
# 11 12 13   14 15 16   17 18 19
# 21 22 23   24 25 26   27 28 29
# 31 32 33   34 35 36   37 38 39
#
# 41 42 43   44 45 46   47 48 49
# 51 52 53   54 55 56   57 58 59
# 61 62 63   64 65 66   67 68 69
#
# 71 72 73   74 75 76   77 78 79
# 81 82 83   84 85 86   87 88 89
# 91 92 93   94 95 96   97 98 99

#################################################################
def resoudSudoku(lignes, rejpertoire):
    # 1) inits
    # init valeurs
    sudokuValeurs = SudokuValeurs(lignes)
    nbCellulesEnoncej = len(sudokuValeurs.lesCellulesAffectejes())
    # init la vejrification, sort en exception si la grille est mal formeje (contraintes non respectejes)
    sudokuVejrification = SudokuVejrification(lignes)
    # init le PDF de sortie
    identifiant = lignes.split(',')[0]
    nomFichierSortie = '%s/sudokuSolution-%s.pdf'%(rejpertoire, identifiant)
    print('====> ', nomFichierSortie)
    sudokuPdfDoc = SudokuPdfDoc(nomFichierSortie, identifiant)
    # init mejthodes
    sudokuMejthodes = SudokuMejthodes(sudokuValeurs, sudokuPdfDoc)
    # 1) affiche l'ejnoncej
    sudokuPdfDoc.ejcritTour('ejnoncé')
    sudokuMejthodes.ejcritMejthode('')
    sudokuPdfDoc.pdfGrilles()
    # 2) ejcrit les conclusions sur la rejsolution
    sudokuMejthodes.ejcritVerification(sudokuVejrification)
    # 3) amejliore jusqu'ah la victoire ou jusqu'ah la limite de ce qu'on sait amejliorer
    tour = 0
    coloration = False
    while True:
        # affiche le nombre de cellules affectejes d'une valeur
        #print ('tour n° %d : %d cellules affectejes'%(tour, len(sudokuValeurs.lesCellulesAffectejes())))  
        # n° tour suivant, celui sur lequel on travaille dans la boucle
        tour +=1
        sudokuPdfDoc.ejcritTour('tour n° %d'%(tour))
        while True:            
            # ejcrit une grille de valeurs possibles
            sudokuMejthodes.ejcritValeursPossibles()
            # mejthodes 1, 2, 3, 4
            sudokuMejthodes.mejthode_1()
            sudokuMejthodes.mejthode_2()
            sudokuMejthodes.mejthode_3()
            sudokuMejthodes.mejthode_4()
            # et mejthode 5 pour l'affectation par les rejseaux virtuels
            sudokuMejthodes.mejthode_5()
            # si au moins une cellule a ejtej pourvue, c'est terminej
            if sudokuValeurs.existeValeurTour(): break
            # calcule groupes n-n et repart pour un tour si changement
            if sudokuMejthodes.trouveGroupesNn(): continue
            # calcule alignements et repart pour un tour si changement
            if sudokuMejthodes.trouveValeursAlignejes(): continue
            # si le premiehre fois qu'on utilise la coloration, ejcrit les explications
            if not coloration:
                sudokuPdfDoc.ejcritExplicationsColoration()
                coloration = True
                sudokuMejthodes.ejcritValeursPossibles()
            # calcule les rejseaux gejnejriques et repart pour un tour si changement
            if sudokuMejthodes.trouveRejseauxGejnejriques(): continue
            # calcule les rejseaux virtuels et repart pour un tour si changement
            if sudokuMejthodes.trouveRejseauxVirtuels(): continue
            # si aucun changement, c'est terminej
            # avant de proclamer l'ejchec, regarde les rejseaux gejnejriques carambolejs
            carambolage = sudokuMejthodes.trouveRejseauxGejnejriquesCarambolejs()
            # et les rejseaux virtuels carambolejs
            sudokuMejthodes.trouveRejseauxVirtuelsCarambolejs(carambolage)
            break
        # pour afficher les grilles en attente
        sudokuPdfDoc.pdfGrilles()
        # s'il y a du carambolage, ejchec 
        if sudokuValeurs.existeValeurCaramboleje(): break
        # si aucune cellule n'a ejtej pourvue, ejchec
        if not sudokuValeurs.existeValeurTour(): break
        # entejrine le tour
        sudokuValeurs.finTour()
        # si toutes cellules trouvejes, terminej
        if len(sudokuValeurs.lesCellulesAffectejes()) == 81: break
    # 4) affiche resultat
    nbAffectations = len(sudokuValeurs.lesCellulesAffectejes()) - nbCellulesEnoncej
    sudokuPdfDoc.ejcritRejsultat(nbAffectations, tour)
    sudokuMejthodes.ejcritRejsultat()
    sudokuPdfDoc.pdfGrilles()
    # 5) si pas terminej, affiche l'ejchec
    if len(sudokuValeurs.lesCellulesAffectejes()) != 81: 
        print('EJCHEC : %d valeurs affectejes en %d tours'%(nbAffectations, tour))
        sudokuPdfDoc.ejcritEjchec()
        sudokuPdfDoc.ejcritTour('pour rejflejchir encore...')
        sudokuMejthodes.ejcritValeursPossibles()
        sudokuMejthodes.trouveRejseauxGejnejriques()
        sudokuMejthodes.trouveRejseauxVirtuels()
        sudokuMejthodes.dumpeRejseauxVirtuels()
        sudokuPdfDoc.pdfGrilles()
    else:
        print('SUCCEHS : %d valeurs affectejes en %d tours'%(nbAffectations, tour))
    sudokuPdfDoc.termine()
        
if __name__ == '__main__':
    main()
