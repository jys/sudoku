#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2019 LATEJCON"
__license__ = "GNU AGPL"
__version__ = "2.0.1"

import sys
from os import path
import copy

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (u"""© l'ATEJCON.  
Programme de test de la classe SudokuValeurs.
Donne la liste des cellules occupejes aprehs l'initialisation avec leur valeur

SudokuValeurs gehre les valeurs d'une grille de sudoku anthropomorphique.
Il s'agit des valeurs affectejes, pas des valeurs spejculatives qui sont gejrejes
par une autre classe.

usage   : %s <lig1,lig2,lig3,lig4,lig5,lig6,lig7,lig8,lig9> 
example : %s 000008109,230670008,090000000,408001900,300000005,009300702,000000090,500093086,906400000
"""%(script, script))

def main():
    if len(sys.argv) < 2 :
        usage()
        sys.exit()
    lignes = sys.argv[1]
    
    sudokuValeurs = SudokuValeurs(lignes)
    rejsultat = ''
    for cellule in sudokuValeurs.cellulesOccupejes():
        valeur = sudokuValeurs.valeurCellule(cellule)
        rejsultat += '%d:%d '%(cellule, valeur)
    print (rejsultat)
    print (sudokuValeurs.cellulesOccupejes())
    #print (sudokuValeurs.cellulesOccupejes(-1))

#################################################################      
# SudokuValeurs est la classe qui maintient les valeurs rejelles de la grille
# chaque cellule affecteje d'une valeur est rejfejrenceje avec sa valeur
# LEXIQUE : la rejsolution se fait par une succession de TOURS. 
# Durant chaque tour, il y a plusieurs applications de MEJTHODES.
# Il y a 3 ensembles de valeurs (gejerejs par des dict)
# 1) les VALEURS AFFECTEJES : les valeurs affectejes avant le tour actuel
# 2) les VALEURS COURANTES : les valeurs affectejes par la mejthode courante 
# 3) les VALEURS DU TOUR : mejmorisation des valeurs affectées par les mejthodes precejdentes
# les nouvelles valeurs trouvejes par une mejthode sont ajoutejes dans les VALEURS COURANTES 
# ah la fin de la mejthode, les VALEURS COURANTES sont ajoutejes aux VALEURS DU TOUR
# ah la fin du tour, les VALEURS DU TOUR sont ajoutejes aux VALEURS AFFECTEJES

#numejrotation des 81 cellules
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

class SudokuValeurs:
    def __init__(self, lignes):
        self.valeursAffectejes = {}
        self.valeursduTour = {}
        self.valeursCourantes = {}
        self.cellulesInterdites = {}
        self.carambolage = []
        self.memCarambolage = False
        noLigne = 0
        for lig in lignes.split(','):
            noLigne += 10
            if len(lig) != 9: raise Exception('ERREUR : %s lignes non conforme'%(lig))
            if not lig.isdigit(): raise Exception('ERREUR : %s lignes non conforme'%(lig))
            for idx in range(9):
                valeur = int(lig[idx])
                if valeur == 0: continue
                cellule = noLigne + idx + 1
                self.valeursAffectejes[cellule] = valeur

    # sauvegarde les valeurs affectejes
    def sauvegarde(self):
        self.sauvegardeValeursAffectejes = copy.deepcopy(self.valeursAffectejes)

    # restaure les valeurs affectejes
    def restaure(self):
        self.valeursAffectejes = copy.deepcopy(self.sauvegardeValeursAffectejes)

    # insehre une valeur pour une cellule dans les valeurs courantes
    def insehreValeur(self, cellule, valeur):
        #une cellule affecteje ne peut estre rejaffecteje (dans les valeurs et les valeurs courantes)
        if cellule in self.valeursAffectejes or cellule in self.valeursCourantes: 
            self.carambolage.append((cellule, valeur))
            self.memCarambolage = True
        else: self.valeursCourantes[cellule] = valeur
        
    # passe les valeurs courantes dans les valeurs du tour et raz valeurs courantes
    def finMejthode(self):
        self.valeursduTour.update(self.valeursCourantes)
        self.valeursCourantes = {}
        self.carambolage = []
       
    # passe les valeurs du tour dans les valeurs affectejes et raz valeurs du tour
    def finTour(self):
        self.valeursAffectejes.update(self.valeursduTour)
        self.valeursduTour = {}
        
    # insehre les cellule-valeurs interdites
    def insehreCelluleValeursInterdites(self, celluleValeursInterdites):
        for (cellule, valeur) in celluleValeursInterdites:
            if valeur not in self.cellulesInterdites: self.cellulesInterdites[valeur] = []
            self.cellulesInterdites[valeur].append(cellule)
            
    # raz la mejmoire du carambolage
    def razMemCarambolage(self):
        self.memCarambolage = False
       
    # donne la valeur d'une cellule dans les valeurs affectejes et les valeurs courantes
    def laValeurCellule(self, cellule):
        if cellule in self.valeursAffectejes: return self.valeursAffectejes[cellule]
        if cellule in self.valeursCourantes: return self.valeursCourantes[cellule]
        return 0
        
    # donne la liste des cellules affectejes 
    def lesCellulesAffectejes(self):
        return self.valeursAffectejes.keys() 
    
    # donne la liste des cellules affectejes avec leur valeur
    def lesValeursAffectejes(self):
        return self.valeursAffectejes 
    
    # donne la liste des cellules du tour 
    def lesCellulesduTour(self):
        return self.valeursduTour.keys() 
    
    # donne la liste des cellules du tour et leur valeur  
    def lesCelluleValeursduTour(self):
        return self.valeursduTour.items() 
    
    # retourne True si au moins une valeur du tour
    def existeValeurTour(self):
        return len(self.valeursduTour) != 0
    
    # donne la liste des cellules courantes 
    def lesCellulesCourantes(self):
        return self.valeursCourantes.keys() 
    
    # retourne True si au moins une valeur courante
    def existeValeurCourante(self):
        return len(self.valeursCourantes) != 0
    
    # donne la liste des cellules-valeurs en carambolage 
    def lesCellulesCarambolejes(self):
        return self.carambolage 

    # retourne True si au moins une valeur caramboleje
    def existeValeurCaramboleje(self):
        return self.memCarambolage

    # donne la liste des cellules affectejes avec une valeur spejcifieje 
    def lesCellulesDeValeur(self, valeurRef):
        listeCellules = []
        for (cellule, valeur) in self.valeursAffectejes.items():
            if valeur == valeurRef: listeCellules.append(cellule)
        return listeCellules
    
    # donne la liste des valeurs affectejes ah un groupe de cellules spejcifiej 
    def lesValeursDeCellules(self, cellulesRef):
        listeValeurs = []
        for (cellule, valeur) in self.valeursAffectejes.items():
            if cellule in cellulesRef: listeValeurs.append(valeur)
        return listeValeurs

    # donne la liste des cellules explicitement interdites pour la valeur spejcifieje
    def lesCellulesInterdites(self, valeurRef):
        if valeurRef in self.cellulesInterdites: return self.cellulesInterdites[valeurRef]
        else: return []
           
if __name__ == '__main__':
    main()
              
