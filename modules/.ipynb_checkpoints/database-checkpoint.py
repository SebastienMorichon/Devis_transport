import sqlite3
import pandas as pd

def connect_db():
    conn = sqlite3.connect("devis.db")
    cursor = conn.cursor()
    
    # Création de la table des cartons
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cartons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            longueur INTEGER NOT NULL,
            largeur INTEGER NOT NULL,
            hauteur INTEGER NOT NULL
        )
    ''')
    
    # Création de la table des devis
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            nombre_colis INTEGER NOT NULL,
            poids_total REAL NOT NULL,
            type_transport TEXT NOT NULL,
            carton_utilise TEXT NOT NULL,
            nombre_palettes INTEGER NOT NULL,
            prix_unitaire REAL NOT NULL,
            total REAL NOT NULL
        )
    ''')
    
    # Création de la table des tarifs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarifs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            poids_min REAL NOT NULL,
            poids_max REAL NOT NULL,
            tarif REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_carton(nom, longueur, largeur, hauteur):
    conn = sqlite3.connect("devis.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cartons (nom, longueur, largeur, hauteur) VALUES (?, ?, ?, ?)", 
                   (nom, longueur, largeur, hauteur))
    conn.commit()
    conn.close()

def get_cartons():
    conn = sqlite3.connect("devis.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, nom, longueur, largeur, hauteur FROM cartons")
    cartons = cursor.fetchall()
    conn.close()
    return cartons

def delete_carton(carton_id):
    conn = sqlite3.connect("devis.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cartons WHERE id = ?", (carton_id,))
    conn.commit()
    conn.close()
    
def get_devis():
    conn = sqlite3.connect("devis.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, destination, nombre_colis, poids_total, type_transport, 
               carton_utilise, nombre_palettes, prix_unitaire, total 
        FROM devis
    """)
    devis = cursor.fetchall()
    conn.close()
    
    # 🛠️ Correction : On garde prix_unitaire et total en float et on les formate seulement à l'affichage
    devis_list = []
    for d in devis:
        devis_list.append({
            "ID": d[0],
            "Destination": d[1],
            "Carton": d[5],  # Vérifie que carton_utilise est bien en position 5
            "Quantité": d[2],
            "Poids total (kg)": d[3],
            "Type livraison": d[4],
            "Palettes": d[6],
            "Tarif unitaire (€)": float(d[7]),  # ✅ On garde en float
            "Total (€)": float(d[8])  # ✅ On garde en float
        })
    
    return devis_list


def add_devis(destination, nombre_colis, poids_total, type_transport, carton_utilise, nombre_palettes, prix_unitaire, total):
    conn = sqlite3.connect("devis.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO devis (destination, nombre_colis, poids_total, type_transport, carton_utilise, nombre_palettes, prix_unitaire, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (destination, nombre_colis, poids_total, type_transport, carton_utilise, nombre_palettes, prix_unitaire, total))
    conn.commit()
    conn.close()
def delete_devis(devis_id):
    conn = sqlite3.connect("devis.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM devis WHERE id = ?", (devis_id,))
    conn.commit()
    conn.close()
    
def get_tarif(destination, poids):
    # 📂 Charger le fichier Excel contenant les tarifs
    try:
        data = pd.read_excel("tarifs_livraison.xlsx")
    except Exception as e:
        print(f"❌ Erreur lors de l'ouverture du fichier Excel : {e}")
        return None

    # 📌 Vérification de la colonne des destinations
    destination_col = "Destination (département)"
    if destination_col not in data.columns:
        print("⚠️ Colonne des destinations introuvable dans le fichier Excel.")
        return None

    # 📊 Récupération de toutes les plages de poids
    weight_ranges = [col for col in data.columns if col != destination_col]

    # 🔍 Recherche de la plage de poids correspondante
    weight_range = None
    for col in weight_ranges:
        if 'à' in col:
            try:
                limits = list(map(int, col.split(' à ')))  # Convertir "0 à 10" en [0, 10]
                if limits[0] <= poids <= limits[1]:
                    weight_range = col
                    break
            except ValueError:
                continue

    if weight_range:
        try:
            tarif = data.loc[data[destination_col] == destination, weight_range].values[0]
            return float(tarif)
        except (IndexError, ValueError):
            print(f"⚠️ Aucun tarif trouvé pour {destination} avec {poids} kg dans {weight_range}")
            return None

    print(f"⚠️ Aucun tarif correspondant pour {poids} kg")
    return None


# Initialisation de la base de données au lancement
connect_db()