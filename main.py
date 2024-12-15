from random import randint
import time
import extract
from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import FctUsuelle
#source venv/bin/activate

#je veux utiliser les cookies afin de stocker les informations de l'utilisateur tel que l'id de son agence
#et ses permissions administrateurs
#comment faire pour stocker les informations de l'utilisateur dans les cookies
  
app = Flask(__name__)

app.secret_key = b'd2b01c987b6f7f0d5896aae06c4f318c9772d6651abff24aec19297cdf5eb199'

@app.before_request
def clear_session_on_restart():
    if not session.get("initialized"):
        session.clear()
        session["initialized"] = True

@app.route("/")
def acc():
    return redirect(url_for('accueil'))

@app.route("/Accueil", methods=["GET", "POST"])
def accueil():
    with extract.conn.cursor() as cur_acc:
        # Vérifiez si l'utilisateur est connecté
        temp_connected = session.get("user_id") is not None
        temp_user = session.get("work_id") is not None
        temp_admin = session.get("admin") is not None
        user_connected = temp_connected or temp_user

        if request.method == "POST":
            # Gestion de la déconnexion
            if "logout" in request.form:  # Bouton de déconnexion
                session.pop("user_id", None)  # Supprime l'utilisateur de la session
                session.pop("work_id", None)  # Supprime l'utilisateur de la session
                session.pop("admin", None)  # Supprime l'utilisateur de la session
                session.pop("id_agence", None)  # Supprime l'utilisateur de la session
                flash("Déconnexion réussie.", "success")
                return redirect(url_for("accueil"))

            # Afficher le formulaire de connexion
            if "connexion" in request.form:
                return render_template(
                    "Accueil.html",
                    show_form=True,
                    form_type="connexion",
                    user_connected=user_connected,
                    work_connected=temp_user,
                )

            # Afficher le formulaire d'inscription
            elif "inscription" in request.form:
                return render_template(
                    "Accueil.html",
                    show_form=True,
                    form_type="inscription",
                    user_connected=user_connected,
                    work_connected=temp_user,
                )

            # Validation de la connexion
            if "validation_connexion" in request.form:
                username = request.form.get("username")
                password = request.form.get("password")


                cur_acc.execute(
                    "SELECT id_utilisateur, courriel, mdp FROM client WHERE courriel = %s;",
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
                        work_connected=temp_user,
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
                        work_connected=temp_user,
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
    return render_template("Accueil.html", show_form=False, user_connected=user_connected, work_connected=temp_user, work_resp = temp_admin,)


@app.route("/page_recherche", methods=["GET"])
def voyage():
    search_query = request.args.get("search", "").strip()  # Récupère le paramètre 'search'
    liste_voyage = []
    temp_user = session.get("work_id") is not None
    resp = session.get("work_resp") is not None
    temp_admin = session.get("admin") is not None



    with extract.conn.cursor() as cur_lvoyage:
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

    return render_template("page_recherche.html", liste_voyage=liste_voyage, work_connected = temp_user, work_resp = temp_admin,)


@app.route('/detail/<int:item_id>', methods=["GET", "POST"])
def detail(item_id):
    temp_admin = session.get("admin") is not None
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
            
    with extract.conn.cursor() as cur_detail:
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
            agence = FctUsuelle.convert(str(detail.id_agence),"SELECT nom FROM Agence WHERE id_agence = %s ","nom")
            agence_adresse = FctUsuelle.convert(str(detail.id_agence),"SELECT adresse FROM Agence WHERE id_agence = %s ","adresse")
            agence_ville = FctUsuelle.convert(str(detail.id_agence),"SELECT ville FROM Agence WHERE id_agence = %s ","ville")
            agence_telephone = FctUsuelle.convert(str(detail.id_agence),"SELECT telephone  FROM Agence WHERE id_agence = %s ","telephone")

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
                "agence_telephone" : '0' + str(agence_telephone)
            })
    return render_template("detail.html", details=results, work_resp = temp_admin,)

@app.route('/Personnal', methods=["GET", "POST"])
def Personne():
    temp_admin = session.get("admin") is not None
    #Verifie que le client est connecter
    id_utilisateur = session.get('user_id')
    id_work = session.get('work_id')
    if not id_utilisateur and not id_work:
        flash("Vous devez être connecté pour avoir acces a votre espace personnel.", "danger")
        return redirect(url_for('accueil'))
    if request.method == "POST":
        #Recupere les input
        if id_utilisateur:
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
                with extract.conn.cursor() as cur_per:
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
        elif id_work:
            login = request.form.get("login")
            mdp = request.form.get("password")
            with extract.conn.cursor() as cur_per:
                cur_per.execute("""
                    SELECT login, mdp
                    FROM Travailleur WHERE id_travailleur = %s
                """, (id_work,))
                current_info = cur_per.fetchone()

                login = login if login else current_info.login
                hashed_password = (generate_password_hash(mdp) if mdp else None)

                query =""" 
                    UPDATE Travailleur 
                    SET login = %s, mdp = COALESCE(%s, mdp) 
                    WHERE id_travailleur = %s
                """
                cur_per.execute(query, (login, hashed_password, id_work))
                extract.conn.commit()
                flash("Vos informations ont été mises à jour avec succès.", "success")
                return redirect(url_for('accueil'))


    #Permet d'envoyer les informations concernant l'historique des voyages au front 
    if id_utilisateur:       
        with extract.conn.cursor() as cur_per:

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
        with extract.conn.cursor() as cur_per:
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

        return render_template("Personnal.html", details=result, details2 = [],voyage_passer=voyage_passer,voyage_actuelle=voyage_actuelle, work_connected = False)
    elif id_work:
        with extract.conn.cursor() as cur:
            cur.execute("""
                SELECT login
                FROM Travailleur WHERE id_travailleur = %s
            """,(id_work,))
            result = cur.fetchall()


        return render_template("Personnal.html", details=[], details2 = result, voyage_passer=[], voyage_actuelle=[], work_connected = True, work_resp = temp_admin,)













@app.route("/configUser")
def liste_utilisateur():
    temp_connected = session.get("user_id") is not None
    temp_user = session.get("work_id") is not None
    user_connected = temp_connected or temp_user
    temp_admin = session.get("admin") is not None
    with extract.conn as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Travailleur WHERE id_agence = %s and id_travailleur <> %s;", (session['id_agence'], session['work_id']))
            result = cur.fetchall()
    return render_template("uti_list.html", ulist = result, user_connected = temp_connected, work_resp = temp_admin, work_connected=temp_user,)

"""@app.route("/configUser/<int:id_user>")
def profile(id_user):
    with extract.connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * from client where id_utilisateur = %s;", (id_user,))
            res = cur.fetchone()
            if not res:
                return render_template("user_error.html")
    return render_template("userProfile.html", lst_att = res)"""

@app.route("/configUser/<int:id_user>", methods=['GET'])
def show_form(id_user):
    temp_connected = session.get("user_id") is not None
    temp_user = session.get("work_id") is not None
    user_connected = temp_connected or temp_user
    temp_admin = session.get("admin") is not None
    with extract.conn as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Travailleur WHERE id_travailleur = %s AND id_agence = %s;", (id_user, session['id_agence']))
    

            temp_user = cur.fetchone()
    with extract.conn as conn:
        with conn.cursor() as curtest:
            curtest.execute("SELECT * from Agence;")
            lst_agence = curtest.fetchall()
    if not temp_user:
        return "Utilisateur introuvable", 404

    return render_template("editUser.html", user=temp_user, user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin, lst_agence = lst_agence,)    



@app.route("/configUser/<int:id_user>/edit", methods = ['post'])
def configProfile(id_user):
    temp_user = session.get("work_id") is not None
    temp_admin = session.get("admin") is not None
    if temp_admin:
        temp_id = session.get("id_agence")

    login = request.form['login']
    id_agence = request.form['id_agence']
    responsable = request.form['responsable']

    with extract.conn as conn:
        with conn.cursor() as curtest:
            curtest.execute("SELECT * from travailleur where id_travailleur = %s;", (id_user,))
            res = curtest.fetchone()

    with extract.conn as conn:
        with conn.cursor() as curtest:
            curtest.execute("SELECT * from travailleur where id_agence = %s AND est_responsable = 'True';", (id_agence,))
            test = curtest.fetchone()



    with extract.conn as conn:
        with conn.cursor() as cur:

            compt = 0
            if(login != res.login):
                cur.execute("UPDATE travailleur SET login = %s WHERE id_travailleur = %s;", (login, id_user))
                compt+=1

            if(int(id_agence) != res.id_agence):
                cur.execute("UPDATE travailleur SET id_agence = %s WHERE id_travailleur = %s;", (id_agence, id_user))
                compt+=1

            if(responsable == "True" and test != None):
                return render_template("error.html", user_connected = temp_user, work_connected=temp_user, work_resp = temp_admin,)
                
                        

            elif(str(responsable) != str(res.est_responsable) and responsable != True):
                cur.execute("UPDATE travailleur SET est_responsable = %s WHERE id_travailleur = %s;", (responsable, id_user))
                compt+=1
                
            if(compt>0):
                conn.commit()
    return render_template("sucessEdit.html", nbModif = compt, user_connected = temp_admin, work_connected = temp_user, work_resp = temp_admin,)

@app.route("/configUser/<int:id_user>/delete", methods = ['post'])
def delete(id_user):
    temp_admin = session.get("admin") is not None
    temp_connected = session.get("user_id") is not None
    temp_user = session.get("work_id") is not None
    user_connected = temp_connected or temp_user
    with extract.conn as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM client WHERE id_utilisateur = %s;", (id_user,))
            conn.commit()
    return render_template("delete.html", user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)



@app.route("/configTrip")
def liste_voyage():
    temp_admin = session.get("admin") is not None
    temp_connected = session.get("user_id") is not None
    temp_user = session.get("work_id") is not None
    temp_id = session.get("id_agence")
    if not temp_admin:
        return render_template("trip_error.html", user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)
    

    with extract.conn as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM voyage where id_agence = %s;", (temp_id,))   
            result = cur.fetchall()
    return render_template("showTrip.html", tripList = result, user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)

@app.route("/configTrip/<int:id_voyage>")
def show_trip(id_voyage):
    temp_admin = session.get("admin") is not None
    temp_connected = session.get("user_id") is not None
    temp_user = session.get("work_id") is not None
    user_connected = temp_user
    agence = session.get("id_agence")
    
    with extract.conn as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM voyage WHERE id_voyage = %s;", (id_voyage,))
            res = cur.fetchone()
    with extract.conn as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM etape WHERE id_voyage = %s;", (id_voyage,))
            res2 = cur.fetchall()
            if not res:
                return render_template("trip_error.html", user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)
    
    if res.id_agence != agence or not temp_admin:
        return render_template("trip_error.html", user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)
    return render_template("editTrip.html", trip = res, work_connected=temp_user, work_resp = temp_admin, etapeList = res2,)

@app.route("/configTrip/<int:id_voyage>/edit", methods = ['post'])
def configTrip(id_voyage):
    temp_admin = session.get("admin") is not None
    temp_connected = session.get("user_id") is not None
    temp_user = session.get("work_id") is not None
    user_connected = temp_user


    nom = request.form['nom']
    date_debut = request.form['date_debut']
    date_fin = request.form.get('date_fin')
    prix = request.form['prix']
    reservation = request.form.get('reservation')
    agence = session.get("id_agence")


    with extract.conn as conn:
        with conn.cursor() as curtest:
            curtest.execute("SELECT * from voyage where id_voyage = %s;", (id_voyage,))
            res = curtest.fetchone()

    agence = session.get("id_agence")
    if res.id_agence != agence or not temp_admin:
        return render_template("trip_error.html", user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)

    with extract.conn as conn:
        with conn.cursor() as cur:
            compt = 0
            if(nom != res.nom):
                cur.execute("UPDATE voyage SET nom = %s WHERE id_voyage = %s;", (nom , id_voyage))
                compt+=1
            if(str(res.date_debut) != str(date_debut)):
                cur.execute("UPDATE voyage SET date_debut = %s WHERE id_voyage = %s;", (date_debut, id_voyage))
                compt+=1
            if(str(date_fin) != str(res.date_de_fin)):
                cur.execute("UPDATE voyage SET date_de_fin = %s WHERE id_voyage = %s;", (date_fin, id_voyage))
                compt+=1
            if(str(res.cout_par_personne) != str(prix)):
                cur.execute("UPDATE voyage SET cout_par_personne = %s WHERE id_voyage = %s;", (prix, id_voyage))
                compt+=1
            if(reservation == "True" or reservation == "False"):
                cur.execute("UPDATE voyage SET reservation = %s WHERE id_voyage = %s;", (reservation, id_voyage))
                compt+=1
            print(reservation)
            if reservation != res.reservation:
                cur.execute("UPDATE voyage SET reservation = %s WHERE id_voyage = %s;", (reservation, id_voyage))
                compt+=1
            if(compt>0):
                conn.commit()
    return render_template("sucessEdit.html", nbModif = compt, user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)


@app.route("/configTrip/tmp")
def addTriptemp():
    temp_admin = session.get("admin") is not None
    temp_connected = session.get("user_id") is not None
    temp_user = session.get("work_id") is not None
    user_connected = temp_user
    agence = session.get("id_agence")
    
    return render_template("addTrip.html", villeList = res, user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)

"""@app.route("/configTrip/add")
def addTrip():
    temp_admin = session.get("admin") is not None
    temp_connected = session.get("user_id") is not None
    temp_user = session.get("work_id") is not None
    user_connected = temp_user
    agence = session.get("id_agence")
    
    return render_template("addTrip.html", user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)
"""
@app.route("/configTrip/add", methods = ['post'])
def addTrip():
    temp_admin = session.get("admin") is not None
    temp_connected = session.get("user_id") is not None
    temp_user = session.get("work_id") is not None
    user_connected = temp_user
    if not temp_admin:
        return render_template("trip_error.html", user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)
    return render_template("addTrip.html", user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)
    

@app.route("/addProcess", methods = ['post'])
def addProcess():

    nom = request.form['nom']
    date_debut = request.form['date_debut']
    date_fin = request.form.get('date_fin')
    prix = request.form['prix']
    reservation = request.form.get('reservation')

    temp_admin = session.get("admin") is not None
    temp_connected = session.get("user_id") is not None
    temp_user = session.get("work_id") is not None
    user_connected = temp_user
    agence = session.get("id_agence")

    if not temp_admin:
        return render_template("trip_error.html", user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)
    
    with extract.conn as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO voyage(nom, date_debut, date_de_fin, cout_par_personne, reservation, id_agence) VALUES (%s, %s, %s, %s, %s, %s);", (nom, date_debut, date_fin, prix, reservation, agence))
            conn.commit()
    return render_template("sucessAdd.html", user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)
  

@app.route("/configTrip/<int:id_voyage>/delete", methods = ['post'])
def deleteTrip(id_voyage):
    temp_admin = session.get("admin") is not None
    temp_connected = session.get("user_id") is not None
    temp_user = session.get("work_id") is not None
    user_connected = temp_user
    agence = session.get("id_agence")

    if not temp_admin:
        return render_template("trip_error.html", user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)

    with extract.conn as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM voyage WHERE id_voyage = %s;", (id_voyage,))
            conn.commit()
    return redirect(url_for('liste_voyage'))

@app.route("/configTrip/<int:id_voyage>/configStage/<int:id_stage>")
def show_stage(id_stage):
    temp_admin = session.get("admin") is not None
    if not temp_admin:
        return render_template("trip_error.html", user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)

    return render_template("editStage.html", stage = res, work_resp = temp_admin,)


@app.route("/conn", methods = ['POST', 'GET'])
def conn():   
    return render_template("connexionAdmin.html")

@app.route("/connexionAdmin", methods = ['post'])
def connexionAdmin():

    login = request.form['login']
    mdp = request.form['password']

    with extract.conn as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Travailleur WHERE login = %s;", (login,))
            res = cur.fetchone()
            if not res:
                return render_template("admin_error.html")
            if res.est_responsable == 't':
                session['admin'] = True
            else:
                session['admin'] = False
            session['id_agence'] = res.id_agence
            session['work_id'] = res.id_travailleur
            user_connected = True
            return redirect(url_for("accueil"))
@app.route("/infoAgence/<int:id_agence>")
def infoAgence(id_agence):
    temp_admin = session.get("admin") is not None
    temp_connected = session.get("user_id") is not None
    temp_user = session.get("work_id") is not None
    agence = session.get("id_agence")
    user_connected = temp_user

    if not temp_admin or agence != id_agence:
        return render_template("trip_error.html", user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)

    with extract.conn as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM clients_en_voyage WHERE id_agence = %s;", (id_agence,))
            res = cur.fetchall()

    with extract.conn as conn2:
        with conn2.cursor() as cur2:
            cur2.execute("SELECT * FROM reservations_en_cours WHERE id_agence = %s;", (id_agence,))
            res2 = cur2.fetchall()

    with extract.conn as conn3:
        with conn3.cursor() as cur3:
            cur3.execute("SELECT semaine, id_agence, count FROM voyages_en_cours WHERE id_agence = %s;", (id_agence,))
            res3 = cur3.fetchall()
    
    with extract.conn as conn4:
        with conn4.cursor() as cur4:
            cur4.execute("SELECT * FROM voyages_en_cours WHERE id_agence = %s;", (id_agence,))
            res4 = cur4.fetchall()

    with extract.conn as conn5:
        with conn5.cursor() as cur5:
            cur5.execute("SELECT * FROM voyages_ouverts_reservation WHERE id_agence = %s;", (id_agence,))
            res5 = cur5.fetchall()
    
    return render_template("agence.html",voyages_open = res5, voyages = res4, reservations = res2, agences = res, user_connected = temp_connected, work_connected=temp_user, work_resp = temp_admin,)

if __name__ == '__main__':
    app.run(debug=True)
