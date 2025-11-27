# app.py
import streamlit as st
import datetime
import pandas as pd
import time
import os
import re 

# Importa as views (arquivos separados)
from cliente_view import render_cliente_view
from admin_view import render_admin_view

# IMPORTA O GERENCIADOR DE DADOS
from data_manager import carregar_dados, salvar_dados 

# --- CSS INLINE PARA TEMA DE BARBEARIA MODERNA (PRETO/DOURADO) ---
CUSTOM_THEME_CSS = """
<style>
/* 1. Importação das Fontes (Poppins e Montserrat) */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&family=Poppins:wght@400;600;700&display=swap');

/* Define a fonte padrão para o corpo e títulos */
html, body, [class*="st-"] {
    font-family: 'Poppins', 'Montserrat', sans-serif;
    color: #F9F9F9; /* Texto Branco */
}

/* 2. Estilo dos Containers/Cards (Cinza Suave) */
section.main .block-container, 
section.main [data-testid="stVerticalBlock"],
section.main [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
    background-color: #1C1C1C !important; /* Fundo Principal Grafite */
}

/* Estiliza containers internos (cards) */
.stContainer, [data-testid="stVerticalBlock"] > div:has(> .stAlert) {
    background-color: #2B2B2B !important; /* Fundo Secundário Cinza Suave */
    padding: 15px;
    border-radius: 10px; /* Cards Arredondados */
    box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2); /* Sombra Leve */
    margin-bottom: 15px;
}

/* 3. Estilo dos Botões Primários (Dourado) */
div.stButton > button:first-child[kind="primary"] {
    background-color: #D4A657 !important; /* Dourado */
    color: #1C1C1C !important; /* Texto Preto no Dourado */
    border: none;
    border-radius: 8px;
    font-weight: 600;
}

div.stButton > button:first-child[kind="primary"]:hover {
    background-color: #C39546 !important; /* Dourado mais escuro ao passar o mouse */
}

/* 4. Estilo dos Botões Secundários */
div.stButton > button:first-child {
    background-color: #2B2B2B !important; 
    color: #F9F9F9 !important;
    border: 1px solid #444444; 
    border-radius: 8px;
}

/* 5. Alertas de Erro (Vermelho Suave) */
div[data-testid="stAlert"] {
    background-color: #E04B4B !important; 
    color: #F9F9F9 !important;
}

/* 6. Títulos das Seções (Dourado) */
h1, h2, h3, h4, h5 {
    color: #D4A657; 
}

/* Inputs (Text, Date, Select) para Fundo Escuro */
input[type="text"], input[type="password"], input[type="date"], textarea, [data-testid="stSelectbox"] div[role="button"] {
    background-color: #2B2B2B !important; 
    border: 1px solid #444444; 
    border-radius: 5px;
    color: #F9F9F9 !important;
}

</style>
"""

# --- Função Principal de Injeção de CSS ---
def injetar_css_inline():
    """Injeta o CSS de tema diretamente na aplicação."""
    st.markdown(CUSTOM_THEME_CSS, unsafe_allow_html=True)
    
# --- Configuração da Página ---
st.set_page_config(
    page_title="BARBEARIA - Agendamento", 
    page_icon="✂️",
    layout="wide"
)

# --- CHAMADA DO CSS NO INÍCIO DA APLICAÇÃO ---
injetar_css_inline() 

# --- Dados de Configuração ---
SERVICOS = {
    "Corte de Cabelo": 50.00,
    "Barba (Toalha Quente)": 40.00,
    "Combo (Cabelo + Barba)": 85.00,
    "Pezinho / Acabamento": 20.00
}

HORARIOS = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30",
    "17:00", "17:30", "18:00", "18:30", "19:00"
]

# MAPAS DE ACESSO ADMIN (Lido do st.secrets)
ADMIN_ACCOUNTS = st.secrets.get("admin_accounts", {})

# MAPAS DE CONFIGURAÇÃO DE BARBEARIAS
BARBER_CONFIGS = st.secrets.get("barber_config", {})
# ---------------------------

# --- 1. Variáveis Globais (Session State) ---

BARBER_IDS = list(BARBER_CONFIGS.keys())
if 'GERAL' not in BARBER_IDS:
    BARBER_IDS.append('GERAL')

if 'modo_admin' not in st.session_state:
    st.session_state.modo_admin = False

# NOVO CONTROLE DE ACESSO
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if 'cliente_action' not in st.session_state:
    st.session_state.cliente_action = 'HOME' 

if 'barber_id' not in st.session_state:
    real_barber_ids = [id for id in BARBER_IDS if id != 'GERAL']
    
    if real_barber_ids:
        st.session_state.barber_id = real_barber_ids[0]
    else:
        st.session_state.barber_id = 'GERAL'

if 'agendamentos' not in st.session_state:
    st.session_state.agendamentos = carregar_dados() 

# --- 2. Funções Auxiliares (Globais) ---
def recarregar_dados_barbearia():
    st.session_state.agendamentos = carregar_dados()

def formatar_moeda(valor):
    return f"R$ {valor:.2f}"

def gerar_link_whatsapp(numero_whatsapp, servico_com_data, horario, nome, codigo_cancelamento):
    texto = f"Seu corte está agendado para {servico_com_data} às {horario}. Para CANCELAR, envie 'cancelar {codigo_cancelamento}'. Obrigado, {nome}."
    texto_encoded = texto.replace(" ", "%20").replace(":", "%3A").replace("'", "%27")
    
    numero_formatado = numero_whatsapp if numero_whatsapp.startswith('+') else f"{numero_whatsapp}" 
    
    return f"https://wa.me/{numero_formatado}?text={texto_encoded}"

# --- FUNÇÃO DE LOGOUT ---
def logout_admin():
    st.session_state.admin_logged_in = False
    st.session_state.modo_admin = False
    st.session_state.barber_id = 'GERAL' # Volta para o ID padrão
    recarregar_dados_barbearia() 
    st.rerun()

# --- 3. Barra Lateral (Menu/Admin) ---
with st.sidebar:
    st.header("💈 Lojas") 
    st.markdown("---")
    
    id_anterior = st.session_state.barber_id 
    
    # Se o usuário estava logado, mostramos a opção de Logout
    if st.session_state.admin_logged_in:
        st.success(f"Acesso Admin ({st.session_state.barber_id}) Liberado!")
        if st.button("🔓 Logout", type="secondary"):
            logout_admin()

        # O Modo rádio só é exibido se não estiver logado
        modo = st.radio("Selecione o Modo:", ["Cliente", "Administrador"], 
                        index=1, disabled=True) 

    else:
        # Se não estiver logado, exibe o rádio button
        modo = st.radio("Selecione o Modo:", ["Cliente", "Administrador"], 
                        index=0 if not st.session_state.modo_admin else 1)
        
    # Lógica de Administração
    if modo == "Administrador" and not st.session_state.admin_logged_in:
        st.session_state.modo_admin = True
        st.subheader("Acesso Restrito")
        
        # Formulário de Login
        with st.form("admin_login_form"):
            login_digitado = st.text_input("👤 Login:")
            senha_digitada = st.text_input("🔑 Senha:", type="password")
            btn_login = st.form_submit_button("Entrar", type="primary")

        if btn_login:
            senha_correta = ADMIN_ACCOUNTS.get(login_digitado)
            
            if senha_correta == senha_digitada:
                # 🔒 SUCESSO NO LOGIN
                st.session_state.admin_logged_in = True
                st.session_state.barber_id = login_digitado.upper() 
                st.session_state.cliente_action = 'HOME'
                recarregar_dados_barbearia()
                st.rerun()
                
            elif senha_digitada:
                st.error("Login ou Senha Incorreta.")
                st.session_state.admin_logged_in = False
                st.session_state.barber_id = 'GERAL'
        
    # Lógica Cliente
    elif modo == "Cliente" and not st.session_state.admin_logged_in:
        st.session_state.modo_admin = False
        
        if st.session_state.cliente_action != 'HOME':
            if st.button("⬅️ Voltar ao Menu Principal"):
                st.session_state.cliente_action = 'HOME'
                
                if 'agendamento_step' in st.session_state:
                    del st.session_state.agendamento_step
                if 'agendamento_data' in st.session_state:
                    del st.session_state.agendamento_data
                
                st.rerun()

    # --- LÓGICA DE RECARGA FINAL: Se o ID mudou no login Admin, recarrega ---
    if st.session_state.barber_id != id_anterior and st.session_state.modo_admin:
        recarregar_dados_barbearia() 
        st.rerun()

    st.markdown("---")
    st.markdown("🌐 **Mudar Tema:** `⋮` > `Settings` > `Theme`.")

# --- 4. Carregar Configuração da Barbearia Atual ---
config_barbearia = st.secrets.get("barber_config", {}).get(st.session_state.barber_id, {})
nome_display = config_barbearia.get('name', st.session_state.barber_id) 

# --- 5. Lógica Principal de Redirecionamento ---

if st.session_state.admin_logged_in:
    # 🔒 ACESSO PERMITIDO: RENDERIZA O PAINEL ADMIN
    st.title(f"👑 Painel Administrativo - {nome_display}")
    render_admin_view(SERVICOS, formatar_moeda, gerar_link_whatsapp, salvar_dados, config_barbearia)

elif st.session_state.modo_admin:
    # ACESSO BLOQUEADO: MODO ADMIN SELECIONADO, MAS NÃO AUTENTICADO
    st.title("Acesso Restrito 🛡️")
    st.warning("Por favor, insira suas credenciais na barra lateral para acessar a gestão.")

else:
    # CLIENTE: Implementação da Tela Inicial Simplificada
    
    st.title("Agendamento Online 💈")
    st.header(nome_display)

    if st.session_state.cliente_action == 'HOME':
        st.markdown("### Selecione uma opção abaixo:")
        
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📅 Agendar Serviço", key="btn_agendar", use_container_width=True, type="primary"):
                st.session_state.cliente_action = 'AGENDAR'
                st.rerun()
            
        with col2:
            if st.button("📝 Meus Agendamentos (Consultar/Cancelar)", key="btn_meus_agendamentos", use_container_width=True):
                st.session_state.cliente_action = 'MEUS_AGENDAMENTOS'
                st.rerun()

    render_cliente_view(
        SERVICOS, 
        HORARIOS, 
        formatar_moeda, 
        gerar_link_whatsapp, 
        salvar_dados, 
        config_barbearia,
        st.session_state.cliente_action 
    )