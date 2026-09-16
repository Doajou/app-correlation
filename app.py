import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Guess the Correlation", layout="wide")

# Paramètres de la partie (À modifier selon vos graphiques)
VRAIS_R = [0.33, 0.53, 0.58, 0.41, 0.73, 0.99, 0.78, 0.64, 0.03, 0.26]  # Vos valeurs réelles
NB_QUESTIONS = len(VRAIS_R)

# ---------------------------------------------------------
# STOCKAGE CENTRALISÉ (PARTAGÉ ENTRE TOUS LES APPAREILS)
# ---------------------------------------------------------
@st.cache_resource
def get_global_database():
    # Ce dictionnaire est partagé par tous les utilisateurs de l'application
    return {}

scores_db = get_global_database()

# Barre latérale : Commutateur Vue Élève / Vue Enseignant
mode = st.sidebar.radio("Mode d'affichage", ["Smartphone Élève", "Écran Projeté (Classement)"])

# ---------------------------------------------------------
# MODE 1 : INTERFACE SMARTPHONE ÉLÈVE
# ---------------------------------------------------------
if mode == "Smartphone Élève":
    st.title("📊 Trouvez la bonne valeur du $R^2$")
    
    pseudo = st.text_input("Entrez votre Prénom (oui, le prénom, pas un pseudo):", key="user_pseudo")
    
    if pseudo:
        st.subheader(f"Bonjour {pseudo} !")
        st.write("Proposez une valeur de $r$ pour chaque graphique :")
        
        estimations = []
        for i in range(NB_QUESTIONS):
            val = st.slider(
                f"Graphique {i+1} :", 
                min_value=0.00, 
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
            
            # Sauvegarde dans la base partagée
            scores_db[pseudo] = score_total
            st.success(f"Réponses enregistrées ! Votre score total : **{score_total} pts**")

# ---------------------------------------------------------
# MODE 2 : ÉCRAN PROJETÉ (VIDÉOPROJECTEUR)
# ---------------------------------------------------------
else:
    st.title("🏆 Classement en direct")
    
    if scores_db:
        # Conversion du dictionnaire partagé en DataFrame Pandas
        df = pd.DataFrame(
            list(scores_db.items()), 
            columns=["Élève", "Score Total"]
        )
        df = df.sort_values(by="Score Total", ascending=False).reset_index(drop=True)
        df.index += 1  # Rang à partir de 1
        
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.info("En attente des premières réponses des élèves...")
    
    if st.button("🔄 Rafraîchir le classement"):
        st.rerun()