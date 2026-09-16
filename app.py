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
    
    # Vérification si l'élève a déjà soumis une réponse active
    already_submitted = st.session_state.get("submitted_pseudo", None)
    
    # Si le classement a été réinitialisé par l'enseignant, on débloque l'élève
    if already_submitted and already_submitted not in scores_db:
        st.session_state.submitted_pseudo = None
        already_submitted = None

    # CAS 1 : L'élève a déjà envoyé ses réponses
    if already_submitted and already_submitted in scores_db:
        st.success(f"✅ Réponses enregistrées pour **{already_submitted}** !")
        st.info(f"Votre score actuel : **{scores_db[already_submitted]} pts / 1000**.\n\nAttendez la réinitialisation du classement par l'enseignant pour rejouer.")
    
    # CAS 2 : L'élève n'a pas encore soumis
    else:
        pseudo = st.text_input("Entrez votre Prénom (oui, le prénom, pas un pseudo) :", key="user_pseudo")
        
        if pseudo:
            pseudo_clean = pseudo.strip()
            
            # Anti-triche : empêche d'utiliser le prénom d'un élève ayant déjà soumis
            if pseudo_clean in scores_db:
                st.warning(f"⚠️ Le prénom **{pseudo_clean}** a déjà envoyé ses réponses. Attendez le prochain tour !")
            else:
                st.subheader(f"Bonjour {pseudo_clean} !")
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
                    
                    # Enregistrement du score et verrouillage de la session
                    scores_db[pseudo_clean] = score_total
                    st.session_state.submitted_pseudo = pseudo_clean
                    st.rerun()

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
        df.index += 1
        
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