import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from urllib.parse import quote_plus
from PIL import Image

# --- Configuração da página ---
st.set_page_config(
    page_title="Assistências Técnicas",
    layout="wide"
    # Não precisamos mais do initial_sidebar_state
)

# --- Logo e Título (ocupam a largura total antes das colunas) ---
col_logo1, col_logo2, col_logo3 = st.columns([1,0.5,1])
with col_logo2:
    try:
        logo = Image.open("logo-smartway.jpg")
        st.image(logo, use_container_width=True)
    except FileNotFoundError:
        st.warning("Arquivo 'logo-smartway.jpg' não encontrado.")
    except Exception as e:
        st.error(f"Erro ao carregar a logo: {e}")


st.markdown("""
    <div style='text-align:center; font-size: 1.5em; font-weight:bold; margin-bottom:0.3em;'>
        🤝 Mapa de Parceiros da Smartway
    </div>
    <div style='text-align:center; color:#228B22; margin-bottom:1em;'>
        Encontre e entre em contato com parceiros da Smartway!
    </div>
    """, unsafe_allow_html=True)

# --- Função para carregar os dados com cache ---
@st.cache_data
def carregar_dados():
    try:
        dados = pd.read_csv("assistencia.csv")
        return dados
    except FileNotFoundError:
        st.error("Erro: O arquivo 'assistencia.csv' não foi encontrado. Verifique se ele está na mesma pasta do seu script.")
        return pd.DataFrame()

dados = carregar_dados()

if dados.empty:
    st.stop()

# --- CRIAÇÃO DO LAYOUT DE COLUNAS FIXAS ---
# Criamos duas colunas. A primeira terá 35% da largura e a segunda 65%.
# Estes valores podem ser ajustados (ex: [1, 2] ou [2, 5])
left_column, right_column = st.columns([0.35, 0.65])

# --- Coluna da Esquerda (nossa nova "sidebar fixa") ---
with left_column:
    st.header("Filtros de Busca")
    
    if "Estado" in dados.columns:
        estados_disponiveis = sorted(dados["Estado"].dropna().unique())
        estados = st.multiselect(
            "Estados:",
            options=estados_disponiveis,
            default=estados_disponiveis
        )
    else:
        st.warning("A coluna 'Estado' não foi encontrada no arquivo CSV.")
        estados = []

    cidade_busca = st.text_input("Buscar por Cidade:")

    # --- Novo filtro de Serviços ---
    if "Serviços" in dados.columns:
        servicos_disponiveis = sorted(dados["Serviços"].dropna().unique())
        servicos_selecionados = st.multiselect(
            "Tipo de Serviço:",
            options=servicos_disponiveis,
            default=servicos_disponiveis # Pode definir um default diferente se preferir
        )
    else:
        st.warning("A coluna 'Serviços' não foi encontrada no arquivo CSV.")
        servicos_selecionados = []

# --- Coluna da Direita (nosso conteúdo principal) ---
with right_column:
    # --- Aplicar filtros (baseado nas seleções da coluna da esquerda) ---
    dados_filtrados = dados.copy()
    if "Estado" in dados.columns and estados:
        dados_filtrados = dados_filtrados[dados_filtrados["Estado"].isin(estados)]
    if "Cidade" in dados.columns and cidade_busca:
        dados_filtrados = dados_filtrados[dados_filtrados["Cidade"].str.contains(cidade_busca, case=False, na=False)]
    # Aplicar o novo filtro de Serviços
    if "Serviços" in dados.columns and servicos_selecionados:
        dados_filtrados = dados_filtrados[dados_filtrados["Serviços"].isin(servicos_selecionados)]

    # --- Informação de assistências encontradas ---
    st.markdown(f"<div style='text-align:center;font-size:1.1em;'><b>{len(dados_filtrados)} parceiro(s) encontrado(s)</b></div>", unsafe_allow_html=True)

    # --- Mapa ---
    mapa = folium.Map(location=[-14.2350, -51.9253], zoom_start=4, control_scale=True)

    if dados_filtrados.empty:
        st.warning("Nenhuma assistência técnica encontrada para os filtros selecionados.")
    else:
        for _, row in dados_filtrados.iterrows():
            telefone = ''.join(filter(str.isdigit, str(row.get('Contato', ''))))
            if telefone and not telefone.startswith('55'):
                telefone = '55' + telefone

            mensagem = quote_plus("Olá, encontrei seu contato na Smartway. Poderia me ajudar com minha scooter?")
            link_whatsapp = f"https://wa.me/{telefone}?text={mensagem}"

            popup_html = (
                f"<div style='font-size:16px; line-height:1.6;'>"
                f"<b>{row.get('Nome', 'N/A')}</b><br>"
                f"📍 <b>{row.get('Cidade', 'N/A')}</b> - {row.get('Estado', 'N/A')}<br>"
                f"📞 <a href='{link_whatsapp}' target='_blank'>{row.get('Contato', 'N/A')} (WhatsApp)</a><br>"
                f"🔧 <b>Serviços:</b> {row.get('Serviços', 'N/A')}"
                f"</div>"
            )
            
            if pd.notna(row.get('Latitude')) and pd.notna(row.get('Longitude')):
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=row.get('Nome', 'N/A'),
                    icon=folium.Icon(color='orange', icon='wrench', prefix='fa')
                ).add_to(mapa)

        st_folium(mapa, use_container_width=True, height=500)

# --- Estilos (pode não ser mais necessário, mas mantido caso queira outros ajustes) ---
st.markdown("""
<style>
/* Em telas pequenas, faz as colunas virarem linhas (uma embaixo da outra) */
@media (max-width: 768px) {
    .main > div {
        flex-direction: column;
    }
}
</style>
""", unsafe_allow_html=True)
