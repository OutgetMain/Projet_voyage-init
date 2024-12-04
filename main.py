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

@app.route("/page_recherche", methods=["GET"])
def voyage():
    search_query = request.args.get("search", "").strip()  # Récupère le paramètre 'search'
    liste_voyage = []

    with extract.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur_lvoyage:
        # Si une recherche est effectuée, applique un filtre
        if search_query:
            cur_lvoyage.execute("""
                SELECT id_voyage, id_ville, date_depart, date_arrivée, date_debut, date_de_fin
                FROM Etape NATURAL JOIN voyage
                WHERE reservation = true AND (
                    CAST(id_voyage AS TEXT) ILIKE %s OR
                    id_ville IN (
                        SELECT id_ville FROM Ville WHERE nom ILIKE %s
                    )
                )
            """, (f"%{search_query}%", f"%{search_query}%"))
        else:
            cur_lvoyage.execute("""
                SELECT id_voyage, id_ville, date_depart, date_arrivée, date_debut, date_de_fin
                FROM Etape NATURAL JOIN voyage
                WHERE reservation = true
            """)
        
        for result in cur_lvoyage:
            voyage_existe = False
            for groupe in liste_voyage:
                if groupe[0] == result.id_voyage:
                    groupe.append([
                        FctUsuelle.convert(str(result.id_ville), "SELECT nom FROM Ville WHERE id_ville = %s ", "nom"),
                        result.id_voyage,
                        (result.date_depart.year, result.date_depart.month, result.date_depart.day),
                        (result.date_arrivée.year, result.date_arrivée.month, result.date_arrivée.day)
                    ])
                    voyage_existe = True
                    break

            if not voyage_existe:
                liste_voyage.append([
                    result.id_voyage,
                    (result.date_debut.year, result.date_debut.month, result.date_debut.day),
                    (result.date_de_fin.year, result.date_de_fin.month, result.date_de_fin.day),
                    [
                        FctUsuelle.convert(str(result.id_ville), "SELECT nom FROM Ville WHERE id_ville = %s ", "nom"),
                        result.id_voyage,
                        (result.date_depart.year, result.date_depart.month, result.date_depart.day),
                        (result.date_arrivée.year, result.date_arrivée.month, result.date_arrivée.day)
                    ]
                ])

    return render_template("page_recherche.html", liste_voyage=liste_voyage)


@app.route('/detail/<int:item_id>', methods=["GET", "POST"])
def detail(item_id):
    with extract.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur_detail:
        cur_detail.execute("""
            SELECT id_voyage, id_ville, date_depart, date_arrivée,date_debut,date_de_fin,id_logement,id_transport,id_et_type
            FROM Etape NATURAL JOIN voyage 
            WHERE id_voyage = %s
        """,(item_id,))
        details = cur_detail.fetchall()

        results = []
        for detail in details:
            nom_ville = FctUsuelle.convert(str(detail.id_ville),"SELECT nom FROM Ville WHERE id_ville = %s ","nom")
            logement = FctUsuelle.convert(str(detail.id_logement),"SELECT id_type_logement FROM logement WHERE id_logement = %s ","id_type_logement")
            type_logement = FctUsuelle.convert(logement,"SELECT valeur FROM type_logement WHERE id_type_logement = %s ","valeur")
            transport = FctUsuelle.convert(str(detail.id_transport),"SELECT valeur FROM moyen_transport WHERE id_transport = %s ","valeur")
            type = FctUsuelle.convert(str(detail.id_et_type),"SELECT valeur FROM type_etape WHERE id_et_type = %s ","valeur")
            # Ajouter le nom de la ville à chaque ligne de résultat
            results.append({
                "id_voyage": detail.id_voyage,
                "id_ville": detail.id_ville,
                "nom_ville": nom_ville,
                "date_depart": detail.date_depart,
                "date_arrivée": detail.date_arrivée,
                "date_debut": detail.date_debut,
                "date_de_fin": detail.date_de_fin,
                "type_logement": type_logement,
                "type": type,
                "transport": transport
            })
    return render_template("detail.html", details=results)


if __name__ == '__main__':
    app.run(debug=True)