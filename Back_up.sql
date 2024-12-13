DROP TABLE IF EXISTS client CASCADE;
DROP TABLE IF EXISTS type_etape CASCADE;
DROP TABLE IF EXISTS moyen_transport CASCADE;
DROP TABLE IF EXISTS type_logement CASCADE;
DROP TABLE IF EXISTS Agence CASCADE;
DROP TABLE IF EXISTS langue CASCADE;
DROP TABLE IF EXISTS Travailleur CASCADE;
DROP TABLE IF EXISTS voyage CASCADE;
DROP TABLE IF EXISTS pays CASCADE;
DROP TABLE IF EXISTS Ville CASCADE;
DROP TABLE IF EXISTS logement CASCADE;
DROP TABLE IF EXISTS Etape CASCADE;
DROP TABLE IF EXISTS Participe CASCADE;
DROP TABLE IF EXISTS historique_indicateurs CASCADE;

CREATE TABLE client(
   id_utilisateur serial,
   nom VARCHAR(50) NOT NULL,
   sexe VARCHAR(50) NOT NULL,
   courriel VARCHAR(50) NOT NULL,
   prenom VARCHAR(50) NOT NULL,
   tel VARCHAR(50) NOT NULL,
   adresse VARCHAR(50) NOT NULL,
   age DATE NOT NULL,
   nationnalite VARCHAR(50) NOT NULL,
   mdp TEXT NOT NULL,
   PRIMARY KEY(id_utilisateur)

);

 

CREATE TABLE type_etape(
   id_et_type serial,
   valeur VARCHAR(50) NOT NULL,
   PRIMARY KEY(id_et_type)
);



CREATE TABLE moyen_transport(
   id_transport serial,
   valeur VARCHAR(50) NOT NULL,
   PRIMARY KEY(id_transport)
);



CREATE TABLE type_logement(
   id_type_logement serial,
   valeur VARCHAR(50) NOT NULL,
   PRIMARY KEY(id_type_logement)
);



CREATE TABLE Agence(
   id_agence serial,
   nom VARCHAR(50),
   ville VARCHAR(50),
   telephone int,
   adresse VARCHAR(50),
   PRIMARY KEY(id_agence)
);




CREATE TABLE langue(
   id_langue serial,
   langue VARCHAR(50),
   PRIMARY KEY(id_langue)
);



CREATE TABLE Travailleur(
   id_travailleur serial,
   mdp VARCHAR(50) NOT NULL,
   login VARCHAR(50) NOT NULL,
   id_agence int NOT NULL,
   est_Responsable BOOLEAN NOT NULL,
   PRIMARY KEY(id_travailleur),
   FOREIGN KEY(id_agence) REFERENCES Agence(id_agence) ON DELETE SET NULL
   );

CREATE UNIQUE INDEX uniq_resp_agence ON Travailleur (id_agence) WHERE est_Responsable = TRUE;


CREATE TABLE voyage(
   id_voyage serial,
   reservation BOOLEAN NOT NULL,
   date_reservation_ouverture DATE,
   date_reservation_fermeture DATE,
   date_debut DATE NOT NULL,
   date_de_fin DATE NOT NULL,
   cout_par_personne DECIMAL(6,2) NOT NULL,
   id_agence int NOT NULL,
   PRIMARY KEY(id_voyage),
   FOREIGN KEY(id_agence) REFERENCES Agence(id_agence) ON DELETE SET NULL,
   CONSTRAINT verif_date CHECK ((date_debut < date_de_fin) AND (date_reservation_fermeture<date_debut))
);



CREATE TABLE pays(
   id_pays serial,
   nom VARCHAR(50),
   description text,
   id_langue int NOT NULL,
   PRIMARY KEY(id_pays),
   FOREIGN KEY(id_langue) REFERENCES langue(id_langue) ON DELETE CASCADE
);




CREATE TABLE Ville(
   id_ville serial,
   nom VARCHAR(50) NOT NULL,
   id_pays int NOT NULL,
   PRIMARY KEY(id_ville),
   FOREIGN KEY(id_pays) REFERENCES pays(id_pays) ON DELETE SET NULL
);



CREATE TABLE logement(
   id_logement serial,
   id_ville int NOT NULL,
   id_type_logement int NOT NULL,
   PRIMARY KEY(id_logement),
   FOREIGN KEY(id_ville) REFERENCES Ville(id_ville) ON DELETE SET NULL,
   FOREIGN KEY(id_type_logement) REFERENCES type_logement(id_type_logement) ON DELETE SET NULL
);



CREATE TABLE Etape(
   id_etape serial primary key,
   visa BOOLEAN NOT NULL,
   date_arrivée DATE NOT NULL,
   date_depart DATE NOT NULL,
   id_ville int NOT NULL,
   id_et_type int NOT NULL,
   id_logement int NOT NULL,
   id_transport int NOT NULL,
   id_voyage int NOT NULL,
   FOREIGN KEY(id_ville) REFERENCES Ville(id_ville) ON DELETE CASCADE,
   FOREIGN KEY(id_et_type) REFERENCES type_etape(id_et_type) ON DELETE CASCADE,
   FOREIGN KEY(id_logement) REFERENCES logement(id_logement) ON DELETE SET NULL,
   FOREIGN KEY(id_transport) REFERENCES moyen_transport(id_transport) ON DELETE SET NULL,
   FOREIGN KEY(id_voyage) REFERENCES voyage(id_voyage) ON DELETE CASCADE,
   CONSTRAINT verif_date CHECK (date_arrivée > date_depart)
);

CREATE TABLE participe(
   id_utilisateur int,
   id_voyage int,
   PRIMARY KEY(id_utilisateur, id_voyage),
   FOREIGN KEY(id_utilisateur) REFERENCES client(id_utilisateur) ON DELETE CASCADE,
   FOREIGN KEY(id_voyage) REFERENCES voyage(id_voyage) ON DELETE CASCADE
);

CREATE TABLE historique_indicateurs (
    id_agence INT,
    semaine DATE,
    nb_voyages_en_cours INT,
    nb_voyages_ouverts INT,
    nb_clients_en_voyage INT,
    nb_reservations_en_cours INT,
    PRIMARY KEY (id_agence, semaine)
);

INSERT INTO client(nom, prenom, sexe, courriel, tel, adresse, mdp, age, nationnalite)VALUES
('Bertrand', 'Pierre', 'H', 'bertrand.pierre@gmail.com', '0634828293', '12 rue du cloché','1234', '2000/10/19', 'FRANCE'),
('Cléa', 'Pierre', 'H', 'clea.pierre@gmail.com', '0732549382', '1 avenue Beaubourg','1234', '1995-08-09', 'ESPAGNE'),
('Lore', 'Stamina', 'F', 'lore.stamina@gmail.com', '0692839562', '3 boulevard saint honoré','1234', '2003-10-5', 'PORTUGAL');


INSERT INTO type_etape(valeur)VALUES
('Croisière'),
('Hôtel'),
('Camping');

INSERT INTO moyen_transport(valeur) VALUES
('Train'),
('Avion'),
('Bateau'),
('Voiture');

INSERT INTO type_logement(valeur) VALUES
('Airbnb'),
('Hôtel'),
('Aubgerge');

INSERT INTO Agence(nom,ville,telephone,adresse) VALUES
('Cleo','Metz',0651281474,'10 rue des petits rond'),
('Fram','Nancy',0651284125,'43 rue des roulletes'),
('Covoyage','Paris',0651748274,'51 avenue montagien');

INSERT INTO langue(langue) VALUES
('Anglais'),
('Français'),
('Espagnol'),
('Allemand'),
('Japonais');

INSERT INTO Travailleur(login, mdp, id_agence, est_Responsable) VALUES
('travailleur1', 'mdp1', 2, false),
('travailleur2', 'mdp2', 2, true),
('travailleur3', 'mdp3', 3, true),
('travailleur4', 'mdp4', 2, false),
('travailleur5', 'mdp5', 3, false),
('travailleur6', 'mdp6', 3, false),
('travailleur7', 'mdp7', 2, false),
('travailleur8', 'mdp8', 3, false);


INSERT INTO voyage(reservation, date_debut, date_de_fin, cout_par_personne, id_agence) VALUES
(true, '2024-12-20', '2024-12-29', 1300, 1),
(false, '2024-09-15', '2024-09-29', 1950, 2),
(true, '2025-08-09', '2025-08-25', 1675, 3),
(false, '2024-11-10', '2024-11-22', 1263, 2);

INSERT INTO pays(nom ,description, id_langue) VALUES
('Angleterre', 'Texte presentation 1', 1),
('France' ,'Texte presentation 2', 2),
('Espagne' ,'Texte presentation 3', 3),
('Allemagne', 'Texte presentation 4', 4),
('Japon', 'Texte de presentation 5', 5);

INSERT INTO Ville(nom, id_pays) VALUES
('Paris', 1),
('Londres', 2),
('Madrid', 3);

INSERT INTO logement(id_ville, id_type_logement) VALUES
(2, 1),
(3, 2),
(1, 3);

INSERT INTO Etape(visa, date_depart, date_arrivée, id_ville, id_et_type, id_logement, id_transport, id_voyage) VALUES
(TRUE, '2024/12/20', '2024/12/29', 1, 1, 2, 3, 1),
(TRUE, '2024/01/10', '2025/01/29', 3, 2, 1, 2, 1),
(TRUE, '2025/08/09', '2025/08/19', 1, 1, 2, 1, 3),
(TRUE, '2025/08/20', '2025/08/25', 2, 1, 2, 3, 3),
(TRUE, '2025/08/20', '2025/08/25', 2, 1, 2, 3, 2);

INSERT INTO participe(id_utilisateur, id_voyage) VALUES
(1, 1),
(2, 1),
(2, 2),
(3, 2),
(3, 1),
(3, 4),
(1, 3),
(1, 4);


/*nombre de voyage par semaine*/
CREATE VIEW voyages_en_cours AS
SELECT DATE_PART('week',date_debut)AS semaine,
   id_agence,count(id_voyage) 
FROM voyage 
GROUP BY semaine,id_agence;

/* client par voyage*/
CREATE VIEW clients_en_voyage AS
SELECT DATE_PART('Year',date_debut)AS Annee,
id_agence,COUNT(DISTINCT id_utilisateur),
DATE_PART('week',date_debut)AS semaine 
FROM participe NATURAL JOIN voyage 
GROUP BY annee,semaine,id_agence;

/* nombre de voyage ouvert a reservation par semaine*/
CREATE VIEW voyages_ouverts_reservation AS
SELECT DATE_PART('Year',date_reservation_ouverture)AS Annee,
   id_agence,COUNT(DISTINCT id_voyage),
   DATE_PART('week',date_reservation_ouverture)AS semaine 
FROM participe NATURAL JOIN voyage WHERE reservation = TRUE 
GROUP BY Annee,semaine,id_agence;

/* nombre de client reservation voyage*/
CREATE VIEW reservations_en_cours AS
SELECT  id_agence,
   count(DISTINCT id_utilisateur)AS nb_reservation,
   DATE_PART('week',date_reservation_ouverture)AS semaine,
   DATE_PART('year',date_reservation_ouverture)AS annee  
FROM participe NATURAL JOIN voyage  
GROUP BY id_agence,semaine,annee;
