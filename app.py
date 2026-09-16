import streamlit as st
import pandas as pd
import numpy as np

# Configuration de la page
st.set_page_config(page_title="Guess the Correlation", layout="wide")

# Paramètres de la partie (À modifier selon vos graphiques)
VRAIS_R = [0.82, -0.45, 0.15, -0.90]  # Vos valeurs réelles pour chaque graphique
NB_QUESTIONS = len(VRAIS_R)

# Initialisation de la base de données en mémoire
if "scores_db" not in st.session_state:
    st.session_state.scores_db = {}

# Barre latérale : Commutateur Vue Élève / Vue Enseignant
mode = st.sidebar.radio("Mode d'affichage", ["Smartphone Élève", "Écran Projeté (Classement)"])

# ---------------------------------------------------------
# MODE 1 : INTERFACE SmartPhone ÉLÈVE
# ---------------------------------------------------------
if mode == "Smartphone Élève":
    st.title("📊 Guess the Correlation")
    
    pseudo = st.text_input("Entrez votre Prénom ou Pseudo :", key="user_pseudo")
    
    if pseudo:
        st.subheader(f"Bonjour {pseudo} !")
        st.write("Proposez une valeur de $r$ pour chaque graphique :")
        
        estimations = []
        for i in range(NB_QUESTIONS):
            val = st.slider(
                f"Graphique {i+1} :", 
                min_value=-1.00, 
                max_value=1.00, 
                value=0.00, 
                step=0.01, 
                key=f"g_{i}"
            )
            estimations.append(val)
        
        if st.button("Envoyer mes réponses 🚀", type="primary"):
            # Calcul du score global
            score_total = 0
            for est, vrai in zip(estimations, VRAIS_R):
                ecart = abs(est - vrai)
                pts = max(0, int(round(100 * (1 - ecart))))
                score_total += pts
            
            # Sauvegarde du score de l'élève
            st.session_state.scores_db[pseudo] = score_total
            st.success(f"Réponses enregistrées ! Votre score total : **{score_total} pts**")

# ---------------------------------------------------------
# MODE 2 : ÉCRAN PROJETÉ (VIDÉOPROJECTEUR)
# ---------------------------------------------------------
else:
    st.title("🏆 Classement en direct")
    
    if st.session_state.scores_db:
        # Conversion du dictionnaire en DataFrame Pandas
        df = pd.DataFrame(
            list(st.session_state.scores_db.items()), 
            columns=["Élève", "Score Total"]
        )
        df = df.sort_values(by="Score Total", ascending=False).reset_index(drop=True)
        df.index += 1  # Pour commencer le rang à 1 au lieu de 0
        
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.info("En attente des premières réponses des élèves...")
    
    if st.button("🔄 Rafraîchir le classement"):
        st.rerun()