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
    return {
        "scores": {},        # {pseudo: score_total}
        "responses": {},     # {pseudo: [val_g1, val_g2, ...]}
        "show_correction": False
    }

db = get_global_database()

# Barre latérale : Commutateur Vue Élève / Vue Enseignant
mode = st.sidebar.radio("Mode d'affichage", ["Smartphone Élève", "Écran Projeté (Classement)"])

# ---------------------------------------------------------
# MODE 1 : INTERFACE SMARTPHONE ÉLÈVE
# ---------------------------------------------------------
if mode == "Smartphone Élève":
    st.title("📊 Trouvez la bonne valeur du $R^2$")
    
    already_submitted = st.session_state.get("submitted_pseudo", None)
    
    # Si le classement a été réinitialisé, on débloque l'élève
    if already_submitted and already_submitted not in db["scores"]:
        st.session_state.submitted_pseudo = None
        already_submitted = None

    # CAS 1 : LA CORRECTION EST ACTIVÉE PAR L'ENSEIGNANT
    if db["show_correction"]:
        st.header("📝 Correction détaillée")
        
        if already_submitted and already_submitted in db["responses"]:
            st.subheader(f"Résultats de **{already_submitted}** (Score : {db['scores'][already_submitted]} pts)")
            
            user_res = db["responses"][already_submitted]
            data_corr = []
            for i, item in enumerate(GRAPHIQUES):
                est = user_res[i]
                vrai = item["vrai_r"]
                ecart = abs(est - vrai)
                pts = max(0, int(round(100 * (1 - ecart))))
                data_corr.append({
                    "Graphique": f"G{i+1}",
                    "Votre réponse": f"{est:.2f}",
                    "Vraie valeur R²": f"{vrai:.2f}",
                    "Écart": f"{ecart:.2f}",
                    "Points": f"{pts} pts"
                })
            
            st.dataframe(pd.DataFrame(data_corr), use_container_width=True, hide_index=True)
        else:
            st.info("La correction est affichée au tableau. Vous n'avez pas soumis de réponses pour cette session.")

    # CAS 2 : ÉLÈVE AYANT DÉJÀ SOUMIS (EN ATTENTE DE CORRECTION)
    elif already_submitted and already_submitted in db["scores"]:
        st.success(f"✅ Réponses enregistrées pour **{already_submitted}** !")
        st.info(f"Votre score actuel : **{db['scores'][already_submitted]} pts / 1000**.\n\nEn attente de la correction par l'enseignant...")

    # CAS 3 : FORMULAIRE DE Saisie
    else:
        pseudo = st.text_input("Entrez votre Prénom (oui, le prénom, pas un pseudo) :", key="user_pseudo")
        
        if pseudo:
            pseudo_clean = pseudo.strip()
            
            if pseudo_clean in db["scores"]:
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
                    
                    db["scores"][pseudo_clean] = score_total
                    db["responses"][pseudo_clean] = estimations
                    st.session_state.submitted_pseudo = pseudo_clean
                    st.rerun()

# ---------------------------------------------------------
# MODE 2 : ÉCRAN PROJETÉ (VIDÉOPROJECTEUR)
# ---------------------------------------------------------
else:
    st.title("🏆 Classement en direct")
    
    if db["scores"]:
        df = pd.DataFrame(
            list(db["scores"].items()), 
            columns=["Élève", "Score Total (/1000)"]
        )
        df = df.sort_values(by="Score Total (/1000)", ascending=False).reset_index(drop=True)
        df.index += 1
        
        st.dataframe(df, use_container_width=True, height=300)
    else:
        st.info("En attente des premières réponses des élèves...")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Rafraîchir"):
            st.rerun()
    with col2:
        btn_label = "🙈 Masquer la correction" if db["show_correction"] else "👁️ Afficher la correction"
        if st.button(btn_label):
            db["show_correction"] = not db["show_correction"]
            st.rerun()
    with col3:
        if st.button("🗑️ Réinitialiser tout"):
            db["scores"].clear()
            db["responses"].clear()
            db["show_correction"] = False
            st.rerun()

    # SECTION CORRECTION AU TABLEAU
    if db["show_correction"]:
        st.divider()
        st.subheader("📊 Correction générale (Moyenne de la classe vs Vraie valeur)")
        
        if db["responses"]:
            all_resp = list(db["responses"].values())
            df_resp = pd.DataFrame(all_resp, columns=[f"G{i+1}" for i in range(len(GRAPHIQUES))])
            moyennes = df_resp.mean().round(2)
            
            corr_summary = []
            for i, item in enumerate(GRAPHIQUES):
                vrai = item["vrai_r"]
                moy_class = moyennes[i]
                ecart_moyen = abs(moy_class - vrai)
                corr_summary.append({
                    "Graphique": f"Graphique {i+1}",
                    "Vraie valeur R²": vrai,
                    "Moyenne de la classe": moy_class,
                    "Écart moyen": round(ecart_moyen, 2)
                })
            
            st.dataframe(pd.DataFrame(corr_summary), use_container_width=True, hide_index=True)
        else:
            st.info("Aucune réponse enregistrée pour calculer la moyenne de la classe.")