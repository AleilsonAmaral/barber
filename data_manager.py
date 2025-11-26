# data_manager.py
import pandas as pd
import streamlit as st
import os

# Função para obter o nome do arquivo dinamicamente baseado no ID da barbearia.
# O ID é definido na sessão após o login (st.session_state.barber_id)
def get_data_filepath():
    """
    Retorna o caminho do arquivo CSV específico para a barbearia logada.
    Se não houver ID na sessão (modo cliente/público), usa 'GERAL'.
    """
    # Tenta obter o ID da sessão, usando 'GERAL' como fallback para clientes.
    barber_id = st.session_state.get('barber_id', 'GERAL')
    
    # Formato: agendamentos_BARBERID.csv (Ex: agendamentos_ALPHA.csv)
    return f'agendamentos_{barber_id}.csv'

def carregar_dados():
    """
    Carrega os agendamentos do arquivo CSV específico para a barbearia logada.
    """
    # Obtém o nome do arquivo dinamicamente
    ARQUIVO_DADOS = get_data_filepath()
    
    # Verifica se o arquivo existe
    if os.path.exists(ARQUIVO_DADOS):
        try:
            # Carrega o CSV para um DataFrame
            df = pd.read_csv(ARQUIVO_DADOS)
            
            # Converte o DataFrame de volta para uma lista de dicionários
            return df.to_dict('records')
        except Exception as e:
            # st.error(f"Erro ao carregar dados: {e}") # Desativado para evitar erro Streamlit no início
            return []
    else:
        # Se o arquivo não existir, retorna uma lista vazia
        return []

def salvar_dados(agendamentos):
    """
    Salva a lista atual de agendamentos no arquivo CSV específico para a barbearia logada.
    """
    # Obtém o nome do arquivo dinamicamente
    ARQUIVO_DADOS = get_data_filepath()
    
    if agendamentos:
        try:
            # Converte a lista de dicionários para um DataFrame
            df = pd.DataFrame(agendamentos)
            
            # Salva o DataFrame no arquivo CSV (sem incluir o índice do DataFrame)
            df.to_csv(ARQUIVO_DADOS, index=False)
        except Exception as e:
            st.error(f"Erro ao salvar dados: {e}")