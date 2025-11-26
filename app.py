# app.py
import streamlit as st
import datetime
import pandas as pd
import time

# Importa as views (arquivos separados)
from cliente_view import render_cliente_view
from admin_view import render_admin_view

# IMPORTA O NOVO GERENCIADOR DE DADOS
from data_manager import carregar_dados, salvar_dados 

# --- Configuração da Página ---
st.set_page_config(
    page_title="BARBEARIA - Agendamento",
    page_icon="✂️",
    layout="centered"
)

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

# --- CONSTANTE DA IMAGEM ---
# REMOVIDO: CAMINHO_IMAGEM_AGENDAMENTO não é mais usado
# ---------------------------

# MAPAS DE ACESSO ADMIN (Lido do st.secrets)
ADMIN_ACCOUNTS = st.secrets.get("admin_accounts", {})
# ---------------------------

# --- FUNÇÃO PRINCIPAL PARA GERENCIAR A CARGA DE DADOS ---
def recarregar_dados_barbearia():
    """
    Função que força o carregamento dos dados da agenda baseados no ID atual.
    Deve ser chamada após login ou na inicialização.
    """
    st.session_state.agendamentos = carregar_dados()
    st.rerun()

# --- 1. Base de Dados AGORA PERSISTENTE e Variáveis Globais (Session State) ---

# AQUI, CARREGAMOS APENAS NA PRIMEIRA VEZ, SEMPRE USANDO O ID PADRÃO (GERAL)
if 'agendamentos' not in st.session_state:
    st.session_state.agendamentos = carregar_dados() 

if 'modo_admin' not in st.session_state:
    st.session_state.modo_admin = False

if 'barber_id' not in st.session_state:
    st.session_state.barber_id = 'GERAL'

# --- 2. Funções Auxiliares (Globais) ---
def formatar_moeda(valor):
    """Formata um valor float para a string de moeda (Real Brasileiro)."""
    return f"R$ {valor:.2f}"

# A função AGORA RECEBE O NÚMERO DE WHATSAPP DA CONFIGURAÇÃO
def gerar_link_whatsapp(numero_whatsapp, servico_com_data, horario, nome):
    """Gera o link de confirmação via WhatsApp, usando o número dinâmico."""
    texto = f"Olá! Gostaria de confirmar o agendamento: {servico_com_data}. Cliente: {nome}."
    texto_encoded = texto.replace(" ", "%20").replace(":", "%3A")
    return f"https://wa.me/{numero_whatsapp}?text={texto_encoded}"

# --- 3. Barra Lateral (Menu) ---
with st.sidebar:
    st.title("Menu")
    
    # Armazenamos o estado anterior do ID para detectar a mudança
    id_anterior = st.session_state.barber_id 
    
    modo = st.radio("Escolha a Visão:", ["Cliente", "Dono da Barbearia"])
    
    # Define o estado do modo Admin
    if modo == "Dono da Barbearia":
        st.subheader("Acesso Administrador")
        
        # Campos de Login
        login_digitado = st.text_input("👤 Login:", key="admin_login")
        senha_digitada = st.text_input("🔑 Senha:", type="password", key="admin_senha")
        
        # Lógica de Autenticação Multi-Conta
        if login_digitado and senha_digitada:
            senha_correta = ADMIN_ACCOUNTS.get(login_digitado)
            
            if senha_correta == senha_digitada:
                st.session_state.modo_admin = True
                # CRIA O ID ÚNICO DA BARBEARIA NA SESSÃO
                st.session_state.barber_id = login_digitado.upper() 
                st.success(f"Acesso Admin ({login_digitado}) Liberado!")
                
            elif senha_digitada:
                st.session_state.modo_admin = False
                st.session_state.barber_id = 'GERAL'
                st.error("Login ou Senha Incorreta.")
        elif not ADMIN_ACCOUNTS:
             st.warning("Nenhuma conta de Admin configurada no secrets.toml ou no Streamlit Cloud.")
        else:
            st.session_state.modo_admin = False
            st.session_state.barber_id = 'GERAL'
            
    else:
        # Se sair do modo admin (voltar para cliente), o ID deve ser redefinido
        st.session_state.modo_admin = False
        st.session_state.barber_id = 'GERAL'
        
    # --- LÓGICA DE RECARGA: Se o ID da Barbearia Mudou, Recarrega os Dados ---
    if st.session_state.barber_id != id_anterior:
        recarregar_dados_barbearia() # Chama a recarga para isolar os dados

    # 💡 Dica de Tema Adicionada
    st.markdown("---")
    st.markdown("🌐 **Mudar Tema (Claro/Escuro):**")
    st.markdown("Vá em `⋮` (canto superior direito) > `Settings` > `Theme`.")

# --- CARREGAR CONFIGURAÇÃO DA BARBEARIA ATUAL ---
# Tenta buscar a configuração com o ID atual (Ex: BARBER_ALPHA)
# O .get({}, {}).get() protege contra a falta da chave principal e da chave secundária.
config_barbearia = st.secrets.get("barber_config", {}).get(st.session_state.barber_id, {})
# ------------------------------------------------

# --- 4. Lógica Principal de Redirecionamento ---

# NOTA: O 'data_manager.py' e as views agora precisam usar st.session_state.barber_id
if not st.session_state.modo_admin:
    # CLIENTE: 6 argumentos (REMOVEMOS O CAMINHO DA IMAGEM)
    render_cliente_view(SERVICOS, HORARIOS, formatar_moeda, gerar_link_whatsapp, salvar_dados, config_barbearia)
else:
    # ADMIN: 5 argumentos (NÃO HOUVE MUDANÇA)
    render_admin_view(SERVICOS, formatar_moeda, gerar_link_whatsapp, salvar_dados, config_barbearia)