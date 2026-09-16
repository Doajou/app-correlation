import streamlit as st
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Guess the Correlation", layout="wide")

# Paramètres de la partie (10 graphiques en .png)
VRAIS_R2 = [0.33, 0.53, 0.58, 0.41, 0.73, 0.99, 0.78, 0.64, 0.03, 0.26]
GRAPHIQUES = [
    {"image": f"g{i+1}.png", "vrai_r": r2} 
    for i, r2 in enumerate(VRAIS_R2)
]

# ---------------------------------------------------------
# STOCKAGE CENTRALISÉ (PARTAGÉ ENTRE TOUS LES APPAREILS)
# ---------------------------------------------------------
@st.cache_resource
def get_global_database():
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
        st.write("Proposez une valeur de $R^2$ pour chaque graphique :")
        
        estimations = []
        
        for i, item in enumerate(GRAPHIQUES):
            st.markdown(f"### Graphique {i+1}")
            
            try:
                st.image(item["image"], use_container_width=True)
            except Exception:
                st.warning(f"Image '{item['image']}' non trouvée sur GitHub.")
            
            val = st.slider(
                f"Estimation de $R^2$ (Graphique {i+1}) :", 
                min_value=0.00, 
                max_value=1.00, 
                value=0.00, 
                step=0.01, 
                key=f"g_{i}"
            )
            estimations.append(val)
            st.divider()
        
        if st.button("Envoyer mes réponses 🚀", type="primary"):
            score_total = 0
            for est, item in zip(estimations, GRAPHIQUES):
                ecart = abs(est - item["vrai_r"])
                pts = max(0, int(round(100 * (1 - ecart))))
                score_total += pts
            
            scores_db[pseudo] = score_total
            st.success(f"Réponses enregistrées ! Votre score total : **{score_total} pts / 1000**")

# ---------------------------------------------------------
# MODE 2 : ÉCRAN PROJETÉ (VIDÉOPROJECTEUR)
# ---------------------------------------------------------
else:
    st.title("🏆 Classement en direct")
    
    if scores_db:
        df = pd.DataFrame(
            list(scores_db.items()), 
            columns=["Élève", "Score Total (/1000)"]
        )
        df = df.sort_values(by="Score Total (/1000)", ascending=False).reset_index(drop=True)
        df.index += 1  # Rang à partir de 1
        
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.info("En attente des premières réponses des élèves...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Rafraîchir le classement"):
            st.rerun()
    with col2:
        if st.button("🗑️ Réinitialiser le classement"):
            scores_db.clear()
            st.rerun()