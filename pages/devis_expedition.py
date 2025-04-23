import streamlit as st
import math
import pandas as pd
from modules.database import get_tarif
from modules.scraper import get_cnr_index
from modules.data_loader import load_data

# 📌 Constantes pour le nombre de coffrets par palette
COFFRETS_PAR_PALETTE = {
    "Coffret S": 175,
    "Coffret M": 150
}

# 📌 Coût fixe de palettisation ESAT par palette
COUT_PALETTISATION_ESAT = 45  # euros par palette

def convert_to_float(value):
    """ Convertit une valeur en float, retourne 0.00 si impossible. """
    try:
        return float(str(value).replace(" €", "").replace(",", "."))
    except ValueError:
        st.error(f"❌ Erreur de conversion en float : {value} (Type: {type(value)})")
        return 0.00  # Valeur par défaut en cas d'erreur

def calculate_tarif_poids(poids_total, tarif_100kg):
    """
    Calcule le tarif total selon les règles suivantes :
    - Au-dessus de 100kg : prix aux 100kg avec arrondi aux 10kg
    - Au-dessus de 3000kg : prix aux 100kg avec arrondi aux 50kg
    """
    if poids_total <= 100:
        return tarif_100kg  # Pour les poids ≤ 100kg, on utilise directement le tarif

    # Arrondi du poids selon les règles
    if poids_total > 3000:
        # Arrondi aux 50kg
        poids_arrondi = math.ceil(poids_total / 50) * 50
    else:
        # Arrondi aux 10kg
        poids_arrondi = math.ceil(poids_total / 10) * 10

    # Calcul du nombre de centaines de kg
    nb_centaines = poids_arrondi / 100
    
    # Calcul du tarif total
    return nb_centaines * tarif_100kg

def get_tarif_depuis_excel(destination, poids_total, data):
    """ Recherche le tarif applicable en fonction de la destination et du poids total dans le fichier de tarifs. """
    destination_col = "Destination (département)"
    
    # Pour les poids > 100kg, chercher dans les colonnes de prix aux 100kg
    if poids_total > 100:
        # Arrondi aux 10kg ou 50kg selon le poids
        if poids_total > 3000:
            poids_arrondi = math.ceil(poids_total / 50) * 50
        else:
            poids_arrondi = math.ceil(poids_total / 10) * 10
            
        # Sélection de la colonne de tarif appropriée
        if poids_arrondi <= 300:
            col_name = "300"
        elif poids_arrondi <= 500:
            col_name = "500"
        elif poids_arrondi <= 700:
            col_name = "700"
        elif poids_arrondi <= 1000:
            col_name = "1000"
        else:
            col_name = "3000"
            
        try:
            # Récupérer le tarif aux 100kg
            tarif_100kg = float(data.loc[data[destination_col] == destination, col_name].values[0])
            # Calculer le prix total : (poids/100) × prix_100kg
            return (poids_arrondi / 100) * tarif_100kg
        except (IndexError, ValueError, KeyError) as e:
            print(f"Erreur lors du calcul du tarif : {e}")
            return None
            
    else:
        # Pour les poids ≤ 100kg, chercher dans les colonnes spécifiques
        for col in data.columns:
            if col == destination_col:
                continue
            try:
                if '-' in col:
                    min_val, max_val = map(int, col.split('-'))
                    if min_val <= poids_total <= max_val:
                        return float(data.loc[data[destination_col] == destination, col].values[0])
            except:
                continue
    
    return None

def show_devis_expedition():
    st.title('📦 Calculateur de Frais de Livraison')

    # 📌 Récupération de l'indice CNR
    cnr_index = get_cnr_index()
    st.markdown(f"### 📊 Indice CNR actuel : **{cnr_index}**")

    # 📌 Chargement des tarifs de livraison
    data_poids, data_palettes = load_data()
    if data_poids is None or data_palettes is None:
        return


    # 📌 Sélection de la destination
    destination_col = "Destination (département)"
    if destination_col in data_poids.columns:
        destination = st.selectbox('📍 Destination', options=data_poids[destination_col].dropna().unique())
    else:
        st.error("⚠️ Colonne des destinations introuvable dans le fichier Excel.")
        return

    with st.form("expedition_form"):
        # Informations communes
        selected_carton = st.selectbox("📦 Type de coffret", options=list(COFFRETS_PAR_PALETTE.keys()))
        nombre_colis = st.number_input('📦 Nombre de coffrets', min_value=1, max_value=1000, value=1, step=1)
        poids_colis = st.number_input('⚖ Poids par coffret (kg)', min_value=0.1, max_value=100.0, value=1.0, step=0.1)
        
        calculate_button = st.form_submit_button("🧮 Calculer les tarifs")

    if calculate_button:
        if not destination:
            st.error("Veuillez entrer une destination.")
            return
            
        print("=== Début du calcul des tarifs ===")
        # Calcul des informations communes
        poids_total = poids_colis * nombre_colis
        coffrets_par_palette = COFFRETS_PAR_PALETTE[selected_carton]
        nombre_palettes = math.ceil(nombre_colis / coffrets_par_palette)
        cout_palettisation = nombre_palettes * COUT_PALETTISATION_ESAT
        print(f"Informations calculées : poids={poids_total}, palettes={nombre_palettes}, cout_palettisation={cout_palettisation}")
            
        # Calcul des deux options de tarification
        tarif_poids, tarif_palette = get_tarif(
            destination=destination,
            poids=poids_total,
            nombre_palettes=nombre_palettes
        )
        print(f"Tarifs obtenus : poids={tarif_poids}, palette={tarif_palette}")

        # Affichage des deux options
        st.markdown("### 🔄 Options de tarification disponibles")
        col1, col2 = st.columns(2)
        
        # Variables pour stocker les totaux
        total_poids = None
        total_palette = None
        
        with col1:
            st.markdown("### Option 1 : Tarification par poids")
            if isinstance(tarif_poids, str) and tarif_poids == "DEVIS":
                st.warning("⚠️ Pour un poids supérieur à 3000kg, veuillez contacter le service commercial pour un devis personnalisé")
            elif tarif_poids is not None:
                # Calcul de l'ajustement CNR
                CNR_BASE = 184.12
                ajustement_cnr = tarif_poids * (cnr_index - CNR_BASE) / CNR_BASE
                total_poids = tarif_poids + cout_palettisation + ajustement_cnr
                
                st.markdown(f"📦 **Poids total :** {poids_total} kg")
                st.markdown(f"🎯 **Nombre de palettes nécessaires :** {nombre_palettes}")
                st.markdown(f"💰 **Coût transport initial :** {round(tarif_poids, 2)} €")
                st.markdown(f"📈 **Ajustement CNR ({round(cnr_index, 2)}) :** {round(ajustement_cnr, 2)} €")
                st.markdown(f"🏭 **Coût palettisation ESAT :** {cout_palettisation} €")
                st.markdown(f"💶 **Total :** {round(total_poids, 2)} €")
            else:
                st.warning("⚠️ Tarification par poids non disponible")

        with col2:
            st.markdown("### Option 2 : Tarification par palette")
            if isinstance(tarif_palette, str) and tarif_palette == "DEVIS":
                st.warning("⚠️ Au-delà de 5 palettes, veuillez contacter le service commercial pour un devis personnalisé")
            elif tarif_palette is not None:
                # Calcul de l'ajustement CNR
                CNR_BASE = 184.12
                ajustement_cnr = tarif_palette * (cnr_index - CNR_BASE) / CNR_BASE
                total_palette = tarif_palette + cout_palettisation + ajustement_cnr
                
                st.markdown(f"📦 **Nombre de palettes :** {nombre_palettes}")
                st.markdown(f"ℹ️ **Capacité d'une palette :** {coffrets_par_palette} coffrets")
                st.markdown(f"💰 **Coût transport initial :** {round(tarif_palette, 2)} €")
                st.markdown(f"📈 **Ajustement CNR ({round(cnr_index, 2)}) :** {round(ajustement_cnr, 2)} €")
                st.markdown(f"🏭 **Coût palettisation ESAT :** {cout_palettisation} €")
                st.markdown(f"💶 **Total :** {round(total_palette, 2)} €")
            else:
                st.warning("⚠️ Tarification par palette non disponible")

       