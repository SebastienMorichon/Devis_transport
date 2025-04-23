import streamlit as st
from pages.devis_expedition import show_devis_expedition


st.set_page_config(page_title="Application B2B", page_icon="📦", layout="wide")

# 📌 Menu de navigation personnalisé
st.sidebar.markdown("📌 **Navigation**")


page = st.sidebar.radio("Choisissez une section :", ["Devis Expédition"])


# Affichage du contenu en fonction de la section choisie
if page == "Devis Expédition":
    try:
        show_devis_expedition()
    except Exception as e:
        st.error(f"Erreur lors de l'affichage du devis : {str(e)}")
