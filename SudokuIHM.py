#!/usr/bin/env python3
# -*- coding: utf-8 -*-
 
import sys
from os import path
import socket
import urllib
import re
import cgi
import subprocess
from time import ctime
import base64
import traceback
from Sudoku import Sudoku

HOST = ''
PORT = 8582
IMAGE = "echiquierLatejcon4-200T.png"

def usage():
    script = path.basename(sys.argv[0])
    print ("""© l'ATEJCON.
Serveur http de sudoku anthropomorphique.
Il démarre en localhost et attend sur le port {}
En mode 'local', le client démarre automatiquement sur Firefox.
En mode 'distant', le client se connecte par un navigateur à l'adresse :
http://192.168.1.25:{} ou http://localhost:{} 
Le client a été testé avec succès sur Firefox 70.0.

usage   : {} <LOCAL | DISTANT> 
exemple : {} local
""".format(PORT, PORT, PORT, script, script))
    
def main():
    try:
        if len(sys.argv) < 2 : raise Exception()
        localDistant = sys.argv[1].lower()
        if localDistant.startswith('loc'): local = True
        elif localDistant.startswith('dis'): local = False
        else: raise Exception('INCONNU : {}'.format(sys.argv[1]))
        ServeurHtml(local)
    except Exception as exc:
        if len(exc.args) == 0: usage()
        else:
            print ("******************************")
            traceback.print_exc()
            print ("******************************")
        sys.exit()
        
class ServeurHtml():
    def __init__(self, local):
        self.ejnoncej = ''
        # init la socket
        c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        c.bind((HOST, PORT))
        print ('attend sur le port {}'.format(PORT))
        # 1 seul client a la fois, ca permet d'utiliser la socket de connexion pour la reponse
        c.listen(1)  
        # si local, lance le client firefox
        if local: subprocess.run(['firefox', 'http://localhost:{}'.format(PORT)])
        # attend l'utilisateur et ce, indefiniment
        while True:
            try:
                csock, caddr = c.accept() 
                #print('----------------------\nServeurHtml travaille')
                donnejesRecues = urllib.parse.unquote_plus(csock.recv(4096).decode('utf-8'))
                #repond au client que tout va bien
                csock.send(b'HTTP/1.0 200 OK\n\n') 
                #print(donnejesRecues)
                # GET / HTTP/1.1 = 1ehre fois
                if 'GET / HTTP/1.1' in donnejesRecues:
                    print('Première fois')
                    self.afficheSaisieGrille(csock)
                # POST /saisie-cc HTTP/1.1
                elif 'POST /saisie-cc HTTP/1.1' in donnejesRecues:
                    print('saisie-cc')
                    self.traiteCopierColler(csock, donnejesRecues)
                # POST /saisie-grille HTTP/1.1
                elif 'POST /saisie-grille HTTP/1.1' in donnejesRecues:
                    print('saisie-grille')
                    self.traiteSaisieGrille(csock, donnejesRecues)
                elif 'POST /calcul-sudoku HTTP/1.1' in donnejesRecues:
                     print('calcul-sudoku')
                     self.traiteCalculSudoku(csock)
                else: print("PUTAIN C'EST QUOI ?")
                csock.close()  
                #print('----------------------')
            except Exception as exc:
                if not exc.args == (32, 'Broken pipe'): raise
                print (exc.args)

    ###################################
    def afficheSaisieGrille(self, csock):
        self.afficheEnTeste(csock)
        self.afficheTitreEtSaisie(csock)
        self.afficheRejsultatVide(csock)
        self.afficheQueue(csock)
        
    ###################################
    def traiteCopierColler(self, csock, donnejesRecues):
        self.ejnoncej = ''
        # copiercoller=003104800,000000000,400508001,790060048,080473090,530010027,800302004,000000000,002701500
        match = re.search('copiercoller=(.*)', donnejesRecues)
        if match: 
            for caractehre in match.group(1):
                if caractehre in ('1','2','3','4','5','6','7','8','9'): self.ejnoncej += caractehre
                elif caractehre in ('0',' ','.'): self.ejnoncej += '.'
                # max 81 + 8 virgules
                if len(self.ejnoncej) == 89: break
                # insertion barre sejparation
                if len(self.ejnoncej) %10 == 9: self.ejnoncej += '|'
        else: print('saisie-cc INCONNU')
        self.afficheSaisieGrille(csock)
      
    ###################################
    def traiteSaisieGrille(self, csock, donnejesRecues):
        self.ejnoncej = ''
        # 11=3&12=1&13=&...&98=&99=&raz=raz
        if 'raz=raz' in donnejesRecues: 
            self.afficheSaisieGrille(csock)
            return
        # 11=3&12=1&13=&...&98=&99=&soumettre=soumettre
        match = re.search('(11=.*)&soumettre=soumettre', donnejesRecues)
        if not match: 
            print('saisie-grille INCONNU')
            self.afficheSaisieGrille(csock)
            return
        for affectation in match.group(1).split('&'):
            # 12=1 ou 13=
            valeur = affectation.split('=')[1]
            if valeur == '': self.ejnoncej += '.'
            else: self.ejnoncej += valeur
            # max 81 + 8 virgules
            if len(self.ejnoncej) == 89: break
            # insertion barre sejparation
            if len(self.ejnoncej) %10 == 9: self.ejnoncej += '|'
        if len(self.ejnoncej) != 89: 
            print('saisie-grille ERRONNÉE ({})'.format(len(self.ejnoncej)))
            self.afficheSaisieGrille(csock)
            return
        # affiche
        self.afficheEnTeste(csock)
        self.afficheTitreEtSaisie(csock)
        self.afficheValeursPossibles(csock)
        self.afficheQueue(csock)
       
    ###################################
    def traiteCalculSudoku(self, csock):
        # affiche
        self.afficheEnTeste(csock)
        self.afficheTitreEtSaisie(csock)
        self.afficheRejsultatVide(csock)
        self.afficheCalculPdf(csock)
        self.afficheQueue(csock)
        
    ###################################
    def afficheCalculPdf(self, csock):
        #le rejpertoire courant pour y foutre le pdf
        rejpertoire = path.abspath(path.curdir)
        succehs, nbAffectations, tour, nomFichierSortie = self.sudoku.resoudSudoku(rejpertoire)
        if succehs:
            csock.sendall("<p>SUCCÈS !".encode('utf-8'))
        else:
            csock.sendall("<p>ÉCHEC !".encode('utf-8'))
        csock.sendall((
            """ Le sudoku anthropomorphique a affecté {} valeurs en {} tours</br>
            Le résultat est consultable sur {}<p>
            """.format(nbAffectations, tour, nomFichierSortie)).encode('utf-8'))
        fichier = path.basename(nomFichierSortie)
        csock.sendall(('<a href="{}" target="_blank"></a>'.format(fichier)).encode('utf-8'))
      
    ###################################
    def afficheValeursPossibles(self, csock):
        # avec le programme de calcul maintenant
        lignes = self.ejnoncej.replace('|', ',')
        lignes = lignes.replace('.', '0')
        self.sudoku = Sudoku(lignes)
        lesInvalides = self.sudoku.cellulesInvalides()
        lesValeurs, lesPossibles = self.sudoku.valeurs()
        correspondance = [
            11, 12, 13, 21, 22, 23, 31, 32, 33, 
            14, 15, 16, 24, 25, 26, 34, 35, 36, 
            17, 18, 19, 27, 28, 29, 37, 38, 39,
            41, 42, 43, 51, 52, 53, 61, 62, 63,
            44, 45, 46, 54, 55, 56, 64, 65, 66,
            47, 48, 49, 57, 58, 59, 67, 68, 69,
            71, 72, 73, 81, 82, 83, 91, 92, 93,
            74, 75, 76, 84, 85, 86, 94, 95, 96,
            77, 78, 79, 87, 88, 89, 97, 98, 99]
        csock.sendall('<table class="tableRejultat">'.encode('utf-8'))
        nbCase = 0
        for lig in range(1, 4):
            csock.sendall('<tr>'.encode('utf-8'))
            for col in range(1, 4):
                csock.sendall('<td><table class="tableCarrej">'.encode('utf-8'))
                for lig2 in range(1, 4):
                    csock.sendall('<tr>'.encode('utf-8'))
                    for col2 in range(1, 4):
                        cellule = correspondance[nbCase]
                        nbCase +=1
                        csock.sendall('<td class="tdRej'.encode('utf-8'))
                        if cellule in lesValeurs:
                            if cellule in lesInvalides:
                                csock.sendall(' tdErr">'.encode('utf-8'))
                            else:
                                csock.sendall(' tdSim">'.encode('utf-8'))
                            csock.sendall(('{}</td>'.format(lesValeurs[cellule])).encode('utf-8'))
                        else:
                            valeurs = [str(elem) for elem in lesPossibles[cellule]]
                            valeurs.sort()
                            if len(valeurs) > 7: csock.sendall(' tdMu2">'.encode('utf-8'))
                            else: csock.sendall(' tdMul">'.encode('utf-8'))
                            if len(valeurs) > 6: 
                                texte = ''.join(valeurs[:4]) + '<br/>' + ''.join(valeurs[4:])
                            elif len(valeurs) > 4: 
                                texte = ' '.join(valeurs[:3]) + '<br/>' + ' '.join(valeurs[3:])
                            elif len(valeurs) > 2: 
                                texte = ' '.join(valeurs[:2]) + '<br/>' + ' '.join(valeurs[2:])
                            else : texte = ' '.join(valeurs)
                            csock.sendall(('{}</td>'.format(texte)).encode('utf-8'))
                    csock.sendall('</tr>\n'.encode('utf-8'))
                csock.sendall('</table></td>\n'.encode('utf-8'))
            csock.sendall('</tr>\n'.encode('utf-8'))
        csock.sendall('</table>\n'.encode('utf-8'))
        csock.sendall('</td></tr></table>'.encode('utf-8'))
        # affiche les informations de validitej
        if len(lesInvalides) != 0:
            csock.sendall('<p>La grille présente des incompatibilités sur les cellules marquées en rouge</p>\n'.encode('utf-8'))
            return
        # le diagnostic par la mejthode bourrin
        tropDeSolutions, rejsultat = self.sudoku.nombreSolutions()
        if rejsultat == 0:
            csock.sendall("<p>La grille n'a aucune solution</p>\n".encode('utf-8'))
        elif rejsultat == 1:
            csock.sendall("<p>La grille a une solution et une seule</p>\n".encode('utf-8'))
        elif tropDeSolutions:
            csock.sendall("<p>La grille a plus de 100 solutions</p>\n".encode('utf-8'))
        else:
            csock.sendall(("<p>La grille a {} solutions</p>\n".format(rejsultat)).encode('utf-8'))
        # le calcul par le sudoku anthropomorphique
        csock.sendall("""
         <form name="calcul" method="post" action="calcul-sudoku">
            <input type="submit" value="Tentative de résolution par le Sudoku anthropomorphique">
        </form>
            """.encode('utf-8'))
        
          
    ###################################
    def afficheTitreEtSaisie(self, csock):
        imageHtml = self.imageBase64("echiquierLatejcon4-200T.png")
        csock.sendall((
            """        
        <table><tr><td><h1>Le sudoku anthropomorphique de</h1></td><td>{}</td></tr>
        </table>
        <table class="saisiecc"><tr><td height="50px">
        <form name="saisie-cc" method="post" action="saisie-cc">
            <input type="text" id="copiercoller" name="copiercoller" maxlength="90" size="89" value="{}"/>
            <input type="submit" value="V">
        </form>
        </td></tr></table>
        <br/>
        """.format(imageHtml, self.ejnoncej)).encode('utf-8'))
        
        csock.sendall(
            """
        <table><tr><td  class="zone-saisie">
            <form name="saisie-grille" method="post" action="saisie-grille">
            """.encode('utf-8'))
        
        inputId = 0
        ejnoncej = self.ejnoncej.replace('|', '')
        for ligne in range(1, 10):
            csock.sendall(('<div id="ligne{}" class="ligne-saisie">\n'.format(ligne)).encode('utf-8'))
            for colonne in range(1, 10):
                if inputId < len(ejnoncej): valeur = ejnoncej[inputId]
                else: valeur = ''
                if valeur == '.': valeur = ''
                inputId +=1
                html = '<input type="text" id="{}" name="{}{}" maxlength="1" value="{}" class="chiffre'.format(inputId, ligne, colonne, valeur)
                if colonne in (3, 6): html += ' sep'
                if ligne in (4, 7): html += ' sep2'
                if inputId == 1: html += '" autofocus/>\n'
                else: html += '"/>\n'
                csock.sendall(html.encode('utf-8'))
            csock.sendall('</div>\n'.encode('utf-8'))
 
        csock.sendall(
            """
                    <br/>
                </div>
                <p>&nbsp;</p><br/>
                <div>
                <input type="submit" name="raz" value="raz" formmethod="post">
                <input type="submit" name="soumettre" value="soumettre" formmethod="post">
                </div>
            </form></td>
            <td class="zone-rejsultat">
            """.encode('utf-8'))
        
    ###################################
    def afficheRejsultatVide(self, csock):
        csock.sendall('</td></tr></table>'.encode('utf-8'))
        
    ###################################
    def imageBase64(self, nom):
        try:
            with open(nom, 'rb') as img:
                extension = nom.split('.')[-1]
                imgStr = base64.b64encode(img.read()).decode()
                return '<img src="data:image/{};base64,{}"/>\n'.format(extension, imgStr)
        except Exception:
            traceback.print_exc()
            return '<blink>Image pas trouveje !</blink>'
        
    ###################################
    def afficheEnTeste(self, csock):
        csock.sendall(
            """
<!DOCTYPE html>
<html  lang="fr">
    <head>
        <meta charset="utf-8">
        <title>Sudoku anthropomorphique de l'Atejcon</title>
        <style type="text/css">
            .ligne-saisie input[type='text'].chiffre {width: 32px; }
            .ligne-saisie input[type='text'].sep {margin-right: 2px; }
            .ligne-saisie input[type='text'].sep2 {margin-top: 1px; }
            .ligne-saisie input[type='text'] {
                background: #fff;
                border: 1px solid #d6d6d6;
                border-radius: 2px;
                padding: 0 5px;
                line-height: 2.81em;
                font-family: "Open Sans";
                font-size: 30px;
                float: left;
                margin-left: -1px;
                text-align: center; }
            .ligne-saisie input[type='text'] {height: 41px !important; } 
            .ligne-saisie {
                position:relative;
                min-height:1px;
                padding-right:15px; 
                padding-left:15px}
            .ligne-saisie {float:left}
            .ligne-saisie {width:100%}
            .zone-saisie {
                width:450px; height:500px; 
                text-align:center; vertical-align:center; 
                background-color: #E5E5E4;}
            .zone-rejsultat {
                width:500px; height:500px; 
                text-align:center; vertical-align:center; 
                background-color: #f4f4f4;}
            .tableRejultat {
                border: 1px solid #d6d6d6; border-collapse: collapse; 
                background-color: #d6d6d6;}
            .tableCarrej {border: 1px solid black; border-collapse: collapse; }
            .tdRej {
                font-family: "Open Sans";
                width: 50px; height: 50px;
                border: 1px solid #d6d6d6; border-collapse: collapse; 
                empty-cells: show;}
            .tdSim {
                background-color: #f4f4f4;
                font-size: 35px; }
            .tdErr {
                background-color: red;
                font-size: 35px; }
            .tdMul {
                background-color: white;
                font-size: 18px; }
            .tdMu2 {
                background-color: white;
                font-size: 16px; }
            .saisiecc {
                background-color: #E5E5E4;}   
            #copiercoller {
                font-family:courier, courier new, sans-serif;
                font-size: 16px; }
        </style>
    </head>
    <body>
            """.encode('utf-8'))

    ###################################
    def afficheQueue(self, csock):
        csock.sendall(
            """
        <script>
            var inputs = document.getElementsByClassName('chiffre');
            for (var i=0; i < inputs.length; i++) 
                inputs[i].addEventListener('input', prochain);
            function prochain() {
                //il faut un signe "-" pour que ca calcule, "+" fait de la concatejnation
                var valeur = this.value;
                if (valeur != '') {
                    valeur = valeur.replace(/[^1-9]/g, '');
                    this.value = valeur
                    document.getElementById(this.id-1+2).focus();
                }
            }
        </script>
    </body>
</html>
            """.encode('utf-8'))


    
if __name__ == '__main__':
    main()
    
