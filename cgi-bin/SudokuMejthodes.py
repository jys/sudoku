#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2019 LATEJCON"
__license__ = "GNU AGPL"
__version__ = "2.0.1"

import sys
from io import StringIO
from itertools import combinations
from SudokuPdfDoc import SudokuPdfDoc
from SudokuValeurs import SudokuValeurs
from SudokuContraintes import SudokuContraintes
from SudokuVejrification import SudokuVejrification

class SudokuMejthodes:
    def __init__(self, sudokuValeurs, sudokuPdfDoc):
        # init contraintes
        self.sudokuContraintes = SudokuContraintes()
        # init valeurs
        self.sudokuValeurs = sudokuValeurs
        # init sortie pdf
        self.sudokuPdfDoc = sudokuPdfDoc
        # mejmorise l'ejnoncej
        self.affectejesEjnoncej = []
        self.affectejesEjnoncej.extend(self.sudokuValeurs.lesCellulesAffectejes())
        # mejmoire des cellules-valeurs affectejes par les rejseaux virtuels
        self.cellulesValeursAffectejes = []
        
    ##########################################
    # pour tous les blocs, cherche l'emplacement unique
    def mejthode_1(self):
        for valeur in range(1,10):
            cellulesInterdites = self.cellulesInterdites(valeur)
            for bloc in self.sudokuContraintes.blocs():
                cellulesPossibles = set(bloc) - cellulesInterdites
                if len(cellulesPossibles) != 1: continue
                self.sudokuValeurs.insehreValeur(list(cellulesPossibles)[0], valeur)
        if self.sudokuValeurs.existeValeurCourante() : self.ejcritMejthode('1 (carrejs)')
        self.sudokuValeurs.finMejthode()

    ##########################################
    # pour toutes les lignes, cherche l'emplacement unique
    def mejthode_2(self):
        for valeur in range(1,10):
            cellulesInterdites = self.cellulesInterdites(valeur)
            for ligne in self.sudokuContraintes.lignes():
                cellulesPossibles = set(ligne) - cellulesInterdites
                if len(cellulesPossibles) != 1: continue
                self.sudokuValeurs.insehreValeur(list(cellulesPossibles)[0], valeur)
        if self.sudokuValeurs.existeValeurCourante() : self.ejcritMejthode('2 (lignes)')
        self.sudokuValeurs.finMejthode()

    ##########################################
    # pour toutes les colonnes, cherche l'emplacement unique
    def mejthode_3(self):
        for valeur in range(1,10):
            cellulesInterdites = self.cellulesInterdites(valeur)
            for colonne in self.sudokuContraintes.colonnes():
                cellulesPossibles = set(colonne) - cellulesInterdites
                if len(cellulesPossibles) != 1: continue
                self.sudokuValeurs.insehreValeur(list(cellulesPossibles)[0], valeur)
        if self.sudokuValeurs.existeValeurCourante() : self.ejcritMejthode('3 (colonnes)')
        self.sudokuValeurs.finMejthode()

    ##########################################
    # pour chaque cellule de la grille, vejrifie s'il y a une seule possibilitej de valeur
    def mejthode_4(self):
        lesValeursPossibles, lesCellulesPossibles = self.lesValeursEtCellulesPossibles()
        # trouve les valeurs uniques
        for (cellule, valeurs) in lesValeursPossibles.items():
            if len(valeurs) == 1: self.sudokuValeurs.insehreValeur(cellule, valeurs[0])
        if self.sudokuValeurs.existeValeurCourante() : self.ejcritMejthode('4 (uniques)')
        self.sudokuValeurs.finMejthode()
        
    ##########################################
    # les 4 mejthodes d'affectation comme une seule mejthode 
    def mejthodes_1234(self):
        # mejthode 1, 2, 3
        for valeur in range(1,10):
            cellulesInterdites = self.cellulesInterdites(valeur)
            # pour chacune des 27 structures de contraintes (9 carrejs, 9 lignes, 9 colonnes)
            for structure in self.sudokuContraintes.toutesStructures():
                cellulesPossibles = set(structure) - cellulesInterdites
                if len(cellulesPossibles) != 1: continue
                self.sudokuValeurs.insehreValeur(list(cellulesPossibles)[0], valeur)
        # mejthode 4
        lesValeursPossibles, lesCellulesPossibles = self.lesValeursEtCellulesPossibles()
        # trouve les valeurs uniques
        for (cellule, valeurs) in lesValeursPossibles.items():
            if len(valeurs) == 1: self.sudokuValeurs.insehreValeur(cellule, valeurs[0])
        
    ##########################################
    # affecte les cellules-valeurs trouvejes par les rejseaux virtuels
    def mejthode_5(self):
        # vire les doublons
        for (cellule, valeur) in set(self.cellulesValeursAffectejes):
            self.sudokuValeurs.insehreValeur(cellule, valeur)
        self.cellulesValeursAffectejes.clear()
        if self.sudokuValeurs.existeValeurCourante() : self.ejcritMejthode('5 (virtuels)')
        self.sudokuValeurs.finMejthode()

    ##########################################
    # calcule les valeurs interdites 
    def cellulesInterdites(self, valeur):
        # la liste des cellules interdites est initialiseje par la liste des cellules dejjah occupejes
        cellulesInterdites = self.sudokuValeurs.lesCellulesAffectejes()
        # ajoute toutes les cellules interdites par les cellules qui ont dejjah cette valeur 
        for cellule in self.sudokuValeurs.lesCellulesDeValeur(valeur):
            cellulesInterdites |= self.sudokuContraintes.contraintesSurUneCellule(cellule)
        # ajoute toutes les cellules explicitement interdites pour cette valeur 
        cellulesInterdites |= set(self.sudokuValeurs.lesCellulesInterdites(valeur))
        return cellulesInterdites
            
    ##########################################
    # calcule les groupes n-n (n valeurs sur n cellules d'un groupe de contraintes) 
    # et en tire les consejquences en trouvant les cellule-valeurs interdites.
    def trouveGroupesNn(self):
        # 1) trouve les groupes n-n
        valeursGroupejes = set()           # set ( (tuple cellules) (tuple valeurs) )
        # les valeurs possibles et les cellules possibles
        lesValeursPossibles, lesCellulesPossibles = self.lesValeursEtCellulesPossibles()
        # pour chacune des 27 structures de contraintes (9 carrejs, 9 lignes, 9 colonnes)
        for structure in self.sudokuContraintes.toutesStructures():
            #trouve les cellules de la structure pas encore affectejes
            cellules = list(set(structure) - set(self.sudokuValeurs.lesCellulesAffectejes()))
            cellules.sort()
            tailleLibres = len(cellules)
            #trouve toutes les combinaisons possibles pour tester le n-n
            for taille in range(2, tailleLibres):
                groupes = combinations(cellules, taille)
                #pour chaque groupe de cellules, trouve les diffejrentes valeurs possibles
                for groupe in groupes :
                    valeursPossibles = set()
                    for cellule in groupe: valeursPossibles |= set(lesValeursPossibles[cellule])
                    #si le nombre de valeurs possibles est ejgal au nombre  de cellules, c'est gagnej
                    if len(valeursPossibles) == taille: 
                        valeurs = list(valeursPossibles)
                        valeurs.sort()
                        valeursGroupejes.add((groupe, tuple(valeurs)))
            #trouve les valeurs non encore affectejes pour la structure
            valeurs = list(set([v for v in range(1,10)]) - set(self.sudokuValeurs.lesValeursDeCellules(structure,)))
            valeurs.sort()
            tailleLibres = len(valeurs)
            #trouve toutes les combinaisons possibles pour tester le n-n
            for taille in range(2, tailleLibres):
                groupes = combinations(valeurs, taille)
                #pour chaque groupe de valeurs, trouve les diffejrentes cellules possibles
                for groupe in groupes :
                    cellulesPossibles = set()
                    for valeur in groupe: cellulesPossibles |= (set(lesCellulesPossibles[valeur]) & set(structure))
                    #si le nombre de cellules possibles est ejgal au nombre  de valeurs, c'est gagnej
                    if len(cellulesPossibles) == taille: 
                        cellules = list(cellulesPossibles)
                        cellules.sort()
                        valeursGroupejes.add((tuple(cellules), groupe))
        # 2) trouve les cellule-valeurs ejliminejes
        groupesEfficients = []
        for (cellules, valeurs) in valeursGroupejes:
            celluleValeursInterdites = []
            # d'abord la liste de cellules interdites des valeurs du groupe
            for cellule in self.sudokuContraintes.contraintesSurValeursGroupejes(cellules):
                for valeur in lesValeursPossibles[cellule]:
                    if valeur in valeurs: celluleValeursInterdites.append((cellule, valeur))
            # ensuite la liste de valeurs interdites aux cellules du groupe
            for cellule in cellules:
                for valeur in lesValeursPossibles[cellule]:
                    if valeur not in valeurs: celluleValeursInterdites.append((cellule, valeur))
            # si au moins une valeur interdite, c'est un groupe efficient
            if len(celluleValeursInterdites) != 0:
                groupesEfficients.append((len(cellules), cellules, valeurs, celluleValeursInterdites))
        # si aucun groupe efficient, ejchec 
        if len(groupesEfficients) == 0: return False
        # classe les groupes efficients les plus petits en teste
        groupesEfficients.sort()
        # 3) affiche les groupes de taille la plus petite et mejmorise les cellule-valeurs interdites
        tailleRetenue = groupesEfficients[0][0]
        lesInterdites = set()
        for (taille, cellules, valeurs, celluleValeursInterdites) in groupesEfficients:
            if taille == tailleRetenue and not set(celluleValeursInterdites).issubset(lesInterdites):
                self.ejcritGroupe(cellules, valeurs, celluleValeursInterdites, 'groupe n-n')
                lesInterdites |= set(celluleValeursInterdites)
        self.sudokuValeurs.insehreCelluleValeursInterdites(list(lesInterdites))
        return True

    ##########################################
    #calcule les valeurs alignejes et en tire les consejquences en trouvant les cellule-valeurs interdites.
    def trouveValeursAlignejes(self):
        # 1) trouve les valeurs alignejes
        valeursAlignejes = set()
        # les valeurs possibles et les cellules possibles
        lesValeursPossibles, lesCellulesPossibles = self.lesValeursEtCellulesPossibles()
        # les cellules alignejes ont toutes la mesme valeur
        for valeur in range(1,10):
            for cellulesBloc in self.sudokuContraintes.blocs():
                cellulesValeur = set(cellulesBloc) & lesCellulesPossibles[valeur]
                #si la valeur est dejjah affecteje, il y a 0 cellules. 
                #pas possible qu'il n'y ait qu'1 cellule, elle aurait ejtej trouveje par la mejthode 1 
                if len(cellulesValeur) == 0: continue
                for cellulesLigne in self.sudokuContraintes.lignes():
                    if cellulesValeur <= set(cellulesLigne): valeursAlignejes.add((tuple(cellulesValeur), valeur))
                for cellulesColonne in self.sudokuContraintes.colonnes():
                    if cellulesValeur <= set(cellulesColonne): valeursAlignejes.add((tuple(cellulesValeur), valeur))
            for cellulesLigne in self.sudokuContraintes.lignes():
                cellulesValeur = set(cellulesLigne) & lesCellulesPossibles[valeur]
                #si la valeur est dejjah affecteje, il y a 0 cellules. 
                #pas possible qu'il n'y ait qu'1 cellule, elle aurait ejtej trouveje par la mejthode 2
                if len(cellulesValeur) == 0: continue
                for cellulesBloc in self.sudokuContraintes.blocs():
                    if cellulesValeur <= set(cellulesBloc): valeursAlignejes.add((tuple(cellulesValeur), valeur))
            for cellulesColonne in self.sudokuContraintes.colonnes():
                cellulesValeur = set(cellulesColonne) & lesCellulesPossibles[valeur]
                #si la valeur est dejjah affecteje, il y a 0 cellules. 
                #pas possible qu'il n'y ait qu'1 cellule, elle aurait ejtej trouveje par la mejthode 3
                if len(cellulesValeur) == 0: continue
                for cellulesBloc in self.sudokuContraintes.blocs():
                    if cellulesValeur <= set(cellulesBloc): valeursAlignejes.add((tuple(cellulesValeur), valeur))
        # 2) trouve les cellule-valeurs ejliminejes
        groupesEfficients = []
        for (cellules, valeurAlignee) in valeursAlignejes:
            celluleValeursInterdites = []
            # la liste de cellules interdites de la valeur de cet alignement
            for cellule in self.sudokuContraintes.contraintesSurValeursGroupejes(cellules):
                for valeur in lesValeursPossibles[cellule]:
                    if valeur == valeurAlignee: celluleValeursInterdites.append((cellule, valeurAlignee))
            # si au moins une valeur interdite, c'est un groupe efficient
            if len(celluleValeursInterdites) != 0:
                groupesEfficients.append((len(cellules), cellules, tuple([valeurAlignee]), celluleValeursInterdites))
        # si aucun groupe efficient, ejchec 
        if len(groupesEfficients) == 0: return False
        # classe les groupes efficients les plus petits en teste
        groupesEfficients.sort()
        # 3) affiche les groupes de taille la plus petite et mejmorise les cellule-valeurs interdites
        tailleRetenue = groupesEfficients[0][0]
        lesInterdites = set()
        for (taille, cellules, valeurs, celluleValeursInterdites) in groupesEfficients:
            if taille == tailleRetenue and not set(celluleValeursInterdites).issubset(lesInterdites):
                self.ejcritGroupe(cellules, valeurs, celluleValeursInterdites, 'alignement dans carré')
                lesInterdites |= set(celluleValeursInterdites)
        self.sudokuValeurs.insehreCelluleValeursInterdites(list(lesInterdites))
        return True
        
    ##########################################
    # calcule les valeurs possibles pour chaque cellule libre ainsi que les cellules possibles pour les 9 valeurs
    def lesValeursEtCellulesPossibles(self):
        lesValeursPossibles = {key:[] for key in range(1,100)}  
        lesCellulesPossibles = {key:set() for key in range(1,10)}  
        #trouve pour chaque cellule libre la liste des valeurs possibles 
        for valeur in range(1,10):
            #la liste des cellules interdites est initialiseje par la liste des cellules dejjah occupejes
            cellulesInterdites = self.sudokuValeurs.lesCellulesAffectejes()
            #ajoute aux cellules interdites toutes les cellules interdites par les cellules qui ont dejjah cette valeur 
            for cellule in self.sudokuValeurs.lesCellulesDeValeur(valeur):
                cellulesInterdites |= self.sudokuContraintes.contraintesSurUneCellule(cellule)           
            # ajoute toutes les cellules explicitement interdites pour cette valeur 
            cellulesInterdites |= set(self.sudokuValeurs.lesCellulesInterdites(valeur))
            #pour toutes les cellules (prises par blocs), cherche si la valeur est possible
            for bloc in self.sudokuContraintes.blocs():
                cellules = set(bloc) - cellulesInterdites
                #ajoute la valeur ah toutes les cellules possibles
                for cellule in cellules: lesValeursPossibles[cellule].append(valeur)
                #ajoute toutes les cellules possibles ah la valeur
                lesCellulesPossibles[valeur] |= cellules
        return lesValeursPossibles, lesCellulesPossibles 
            
    ################################################
    def trouveRejseauxGejnejriques(self):
        # calcule les liens forts 
        self.ejtablitLiensforts()
        # les regroupe en rejseau gejnejrique
        self.ejtablitRejseauxGejnejriques()
        # isole les rejseaux gejnejriques efficients
        return self.ejtablitRejseauxGejnejriquesEfficients()

    ################################################
    # calcule tous les liens forts parmi les valeurs possibles
    def ejtablitLiensforts(self):
        lesValeursPossibles, lesCellulesPossibles = self.lesValeursEtCellulesPossibles()
        self.liensForts = []
        # uniquement avec les valeurs possibles
        for cellule, valeurs in lesValeursPossibles.items():
            # d'abord toutes les cellules qui n'ont que 2 valeurs possibles
            if len(valeurs) == 2: 
                self.liensForts.append(((cellule, valeurs[0]), (cellule, valeurs[1])))
        # ensuite les valeurs qui n'ont que 2 reprejsentants dans un bloc donné
        for structure in self.sudokuContraintes.toutesStructures():
            valeurCellules = {}
            # les cellules des valeurs possibles qui sont dans cette structure 
            for cellule in set(structure) & set(lesValeursPossibles.keys()):
                for valeur in lesValeursPossibles[cellule]:
                    if valeur not in valeurCellules: valeurCellules[valeur] = []
                    valeurCellules[valeur].append(cellule)
            #trouve les valeurs qui ont 2 occurrences et 2 seules
            for valeur, cellules in valeurCellules.items():
                if len(cellules) == 2:
                    # on ne prend pas les doublons fonctionnels
                    if ((cellules[0], valeur), (cellules[1], valeur)) not in self.liensForts and ((cellules[1], valeur), (cellules[0], valeur)) not in self.liensForts:
                        self.liensForts.append(((cellules[0], valeur), (cellules[1], valeur)))

    ################################################
    def lesLiensForts(self):
        return self.liensForts
    
    ################################################
    # regroupe les liens forts en rejseaux gejnejriques 
    def ejtablitRejseauxGejnejriques(self):
        # un rejseau gejenejrique est un couple de listes de cellule-valeurs 
        self.gejnejriques = []
        for (celluleValeur1, celluleValeur2) in self.liensForts:
            # l'invariant est qu'une cellule-valeur ne peut estre que dans une seule liste
            # 3 cas possibles :
            # 1) aucune des 2 cellule-valeurs n'est connue => nouveau rejseau
            # 2) une seule des 2 cellule-valeurs est connue => on met la seconde dans la liste opposeje
            # 3) les 2 cellule-valeurs sont connues => 2 cas :
            #     A) elles sont dans les deux listes opposejes du mesme rejseau => raf
            #     B) elles sont dans des listes de rejseaux diffejrents => fusion des 2 rejseaux en 1 seul
            nouveauRejseau = True
            for (listeRouge, listeBleue) in self.gejnejriques:
                if celluleValeur1 in listeRouge:
                    if celluleValeur2 in listeBleue: 
                        nouveauRejseau = False
                        break                                       # cas 3A => raf
                    listesConcernejes = (listeBleue, listeRouge)
                    celluleValeurAjouteje = celluleValeur2
                elif celluleValeur1 in listeBleue:
                    if celluleValeur2 in listeRouge: 
                        nouveauRejseau = False
                        break                                       # cas 3A => raf
                    listesConcernejes = (listeRouge, listeBleue)
                    celluleValeurAjouteje = celluleValeur2
                elif celluleValeur2 in listeRouge:
                    listesConcernejes = (listeBleue, listeRouge)
                    celluleValeurAjouteje = celluleValeur1
                elif celluleValeur2 in listeBleue:
                    listesConcernejes = (listeRouge, listeBleue)
                    celluleValeurAjouteje = celluleValeur1
                else: continue                                  # aucune des deux dans ce rejseau
                nouveauRejseau = False
                # une seule cellule-valeur a ejtej trouveje
                # vejrifie si la valeur est dejjah dans un autre rejseau
                nouvelleCelluleValeur = True
                for (listeRouge, listeBleue) in self.gejnejriques:
                    if celluleValeurAjouteje in listeRouge:
                        # fusionne les listes
                        listesConcernejes[0].extend(listeRouge)
                        listesConcernejes[1].extend(listeBleue)
                    elif celluleValeurAjouteje in listeBleue:
                        # fusionne les listes
                        listesConcernejes[0].extend(listeBleue)
                        listesConcernejes[1].extend(listeRouge)
                    else: continue
                    nouvelleCelluleValeur = False
                    # il faut supprimer le rejseau 
                    self.gejnejriques.remove((listeRouge, listeBleue))
                    break
                # l'autre cellule-valeur est mise dans la liste opposeje
                if nouvelleCelluleValeur: listesConcernejes[0].append(celluleValeurAjouteje)
                # ok pour ce lien fort 
                break                                               # cas 2 et 3B
            # cas 1, crejation d'un rejseau
            if nouveauRejseau: self.gejnejriques.append(([celluleValeur1], [celluleValeur2]))
        #met les listes en ordre
        for (listeRouge, listeBleue) in self.gejnejriques:
            listeRouge.sort()
            listeBleue.sort()

    ################################################
    def lesGejnejriques(self):
        return self.gejnejriques
    
    ################################################
    # isole parmi les rejseaux gejejriques ceux qui permettent d'ejliminer des cellule-valeurs 
    def ejtablitRejseauxGejnejriquesEfficients(self):
        self.gejnejriquesEfficients = []
        # examine chaque rejseau indejpendamment
        for (listeRouge, listeBleue) in self.gejnejriques:
            # trouve les cellule-valeurs interdites par le rejseau gejnejrique
            celluleValeursInterdites = self.trouveCelluleValeursInterdites(listeRouge, listeBleue)
            # s'il y a au moins une cellule-valeur interdite, le rejseau gejnejrique est efficient 
            if len(celluleValeursInterdites) != 0:
                self.gejnejriquesEfficients.append((listeRouge, listeBleue, celluleValeursInterdites))
        # si aucun rejseau efficient, ejchec 
        if len(self.gejnejriquesEfficients) == 0: return False
        # prend en compte et affiche les rejseaux efficients
        for (listeRouge, listeBleue, celluleValeursInterdites) in self.gejnejriquesEfficients:
            # l'affiche 
            self.ejcritRejseau(listeRouge, listeBleue, [], [], celluleValeursInterdites, 'rejseau gejnejrique')
            self.sudokuValeurs.insehreCelluleValeursInterdites(celluleValeursInterdites)
        return True

    ################################################
    # trouve les branches de rejseaux dynamiques carambolejs 
    def trouveRejseauxGejnejriquesCarambolejs(self):
        carambolage = []
        for (listeRouge, listeBleue) in self.gejnejriques:
            cellules = set()
            for (cellule, valeur) in listeRouge: cellules.add(cellule)
            # carambolé ?
            if len(cellules) != len(listeRouge): carambolage.append((listeRouge, listeBleue, listeRouge))
            cellules = set()
            for (cellule, valeur) in listeBleue: cellules.add(cellule)
            # carambolé ?
            if len(cellules) != len(listeBleue): carambolage.append((listeRouge, listeBleue, listeBleue))
        # si pas de carambolage, terminej
        if len(carambolage) == 0: return False
        self.sudokuPdfDoc.ejcritExplicationsCarambolage()
        for (listeRouge, listeBleue, barrejs) in carambolage:
            # affiche le rejseau carambolej
            self.ejcritRejseau(listeRouge, listeBleue, [], [], barrejs, 'rejseau gejnejrique carambolé')
        # signale dejjah carambolage
        return True
                    
    ################################################
    def lesGejnejriquesEfficients(self):
        return self.gejnejriquesEfficients
    
    ################################################
    def trouveRejseauxVirtuels(self):
        #self.afficheRejseauxGejnejriques()
        # lorsque cette mejthode est appeleje, les rejseaux gejnejriques ont dejjah ejtej calculejs
        # le principe consiste ah appliquer les 4 mejthodes d'affectation sur chaque rejseau gejnejrique
        # une fois "comme si rouge ejtait vrai" et une fois "comme si bleu ejtait vrai" 
        # la recherche se fait itejrativement avec une profondeur augmentante
        # l'arrest de l'itejration se fait quand une ejlimination est trouveje ou quand aucune nouvelle
        # cellule-valeur virtuelle n'a ejtej trouveje ah la derniehre itejration.
        # la condition de sortie en succehs est au moins une ejlimination d'une cellule-valeur exogehne.
        # la condition de sortie en ejchec est aucune ejlimination d'une cellule-valeur exogehne.
        self.virtuelsEfficients = []
        self.virtuelsTerminaux = set()
        profondeur = 0
        while True:
            # la profondeur du calcul 
            profondeur +=1
            augmentationDernierTour = 0
            for (listeRouge, listeBleue) in self.gejnejriques:
                virtuellesRouges, augmentation = self.trouveValeursVirtuelles(listeRouge, profondeur)
                augmentationDuRejseau = augmentation
                virtuellesBleues, augmentation = self.trouveValeursVirtuelles(listeBleue, profondeur)
                augmentationDuRejseau += augmentation
                # trouve les cellule-valeurs interdites par le rejseau gejnejrique + son rejseau virtuel
                listeRougeEjtendue = list(set(listeRouge) | set(virtuellesRouges))
                listeBleueEjtendue = list(set(listeBleue) | set(virtuellesBleues))
                celluleValeursInterdites = self.trouveCelluleValeursInterdites(listeRougeEjtendue, listeBleueEjtendue)
                # trouve les cellule-valeurs affectejes par le rejseau virtuel
                cellulesValeursAffectejes = self.trouveCelluleValeursAffectejes(virtuellesRouges, virtuellesBleues)
                # s'il y a au moins une cellule-valeur interdite ou affecteje, le rejseau virtuel est efficient 
                if len(celluleValeursInterdites) + len(cellulesValeursAffectejes) != 0:
                    self.virtuelsEfficients.append((listeRouge, listeBleue, virtuellesRouges, virtuellesBleues, celluleValeursInterdites, cellulesValeursAffectejes))
                # mejmorise le rejseau virtuel terminal pour dejtection carambolage ejventuelle
                if augmentationDuRejseau == 0:
                    self.virtuelsTerminaux.add((tuple(listeRouge), tuple(listeBleue), tuple(virtuellesRouges), tuple(virtuellesBleues)))
                augmentationDernierTour += augmentationDuRejseau
            # si aucune nouvelle virtuelle au dernier tour ejchec 
            if augmentationDernierTour == 0: return False
            # si aucun rejeseau vrtuel efficient, on continue avec une profondeur de calcul augmenteje
            if len(self.virtuelsEfficients) == 0: continue
            # au moins un rejseau efficient trouvej, succehs
            break
        # prend en compte et affiche les rejseaux efficients
        # 1) les affiche
        for (listeRouge, listeBleue, virtuellesRouges, virtuellesBleues, celluleValeursInterdites, cellulesValeursAffectejes) in self.virtuelsEfficients:
            #self.ejcritRejseau(listeRouge, listeBleue, [], [], [], 'rejseau gejnejrique')
            # l'affiche avec les ejventuelles ejliminations
            self.ejcritRejseau(listeRouge, listeBleue, virtuellesRouges, virtuellesBleues, celluleValeursInterdites, 'rejseau virtuel (prof. %d)'%(profondeur))
            # mejmorise les affectations
            self.cellulesValeursAffectejes.extend(cellulesValeursAffectejes)                
        # 2) ejlimine les valeurs interdites
        for (listeRouge, listeBleue, virtuellesRouges, virtuellesBleues, celluleValeursInterdites, cellulesValeursAffectejes) in self.virtuelsEfficients:
            self.sudokuValeurs.insehreCelluleValeursInterdites(celluleValeursInterdites)
        return True
            
    ################################################
    def trouveValeursVirtuelles(self, listeCouleur, profondeur):
        lesNouvellesVirtuelles = []
        # 1) sauvegarde l'ejtat des valeurs 
        self.sudokuValeurs.sauvegarde()
        # 2) ajoute les rouges aux valeurs affectejes
        for (cellule, valeur) in listeCouleur: self.sudokuValeurs.insehreValeur(cellule, valeur)
        self.sudokuValeurs.finMejthode()
        self.sudokuValeurs.finTour()
        for i in range(profondeur):
            # 3) passe les 4 mejthodes d'affectation comme une seule
            self.mejthodes_1234()
            # et rejcupehre les nouvelles cellule-valeurs virtuellement affectejes
            lesNouvellesDuTour = []
            lesNouvellesDuTour.extend(self.sudokuValeurs.lesCellulesCarambolejes())
            self.sudokuValeurs.finMejthode()
            lesNouvellesDuTour.extend(self.sudokuValeurs.lesCelluleValeursduTour())
            #lesNouvellesDuTour.extend(lesCellulesCarambolejes)
            self.sudokuValeurs.finTour()
            lesNouvellesVirtuelles.extend(lesNouvellesDuTour)
            augmentation = len(lesNouvellesDuTour)
            #carambolage = len(lesCellulesCarambolejes) != 0
            # si la branche virtuelle n'augmente pas, on erreste
            if augmentation == 0: break
        # 4) restaure l'ejtat des valeurs
        self.sudokuValeurs.restaure()
        self.sudokuValeurs.razMemCarambolage()
        # retourne les nouvelles cellule-valeurs 
        return lesNouvellesVirtuelles, augmentation
        
    ################################################
    # trouve les rejseaux virtuels carambolejs 
    def trouveRejseauxVirtuelsCarambolejs(self, dejjahCarambolage):
        carambolage = []
        for (listeRouge, listeBleue, virtuellesRouges, virtuellesBleues) in self.virtuelsTerminaux:
            cellules = set()
            for (cellule, valeur) in virtuellesRouges: cellules.add(cellule)
            # carambolé ?
            if len(cellules) != len(set(virtuellesRouges)): 
                carambolage.append((listeRouge, listeBleue, virtuellesRouges, virtuellesBleues, listeRouge))
            cellules = set()
            for (cellule, valeur) in virtuellesBleues: cellules.add(cellule)
            # carambolé ?
            if len(cellules) != len(set(virtuellesBleues)): 
                carambolage.append((listeRouge, listeBleue, virtuellesRouges, virtuellesBleues, listeBleue))
         # si pas de carambolage, terminej
        if len(carambolage) == 0: return
        # carambolage dejjah affichej ?
        if not dejjahCarambolage: self.sudokuPdfDoc.ejcritExplicationsCarambolage()
        for (listeRouge, listeBleue, virtuellesRouges, virtuellesBleues, barrejs) in carambolage:
            self.ejcritRejseau(listeRouge, listeBleue, virtuellesRouges, virtuellesBleues, barrejs, 'rejseau virtuel carambolé')
                
    ################################################
    # dumpe les rejsaux virtuels terminaux  
    def dumpeRejseauxVirtuels(self):
        numeroj = 0
        for (listeRouge, listeBleue, virtuellesRouges, virtuellesBleues) in self.virtuelsTerminaux:
            numeroj += 1
            self.ejcritRejseau(listeRouge, listeBleue, virtuellesRouges, virtuellesBleues, [], 'rejseau virtuel n°%d'%(numeroj))

    ################################################
    def lesVirtuelsEfficients(self):
        return self.virtuelsEfficients
    
    ################################################
    # trouve les cellules-valeurs interdites par une rejseau gejnejrique ou virtuel
    def trouveCelluleValeursInterdites(self, listeRouge, listeBleue):
        celluleValeursInterdites = []
        # valeurs et cellules possibles
        lesValeursPossibles, lesCellulesPossibles = self.lesValeursEtCellulesPossibles()
        # examine les contraintes pour chaque valeur 
        for valeurRef in range(1,10):
            cellulesRejseaux = []
            # on trouve la liste des cellules en contrainte avec cette valeur pour chaque liste 
            contraintesRouges = set()
            for (cellule, valeur) in listeRouge:
                if valeur == valeurRef: 
                    cellulesRejseaux.append(cellule)
                    contraintesRouges |= self.sudokuContraintes.contraintesSurUneCellule(cellule)
            contraintesBleues = set()
            for (cellule, valeur) in listeBleue:
                if valeur == valeurRef: 
                    cellulesRejseaux.append(cellule)
                    contraintesBleues |= self.sudokuContraintes.contraintesSurUneCellule(cellule)
            # une cellule-valeur ah ejliminer devra se trouver ah l'inersection des 3 espaces
            contraintes = (contraintesRouges & contraintesBleues) - set(cellulesRejseaux)
            cellules = set(lesCellulesPossibles[valeurRef]) & contraintes
            # on mejmorise les ejentuelles cellule-valeurs ejliminejes 
            for cellule in cellules: celluleValeursInterdites.append((cellule, valeurRef))
        return celluleValeursInterdites          
            
    ################################################
    # trouve les cellules-valeurs affectejes par un rejseau virtuel
    def trouveCelluleValeursAffectejes(self, virtuellesRouges, virtuellesBleues):
        # ce sont les cellules-valeurs prejsentes dans les deux couleurs
        return list(set(virtuellesRouges) & set(virtuellesBleues))
        
    ################################################
    def afficheRejseauxGejnejriques(self):
        for (listeRouge, listeBleue) in self.gejnejriques:
             self.ejcritRejseau(listeRouge, listeBleue, [], [], [], 'rejseau gejnejrique')
       
    ################################################
    def afficheRejseauxVirtuels(self):
        self.trouveRejseauxVirtuels(True)
       
    ##########################################
    # ejcrit le rejsultat pour une mejthode
    def ejcritMejthode(self, noMejthode):
        # ejcrit le titre de la mejthode 
        if noMejthode != '': self.sudokuPdfDoc.ejcritTitreTable('par mejthode n° %s'%(noMejthode))
        valeurs = []
        verts = []
        erreurs = []
        # les cellules dejjah affectejes en noir
        for cellule in self.sudokuValeurs.lesCellulesAffectejes():
            valeurs.append((coordonnejes(cellule), self.sudokuValeurs.laValeurCellule(cellule)))
        # + les cellules affectejes par la mejthode en vert 
        for cellule in self.sudokuValeurs.lesCellulesCourantes():
            valeurs.append((coordonnejes(cellule), self.sudokuValeurs.laValeurCellule(cellule)))
            verts.append(coordonnejes(cellule))
        # + les cellules en carmabolage en rouge
        for (cellule, valeur) in self.sudokuValeurs.lesCellulesCarambolejes():
            valeurs.append((coordonnejes(cellule), valeur))
            erreurs.append(coordonnejes(cellule))
        self.sudokuPdfDoc.dessineGrille(valeurs, verts, erreurs, [])
        
      ##########################################
    # ejcrit le rejsultat final
    def ejcritRejsultat(self):
        valeurs = []
        verts = []
        # toutes les cellules affectejes
        for cellule in self.sudokuValeurs.lesCellulesAffectejes():
            valeurs.append((coordonnejes(cellule), self.sudokuValeurs.laValeurCellule(cellule)))
        # mais les cellules affectejes hors ejnoncej en vert 
        cellulesAffectejes = set(self.sudokuValeurs.lesCellulesAffectejes()) - set(self.affectejesEjnoncej)
        for cellule in cellulesAffectejes:
            verts.append(coordonnejes(cellule))
        self.sudokuPdfDoc.dessineGrille(valeurs, verts, [], [])
        
    ##########################################
    #ejcrit une grille avec les valeurs possibles
    def ejcritValeursPossibles(self):
        self.sudokuPdfDoc.ejcritTitreTable('cellules-valeurs possibles')
        lesValeurs, lesPossibles = self.lesValeurs()
        self.sudokuPdfDoc.dessineGrille(lesValeurs, [], [], lesPossibles)

    ##########################################
    #ejcrit une grille avec les valeurs possibles et les groupes n-n
    def ejcritGroupe(self, cellules, valeurs, celluleValeursInterdites, libellej):
        self.sudokuPdfDoc.ejcritTitreTable(libellej)
        lesValeurs, lesPossibles = self.lesValeurs()
        # les valeurs barrejes
        barrejes = []
        for (cellule, valeur) in celluleValeursInterdites: barrejes.append((coordonnejes(cellule), valeur))
        # les jaunes (en vrai vertes)
        jaunes = []
        for cellule in cellules:
            for valeur in valeurs:
                jaunes.append((coordonnejes(cellule), valeur))
        self.sudokuPdfDoc.dessineGrille(lesValeurs, [], [], lesPossibles, barrejes, jaunes)
                
    ##########################################
    #ejcrit une grille avec les valeurs possibles et un rejseau gejnejrique
    def ejcritRejseau(self, listeRouge, listeBleue, virtuellesRouges, virtuellesBleues, celluleValeursInterdites, libellej):
        self.sudokuPdfDoc.ejcritTitreTable(libellej)
        lesValeurs, lesPossibles = self.lesValeurs()
        # les valeurs barrejes
        barrejes = []
        for (cellule, valeur) in celluleValeursInterdites: barrejes.append((coordonnejes(cellule), valeur))
        # les rouges
        rouges = []
        for (cellule, valeur) in listeRouge:
            rouges.append((coordonnejes(cellule), valeur))
        # les bleues
        bleues = []
        for (cellule, valeur) in listeBleue:
            bleues.append((coordonnejes(cellule), valeur))
        # les rouges
        rougesclairs = []
        for (cellule, valeur) in virtuellesRouges:
            rougesclairs.append((coordonnejes(cellule), valeur))
        # les bleues
        bleusclairs = []
        for (cellule, valeur) in virtuellesBleues:
            bleusclairs.append((coordonnejes(cellule), valeur))
        self.sudokuPdfDoc.dessineGrille(lesValeurs, [], [], lesPossibles, barrejes, [], rouges, bleues, rougesclairs, bleusclairs)

    ##########################################
    #ejcrit la grille calculeje par la vejrification
    def ejcritVerification(self, sudokuVejrification):
        lesCellulesEnoncej = self.sudokuValeurs.lesCellulesAffectejes()
        (tropDeSolutions, nbreSolutions) = sudokuVejrification.nombreSolutions()
        # pas de solution
        if nbreSolutions == 0:
            self.sudokuPdfDoc.ejcritRejsolution(False, 0, len(lesCellulesEnoncej), [], [], [])
            return
        # au moins 1 solution
        lesValeurs, lesValeurs2 = sudokuVejrification.lesValeurs()
        valeurs = []
        verts = []
        for (cellule, valeur) in lesValeurs: 
            valeurs.append((coordonnejes(cellule), valeur))
            if cellule not in lesCellulesEnoncej: verts.append(coordonnejes(cellule))
        if nbreSolutions == 1:
            self.sudokuPdfDoc.ejcritRejsolution(False, 1, len(lesCellulesEnoncej), valeurs, [], verts)
            return
        # plusieurs solutions 
        valeurs2 = []
        for (cellule, valeur) in lesValeurs2: 
            valeurs2.append((coordonnejes(cellule), valeur))
        self.sudokuPdfDoc.ejcritRejsolution(tropDeSolutions, nbreSolutions, len(lesCellulesEnoncej), valeurs, valeurs2, verts)
     
    ##########################################
    # trouve les valeurs affectejes et les valeurs possibles
    def lesValeurs(self):
        lesValeurs = []
        lesPossibles = []
        # les cellules dejjah affectejes en noir
        for cellule in self.sudokuValeurs.lesCellulesAffectejes():
            lesValeurs.append((coordonnejes(cellule), self.sudokuValeurs.laValeurCellule(cellule)))
        # + les lesValeurs possibles en bleu 
        lesValeursPossibles, lesCellulesPossibles = self.lesValeursEtCellulesPossibles()
        for (cellule, listeValeurs) in lesValeursPossibles.items():
            for valeur in listeValeurs: lesValeurs.append((coordonnejes(cellule), valeur))
            if len(listeValeurs) != 0 : lesPossibles.append(coordonnejes(cellule))
        return lesValeurs, lesPossibles
        
    ################################################
    # retourne les liens forts sous forme de liste de ou exclusifs
    def lesLienFortsXor(self):
        liens = []
        for (celluleValeur1, celluleValeur2) in self.liensForts:
            (cellule1, valeur1) = celluleValeur1
            (cellule2, valeur2) = celluleValeur2
            liens.append('(%d,%d)⊕(%d,%d)'%(cellule1, valeur1, cellule2, valeur2))
        return ', '.join(liens)
    
    ################################################
    # retourne les rejseaux gejnejriques sous forme de liste d'ejquivalence
    def lesRejseauxGejnejriques(self):
        texte = StringIO()
        noRejseau = 0
        for (listeRouge, listeBleue) in self.gejnejriques:
            noRejseau +=1
            texte.write('R-%02d : '%(noRejseau))
            cellulesValeurs = []
            for (cellule, valeur) in listeRouge: cellulesValeurs.append('(%d,%d)'%(cellule, valeur))
            texte.write('≡'.join(cellulesValeurs) + '\n')
            texte.write('B-%02d : '%(noRejseau))
            cellulesValeurs = []
            for (cellule, valeur) in listeBleue: cellulesValeurs.append('(%d,%d)'%(cellule, valeur))
            texte.write('≡'.join(cellulesValeurs) + '\n')
        rejsultat = texte.getvalue()
        texte.close()
        return rejsultat
       
    ################################################
    # retourne les rejseaux gejnejriques sous forme graphviz
    def lesGejnejriquesGraphviz(self):
        texte = StringIO()
        texte.write('graph {\n')
        noRejseau = 0
        for (listeRouge, listeBleue) in self.gejnejriques:
            noRejseau +=1
            texte.write('   "GEN-%02d" -- "rouge-%02d"'%(noRejseau, noRejseau))
            for (cellule, valeur) in listeRouge: texte.write(' -- "(%d, %d)"'%(cellule, valeur))
            texte.write('\n')
            texte.write('   "GEN-%02d" -- "bleue-%02d"'%(noRejseau, noRejseau))
            for (cellule, valeur) in listeBleue: texte.write(' -- "(%d, %d)"'%(cellule, valeur))
            texte.write('\n')
        texte.write('}\n')
        rejsultat = texte.getvalue()
        texte.close()
        return rejsultat
    

# trouve les coordonnejes d'une cellule 
def coordonnejes(cellule):
    return ((cellule // 10) -1, (cellule % 10) -1)
    
