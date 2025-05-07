import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
OUTPUT_FILE = OUTPUT_DIR / "sales_data_raw.csv"

def get_db_connection():
    """Établit et retourne une connexion à la base de données PostgreSQL."""
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        logging.info(f"Connecté à la base de données '{DB_NAME}' avec succès.")
        return conn
    except psycopg2.Error as e:
        logging.error(f"Erreur lors de la connexion à PostgreSQL : {e}")
        raise

def extract_sales_data(conn):
    """Extrait les données de ventes de la base de données."""
    # Note: Pour les champs JSON comme pt.name, vous devrez peut-être ajuster
    # l'extraction en fonction de la langue, ex: pt.name->>'en_US' AS product_name
    # ou utiliser une fonction pour obtenir la traduction par défaut si Odoo le permet.
    # Pour l'instant, nous supposons une structure simple ou que la première clé est la bonne.
    query = """
    SELECT
        sol.id AS sale_order_line_id,
        so.date_order,
        so.partner_id AS customer_id,
        rp.name AS customer_name,
        sol.product_id,        
        COALESCE(pt.name->>'fr_FR', pt.name->>'en_US') AS product_name, -- Tente 'fr_FR' puis 'en_US'
        pp.default_code AS product_default_code,
        pc.name AS product_category_name, -- product_category.name est probablement un champ texte standard
        sol.product_uom_qty AS quantity,
        sol.price_unit,
        sol.discount,
        sol.price_subtotal,
        sol.price_total,
        so.state AS order_state,
        so.name AS order_reference
    FROM
        sale_order_line sol
    JOIN
        sale_order so ON sol.order_id = so.id
    JOIN
        res_partner rp ON so.partner_id = rp.id
    JOIN
        product_product pp ON sol.product_id = pp.id
    JOIN
        product_template pt ON pp.product_tmpl_id = pt.id
    LEFT JOIN
        product_category pc ON pt.categ_id = pc.id
    WHERE
        so.state IN ('sale', 'done') AND (sol.display_type IS NULL OR sol.display_type = 'line');
    """
    logging.info("Exécution de la requête d'extraction des données de ventes...")
    df = pd.read_sql_query(query, conn)
    logging.info(f"{len(df)} lignes de ventes extraites.")
    return df

if __name__ == "__main__":
    conn = None
    try:
        conn = get_db_connection()
        sales_df = extract_sales_data(conn)

        # S'assurer que le répertoire de sortie existe
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        sales_df.to_csv(OUTPUT_FILE, index=False)
        logging.info(f"Données de ventes sauvegardées dans : {OUTPUT_FILE}")

    except Exception as e:
        logging.error(f"Une erreur est survenue dans le script principal : {e}")
    finally:
        if conn:
            conn.close()
            logging.info("Connexion à la base de données fermée.")