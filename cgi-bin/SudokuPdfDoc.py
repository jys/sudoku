#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
__author__ = "jys"
__copyright__ = "Copyright (C) 2019 LATEJCON"
__license__ = "GNU AGPL"
__version__ = "2.0.1"

import sys
from os import path
from copy import deepcopy
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors, enums
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph, Table, Image, Spacer
from reportlab.platypus.flowables import KeepTogether 

def usage():
    script = '$PY/' + path.basename(sys.argv[0])
    print (u"""© l'ATEJCON.  
Programme de test de la classe SudokuPdfDoc.
SudokuPdfDoc creje le document PDF rejsultat du sudoku anthropomorphique.
Le programme de test creje le fichier rejsultat/SudokuPdf-test.pdf 

usage   : %s <n'importe quoi> 
example : %s toto
"""%(script, script))

M_H = 1.5*cm            #marge haute
M_B = 1.5*cm            #marge basse
M_G = 1.5*cm            #marge gauche
M_D = 1.5*cm            #marge droite
C_CEL = 0.5*cm          #longueur costej d'1 cellule
C_TAB = C_CEL*9         #longueur costej d'1 table
C_CEL2 = 0.3*cm         #longueur costej d'1 cellule mini 
C_TAB2 = C_CEL2*9       #longueur costej d'1 table mini 

def main():
    if len(sys.argv) < 2 :
        usage()
        sys.exit()
        
    #nom du fichier
    #nom du fichier de sortie. On prend le chemin moins la fin 
    racine = '/'.join(path.dirname(path.abspath(sys.argv[0])).split('/')[:-1])
    nomFichierSortie = '%s/rejsultats/SudokuPdf-test.pdf'%(racine)
    sudokuPdfDoc = SudokuPdfDoc(nomFichierSortie, '0123456789')
    valeurs = [((1,7),8),((1,7),2),((3,2),6),((3,2),7),((3,2),8),((3,2),9),((1,2),1),((5,5),3),((5,5),2),((5,5),1),((5,5),9),((5,5),8),((5,5),6),((8,3),1),((8,3),7),((8,3),6),((8,3),5),((8,3),2),((3,5),2),((7,1),3),((0,6),4),((4,0),5),((4,0),2),((4,0),8),((6,8),6)]
    verts = [(3,5)]
    sudokuPdfDoc.ejcritTour('ejnoncé')
    sudokuPdfDoc.dessineGrille([((1,7),8),((3,2),6),((1,2),1),((5,5),3)], [], [], [], [], [])
    sudokuPdfDoc.pdfGrilles()
    sudokuPdfDoc.ejcritRejsolution(False, 1, 22, valeurs, verts)
    sudokuPdfDoc.ejcritRejsolution(False, 0, 22, valeurs, verts)
    sudokuPdfDoc.pdfGrilles()
    sudokuPdfDoc.ejcritTour('tour n° 1')
    sudokuPdfDoc.ejcritTitreTable('par mejthode n° 1')
    sudokuPdfDoc.dessineGrille(valeurs, verts, [(7,1)], [(6,8),(8,3),(5,5),(1,7),(3,2),(4,0)], [((5,5),8),((8,3),1)], [((1,7),2),((5,5),8),((4,0),5)], [((1,7),8),((7,1),3)])
    sudokuPdfDoc.ejcritTitreTable('par mejthode n° 2')
    sudokuPdfDoc.dessineGrille(valeurs, verts, [(7,1)], [(6,8),(8,3),(5,5),(1,7),(3,2),(4,0)], [((5,5),8),((8,3),1)], [((1,7),2),((5,5),8),((4,0),5)], [((1,7),8),((7,1),3)])
    sudokuPdfDoc.pdfGrilles()
    sudokuPdfDoc.ejcritExplicationsColoration()
    sudokuPdfDoc.ejcritTitreTable('coloration n° 1')
    sudokuPdfDoc.dessineGrille(valeurs, verts, [(7,1)], [(6,8),(8,3),(5,5),(1,7),(3,2),(4,0)], [((5,5),8),((8,3),1)], [((1,7),2),((5,5),8),((4,0),5)], [((1,7),8),((7,1),3)])
    sudokuPdfDoc.pdfGrilles()
    sudokuPdfDoc.ejcritExplicationsCarambolage()
    sudokuPdfDoc.ejcritTitreTable('carambolage n° 1')
    sudokuPdfDoc.dessineGrille(valeurs, verts, [(7,1)], [(6,8),(8,3),(5,5),(1,7),(3,2),(4,0)], [((5,5),8),((8,3),1)], [((1,7),2),((5,5),8),((4,0),5)], [((1,7),8),((7,1),3)])
    sudokuPdfDoc.ejcritTitreTable('carambolage n° 2')
    sudokuPdfDoc.dessineGrille(valeurs, verts, [(7,1)], [(6,8),(8,3),(5,5),(1,7),(3,2),(4,0)], [((5,5),8),((8,3),1)], [((1,7),2),((5,5),8),((4,0),5)], [((1,7),8),((7,1),3)])
    # teste couleur 
    sudokuPdfDoc.pdfGrilles()
    sudokuPdfDoc.testeCouleur()
    sudokuPdfDoc.termine()
    
#il y a 3 niveaux de tables imbriquejes pour donner la solution du problehme de sudoku
# 1) le plus bas : une table qui reprejsente une grille de sudoku
# 2) intermejdiaire : une table qui regroupe les grilles et leur titre et les prejsente en ligne (1, 2 ou 3 par ligne)
# 3) le plus haut : le regroupement des lignes de grilles et du numejro de tour. C'est pour controsler les sauts de page 
class SudokuPdfDoc:
    def __init__(self):
        return
    
    def init(self, nomFichierSortie, identifiant):
        #self.styles = getSampleStyleSheet()
        self.tousLesStyles()
        self.identifiant = identifiant
        self.numeroPage = 0
        self.doc = BaseDocTemplate(nomFichierSortie, pagesize=A4)
        framePremiehrePage = Frame(M_G, M_B, A4[0] -M_G -M_D, A4[1] -M_H -M_B -3*cm, id='framePremiehrePage')
        templatePremiehrePage = PageTemplate(id='PremiehrePage', frames=framePremiehrePage, onPage=self.enTestePremiehrePage)
        framePageSuivante = Frame(M_G, M_B, A4[0] -M_G -M_D, A4[1] -M_H -M_B -1*cm, id='framePageSuivante')
        templatePageSuivante = PageTemplate(id='pageSuivante', frames=framePageSuivante, onPage=self.enTestePageSuivante)
        self.doc.addPageTemplates([templatePremiehrePage, templatePageSuivante])
        self.flowables = []
        self.grilles = []
        self.titreGrille = []
        self.tour = []
        self.insejcable = []
        #ejcrit le baratin du dejpart commun ah toutes les rejsolutions
        self.ejcritExplications()
        
    #############################################
    def tousLesStyles(self):
        self.explicationsStyle = ParagraphStyle('explications')
        self.explicationsStyle.fontName = 'Helvetica'
        self.explicationsStyle.fontSize = 9
        self.explicationsStyle.bulletFontName = 'Helvetica'
        self.explicationsStyle.bulletFontSize = 9
        self.explicationsStyle.bulletIndent = 0
        self.explicationsStyle.bulletOffsetY = 0
        self.explicationsStyle.alignment = 0         #alignement ah gauche
        self.explicationsStyle.leading = 10
        self.explicationsStyle.spaceBefore = 6
        self.explicationsStyle.spaceAfter = 6   
        self.explicationsStyle.firstLineIndent = 0
        self.explicationsStyle.leftIndent = 0
        
        self.explicationsStyleBullet = deepcopy(self.explicationsStyle)
        self.explicationsStyleBullet.leftIndent = 10
        
        self.tourStyle = ParagraphStyle('tour')
        self.tourStyle.fontName = 'Helvetica-Bold'
        self.tourStyle.fontSize = 9
        self.tourStyle.textColor = 'black'

    #############################################
    def enTestePremiehrePage(self, canvas, doc):
        self.numeroPage +=1
        canvas.saveState()
        imageLogo = '%s/echiquierLatejcon4T.png'%(path.dirname( __file__))
        latecon = Image(imageLogo, width=5.51*cm, height=2.00*cm)
        latecon.drawOn(canvas, 1*cm, A4[1]-(3*cm))
        doc.handle_nextPageTemplate('pageSuivante')
        basdepageStyle = ParagraphStyle('basdepage')
        basdepageStyle.fontName = 'Helvetica-Bold'
        basdepageStyle.fontSize = 7
        basdepageStyle.textColor = 'black'        
        basdepage = Paragraph('Sudoku anthropomorphique de la grille %s'%(self.identifiant), basdepageStyle)
        basdepage.wrap(doc.width, doc.bottomMargin)
        basdepage.drawOn(canvas, doc.leftMargin, 1*cm)
        canvas.restoreState()
        
    #############################################
    def enTestePageSuivante(self, canvas, doc):
        self.numeroPage +=1
        canvas.saveState()
        imageLogo = '%s/echiquierLatejcon5T.png'%(path.dirname( __file__))
        latecon = Image(imageLogo, width=1.48*cm, height=1*cm)
        latecon.drawOn(canvas, 1*cm, A4[1]-(2*cm))
        basdepageStyle = ParagraphStyle('basdepage')
        basdepageStyle.fontName = 'Helvetica-Bold'
        basdepageStyle.fontSize = 7
        basdepageStyle.textColor = 'black'        
        basdepage = Paragraph('Sudoku anthropomorphique de la grille %s'%(self.identifiant), basdepageStyle)
        numeropage = Paragraph('<para alignment="RIGHT">page %d</para>'%(self.numeroPage), basdepageStyle)
        tableStyle = [
            ('ALIGN', (0,0), (0,0), 'LEFT'),
            ('ALIGN', (1,0), (1,0), 'RIGHT')]
        #table = Table([[basdepage, numeropage]], (A4[0] -M_G -M_D)/2)
        table = Table([[basdepage, numeropage]])
        table.setStyle(tableStyle)
        table.wrap(doc.width, doc.bottomMargin)
        table.drawOn(canvas, doc.leftMargin, 1*cm)
        canvas.restoreState()
        
    #############################################
    def ejcritExplications(self):
        racine = '/'.join(path.dirname(path.abspath(sys.argv[0])).split('/')[:-2])
        dateAujourdhuiFrancsais = dateEnFrancsais(date.today().isoformat())
        self.flowables.append(Paragraph('''
        <font size=16><i><b>L'Atelier d'Ejpistejmologie Compulsive</b></i></font> 
        <font size=9> prejsente le %s une tentative de rejsolution d'une grille de sudoku 
        par le programme de sudoku anthropomorphique.</font>
        '''%(dateAujourdhuiFrancsais), self.explicationsStyle))
        self.flowables.append(Spacer(7, 7))     #7=16-9
        self.flowables.append(Paragraph('''
        Le sudoku anthropomorphique est un programme informatique sous licence GNU AGPL. 
        Comme son nom l'indique, il raisonne comme un compejtiteur humain. 
        Ce programme n'utilise, bien susr, aucun mejcanisme d'essais-erreurs et pour chaque valeur trouveje 
        ou chaque valeur ejcarteje, il explique la mejthode utiliseje.<br/> 
        Le but du programme n'est pas de trouver la solution en un minimum de tours, ni mesme de trouver
        la solution mais d'expliquer le plus clairement possible ce qu'il a trouvé et comment il l'a
        trouvé.<br/>
        Qui dira la tristesse que dejgage une grille de sudoku entiehrement complejteje sans la mejmoire
        de tous les raisonnements qui ont permis de la complejter ? Et sans la certitude absolue qu'une erreur
        involontaire ne nous prejcipite pas dans la multitude vile des malraisonneurs de bonne foi ? 
        (la probabilité de trouver la solution en malraisonnant est trehs ejleveje au sudoku, 
        de l'ordre de 0,5)
        ''', self.explicationsStyle))      
        self.flowables.append(Paragraph('''
        Voici les 4 mejthodes d'affectation utilisejes :
        ''', self.explicationsStyle))      
        self.flowables.append(Paragraph('''
        <bullet>&bull;</bullet><b><font color="green">par mejthode n° 1 (carrejs) </font>:</b> 
        Sachant qu'il n'y a qu'une 
        seule cellule possible pour une valeur donneje dans un carré donné, <b><i>pour chaque carré, il faut 
        trouver les valeurs qui ne peuvent avoir qu'une seule implantation possible</i></b>.
        <br/>Controsle : pour chaque cellule-valeur trouveje (en vert), il faut vejrifier qu'aucune autre 
        cellule libre du carré concerné ne peut recevoir cette valeur. 
        ''', self.explicationsStyleBullet))      
        self.flowables.append(Paragraph('''
        <bullet>&bull;</bullet><b><font color="green">par mejthode n° 2 (lignes) </font>:</b> Sachant qu'il
        n'y a qu'une 
        seule cellule possible pour une valeur donneje sur une ligne donneje, <b><i>pour chaque ligne, il faut 
        trouver les valeurs qui ne peuvent avoir qu'une seule implantation possible</i></b>.
        <br/>Controsle : pour chaque cellule-valeur trouveje (en vert), il faut vejrifier qu'aucune autre 
        cellule libre de la ligne concerneje ne peut recevoir cette valeur. 
        ''', self.explicationsStyleBullet))      
        self.flowables.append(Paragraph('''
        <bullet>&bull;</bullet><b><font color="green">par mejthode n° 3 (colonnes) </font>:</b> Sachant qu'il
        n'y a qu'une 
        seule cellule possible pour une valeur donneje dans une colonne donneje, <b><i>pour chaque colonne, il 
        faut trouver les valeurs qui ne peuvent avoir qu'une seule implantation possible</i></b>.
        <br/>Controsle : pour chaque cellule-valeur trouveje (en vert), il faut vejrifier 
        qu'aucune autre cellule libre de la colonne concerneje ne peut recevoir cette valeur. 
        ''', self.explicationsStyleBullet))      
        self.flowables.append(Paragraph('''
        <bullet>&bull;</bullet><b><font color="green">par mejthode n° 4 (uniques)</font>:</b> Sachant qu'il
        n'y a qu'une 
        seule valeur possible pour une cellule donneje, <b><i>pour l'ensemble de la grille, il faut trouver 
        les cellules qui ne peuvent avoir qu'une seule valeur possible</i></b>.
        <br/>Controsle : pour chaque cellule-valeur trouveje (en vert), il faut vejrifier 
        qu'aucune autre valeur ne peut estre affecteje ah la cellule concerneje. 
        ''', self.explicationsStyleBullet))      
        self.flowables.append(Paragraph('''
        <para backColor="lightgreen">Les nouvelles cellules-valeurs apparaissent sur fond vert.</para>
        ''', self.explicationsStyle))      
        self.flowables.append(Paragraph('''
        Les nouvelles cellules-valeurs ne peuvent être affectejes que par une ou plusieurs des 
        quatre mejthodes.
        <br/>Un tour est achevé si au moins une nouvelle valeur a ejté affecteje à une cellule 
        prejcejdemment vide. 
        <br/>Si aucune nouvelle cellule-valeur n'a ejté trouveje, des mejthodes pour ejliminer des 
        cellules-valeurs candidates sont appliquejes. 
        Si au moins une cellule-valeur candidate a ejté ejlimineje, les quatre mejthodes
        d'affectation sont à nouveau appliquejes. Et ce, itejrativement, jusqu'à la fin du tour 
        ou l'ejchec de la rejsolution.
        ''', self.explicationsStyle))      
        self.flowables.append(Paragraph('''
        <bullet>&bull;</bullet><b><font color="green">cellules-valeurs possibles </font>:
        </b> Pour chaque cellule non affecteje, est afficheje la liste des valeurs possibles 
        en fonction des contraintes induites par les cellules-valeurs dejjà affectejes et dejjah ejliminejes.        
        ''', self.explicationsStyleBullet))  
        self.flowables.append(Paragraph('''
        <para backColor="lightcyan">Les cellules-valeurs possibles apparaissent sur fond bleu.</para>
        ''', self.explicationsStyle))      
        self.flowables.append(Paragraph('''
        Voici les deux mejthodes d'ejlimination :
        ''', self.explicationsStyle))      
        self.flowables.append(Paragraph('''
        <bullet>&bull;</bullet><b><font color="green">groupe n-n </font>:</b> Il arrive que certaines 
        cellules d'un espace de contrainte donné (carré, ligne ou colonne) ont les mesmes valeurs possibles.
        Si le nombre de cellules est ejgal au nombre de valeurs, elles sont appelejes groupes n-n
        et gejnehrent des contraintes supplejmentaires : 
        les cellules d'un groupe n-n ne peuvent avoir d'autres valeurs et les valeurs ne peuvent estre 
        affectejes à d'autres cellules que les cellules du groupe n-n.
        Les cellules-valeurs superfejtatoires sont ejliminejes.
        <br/>Il y a 2 façons de dejtecter les groupes n-n : 
        <br/>1. trouver les cellules d'un espace de 
        contrainte qui admettent les mesmes valeurs, 
        <br/>2. trouver les valeurs qui ne peuvent estre affectejes
        que sur certaines cellules d'un espace de contrainte.
        <br/>Pour des raisons pejdagogiques, le sudoku anthropomorphique ne prejsente que les groupes n-n
        de plus faible n qui gejnehrent chacun au moins une ejlimination de cellule-valeur potentielle.
        ''', self.explicationsStyleBullet))    
        self.flowables.append(Paragraph('''
        <bullet>&bull;</bullet><b><font color="green">alignement dans carré </font>:</b> Il arrive que toutes
        les cellules d'un carré qui sont candidates à une valeur donneje sont alignejes, c'est à dire 
        qu'elles appartiennent aussi à une mesme ligne ou une mesme colonne. Les cellules de la ligne ou la
        colonne hors le carré ne peuvent avoir cette valeur.
        <br/>De mesme toutes les cellules d'une ligne
        ou d'une colonne qui sont candidates à une valeur donneje peuvent appartenir à un mesme carré. 
        Les cellules du carré hors la ligne ou la colonne ne peuvent avoir cette valeur.
        <br/>Ce sont les valeurs alignejes dans un carré et les cellules-valeurs superfejtatoires sont
        ejliminejes.
        ''', self.explicationsStyleBullet))            
        self.flowables.append(Paragraph('''
        En cas d'ejchec, la rejsolution est dejclareje en ejchec simple et les méjthodes d'ejlimination
        par coloration sont activejes. Elles seront expliquejes si besoin.
        ''', self.explicationsStyle))      
        self.flowables.append(Paragraph('''
        Pour plus d'explications, consultez la documentation fonctionnelle <b><i>Le sudoku anthropomorphique, inutile et rigolo</i></b>, LAT2019.JYS.R477 revA.
        <br/>Et pour l'ejtrange graphie, lisez <b><i>La dejsaccentuation, quasi-piehce de thejastre</i></b>
        de Ivo Amigo, personnage chroniqueur.<br/><br/>
        ''', self.explicationsStyle))      
             
    #############################################
    def ejcritExplicationsColoration(self):
        # commence par afficher les grilles en attente
        self.pdfGrilles()
        self.flowables.append(Paragraph('''
        Là, les deux mejthodes historiques d'ejlimination sont inopejrandes. L'ejchec partiel est
        donc proclamé.<br/><br/>
        Il faut maintenant activer les mejthodes d'ejlimination de coloration trouvejes dans le
        livre de Bernard Borrelly <b><i>SU-DOKU, le coloriage virtuel</i></b>.
        <br/>La mejthode consiste à identifier les couples de cellules-valeurs en lien d'exclusion mutuelle,
        c'est à dire que si l'une est vraie, l'autre est fausse et réciproquement. C'est ce que le livre 
        nomme les liens forts et que les matheux appellent les disjonctions exclusives. 
        Les liens forts apparaissent dans deux cas :
        <br/>1. quand une mesme cellule a deux valeurs possibles et deux seulement. 
        <br/>2. quand une mesme valeur n'est possible que sur deux cellules d'un espace de contraintes (carré, ligne ou colonne) et deux seulement. 
        <br/>Voici les deux mejthodes supplejmentaires d'ejlimination :
        ''', self.explicationsStyle))
        self.flowables.append(Paragraph('''
        <bullet>&bull;</bullet><b><font color="green">par rejseau gejnejrique </font>:</b> 
        Les liens forts qui ont une cellule-valeur en commun
        sont regroupejs par proximité dans une mesme structure, le rejseau gejnejrique
        composé de deux chaisnes de 
        cellules-valeurs en exclusion mutuelle et coloriejes arbitrairement, l'une en rouge et 
        l'autre en bleu.
        <br/>Une cellule-valeur est ejlimineje par un rejseau gejnejrique si elle se trouve interdite par 
        une cellule-valeur rouge et par une cellule-valeur bleue du mesme rejseau gejnejrique. 
        Elle est, par dejfinition extejrieure, exogehne au rejseau gejnejrique actionné.
        ''', self.explicationsStyleBullet))      
        self.flowables.append(Paragraph('''
        <bullet>&bull;</bullet><b><font color="green">par rejseau virtuel </font>:</b> 
        Lorsque la mejthode d'ejlimination de cellules-valeurs par les rejseaux gejnejriques a ejchoué,
        les rejseaux gejnejriques sont prolongejs en rejseaux virtuels.
        Pour chaque rejseau gejnejrique, chacune de ses deux couleurs est examineje.
        Tout se passe "comme si" la couleur examineje ejtait vraie et les 4 mejthodes d'affectation 
        sont activejes pour trouver les nouvelles cellules-valeurs qui seraient affectejes dans cette
        hypothèse. Des cellules-valeurs virtuelles rouges et des cellules-valeurs 
        virtuelles bleues sont ainsi obtenues. Le rejseau ainsi ejtendu est appelé rejseau virtuel. Il a les
        mesmes propriejtejs d'ejlimination des cellules-valeurs exogehnes que le rejseau genejrique.
        <br/>Les rejseaux virtuels sont prolongejs itejrativement tant que de nouvelles cellules-valeurs 
        virtuelles sont trouvejes par les 4 mejthodes d'affectation. L'itejration s'arreste quand au moins
        une cellule-valeur exogehne peut estre ejlimineje. La profondeur du calcul est indiqueje. 
        ''', self.explicationsStyleBullet))      
        
    #############################################
    def ejcritExplicationsCarambolage(self):
        # commence par afficher les grilles en attente
        self.pdfGrilles()
        self.flowables.append(Paragraph('''
        Là, les deux mejthodes supplejmentaires sont inopejrandes pour ejliminer des cellules-valeurs 
        exogehnes. Les rejseaux gejnejriques et virtuels peuvent prejsenter des impossibilejs sur une
        de leurs deux couleurs. On dit qu'il y a carambolage.
        <br/>En vertu de la doctrine du sudoku anthropomorphique : 
        <b><i>L'essai-erreur est formellement interdit</i></b> et sa dejclinaison pour les
        rejseaux gejnejriques et virtuels : 
        <b><i>Les constructions spejculatives ne peuvent servir qu'à ejliminer des cellules-valeurs 
        exogehnes et en aucun cas des cellules-valeurs endogehnes car ce serait alors considejré comme 
        de l'essai-erreur</i></b>, les rejseaux carambolejs sont affichejs et l'ejchec dejfinitif est
        proclamé.
        ''', self.explicationsStyle))
        self.flowables.append(Paragraph('''
        <bullet>&bull;</bullet><b><font color="green">rejseau gejnejrique carambolé</font>:</b> 
        Si le regroupement des liens forts conduit à avoir deux valeurs de mesme couleur dans une
        mesme cellule, le rejseau est dejclaré carambolé. La couleur fautive est symboliquement barreje.
        ''', self.explicationsStyleBullet))      
        self.flowables.append(Paragraph('''
        <bullet>&bull;</bullet><b><font color="green">rejseau virtuel carambolé</font>:</b> 
        Si l'extension du rejseau virtuel conduit à avoir deux valeurs de mesme couleur dans une
        mesme cellule, le rejseau est dejclaré carambolé. La couleur fautive du rejseau genejrique
        d'origine est symboliquement barreje.
        ''', self.explicationsStyleBullet))      
        
    #############################################
    def ejcritEjchec(self):
        # commence par afficher les grilles en attente
        self.pdfGrilles()
        self.flowables.append(Paragraph('''
        <i><b>L'Atelier d'Ejpistejmologie Compulsive</b></i> conclut à l'ejchec du programme de sudoku 
        anthropomorphique dans la rejsolution de la grille proposeje.
        <br/>C'est normal qu'un programme qui n'a droit ni à la statistique, ni aux essais-erreurs ne soit
        pas plus malin que son concepteur. Il va simplement au bout de ses possibilitejs... plus vite.
        <br/><b>Donc tout est normal</b> et, tout bien considejré, c'est normal que tout soit normal...
        ejpistejmologiquement parlant...
        ''', self.explicationsStyle))

    #############################################
    def grilleStyle(self):
        return [
            ('BOX', (0,0), (8,8), 1, colors.black),
            ('BOX', (0,0), (2,2), 1, colors.black),
            ('BOX', (0,3), (2,5), 1, colors.black),
            ('BOX', (0,6), (2,8), 1, colors.black),
            ('BOX', (3,0), (5,2), 1, colors.black),
            ('BOX', (3,3), (5,5), 1, colors.black),
            ('BOX', (3,6), (5,8), 1, colors.black),
            ('BOX', (6,0), (8,2), 1, colors.black),
            ('BOX', (6,3), (8,5), 1, colors.black),
            ('BOX', (6,6), (8,8), 1, colors.black),
            ('INNERGRID', (0,0), (8,8), 0.1, colors.black),
            ('TEXTFONT', (0,0), (-1,-1), 'Times-Bold'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE')]
    
    #############################################
    def ejcritRejsolution(self, tropDeSolutions, nbRejsolutions, nbCellulesOccupees, valeurs, verts):
        # commence par afficher les grilles en attente
        self.pdfGrilles()
        miniGrilleStyle = self.grilleStyle()
        miniGrilleStyle.extend([
            ('FONTSIZE', (0,0), (-1,-1), 7),
            ('TOPPADDING', (0,0), (-1,-1), 4)])
        texte = '''
        Un programme qui n'est pas du tout anthropomorphique celui-là, a rejsolu prejventivement 
        la grille proposeje...
        <br/>qui a %d cellules dejjah affectejes...       
        <br/>'''%(nbCellulesOccupees)
        if nbRejsolutions == 0: texte += """<b>Cette grille n'a aucune solution !! </b>
            <br/>Le sudoku anthropomorphique n'en trouvera donc pas...
            """
        elif tropDeSolutions: texte += """<b>Cette grille a plus de %d solutions !!</b>
            <br/>Le sudoku anthropomorphique n'en trouvera donc pas parce qu'il ne sait pas faire de choix...
            """%(nbRejsolutions)
        elif nbRejsolutions == 1: texte += """<b>Cette grille a une solution et une seule ! </b>
            <br/>Le sudoku anthropomorphique va faire ce qu'il peut pour la trouver...
            """
        else: texte += """<b>Cette grille a %d solutions ! </b>
            <br/>Le sudoku anthropomorphique n'en trouvera donc pas parce qu'il ne sait pas faire de choix...
            """%(nbRejsolutions)
        if nbRejsolutions == 1:
            grilleValeurs = [['' for i in range(9)] for i in range(9)] 
            for (x, y), valeur in  valeurs: grilleValeurs[x][y] = str(valeur)
            for x, y in verts: miniGrilleStyle.append(('BACKGROUND', (y, x), (y, x), colors.lightgreen))
            #cree la table avec les valeurs et la taille de chaque cellule
            grille = Table(grilleValeurs, C_CEL2, C_CEL2)
            grille.setStyle(miniGrilleStyle)
            table = Table([[Paragraph(texte, self.explicationsStyle), grille]], [14.2*cm, C_TAB2 + 2*C_CEL2])
            table.setStyle([
                #('INNERGRID', (0,0), (-1,-1), 0.1, colors.black), 
                #('BOX', (0,0), (-1,-1), 0.1, colors.black), 
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'), 
                ('VALIGN', (0,0), (-1,-1), 'TOP')])
            table.hAlign = "LEFT"
            self.flowables.append(KeepTogether(table))
        else:
            self.flowables.append(KeepTogether(Paragraph(texte, self.explicationsStyle)))

    #############################################
    def ejcritTour(self, texte):
        self.insejcable.append([Paragraph(texte, self.tourStyle)])
        
    #############################################
    def ejcritRejsultat(self, nbAffectations, nbTours):
        texte = 'rejsultat : <font name="Helvetica">%d affectation'%(nbAffectations)
        if nbAffectations > 1: texte += 's'
        texte += ' en %d tour'%(nbTours)
        if nbTours > 1: texte += 's'
        texte += '</font>'
        rejsultat = Paragraph(texte, self.tourStyle)
        self.insejcable.append([rejsultat])
        
    #############################################
    def ejcritTitreTable(self, texte):
        titreGrilleStyle = ParagraphStyle('titreGrille')
        titreGrilleStyle.fontName = 'Helvetica-Bold'
        titreGrilleStyle.fontSize = 9
        titreGrilleStyle.textColor = 'green'
        titreGrilleStyle.alignment = 2  #alignement ah droite
        self.titreGrille = Paragraph(texte, titreGrilleStyle)
        
    #############################################
    # dessine une grille
    def dessineGrille(self, valeurs, verts, erreurs, possibles, barrejs = [], jaunes = [], rouges = [], bleus = [], rougesclairs = [], bleusclairs = []):
        #si la ligne de grilles a dejjah 3 grilles, passe ah la ligne
        if len(self.grilles) == 3: self.pdfGrilles()
        #cree le quadrillage du sudoku
        grilleStyle = self.grilleStyle()
        grilleStyle.extend([
            ('FONTSIZE', (0,0), (-1,-1), 11),
            ('TOPPADDING', (0,0), (-1,-1), 0)])
        for x, y in verts: 
            grilleStyle.append(('TEXTCOLOR', (y, x), (y, x), colors.black))
            grilleStyle.append(('BACKGROUND', (y, x), (y, x), colors.lightgreen))
        for x, y in erreurs: 
            grilleStyle.append(('BACKGROUND', (y, x), (y, x), colors.red))
        if len(barrejs) + len(jaunes) + len(rouges) + len(bleus) == 0:
            for x, y in possibles: 
                grilleStyle.append(('BACKGROUND', (y, x), (y, x), colors.lightcyan))
        for ((x, y), valeur) in barrejs:
            grilleStyle.append(('BACKGROUND', (y, x), (y, x), colors.lightgoldenrodyellow))
        for ((x, y), valeur) in jaunes:
            grilleStyle.append(('BACKGROUND', (y, x), (y, x), colors.lightgoldenrodyellow))
        for ((x, y), valeur) in rouges:
            grilleStyle.append(('BACKGROUND', (y, x), (y, x), colors.lightgoldenrodyellow))
        for ((x, y), valeur) in bleus:
            grilleStyle.append(('BACKGROUND', (y, x), (y, x), colors.lightgoldenrodyellow))
        for ((x, y), valeur) in rougesclairs:
            grilleStyle.append(('BACKGROUND', (y, x), (y, x), colors.lightgoldenrodyellow))
        for ((x, y), valeur) in bleusclairs:
            grilleStyle.append(('BACKGROUND', (y, x), (y, x), colors.lightgoldenrodyellow))
        # creje le dico des valeurs 
        valeursDic = {}
        for (x, y), valeur in  valeurs: 
            if (x, y) not in valeursDic: valeursDic[(x, y)] = []
            valeursDic[(x, y)].append(valeur)
        # creje les diffejerents styles
        uniqueStyle = ParagraphStyle('unique')
        uniqueStyle.fontName = 'Helvetica'
        uniqueStyle.alignment = enums.TA_CENTER
        uniqueStyle.fontSize = 11
        erreurStyle = ParagraphStyle('erreur')
        erreurStyle.fontName = 'Helvetica'
        erreurStyle.alignment = enums.TA_CENTER
        erreurStyle.fontSize = 9
        multipleStyle = ParagraphStyle('multiple')
        multipleStyle.fontName = 'Helvetica'
        multipleStyle.alignment = enums.TA_CENTER
        multipleStyle.leading = 7
        multipleStyle.fontSize = 6
        # creje la valeur sous forme d'une matrice 9x9, l'initialise ah vide
        grilleValeurs = [['' for i in range(9)] for i in range(9)] 
        # et la remplit avec les valeurs et leur format
        for (x, y), listeValeurs in valeursDic.items():
            listeValeurs.sort()
            listeAffichages = []
            for valeur in listeValeurs:
                #if ((x, y), valeur) in barrejs: listeAffichages.append('<span bgcolor=lightcoral style=strike>' + str(valeur) + '</span>')
                fait = False
                if ((x, y), valeur) in barrejs: valeurStr = '<strike>' + str(valeur) + '</strike>'
                else: valeurStr = str(valeur)
                    #listeAffichages.append('<strike>' + str(valeur) + '</strike>')
                    #fait = True
                if ((x, y), valeur) in jaunes: 
                    listeAffichages.append('<span bgcolor=darkolivegreen textcolor=white>' + valeurStr + '</span>')
                    fait = True
                if ((x, y), valeur) in rouges: 
                    listeAffichages.append('<span bgcolor=red textcolor=white>' + valeurStr + '</span>')
                    fait = True
                if ((x, y), valeur) in bleus: 
                    listeAffichages.append('<span bgcolor=blue textcolor=white>' + valeurStr + '</span>')
                    fait = True
                if ((x, y), valeur) in rougesclairs: 
                    listeAffichages.append('<span bgcolor=lightpink>' + valeurStr + '</span>')
                    fait = True
                if ((x, y), valeur) in bleusclairs: 
                    listeAffichages.append('<span bgcolor=lightskyblue>' + valeurStr + '</span>')
                    fait = True
                if not fait: listeAffichages.append(valeurStr)
            if (x, y) in possibles:  
                if len(listeAffichages) < 6: sep = 2
                else: sep = 3
                grilleValeurs[x][y] = Paragraph(','.join(listeAffichages[:sep]) + '<br/>' + ','.join(listeAffichages[sep:]), multipleStyle)
            elif (x,y) in erreurs:
                grilleValeurs[x][y] = Paragraph(','.join(listeAffichages), erreurStyle)
            else : grilleValeurs[x][y] = Paragraph(','.join(listeAffichages), uniqueStyle)
        #cree la table avec les valeurs et la taille de chaque cellule
        grille = Table(grilleValeurs, C_CEL, C_CEL)
        grille.setStyle(grilleStyle)
        self.grilles.append((self.titreGrille, grille))
        self.titreGrille = []
        
    #############################################
    # passe les grilles en attente dans le PDF
    def pdfGrilles(self):
        if len(self.grilles) == 0: return
        #cree la table des grilles avec leur titre pour que les grilles soient sur la mesme ligne
        tableStyle = [
            ('ALIGN', (0,0), (-1,-1), 'RIGHT')]
        ligneTitres = []
        ligneGrilles = []
        for (titreGrille, grille) in self.grilles:
            ligneTitres.append(titreGrille)
            ligneGrilles.append(grille)
        self.grilles.clear()
        table = Table([ligneTitres, ligneGrilles], C_TAB + 2* C_CEL)
        table.setStyle(tableStyle)
        table.hAlign = "LEFT"
        self.insejcable.append([table])
        self.pdfInsejcable()
        
    #############################################
    # passe les attentes dans le PDF
    def pdfInsejcable(self):
        # si le titre est dans l'affichage, insehre un peu d'espace
        if len(self.insejcable) > 1: self.flowables.append(Spacer(C_CEL, C_CEL))
        table = Table(self.insejcable)
        table.hAlign = "LEFT"
        self.flowables.append(KeepTogether(table))
        self.insejcable.clear()
                 
    #############################################
    def termine(self):
        self.doc.build(self.flowables)
        
    #############################################
    def testeCouleur(self):
        multipleStyle = ParagraphStyle('multiple')
        multipleStyle.fontName = 'Helvetica'
        multipleStyle.alignment = enums.TA_CENTER
        multipleStyle.leading = 7
        multipleStyle.fontSize = 6
        texte = ''
        couleurs = ['ReportLabBlue', 'ReportLabBlueOLD', 'ReportLabBluePCMYK', 'ReportLabFidBlue', 'ReportLabFidRed', 'ReportLabGreen', 'ReportLabLightBlue', 'ReportLabLightGreen', '_CMYK_black', '_CMYK_white', '_PCMYK_black', '_PCMYK_white', 'aliceblue', 'antiquewhite', 'aqua', 'aquamarine', 'azure', 'beige', 'bisque', 'black', 'blanchedalmond', 'blue', 'blueviolet', 'brown', 'burlywood', 'cadetblue', 'chartreuse', 'chocolate', 'coral', 'cornflower', 'cornflowerblue', 'cornsilk', 'crimson', 'cyan', 'darkblue', 'darkcyan', 'darkgoldenrod', 'darkgray', 'darkgreen', 'darkgrey', 'darkkhaki', 'darkmagenta', 'darkolivegreen', 'darkorange', 'darkorchid', 'darkred', 'darksalmon', 'darkseagreen', 'darkslateblue', 'darkslategray', 'darkslategrey', 'darkturquoise', 'darkviolet', 'deeppink', 'deepskyblue', 'dimgray', 'dimgrey', 'dodgerblue', 'fidblue', 'fidlightblue', 'fidred', 'firebrick', 'floralwhite', 'forestgreen', 'fuchsia', 'gainsboro', 'ghostwhite', 'gold', 'goldenrod', 'gray', 'green', 'greenyellow', 'grey', 'honeydew', 'hotpink', 'indianred', 'indigo', 'isPy3', 'ivory', 'khaki', 'lavender', 'lavenderblush', 'lawngreen', 'lemonchiffon', 'lightblue', 'lightcoral', 'lightcyan', 'lightgoldenrodyellow', 'lightgreen', 'lightgrey', 'lightpink', 'lightsalmon', 'lightseagreen', 'lightskyblue', 'lightslategray', 'lightslategrey', 'lightsteelblue', 'lightyellow', 'lime', 'limegreen', 'linen', 'magenta', 'maroon', 'mediumaquamarine', 'mediumblue', 'mediumorchid', 'mediumpurple', 'mediumseagreen', 'mediumslateblue', 'mediumspringgreen', 'mediumturquoise', 'mediumvioletred', 'midnightblue', 'mintcream', 'mistyrose', 'moccasin', 'navajowhite', 'navy', 'oldlace', 'olive', 'olivedrab', 'orange', 'orangered', 'orchid', 'palegoldenrod', 'palegreen', 'paleturquoise', 'palevioletred', 'papayawhip', 'peachpuff', 'peru', 'pink', 'plum', 'powderblue', 'purple', 'red', 'rosybrown', 'royalblue', 'saddlebrown', 'salmon', 'sandybrown', 'seagreen', 'seashell', 'sienna', 'silver', 'skyblue', 'slateblue', 'slategray', 'slategrey', 'snow', 'springgreen', 'steelblue', 'tan', 'teal', 'thistle', 'tomato', 'transparent', 'turquoise', 'violet', 'wheat', 'white', 'whitesmoke', 'yellow', 'yellowgreen']
        for couleur in couleurs:
            texte += '%s : <span bgcolor=%s>123456789</span>   '%(couleur, couleur)
            texte += '%s : <span bgcolor=%s textcolor=white>123456789</span>   '%(couleur, couleur)
        self.flowables.append(Paragraph(texte, multipleStyle))
        

        
#############################################
#convertit une date en Francsais
def dateEnFrancsais(isodate):
    # aaaa-mm-jj
    mois = [u'', u'janvier', u'fejvrier', u'mars', u'avril', u'mai', u'juin', u'juillet', u'aoust', u'septembre', u'octobre', u'novembre', u'dejcembre']
    isodateList = isodate.split('-')
    return '%s %s %s'%(str(int(isodateList[2])), mois[int(isodateList[1])], isodateList[0])  

        
if __name__ == '__main__':
    main()
