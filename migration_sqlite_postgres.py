import sqlite3
import psycopg2
from psycopg2 import sql
import os

# Connexion à la base SQLite locale
sqlite_conn = sqlite3.connect("ma_base.sqlite")
sqlite_cursor = sqlite_conn.cursor()

# Récupération de la database URL depuis l'environnement (Render la fournit)
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise Exception("DATABASE_URL non défini.")

# Connexion PostgreSQL via l'URL (pas de paramètre port séparé)
pg_conn = psycopg2.connect(database_url, sslmode='require')
pg_cursor = pg_conn.cursor()

# Récupérer toutes les tables SQLite
sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in sqlite_cursor.fetchall()]

for table in tables:
    print(f"Migration de la table : {table}")

    # Récupérer la structure de la table dans SQLite
    sqlite_cursor.execute(sql.SQL("PRAGMA table_info({})").format(sql.Identifier(table)))
    columns_info = sqlite_cursor.fetchall()
    column_names = [col[1] for col in columns_info]

    # Créer la table dans PostgreSQL avec colonnes en TEXT (simplification)
    columns_pg = sql.SQL(", ").join(
        sql.SQL("{} TEXT").format(sql.Identifier(name)) for name in column_names
    )
    create_query = sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
        sql.Identifier(table),
        columns_pg
    )
    pg_cursor.execute(create_query)
    pg_conn.commit()

    # Récupérer les données SQLite
    sqlite_cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(table)))
    rows = sqlite_cursor.fetchall()

    # Insérer les données dans PostgreSQL
    for row in rows:
        insert_query = sql.SQL("INSERT INTO {} ({}) VALUES ({})").format(
            sql.Identifier(table),
            sql.SQL(', ').join(map(sql.Identifier, column_names)),
            sql.SQL(', ').join(sql.Placeholder() * len(row))
        )
        pg_cursor.execute(insert_query, row)
    pg_conn.commit()

# Fermeture des connexions
sqlite_conn.close()
pg_cursor.close()
pg_conn.close()

print("Migration terminée avec succès.")
  