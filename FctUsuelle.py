
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
