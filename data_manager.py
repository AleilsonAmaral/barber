# data_manager.py
import pandas as pd
import streamlit as st
import os

# Nome do arquivo onde os agendamentos serão salvos
ARQUIVO_DADOS = 'agendamentos_viking.csv'

def carregar_dados():
    """
    Carrega os agendamentos do arquivo CSV ou retorna uma lista vazia se não existir.
    """
    # Verifica se o arquivo existe
    if os.path.exists(ARQUIVO_DADOS):
        try:
            # Carrega o CSV para um DataFrame
            df = pd.read_csv(ARQUIVO_DADOS)
            
            # Converte o DataFrame de volta para uma lista de dicionários (necessário para o Streamlit Session State)
            return df.to_dict('records')
        except Exception as e:
            st.error(f"Erro ao carregar dados: {e}")
            return []
    else:
        # Se o arquivo não existir, retorna uma lista vazia
        return []

def salvar_dados(agendamentos):
    """
    Salva a lista atual de agendamentos no arquivo CSV.
    """
    if agendamentos:
        try:
            # Converte a lista de dicionários para um DataFrame
            df = pd.DataFrame(agendamentos)
            
            # Salva o DataFrame no arquivo CSV (sem incluir o índice do DataFrame)
            df.to_csv(ARQUIVO_DADOS, index=False)
        except Exception as e:
            st.error(f"Erro ao salvar dados: {e}")