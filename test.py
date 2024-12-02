import extract
import psycopg2
from psycopg2.extras import NamedTupleCursor
from flask import Flask, render_template, request, redirect, url_for, session

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

    return liste_voyage

def ville(id_city):
    liste_ville = []
    cur_ville = extract.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cur_ville.execute("SELECT nom FROM Ville WHERE id_ville = %s ",id_city)
    for result in cur_ville:
        liste_ville.append(result.nom)
    cur_ville.close()
    return liste_ville
print(voyage())
print(ville("1"))
extract.conn.close()