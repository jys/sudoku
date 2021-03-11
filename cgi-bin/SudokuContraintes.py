#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2019 LATEJCON"
__license__ = "GNU AGPL"
__version__ = "2.0.1"

import sys
from os import path

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (u"""© l'ATEJCON.  
Programme de test de la classe SudokuContraintes.
Sort les cellules qui contraignent la cellule spejcifieje par son numejro.

SudokuContraintes gehre les contraintes d'une grille de sudoku anthropomorphique.

usage   : %s <cellule> 
example : %s 91
"""%(script, script))

def main():
    if len(sys.argv) < 2 :
        usage()
        sys.exit()
    cellule = int(sys.argv[1])
    
    sudokuContraintes = SudokuContraintes()
    print (list(sudokuContraintes.contraintesSurUneCellule(cellule)))
        
#################################################################      
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
            
#################################################################
class SudokuContraintes:
    def __init__(self):
        #il y a 27 structures de contraintes : 9 blocs, 9 lignes, 9 colonnes
        bl_11 = (11, 12, 13, 21, 22, 23, 31, 32, 33)
        bl_14 = (14, 15, 16, 24, 25, 26, 34, 35, 36)
        bl_17 = (17, 18, 19, 27, 28, 29, 37, 38, 39)
        bl_41 = (41, 42, 43, 51, 52, 53, 61, 62, 63)
        bl_44 = (44, 45, 46, 54, 55, 56, 64, 65, 66)
        bl_47 = (47, 48, 49, 57, 58, 59, 67, 68, 69)
        bl_71 = (71, 72, 73, 81, 82, 83, 91, 92, 93)
        bl_74 = (74, 75, 76, 84, 85, 86, 94, 95, 96)
        bl_77 = (77, 78, 79, 87, 88, 89, 97, 98, 99)
        lig_1 = (11, 12, 13, 14, 15, 16, 17, 18, 19)
        lig_2 = (21, 22, 23, 24, 25, 26, 27, 28, 29)
        lig_3 = (31, 32, 33, 34, 35, 36, 37, 38, 39)
        lig_4 = (41, 42, 43, 44, 45, 46, 47, 48, 49)
        lig_5 = (51, 52, 53, 54, 55, 56, 57, 58, 59)
        lig_6 = (61, 62, 63, 64, 65, 66, 67, 68, 69)
        lig_7 = (71, 72, 73, 74, 75, 76, 77, 78, 79)
        lig_8 = (81, 82, 83, 84, 85, 86, 87, 88, 89)
        lig_9 = (91, 92, 93, 94, 95, 96, 97, 98, 99)
        col_1 = (11, 21, 31, 41, 51, 61, 71, 81, 91)
        col_2 = (12, 22, 32, 42, 52, 62, 72, 82, 92)
        col_3 = (13, 23, 33, 43, 53, 63, 73, 83, 93)
        col_4 = (14, 24, 34, 44, 54, 64, 74, 84, 94)
        col_5 = (15, 25, 35, 45, 55, 65, 75, 85, 95)
        col_6 = (16, 26, 36, 46, 56, 66, 76, 86, 96)
        col_7 = (17, 27, 37, 47, 57, 67, 77, 87, 97)
        col_8 = (18, 28, 38, 48, 58, 68, 78, 88, 98)
        col_9 = (19, 29, 39, 49, 59, 69, 79, 89, 99)
        #regroupements nejcessaires
        self.bl_00 = (bl_11, bl_14, bl_17, bl_41, bl_44, bl_47, bl_71, bl_74, bl_77)
        self.lig_0 = (lig_1, lig_2, lig_3, lig_4, lig_5, lig_6, lig_7, lig_8, lig_9)
        self.col_0 = (col_1, col_2, col_3, col_4, col_5, col_6, col_7, col_8, col_9)
        self.contraintes = (self.bl_00, self.lig_0, self.col_0)
        #construit le dico inverse : cellule -> bloc, ligne, colonne 
        celluleDico = {}
        for bl in  self.bl_00:
            for cellule in bl:
                if cellule in celluleDico: raise Exception('ERREUR : %d doublon dans les blocs'%(cellule))
                celluleDico[cellule] = [bl]
        for lig in  self.lig_0:
            for cellule in lig:
                if cellule not in celluleDico: raise Exception('ERREUR : %d absente dans les blocs'%(cellule))
                if len(celluleDico[cellule]) != 1: raise Exception('ERREUR : %d doublon dans les lignes'%(cellule))
                celluleDico[cellule].append(lig)
        for col in  self.col_0:
            for cellule in col:
                if cellule not in celluleDico: raise Exception('ERREUR : %d absente dans les blocs'%(cellule))
                if len(celluleDico[cellule]) != 2: raise Exception('ERREUR : %d doublon dans les colonnes'%(cellule))
                celluleDico[cellule].append(col)
        #la structure pejrenne
        self.contraintesParCellule = {}
        for (cellule, (bl, lig, col)) in celluleDico.items():
            self.contraintesParCellule[cellule] = (bl, lig, col)
           
    #retourne toutes les cellules
    def toutesCellules(self):
        rejsultat = []
        for lig in self.lig_0: rejsultat.extend(lig)
        return rejsultat
        
    #retourne les 9 blocs
    def blocs(self):
        return self.bl_00
        
    #retourne les 9 lignes
    def lignes(self):
        return self.lig_0
        
    #retourne les 9 colonnes
    def colonnes(self):
        return self.col_0
        
     #retourne toutes les cellules
    def toutesStructures(self):
        rejsultat = []
        rejsultat.extend(self.bl_00)
        rejsultat.extend(self.lig_0)
        rejsultat.extend(self.col_0)
        return rejsultat
    
   #retourne les 3 contraintes de la cellule spejcifieje
    def contraintesSurUneCellule(self, cellule):
        if cellule not in self.contraintesParCellule: return ()
        (bl, lig, col) = self.contraintesParCellule[cellule]
        return set(bl) | set(lig) | set(col)
        
    #retourne les contraintes des cellules spejcifiejes en valeurs groupejes
    def contraintesSurValeursGroupejes(self, cellules):
        rejsultat = set()
        #seules sont ejligibles les groupes qui contiennent tout le groupe
        for cellule in cellules:
            (bl, lig, col) = self.contraintesParCellule[cellule]
            if set(cellules).issubset(set(bl)): rejsultat |= set(bl)
            if set(cellules).issubset(set(lig)): rejsultat |= set(lig)
            if set(cellules).issubset(set(col)): rejsultat |= set(col)
        #les cellules du groupe sont, bien susr, enlevejes des interdites
        rejsultat -= set(cellules)
        #print (rejsultat)
        return rejsultat
                   
    ##retourne les contraintes des cellules spejcifiejes en valeurs alignejes
    #def contraintesSurValeursAlignejes(self, cellules):
        #rejsultat = set()
        ##seules sont ejligibles les groupes qui contiennent tout le groupe
        #for cellule in cellules:
            #(bl, lig, col) = self.contraintesParCellule[cellule]
            #if set(cellules).issubset(set(bl)): rejsultat |= set(bl)
            #if set(cellules).issubset(set(lig)): rejsultat |= set(lig)
            #if set(cellules).issubset(set(col)): rejsultat |= set(col)
        ##les cellules du groupe sont, bien susr, enlevejes des interdites
        #rejsultat -= set(cellules)
        ##print (rejsultat)
        #return rejsultat
    
    #retourne la ou les structures auxquelles appartient le groupe de cellules spejcifiejes
    #les structures sont nommejes 
    #L11, L21, L31, L41, L51, L61, L71, L81, L91
    #C11, C12, C13, C14, C15, C16, C17, C18, C19
    #B11, B14, B17, B41, B44, B47, B71, B74, B77
    def identifieStructures(self, cellules):
        cellulesSet = set(cellules)
        rejsultat = []
        for bl in  self.bl_00:
            if cellulesSet <= set(bl): rejsultat.append('B%d'%(bl[0]))
        for lig in  self.lig_0:
            if cellulesSet <= set(lig): rejsultat.append('L%d'%(lig[0]))
        for col in  self.col_0:
            if cellulesSet <= set(col): rejsultat.append('C%d'%(col[0]))
        return rejsultat
                        
if __name__ == '__main__':
    main()
