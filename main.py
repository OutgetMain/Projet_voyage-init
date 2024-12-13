from random import randint
import time
import extract
import psycopg2
import FctUsuelle
from psycopg2.extras import NamedTupleCursor
from flask import Flask, render_template, request, redirect, url_for, session, flash

from werkzeug.security import generate_password_hash, check_password_hash


from flask import Flask, render_template, request, redirect, url_for, session
#source venv/bin/activate

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_pour_la_session'

@app.before_request
def clear_session_on_restart():
    if not session.get("initialized"):
        session.clear()
        session["initialized"] = True

@app.route("/Accueil", methods=["GET", "POST"])
def accueil():
    with extract.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur_acc:
        # Vérifiez si l'utilisateur est connecté
        user_connected = session.get("user_id") is not None

        if request.method == "POST":
            # Gestion de la déconnexion
            if "logout" in request.form:  # Bouton de déconnexion
                session.pop("user_id", None)  # Supprime l'utilisateur de la session
                flash("Déconnexion réussie.", "success")
                return redirect(url_for("accueil"))

            # Afficher le formulaire de connexion
            if "connexion" in request.form:
                return render_template(
                    "Accueil.html",
                    show_form=True,
                    form_type="connexion",
                    user_connected=user_connected,
                )

            # Afficher le formulaire d'inscription
            elif "inscription" in request.form:
                return render_template(
                    "Accueil.html",
                    show_form=True,
                    form_type="inscription",
                    user_connected=user_connected,
                )

            # Validation de la connexion
            if "validation_connexion" in request.form:
                username = request.form.get("username")
                password = request.form.get("password")


                cur_acc.execute(
                    "SELECT id_utilisateur, courriel, mdp FROM client WHERE courriel = %s",
                    (username,),
                )
                user = cur_acc.fetchone()

                # valide la session
                if user and check_password_hash(user.mdp, password):
                    session["user_id"] = user.id_utilisateur
                    return redirect(url_for("accueil"))
                else:
                    return render_template(
                        "Accueil.html",
                        show_form=True,
                        form_type="connexion_fail",
                        user_connected=False,
                    )

            # Validation de l'inscription
            if "validation_inscription" in request.form:
                Nom = request.form.get("nom")
                Prenom = request.form.get("prenom")
                Sexe = request.form.get("sexe")
                Age = request.form.get("age")
                Nationalite = request.form.get("nationalite")
                Adresse = request.form.get("adresse")
                Tel = request.form.get("telephone")
                Mail = request.form.get("mail")
                password = request.form.get("password")

                # Vérifier si l'email existe déjà
                cur_acc.execute(
                    "SELECT id_utilisateur FROM client WHERE courriel = %s", (Mail,)
                )
                if cur_acc.fetchone():
                    flash("Ce courriel est déjà utilisé.", "danger")
                    return render_template(
                        "Accueil.html",
                        show_form=True,
                        form_type="inscription_fail",
                        user_connected=user_connected,
                    )

                # Hacher le mot de passe
                hashed_password = generate_password_hash(password)

                # Insérer l'utilisateur
                insert_query = """
                    INSERT INTO client(nom, prenom, sexe, courriel, tel, adresse, mdp, age, nationnalite)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cur_acc.execute(
                    insert_query,
                    (
                        Nom,
                        Prenom,
                        Sexe,
                        Mail,
                        Tel,
                        Adresse,
                        hashed_password,
                        Age,
                        Nationalite,
                    ),
                )
                extract.conn.commit()
                flash(
                    "Inscription réussie ! Vous pouvez maintenant vous connecter.",
                    "success",
                )
                return redirect(url_for("accueil"))

    # Si aucun formulaire n'est soumis, afficher la page d'accueil
    return render_template("Accueil.html", show_form=False, user_connected=user_connected)


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

    id_utilisateur = session.get('user_id')
    if not id_utilisateur:
        flash("Vous devez être connecté pour réserver un voyage.", "danger")
        return redirect(url_for('accueil'))
    
    if request.method == "POST":
        try:
            # Tenter de réserver un voyage
            FctUsuelle.reserver_voyage(id_utilisateur, item_id)
            extract.conn.commit()
            flash("Réservation effectuée avec succès !", "success")
            return redirect(url_for('accueil'))
        except Exception as e:
            flash(str(e), "danger")
            extract.conn.rollback()
            return redirect(url_for('accueil'))
            
    with extract.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur_detail:
        cur_detail.execute("""
            SELECT id_agence,id_voyage, id_ville, date_depart, date_arrivée,date_debut,date_de_fin,id_logement,id_transport,id_et_type
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
            agence = FctUsuelle.convert(str(detail.id_agence),"SELECT nom  FROM Agence WHERE id_agence = %s ","nom")
            agence_adresse = FctUsuelle.convert(str(detail.id_agence),"SELECT adresse  FROM Agence WHERE id_agence = %s ","adresse ")
            agence_ville = FctUsuelle.convert(str(detail.id_agence),"SELECT ville  FROM Agence WHERE id_agence = %s ","ville")
            agence_telephone = FctUsuelle.convert(str(detail.id_agence),"SELECT telephone  FROM Agence WHERE id_agence = %s ","telephone ")

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
                "transport": transport,
                "Agence" : agence,
                "agence_adresse" : agence_adresse,
                "agence_ville" : agence_ville,
                "agence_telephone" : agence_telephone
            })
    return render_template("detail.html", details=results)

@app.route('/Personnal', methods=["GET", "POST"])
def Personne():

    #Verifie que le client est connecter
    id_utilisateur = session.get('user_id')
    if not id_utilisateur:
        flash("Vous devez être connecté pour avoir acces a votre espace personnel.", "danger")
        return redirect(url_for('accueil'))
    
    if request.method == "POST":
        #Recupere les input
        if "mise_a_jour" in request.form:
            nom = request.form.get("nom")
            sexe = request.form.get("sexe")
            courriel = request.form.get("courriel")
            prenom = request.form.get("prenom")
            tel = request.form.get("tel")
            adresse = request.form.get("adresse")
            age = request.form.get("age")
            nationnalite = request.form.get("nationnalite")
            mdp = request.form.get("password")

            #Permet de remplir les case manquante lors de la mise a jour des informations personnels
            with extract.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur_per:
                cur_per.execute("""
                    SELECT nom, sexe, courriel, prenom, tel, adresse, age, nationnalite 
                    FROM client WHERE id_utilisateur = %s
                """, (id_utilisateur,))
                current_info = cur_per.fetchone()

                # Verifie si des champs on etait modifier si oui le changement est appliquer
                # sinon l'information precedent ne change pas 
                nom = nom if nom else current_info.nomhashed_password
                courriel = courriel if courriel else current_info.courriel
                prenom = prenom if prenom else current_info.prenom
                tel = tel if tel else current_info.tel
                adresse = adresse if adresse else current_info.adresse
                age = age if age else current_info.age
                nationnalite = nationnalite if nationnalite else current_info.nationnalite

                hashed_password = (generate_password_hash(mdp) if mdp else None)

                query =""" 
                    UPDATE client 
                    SET nom = %s, sexe = %s, courriel = %s, prenom = %s, tel = %s, adresse = %s, age = %s, nationnalite = %s, mdp = COALESCE(%s, mdp) --COALESCE permet de conserver 
                    WHERE id_utilisateur = %s                                                                                                         --un mot existant si il n'y a pas de nouveau mot de passe
                """
                cur_per.execute(query, (nom, sexe, courriel, prenom, tel, adresse, age, nationnalite,hashed_password, id_utilisateur))
                extract.conn.commit()
                flash("Vos informations ont été mises à jour avec succès.", "success")
                return redirect(url_for('accueil'))
            
    #Permet d'envoyer les informations concernant l'historique des voyages au front        
    with extract.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur_per:

        cur_per.execute("""
            SELECT id_voyage,reservation FROM participe NATURAL JOIN voyage WHERE id_utilisateur = %s
        """,(id_utilisateur,))

        historique = cur_per.fetchall()
        voyage_passer = []
        voyage_actuelle = []

        for hist in historique:
            if hist.reservation:
                voyage_actuelle.append(hist.id_voyage)
            else:
                voyage_passer.append(hist.id_voyage)

    #Permet de renvoyer les informations personnels a afficher au front  
    with extract.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur_per:
        cur_per.execute("""
            SELECT nom,sexe ,courriel ,prenom ,tel ,adresse  ,age ,nationnalite 
            FROM client WHERE id_utilisateur = %s
            
        """,(id_utilisateur,))
        details = cur_per.fetchall()
        result=[]
        for detail in details:
            result.append({
                "nom": detail.nom,
                "sexe": detail.sexe,
                "courriel": detail.courriel,
                "prenom": detail.prenom,
                "tel": detail.tel,
                "adresse": detail.adresse,
                "age": detail.age,
                "nationnalite": detail.nationnalite,
            })
    
    return render_template("Personnal.html", details=result,voyage_passer=voyage_passer,voyage_actuelle=voyage_actuelle)

if __name__ == '__main__':
    app.run(debug=True)