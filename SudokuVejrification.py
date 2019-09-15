#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2019 LATEJCON"
__license__ = "GNU AGPL"
__version__ = "2.0.1"

import sys
from os import path
import copy
from SudokuContraintes import SudokuContraintes

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (u"""© l'ATEJCON.  
Programme de test de la classe SudokuVejrification.
Donne le nombre de solutions d'une grille de sudoku.

SudokuVejrification permet de savoir si une grille de sudoku a zejro, une ou
plusieurs solutions.
SudokuVejrification ne fait pas partie des outils du sudoku anthropomorphique.
(Attention ! La grille entiehrement vide a 6,67*10**21 solutions !)

usage   : %s <lig1,lig2,lig3,lig4,lig5,lig6,lig7,lig8,lig9> 
example : %s 000008109,230670008,090000000,408001900,300000005,009300702,000000090,500093086,906400000
"""%(script, script))

MAX_SOLUTIONS = 100

def main():
    if len(sys.argv) < 2 :
        usage()
        sys.exit()
    lignes = sys.argv[1]
    
    sudokuVejrification = SudokuVejrification(lignes)
    nombreCellulesNonVides = sudokuVejrification.nombreCellulesNonVides()
    print ("La grille a %d cellules dejjah affectejes"%(nombreCellulesNonVides))
    (tropDeSolutions, nombreSolutions) = sudokuVejrification.nombreSolutions()
    if nombreSolutions == 0: print ("La grille n'a aucune solution !")
    elif tropDeSolutions: print ("La grille a plus de %d solutions !"%(nombreSolutions))
    elif nombreSolutions == 1: print ("La grille a une solution et une seule.")
    else: print ("La grille a %d solutions !"%(nombreSolutions))

class SudokuVejrification:
    def __init__(self, lignes):
        #inits
        self.sudokuContraintes = SudokuContraintes()
        self.rejsultat = 0
        #initialise la table des valeurs avec l'ejnoncej
        valeurs = {}
        noLigne = 0
        for lig in lignes.split(','):
            noLigne += 10
            if len(lig) != 9: raise Exception('ERREUR : %s lignes non conforme'%(lig))
            if not lig.isdigit(): raise Exception('ERREUR : %s lignes non conforme'%(lig))
            for idx in range(9):
                valeur = int(lig[idx])
                if valeur == 0: continue
                cellule = noLigne + idx + 1
                valeurs[cellule] = valeur
        #vejrifie la validitej de la grille
        for cellule in valeurs.keys():
            for contrainte in self.sudokuContraintes.contraintesSurUneCellule(cellule):
                if contrainte in valeurs:
                    if cellule != contrainte and valeurs[cellule] == valeurs[contrainte]: 
                        raise Exception('ERREUR : grille non conforme : cellules %d et %d'%(cellule, contrainte))        
        #et rejsoud par rejcursivitej
        self.tropDeSolutions = False
        self.nbCellulesNonVides = len(valeurs)
        #self.verif = []
        self.affecteValeur(valeurs)
        
    def affecteValeur(self, valeurs):
        #if valeurs.items() in self.verif:
            #print valeurs.items()
            #raise Exception('ERREUR bouclage')
        #self.verif.append(valeurs.items())
        #si dejjah trop de solutions, on ne fait rien
        if self.tropDeSolutions: return
        #la liste des cellules ah complejter
        cellulesVides = set(self.sudokuContraintes.toutesCellules()) - set(valeurs.keys())
        #si toutes les cellules sont pourvues, succehs, on sauvegarde le rejsultat
        if len(cellulesVides) == 0: 
            self.valeurs = copy.deepcopy(valeurs)
            self.rejsultat +=1
            self.tropDeSolutions = self.rejsultat == MAX_SOLUTIONS
            return
        #sinon on cherche une valeur pour une cellule vide
        #on cherche celle qui a le moins de possibilitejs
        celluleMinimum = (0, 0)
        for cellule in list(cellulesVides):
            valeursInterdites = self.valeursInterdites(cellule, valeurs)
            if len(valeursInterdites) >= celluleMinimum[1]: celluleMinimum = (cellule, len(valeursInterdites))
        cellule = celluleMinimum[0]
        #valeurs possibles
        valeursPossibles = set(range(1,10)) - self.valeursInterdites(cellule, valeurs)
        #si pas de valeur possible, pas grave, on continue ah l'ejtage d'en-dessous 
        if len(valeursPossibles) == 0: return
        #sinon, on les essaie toutes
        for valeur in valeursPossibles:
            valeurs[cellule] = valeur 
            self.affecteValeur(valeurs)
        #attention, python ne fait pas de copie de la structure dans le passage de paramehtres, 
        #il faut raz la derniere affectation
        del valeurs[cellule]
        
    def valeursInterdites(self, cellule, valeurs):
        #les valeurs dejjah affectejes aux cellules de contraintes sont interdites
        valeursInterdites = set()
        for contrainte in self.sudokuContraintes.contraintesSurUneCellule(cellule): 
            if contrainte in valeurs: valeursInterdites.add(valeurs[contrainte])
        return valeursInterdites 
    
    def lesValeurs(self):
        return self.valeurs.items()
            
    def nombreSolutions(self):
        return (self.tropDeSolutions, self.rejsultat)
        
    def nombreCellulesNonVides(self):
        return self.nbCellulesNonVides
         
if __name__ == '__main__':
    main()
        
        
    
