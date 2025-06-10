import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from urllib.parse import quote_plus
from PIL import Image

# --- Configuração da página ---
st.set_page_config(page_title="Assistências Técnicas", layout="wide")

# --- Logo centralizada no topo ---
try:
    logo = Image.open("logo-smartway.jpg")
    st.image(logo, width=120)
except Exception as e:
    st.error(f"Erro ao carregar a logo: {e}")

# --- Título e descrição curta ---
st.markdown("""
    <div style='text-align:center; font-size: 1.5em; font-weight:bold; margin-bottom:0.3em;'>
        🛠️ Mapa de Assistências Técnicas Parceiras
    </div>
    <div style='text-align:center; color:#228B22; margin-bottom:1em;'>
        Encontre e entre em contato com assistências técnicas parceiras SmartWay!
    </div>
    """, unsafe_allow_html=True)

# --- Função para carregar os dados com cache ---

dados = pd.read_csv("assistencia.csv")

# --- Sidebar com filtros básicos, sem logo ---
with st.sidebar:
    st.header("Filtros de Busca")
    estados = st.multiselect(
        "Estados:",
        sorted(dados["Estado"].dropna().unique()),
        default=sorted(dados["Estado"].dropna().unique())
    )
    cidade_busca = st.text_input("Cidade:")

# --- Aplicar filtros (case-insensitive) ---
filtro = dados["Estado"].isin(estados)
if cidade_busca:
    filtro &= dados["Cidade"].str.contains(cidade_busca, case=False, na=False)
dados_filtrados = dados[filtro].copy()

# --- Informação de assistências encontradas ---
st.markdown(f"<div style='text-align:center;font-size:1.1em;'><b>{len(dados_filtrados)} assistência(s) encontrada(s)</b></div>", unsafe_allow_html=True)

# --- Mapa responsivo para mobile ---
mapa = folium.Map(location=[-14.2350, -51.9253], zoom_start=4, control_scale=True)

if dados_filtrados.empty:
    st.warning("Nenhuma assistência técnica encontrada para os filtros selecionados.")
else:
    for _, row in dados_filtrados.iterrows():
        telefone = ''.join(filter(str.isdigit, str(row.get('Contato', ''))))
        if not telefone.startswith('55'):
            telefone = '55' + telefone

        mensagem = quote_plus(
            "Olá, encontrei seu contato na Smartway. Poderia me ajudar com minha scooter?"
        )
        link_whatsapp = f"https://wa.me/{telefone}?text={mensagem}"

        popup_html = (
            f"<div style='font-size:17px; line-height:1.6;'>"
            f"<b>{row['Nome']}</b><br>"
            f"📍 <b>{row['Cidade']}</b> - {row['Estado']}<br>"
            f"📞 <a href='{link_whatsapp}' target='_blank'>{row['Contato']} (WhatsApp)</a><br>"
            f"🔧 <b>Serviços:</b> {row['Serviços']}"
            f"</div>"
        )

        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=folium.Popup(popup_html, max_width=300, min_width=200),
            tooltip=row['Nome'],
            icon=folium.Icon(color='orange', icon='wrench', prefix='fa')
        ).add_to(mapa)

    st_folium(mapa, use_container_width=True, height=500)

# --- Ajustes de visualização mobile-friendly ---
st.markdown("""
<style>
@media (max-width: 600px) {
    .css-1v0mbdj {padding-left: 0px;}
    .stSidebar {width: 85vw !important;}
    .css-1v0mbdj .stSidebar {width: 90vw !important;}
    .stButton>button {font-size:1.1em !important;}
    .stTextInput>div>div>input {font-size:1.1em !important;}
}
</style>
""", unsafe_allow_html=True)

