
import extract
import psycopg2
from psycopg2.extras import NamedTupleCursor

def convert_ville(id_city):
    liste_ville = []
    cur_ville = extract.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cur_ville.execute("SELECT nom FROM Ville WHERE id_ville = %s ",id_city)
    for result in cur_ville:
        liste_ville.append(result.nom)
    cur_ville.close()
    return liste_ville[0]
