import psycopg2
import os
from dotenv import load_dotenv

# Idéalement, chargez ces informations depuis des variables d'environnement
# Pour ce test, nous pouvons les mettre ici, mais pour le projet, utilisons .env

load_dotenv() # Charge les variables depuis un fichier .env s'il existe

DB_NAME = os.getenv("DB_NAME", "db_mle")
DB_USER = os.getenv("DB_USER", "odoo")
DB_PASSWORD = os.getenv("DB_PASSWORD", "odoo")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def check_db_connection():
    """Tente de se connecter à la base de données PostgreSQL et affiche la version."""
    conn = None
    try:
        print(f"Tentative de connexion à la base de données {DB_NAME} sur {DB_HOST}:{DB_PORT}...")
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        cur = conn.cursor()
        print("Connexion réussie !")
        cur.execute("SELECT version();")
        db_version = cur.fetchone()
        print(f"Version de PostgreSQL : {db_version[0]}")
        cur.close()
    except psycopg2.Error as e:
        print(f"Erreur lors de la connexion à PostgreSQL : {e}")
    finally:
        if conn:
            conn.close()
            print("Connexion fermée.")

if __name__ == "__main__":
    check_db_connection()
