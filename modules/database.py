import pandas as pd
import math


def get_tarif(destination, poids=None, nombre_palettes=None):
    """
    Calcule le tarif en fonction du type de transport (poids ou palette)
    :param destination: département de destination
    :param poids: poids total en kg (pour le transport au poids)
    :param nombre_palettes: nombre de palettes (pour le transport par palette)
    :return: (tarif_poids, tarif_palette) où l'un des deux est None selon le type de transport
    """
    # 📂 Charger le fichier Excel contenant les tarifs
    try:
        data_poids = pd.read_excel("public/tarifs_livraison.xlsx", sheet_name='Poids')
        data_palettes = pd.read_excel("public/tarifs_livraison.xlsx", sheet_name='Palettes')
        print("Colonnes disponibles dans l'onglet Palettes:", data_palettes.columns.tolist())
    except Exception as e:
        print(f"❌ Erreur lors de l'ouverture du fichier Excel : {e}")
        return None, None

    destination_col = "Destination (département)"
    if destination_col not in data_poids.columns or destination_col not in data_palettes.columns:
        print("⚠️ Colonne des destinations introuvable dans le fichier Excel.")
        return None, None

    # 📊 Calcul du tarif par poids
    tarif_poids = None
    if poids is not None:
        if poids > 3000:
            return "DEVIS", None  # Au-dessus de 3000kg, devis nécessaire
        
        if poids <= 100:
            # Pour les poids ≤ 100kg
            colonnes_poids = {
                (1, 9): "1 à 9",
                (10, 19): "10 à 19",
                (20, 29): "20 à 29",
                (30, 39): "30 à 39",
                (40, 49): "40 à 49",
                (50, 59): "50 à 59",
                (60, 69): "60 à 69",
                (70, 79): "70 à 79",
                (80, 89): "80 à 89",
                (90, 100): "90 à 100"
            }
            
            for (min_val, max_val), col in colonnes_poids.items():
                if min_val <= poids <= max_val:
                    try:
                        tarif_poids = float(data_poids.loc[data_poids[destination_col] == destination, col].values[0])
                        break
                    except (IndexError, ValueError) as e:
                        print(f"⚠️ Erreur lors du calcul du tarif poids : {e}")
                        continue
        else:
            try:
                # Arrondir le poids selon les règles
                if poids <= 1000:
                    poids_arrondi = math.ceil(poids / 10) * 10  # Arrondi aux 10kg
                else:
                    poids_arrondi = math.ceil(poids / 50) * 50  # Arrondi aux 50kg

                # Trouver la bonne colonne de tarif aux 100kg
                if 101 < poids <= 299:
                    col_name = "101 à 299"
                elif 300 <= poids <= 499:
                    col_name = "300 à 499"
                elif 500 <= poids <= 699:
                    col_name = "500 à 699"
                elif 700 <= poids <= 999:
                    col_name = "700 à 999"
                else:  # 1000 < poids <= 3000
                    col_name = "1000 à 3000"

                tarif_100kg = float(data_poids.loc[data_poids[destination_col] == destination, col_name].values[0])
                tarif_poids = tarif_100kg * (poids_arrondi / 100)

            except (IndexError, ValueError) as e:
                print(f"⚠️ Erreur lors du calcul du tarif poids : {e}")

    # 📊 Calcul du tarif par palette
    tarif_palette = None
    if nombre_palettes is not None:
        if nombre_palettes > 5:
            return None, "DEVIS"  # Au-delà de 5 palettes, devis nécessaire
        try:
            # Convertir le numéro de colonne en nombre
            col_palette = int(nombre_palettes)
            print(f"Recherche du tarif pour {nombre_palettes} palette(s)")
            print(f"Destination recherchée : {destination}")
            
            # Vérifier si la colonne existe dans les données
            if col_palette in data_palettes.columns:
                print(f"Valeurs disponibles pour la destination :", data_palettes[data_palettes[destination_col] == destination][col_palette].values)
                tarif_palette = float(data_palettes.loc[data_palettes[destination_col] == destination, col_palette].values[0])
                print(f"Tarif trouvé : {tarif_palette}")
            else:
                print(f"⚠️ Colonne {col_palette} non trouvée dans l'onglet Palettes")
                print(f"Colonnes disponibles : {data_palettes.columns.tolist()}")
        except (IndexError, ValueError) as e:
            print(f"⚠️ Erreur lors du calcul du tarif palette : {e}")

    return tarif_poids, tarif_palette