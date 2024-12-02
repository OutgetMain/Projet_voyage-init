from random import randint
import time
import extract
import psycopg2
import FctUsuelle
from psycopg2.extras import NamedTupleCursor
from flask import Flask, render_template, request, redirect, url_for, session
#source venv/bin/activate

app = Flask(__name__)


@app.route("/Accueil", methods=["GET", "POST"])
def accueil():
    with extract.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur_acc:
        if request.method == "POST":
            if "connexion" in request.form:
                return render_template("Accueil.html", show_form=True, form_type="connexion")
            elif "inscription" in request.form:
                return render_template("Accueil.html", show_form=True, form_type="inscription")
            
            if "validation_connexion" in request.form :
                username = request.form.get("username")
                password = request.form.get("password")
                cur_acc.execute("SELECT courriel,mdp FROM client;")
                liste_client = cur_acc.fetchall()
                if (username,password) in liste_client:
                    return render_template("Accueil.html",show_form=True,form_type = "connexion_succes",liste_client=liste_client)
                return render_template("Accueil.html",show_form=True,form_type = "connexion_fail",liste_client=liste_client)
            
            if "validation_inscription" in request.form :
                Nom = request.form.get("nom")
                Prenom = request.form.get("prenom")
                Sexe = request.form.get("sexe")
                Age = request.form.get("age")
                Nationalite = request.form.get("nationalite")
                Adresse = request.form.get("adresse")
                Tel= request.form.get("telephone")
                Mail= request.form.get("mail")
                password = request.form.get("password")
                
                insert_query = """
                    INSERT INTO client(nom, prenom, sexe, courriel, tel, adresse,mdp,age,nationalite)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cur_acc.execute(insert_query, (Nom, Prenom, Sexe, Mail, Tel, Adresse, password,Age,Nationalite))
                extract.conn.commit()
                return render_template("Accueil.html",show_form=True, form_type = "inscription_reussie")
            
    return render_template("Accueil.html", show_form=False)

@app.route("/page_recherche")
def voyage():
    liste_voyage = []  # Liste pour regrouper les voyages par id_voyage
    
    with extract.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur_lvoyage:
        cur_lvoyage.execute("""
            SELECT id_voyage, id_ville, date_debut, date_de_fin 
            FROM Etape NATURAL JOIN voyage 
            WHERE reservation = true
        """)
        
        for result in cur_lvoyage:
            # Chercher si un groupe avec cet id_voyage existe déjà
            voyage_existe = False
            for groupe in liste_voyage:
                if groupe[0] == result.id_voyage:  # Vérifie si le voyage est déjà dans la liste
                    groupe.append([result.id_ville, result.id_voyage, (result.date_debut.year, result.date_debut.month, result.date_debut.day)])
                    voyage_existe = True
                    break
            
            # Si aucun groupe pour cet id_voyage, créer un nouveau groupe
            if not voyage_existe:
                liste_voyage.append([
                    result.id_voyage,  # ID du voyage
                    [result.id_ville, result.id_voyage, (result.date_debut.year, result.date_debut.month, result.date_debut.day)]
                ])
    
    return liste_voyage
    return render_template("page_recherche.html",liste_voyage = liste_voyage)
""""
def liste_voyage():
    liste_voyage = []
    with extract.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur_lvoyage:
        cur_lvoyage.execute("SELECT id_voyage,id_ville,date_debut,date_de_fin FROM Etape NATURAL JOIN voyage WHERE reservation = true ")
        for result in cur_lvoyage:
            for indice in range(len(liste_voyage)):
                if result.id_voyage in liste_voyage[indice]:
                    liste_voyage[indice].append([result.id_voyage,FctUsuelle.convert_ville(str(result.id_ville)), 
                                 (result.date_debut.year,result.date_debut.month,result.date_debut.day), 
                                 (result.date_de_fin.year,result.date_de_fin.month,result.date_de_fin.day)
                                 ]) 
                else:
                    liste_voyage.append([result.id_voyage,FctUsuelle.convert_ville(str(result.id_ville)), 
                                        (result.date_debut.year,result.date_debut.month,result.date_debut.day), 
                                        (result.date_de_fin.year,result.date_de_fin.month,result.date_de_fin.day)
                                        ]) 

    return render_template("page_recherche.html",liste_voyage = liste_voyage)"""



if __name__ == '__main__':
    app.run(debug=True)
