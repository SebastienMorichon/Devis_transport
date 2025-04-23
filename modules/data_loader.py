import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data(file_path=None):
    if file_path is None:
        file_path = os.path.join(os.getcwd(), 'public/tarifs_livraison.xlsx')  # Chemin absolu

    try:
        # Afficher les noms des feuilles disponibles 
        xls = pd.ExcelFile(file_path)
        #st.write("Feuilles disponibles dans le fichier Excel :", xls.sheet_names)
        
        # Charger les deux feuilles
        df_poids = pd.read_excel(file_path, sheet_name='Poids', header=0)  # Première feuille
        df_palettes = pd.read_excel(file_path, sheet_name='Palettes', header=0)  # Deuxième feuille
        
        # Nettoyer les noms de colonnes
        df_poids.columns = df_poids.columns.astype(str).str.strip()
        df_palettes.columns = df_palettes.columns.astype(str).str.strip()
        
        return df_poids, df_palettes
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return None, None
