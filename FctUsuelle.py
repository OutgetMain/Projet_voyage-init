
import extract
import psycopg2
from psycopg2.extras import NamedTupleCursor


def convert(id, query, param_name):
    """ 
    Convertit une requête SQL en récupérant la valeur désirée.
    
    :param id: Identifiant ou paramètre de la requête SQL
    :param query: Requête SQL paramétrée (avec %s pour les placeholders)
    :param param_name: Nom de la colonne contenant la valeur à extraire
    :return: La première valeur trouvée ou None si aucun résultat
    """
    with extract.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur:
        cur.execute(query, (id,))  # Utilisation sécurisée des paramètres
        result = cur.fetchone()  # Récupérer seulement la première ligne
        return getattr(result, param_name, None) if result else None

def verif_chevauchement(id,date_debut,date_fin):

        query = """
            SELECT participe.id_utilisateur, participe.id_voyage
            FROM participe 
            JOIN voyage ON participe.id_voyage = voyage.id_voyage
            WHERE participe.id_utilisateur = %s 
            AND (
                ((date_debut <= %s AND %s <= date_de_fin) AND (date_de_fin <= %s)) -- Cas 1
                OR
                ((date_debut <= %s) AND (date_de_fin >= %s))                       -- Cas 2
                OR
                ((date_debut >= %s) AND (%s >= date_debut AND date_de_fin >= %s))  -- Cas 3
            );         

            """
        
        with extract.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur_verif:
            cur_verif.execute(query, (
                id,
                date_debut,date_debut, date_fin,
                date_debut, date_fin,
                date_debut, date_fin,date_fin
            ))
            return cur_verif.fetchall()
        
def reserver_voyage(id_client, id_voyage):
    with extract.conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor) as cur_reserve:
        cur_reserve.execute("SELECT date_debut, date_de_fin FROM voyage WHERE id_voyage = %s", (id_voyage,))
        voyage = cur_reserve.fetchone()
        print(voyage.date_debut,voyage.date_de_fin)
        temp = verif_chevauchement(id_client, voyage.date_debut, voyage.date_de_fin)
        if temp :
            raise Exception("Chevauchement détecté. Réservation impossible.")
        
        cur_reserve.execute("INSERT INTO participe (id_utilisateur, id_voyage) VALUES (%s, %s)", (id_client, id_voyage))

