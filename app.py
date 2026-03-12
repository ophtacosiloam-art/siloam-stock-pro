import streamlit as st
import pandas as pd
import hashlib
from datetime import datetime
from supabase import create_client, Client

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Siloam Stock Pro",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #F7F8FC; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0A2540 0%, #0D3260 100%);
    border-right: none;
}
[data-testid="stSidebar"] * { color: #E8EDF5 !important; }
[data-testid="stSidebar"] .stRadio label {
    padding: 10px 16px; border-radius: 10px; margin: 3px 0;
    transition: background 0.2s ease; cursor: pointer;
    display: block; font-size: 15px; font-weight: 500;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.08) !important;
}

[data-testid="stMetric"] {
    background: white; border-radius: 16px; padding: 20px 24px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    border: 1px solid rgba(0,0,0,0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
[data-testid="stMetric"]:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,0.10); }
[data-testid="stMetricLabel"] { font-size: 13px !important; font-weight: 500 !important; color: #6B7280 !important; text-transform: uppercase; letter-spacing: 0.05em; }
[data-testid="stMetricValue"] { font-size: 32px !important; font-weight: 700 !important; color: #0A2540 !important; font-family: 'DM Mono', monospace !important; }

.ssp-card {
    background: white; border-radius: 16px; padding: 24px 28px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    border: 1px solid rgba(0,0,0,0.05); margin-bottom: 20px;
    animation: slideUp 0.35s cubic-bezier(0.16,1,0.3,1) both;
}
.ssp-card-title { font-size: 17px; font-weight: 600; color: #0A2540; margin-bottom: 16px; display: flex; align-items: center; gap: 8px; }

.alert-critical {
    background: #FEF2F2; border: 1.5px solid #FECACA; border-left: 4px solid #EF4444;
    border-radius: 10px; padding: 12px 16px; margin: 6px 0;
    animation: pulse-red 2s ease-in-out infinite;
}
.alert-critical .badge { display: inline-block; background: #EF4444; color: white; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.06em; margin-right: 8px; }
.alert-warning { background: #FFFBEB; border: 1.5px solid #FDE68A; border-left: 4px solid #F59E0B; border-radius: 10px; padding: 12px 16px; margin: 6px 0; }
.alert-warning .badge { display: inline-block; background: #F59E0B; color: white; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.06em; margin-right: 8px; }

.page-title { font-size: 28px; font-weight: 700; color: #0A2540; margin-bottom: 4px; letter-spacing: -0.02em; }
.page-subtitle { font-size: 14px; color: #6B7280; margin-bottom: 28px; font-weight: 400; }

@keyframes slideUp { from { opacity:0; transform:translateY(18px); } to { opacity:1; transform:translateY(0); } }
@keyframes pulse-red { 0%,100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.0); } 50% { box-shadow: 0 0 0 6px rgba(239,68,68,0.12); } }

.stForm { background: white; border-radius: 16px; padding: 0 !important; border: none !important; box-shadow: none !important; }
.stTextInput input, .stNumberInput input, .stSelectbox select {
    border-radius: 10px !important; border: 1.5px solid #E5E7EB !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #38BDF8 !important; box-shadow: 0 0 0 3px rgba(56,189,248,0.15) !important;
}
.stButton button { border-radius: 10px !important; font-family: 'DM Sans', sans-serif !important; font-weight: 600 !important; transition: all 0.2s ease !important; }
.stButton button[kind="primary"] { background: linear-gradient(135deg, #0A2540, #0D3260) !important; border: none !important; color: white !important; }
.stButton button[kind="primary"]:hover { transform: translateY(-1px) !important; box-shadow: 0 6px 20px rgba(10,37,64,0.25) !important; }

.login-container { max-width: 400px; margin: 80px auto; background: white; border-radius: 20px; padding: 48px 40px; box-shadow: 0 4px 40px rgba(0,0,0,0.10); animation: slideUp 0.4s cubic-bezier(0.16,1,0.3,1); text-align: center; }
.login-logo { font-size: 52px; margin-bottom: 8px; }
.login-title { font-size: 24px; font-weight: 700; color: #0A2540; margin-bottom: 4px; }
.login-sub { font-size: 13px; color: #9CA3AF; margin-bottom: 32px; }

.ssp-toast { background: #F0FDF4; border: 1.5px solid #BBF7D0; border-left: 4px solid #22C55E; border-radius: 10px; padding: 14px 18px; font-size: 14px; font-weight: 500; color: #166534; animation: slideUp 0.3s ease; }
.sidebar-brand { padding: 20px 16px 28px; border-bottom: 1px solid rgba(255,255,255,0.08); margin-bottom: 12px; }
.sidebar-brand-name { font-size: 18px; font-weight: 700; color: #F0F4FF !important; letter-spacing: -0.01em; }
.sidebar-brand-tagline { font-size: 11px; color: rgba(255,255,255,0.45) !important; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px; }
[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid #E5E7EB; }
</style>
""", unsafe_allow_html=True)

# ─── SUPABASE CONNECTION ───────────────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()

# ─── DATABASE HELPERS ─────────────────────────────────────────────────────────
def load_articles() -> pd.DataFrame:
    res = supabase.table("articles").select("*").order("nom").execute()
    if res.data:
        return pd.DataFrame(res.data)
    return pd.DataFrame(columns=["id","nom","categorie","quantite","seuil_critique","unite","localisation","date_ajout"])

def load_mouvements() -> pd.DataFrame:
    mvts = supabase.table("mouvements").select("*").order("date_mvt", desc=True).limit(200).execute()
    arts = supabase.table("articles").select("id, nom").execute()
    if not mvts.data:
        return pd.DataFrame(columns=["id","article","type","quantite","motif","date"])
    df_m = pd.DataFrame(mvts.data)
    df_a = pd.DataFrame(arts.data).rename(columns={"id": "article_id", "nom": "article"})
    df   = df_m.merge(df_a, on="article_id", how="left")
    df   = df.rename(columns={"type_mvt": "type", "date_mvt": "date"})
    return df[["id","article","type","quantite","motif","date"]]

def add_article(nom, categorie, quantite, seuil, unite, localisation):
    supabase.table("articles").insert({
        "nom": nom, "categorie": categorie, "quantite": quantite,
        "seuil_critique": seuil, "unite": unite, "localisation": localisation,
        "date_ajout": datetime.now().isoformat(timespec='seconds')
    }).execute()

def update_stock(article_id: int, delta: int, type_mvt: str, motif: str):
    res     = supabase.table("articles").select("quantite").eq("id", article_id).single().execute()
    new_qty = res.data["quantite"] + delta
    supabase.table("articles").update({"quantite": new_qty}).eq("id", article_id).execute()
    supabase.table("mouvements").insert({
        "article_id": article_id, "type_mvt": type_mvt,
        "quantite": abs(delta), "motif": motif,
        "date_mvt": datetime.now().isoformat(timespec='seconds')
    }).execute()

# ─── AUTH ──────────────────────────────────────────────────────────────────────
USERS = {
    "admin": hashlib.sha256("admin123".encode()).hexdigest(),
    "stock": hashlib.sha256("stock2024".encode()).hexdigest(),
}

def check_login(username, password):
    return USERS.get(username) == hashlib.sha256(password.encode()).hexdigest()

# ─── SESSION ──────────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username"  not in st.session_state: st.session_state.username  = ""

# ─── LOGIN ────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("""
    <div class="login-container">
        <div class="login-logo">📦</div>
        <div class="login-title">Siloam Stock Pro</div>
        <div class="login-sub">Gestion Logistique Non-Médicale</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.6, 1])
    with col2:
        with st.form("login_form"):
            username  = st.text_input("👤 Identifiant", placeholder="admin")
            password  = st.text_input("🔑 Mot de passe", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Se connecter →", use_container_width=True, type="primary")
            if submitted:
                if check_login(username, password):
                    st.session_state.logged_in = True
                    st.session_state.username  = username
                    st.rerun()
                else:
                    st.error("❌ Identifiant ou mot de passe incorrect.")
        st.caption("Comptes de démo : `admin / admin123`  ·  `stock / stock2024`")
    st.stop()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-name">📦 Siloam Stock Pro</div>
        <div class="sidebar-brand-tagline">Logistique · Non-Médicale</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🏠 Accueil", "➕ Ajouter Article", "📉 Sortie de Stock", "📦 Inventaire Complet"],
        label_visibility="collapsed",
    )

    st.markdown("<div style='height:1px;background:rgba(255,255,255,0.08);margin:20px 0'></div>", unsafe_allow_html=True)

    articles_df = load_articles()
    nb_alertes  = len(articles_df[articles_df["quantite"] <= articles_df["seuil_critique"]]) if not articles_df.empty else 0
    if nb_alertes:
        st.markdown(f"<div style='background:rgba(239,68,68,0.15);border-radius:10px;padding:10px 14px;font-size:13px;color:#FCA5A5;font-weight:600'>🔴 {nb_alertes} alerte(s) critique(s)</div>", unsafe_allow_html=True)

    st.markdown(f"<div style='padding-top:24px;font-size:12px;color:rgba(255,255,255,0.35)'>Connecté en tant que<br><strong style='color:rgba(255,255,255,0.65)'>{st.session_state.username}</strong></div>", unsafe_allow_html=True)

    if st.button("⏏ Déconnexion", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

# ─── PAGE : ACCUEIL ───────────────────────────────────────────────────────────
if page == "🏠 Accueil":
    st.markdown('<div class="page-title">Tableau de Bord</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Vue d\'ensemble du stock en temps réel</div>', unsafe_allow_html=True)

    df          = load_articles()
    stock_total = int(df["quantite"].sum()) if not df.empty else 0
    en_alerte   = len(df[df["quantite"] <= df["seuil_critique"]]) if not df.empty else 0
    rupture     = len(df[df["quantite"] == 0]) if not df.empty else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📋 Références",      len(df))
    col2.metric("📦 Unités en stock", stock_total)
    col3.metric("⚠️ En alerte",       en_alerte,  delta=f"-{en_alerte} sous seuil" if en_alerte else None, delta_color="inverse")
    col4.metric("🚫 Ruptures",        rupture,    delta="Critique" if rupture else "Aucune", delta_color="inverse" if rupture else "normal")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    if not df.empty:
        critiques = df[df["quantite"] <= df["seuil_critique"]]
        if not critiques.empty:
            st.markdown('<div class="ssp-card">', unsafe_allow_html=True)
            st.markdown('<div class="ssp-card-title">🔴 Alertes Stock Critique</div>', unsafe_allow_html=True)
            for _, row in critiques.iterrows():
                niveau    = "alert-critical" if row["quantite"] == 0 else "alert-warning"
                badge_txt = "RUPTURE" if row["quantite"] == 0 else "CRITIQUE"
                st.markdown(f"""
                <div class="{niveau}">
                    <span class="badge">{badge_txt}</span>
                    <strong>{row['nom']}</strong> — {row['quantite']} {row['unite']} restant(e)s
                    <span style='color:#9CA3AF;font-size:12px;margin-left:8px'>· Seuil : {row['seuil_critique']}</span>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="ssp-card">', unsafe_allow_html=True)
    st.markdown('<div class="ssp-card-title">🔄 Derniers Mouvements</div>', unsafe_allow_html=True)
    mvts = load_mouvements()
    if mvts.empty:
        st.info("Aucun mouvement enregistré pour l'instant.")
    else:
        st.dataframe(mvts.head(10), use_container_width=True, hide_index=True,
            column_config={
                "type":     st.column_config.TextColumn("Type"),
                "article":  st.column_config.TextColumn("Article"),
                "quantite": st.column_config.NumberColumn("Qté", format="%d"),
                "motif":    st.column_config.TextColumn("Motif"),
                "date":     st.column_config.TextColumn("Date / Heure"),
            })
    st.markdown("</div>", unsafe_allow_html=True)

# ─── PAGE : AJOUTER ARTICLE ───────────────────────────────────────────────────
elif page == "➕ Ajouter Article":
    st.markdown('<div class="page-title">Ajouter un Article</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Enregistrer un nouvel article dans l\'inventaire</div>', unsafe_allow_html=True)

    st.markdown('<div class="ssp-card">', unsafe_allow_html=True)
    with st.form("form_ajout", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nom       = st.text_input("📝 Nom de l'article *", placeholder="ex: Gants latex L")
            categorie = st.selectbox("🗂️ Catégorie *", [
                "Consommables","Équipements","Produits d'entretien",
                "Bureautique","Alimentation","Textile","Autre"
            ])
            unite = st.text_input("📏 Unité de mesure", value="unité", placeholder="ex: carton, pièce, litre")
        with col2:
            quantite     = st.number_input("📦 Quantité initiale *", min_value=0, value=0, step=1)
            seuil        = st.number_input("⚠️ Seuil critique *", min_value=0, value=5, step=1,
                                            help="Alerte déclenchée quand le stock atteint ce seuil")
            localisation = st.text_input("📍 Localisation", placeholder="ex: Entrepôt A, Rayon 3")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✅ Enregistrer l'article", type="primary", use_container_width=True)
        if submitted:
            if not nom.strip():
                st.error("Le nom de l'article est obligatoire.")
            else:
                add_article(nom.strip(), categorie, quantite, seuil, unite, localisation)
                st.markdown(f'<div class="ssp-toast">✅ Article <strong>{nom}</strong> ajouté avec succès !</div>', unsafe_allow_html=True)
                st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)

    df = load_articles()
    if not df.empty:
        st.markdown('<div class="ssp-card">', unsafe_allow_html=True)
        st.markdown('<div class="ssp-card-title">📋 Articles récemment ajoutés</div>', unsafe_allow_html=True)
        st.dataframe(df.tail(5)[["nom","categorie","quantite","seuil_critique","unite","localisation"]],
            use_container_width=True, hide_index=True,
            column_config={
                "nom":            st.column_config.TextColumn("Nom"),
                "categorie":      st.column_config.TextColumn("Catégorie"),
                "quantite":       st.column_config.NumberColumn("Qté",   format="%d"),
                "seuil_critique": st.column_config.NumberColumn("Seuil", format="%d"),
                "unite":          st.column_config.TextColumn("Unité"),
                "localisation":   st.column_config.TextColumn("Localisation"),
            })
        st.markdown("</div>", unsafe_allow_html=True)

# ─── PAGE : SORTIE DE STOCK ───────────────────────────────────────────────────
elif page == "📉 Sortie de Stock":
    st.markdown('<div class="page-title">Mouvements de Stock</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Enregistrer une entrée ou une sortie de marchandise</div>', unsafe_allow_html=True)

    df = load_articles()
    if df.empty:
        st.warning("⚠️ Aucun article enregistré. Commencez par en ajouter.")
        st.stop()

    tab_sortie, tab_entree = st.tabs(["📉 Sortie de Stock", "📈 Entrée en Stock"])

    with tab_sortie:
        st.markdown('<div class="ssp-card">', unsafe_allow_html=True)
        with st.form("form_sortie", clear_on_submit=True):
            selected  = st.selectbox("📦 Article *", df["nom"].tolist())
            row_sel   = df[df["nom"] == selected].iloc[0]
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📊 Stock actuel : **{row_sel['quantite']} {row_sel['unite']}**")
            with col2:
                max_qty = int(row_sel["quantite"])
                qty     = st.number_input("Quantité à sortir *", min_value=1, max_value=max(max_qty,1), value=1, step=1)
            motif     = st.text_input("📝 Motif / Destination", placeholder="ex: Salle de réunion B")
            submitted = st.form_submit_button("📤 Valider la sortie", type="primary", use_container_width=True)
            if submitted:
                if qty > max_qty:
                    st.error(f"⛔ Stock insuffisant. Disponible : {max_qty} {row_sel['unite']}")
                else:
                    update_stock(int(row_sel["id"]), -qty, "SORTIE", motif)
                    new_qty = max_qty - qty
                    if new_qty <= row_sel["seuil_critique"]:
                        st.markdown(f'<div class="alert-critical"><span class="badge">CRITIQUE</span>Sortie enregistrée. Stock restant : <strong>{new_qty} {row_sel["unite"]}</strong> — Seuil atteint !</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="ssp-toast">✅ Sortie enregistrée. Stock restant : <strong>{new_qty} {row_sel["unite"]}</strong></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab_entree:
        st.markdown('<div class="ssp-card">', unsafe_allow_html=True)
        with st.form("form_entree", clear_on_submit=True):
            selected_e  = st.selectbox("📦 Article *", df["nom"].tolist(), key="sel_e")
            row_e       = df[df["nom"] == selected_e].iloc[0]
            col1, col2  = st.columns(2)
            with col1:
                st.info(f"📊 Stock actuel : **{row_e['quantite']} {row_e['unite']}**")
            with col2:
                qty_e   = st.number_input("Quantité à ajouter *", min_value=1, value=1, step=1)
            motif_e     = st.text_input("📝 Fournisseur / Motif", placeholder="ex: Livraison fournisseur")
            submitted_e = st.form_submit_button("📥 Valider l'entrée", type="primary", use_container_width=True)
            if submitted_e:
                update_stock(int(row_e["id"]), qty_e, "ENTRÉE", motif_e)
                st.markdown(f'<div class="ssp-toast">✅ Entrée enregistrée. Nouveau stock : <strong>{row_e["quantite"] + qty_e} {row_e["unite"]}</strong></div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="ssp-card">', unsafe_allow_html=True)
    st.markdown('<div class="ssp-card-title">📜 Historique des mouvements</div>', unsafe_allow_html=True)
    mvts = load_mouvements()
    if mvts.empty:
        st.info("Aucun mouvement pour le moment.")
    else:
        st.dataframe(mvts, use_container_width=True, hide_index=True,
            column_config={
                "type":     st.column_config.TextColumn("Type"),
                "article":  st.column_config.TextColumn("Article"),
                "quantite": st.column_config.NumberColumn("Qté", format="%d"),
                "motif":    st.column_config.TextColumn("Motif"),
                "date":     st.column_config.TextColumn("Date"),
            })
    st.markdown("</div>", unsafe_allow_html=True)

# ─── PAGE : INVENTAIRE COMPLET ────────────────────────────────────────────────
elif page == "📦 Inventaire Complet":
    st.markdown('<div class="page-title">Inventaire Complet</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Consultation et export de l\'inventaire</div>', unsafe_allow_html=True)

    df = load_articles()
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search = st.text_input("🔍 Rechercher", placeholder="Nom d'article...")
    with col2:
        cats       = ["Toutes"] + sorted(df["categorie"].unique().tolist()) if not df.empty else ["Toutes"]
        cat_filter = st.selectbox("Catégorie", cats)
    with col3:
        alertes_only = st.toggle("⚠️ Alertes seul.", value=False)

    filtered = df.copy()
    if search:             filtered = filtered[filtered["nom"].str.contains(search, case=False, na=False)]
    if cat_filter != "Toutes": filtered = filtered[filtered["categorie"] == cat_filter]
    if alertes_only:       filtered = filtered[filtered["quantite"] <= filtered["seuil_critique"]]

    def statut(row):
        if row["quantite"] == 0:                     return "🔴 Rupture"
        if row["quantite"] <= row["seuil_critique"]: return "🟡 Critique"
        return "🟢 OK"

    st.markdown('<div class="ssp-card">', unsafe_allow_html=True)
    if filtered.empty:
        st.info("Aucun article ne correspond aux filtres sélectionnés.")
    else:
        display               = filtered.copy()
        display["statut"]     = display.apply(statut, axis=1)
        display["date_ajout"] = pd.to_datetime(display["date_ajout"]).dt.strftime("%d/%m/%Y")
        st.dataframe(
            display[["nom","categorie","quantite","seuil_critique","unite","localisation","statut","date_ajout"]],
            use_container_width=True, hide_index=True, height=420,
            column_config={
                "nom":            st.column_config.TextColumn("Nom de l'article"),
                "categorie":      st.column_config.TextColumn("Catégorie"),
                "quantite":       st.column_config.NumberColumn("Quantité", format="%d"),
                "seuil_critique": st.column_config.NumberColumn("Seuil",    format="%d"),
                "unite":          st.column_config.TextColumn("Unité"),
                "localisation":   st.column_config.TextColumn("Emplacement"),
                "statut":         st.column_config.TextColumn("Statut"),
                "date_ajout":     st.column_config.TextColumn("Ajouté le"),
            })
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="ssp-card">', unsafe_allow_html=True)
    st.markdown('<div class="ssp-card-title">📤 Export Inventaire</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if not filtered.empty:
            st.download_button(
                label="⬇️ Télécharger CSV (inventaire)",
                data=filtered.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                file_name=f"inventaire_siloam_{datetime.now().strftime('%Y-%m')}.csv",
                mime="text/csv", use_container_width=True,
            )
    with col2:
        mvts = load_mouvements()
        if not mvts.empty:
            st.download_button(
                label="⬇️ Télécharger CSV (mouvements)",
                data=mvts.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                file_name=f"mouvements_siloam_{datetime.now().strftime('%Y-%m')}.csv",
                mime="text/csv", use_container_width=True,
            )
    st.markdown("</div>", unsafe_allow_html=True)
