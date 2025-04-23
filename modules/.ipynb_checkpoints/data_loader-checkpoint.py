import streamlit as st
import pandas as pd
import os

@st.cache_data
def load_data(file_path=None):
    if file_path is None:
        file_path = os.path.join(os.getcwd(), 'tarifs_livraison.xlsx')  # Chemin absolu

    try:
        df = pd.read_excel(file_path, sheet_name='Feuil1', header=0)
        df.columns = df.columns.astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des données : {e}")
        return None
