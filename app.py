# app.py
import streamlit as st
import datetime
import pandas as pd
import time

# Importa as views (arquivos separados)
from cliente_view import render_cliente_view
from admin_view import render_admin_view

# IMPORTA O NOVO GERENCIADOR DE DADOS
# Requer o arquivo data_manager.py na mesma pasta
from data_manager import carregar_dados, salvar_dados 

# --- Configuração da Página ---
st.set_page_config(
    page_title="Viking Cuts - Agendamento",
    page_icon="✂️",
    layout="centered"
)

# --- Dados de Configuração ---
# Valores ajustados para simular a moeda Real (R$)
SERVICOS = {
    "Corte de Cabelo": 50.00,
    "Barba (Toalha Quente)": 40.00,
    "Combo (Cabelo + Barba)": 85.00,
    "Pezinho / Acabamento": 20.00
}

# Lista de horários expandida
HORARIOS = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30",
    "17:00", "17:30", "18:00", "18:30", "19:00"
]

# SENHA DE ACESSO ADMIN
SENHA_ADMIN = "viking123" # <<< SENHA DEFINIDA AQUI
# ---------------------------

# --- 1. Base de Dados AGORA PERSISTENTE e Variáveis Globais (Session State) ---
if 'agendamentos' not in st.session_state:
    # Carrega os dados persistentes do arquivo CSV ao iniciar
    st.session_state.agendamentos = carregar_dados() 

if 'modo_admin' not in st.session_state:
    st.session_state.modo_admin = False

# --- 2. Funções Auxiliares (Globais) ---
def formatar_moeda(valor):
    """Formata um valor float para a string de moeda (Real Brasileiro)."""
    return f"R$ {valor:.2f}"

def gerar_link_whatsapp(servico_com_data, horario, nome):
    """Gera o link de confirmação via WhatsApp."""
    texto = f"Olá! Gostaria de confirmar o agendamento: {servico_com_data}. Cliente: {nome}."
    texto_encoded = texto.replace(" ", "%20").replace(":", "%3A") # Garantir a codificação correta
    return f"https://wa.me/351999999999?text={texto_encoded}"

# --- 3. Barra Lateral (Menu) ---
with st.sidebar:
    st.title("Menu")
    modo = st.radio("Escolha a Visão:", ["Cliente", "Dono da Barbearia"])
    
    st.info("💡 Dica: A senha de Admin é: 'viking123'")
    
    # Define o estado do modo Admin
    if modo == "Dono da Barbearia":
        # Pede a senha
        senha_digitada = st.text_input("🔑 Digite a Senha de Admin:", type="password")
        
        if senha_digitada == SENHA_ADMIN:
            st.session_state.modo_admin = True
            st.success("Acesso Admin Liberado!")
        elif senha_digitada: # Se algo foi digitado, mas está errado
            st.session_state.modo_admin = False
            st.error("Senha Incorreta.")
        else: # Nada digitado
            st.session_state.modo_admin = False
    else:
        st.session_state.modo_admin = False

    # 💡 Dica de Tema Adicionada
    st.markdown("---")
    st.markdown("🌐 **Mudar Tema (Claro/Escuro):**")
    st.markdown("Vá em `⋮` (canto superior direito) > `Settings` > `Theme`.")

# --- 4. Lógica Principal de Redirecionamento ---
if not st.session_state.modo_admin:
    # CLIENTE: 5 argumentos (inclui HORARIOS e salvar_dados)
    render_cliente_view(SERVICOS, HORARIOS, formatar_moeda, gerar_link_whatsapp, salvar_dados)
else:
    # ADMIN: 4 argumentos (NÃO inclui HORARIOS, mas inclui salvar_dados)
    # A VISÃO ADMIN SÓ É RENDERIZADA SE st.session_state.modo_admin for True
    render_admin_view(SERVICOS, formatar_moeda, gerar_link_whatsapp, salvar_dados)