# data_manager.py
import pandas as pd
import streamlit as st
import os

COLUNAS_ESPERADAS = [
    "barber_id", "cliente", "celular", "servico", "preco", 
    "horario", "data", "codigo_cancelamento", "data_hora_registro"
]

def get_data_filepath():
    """Retorna o caminho do arquivo CSV específico para a barbearia logada."""
    barber_id = st.session_state.get('barber_id', 'GERAL')
    return f'agendamentos_{barber_id}.csv'

def carregar_dados():
    """Carrega os agendamentos do arquivo CSV específico para a barbearia logada."""
    ARQUIVO_DADOS = get_data_filepath()
    
    if os.path.exists(ARQUIVO_DADOS):
        try:
            df = pd.read_csv(ARQUIVO_DADOS)
            return df.to_dict('records')
        except Exception as e:
            return []
    else:
        return []

def salvar_dados(agendamentos):
    """Salva a lista atual de agendamentos no arquivo CSV específico para a barbearia logada."""
    ARQUIVO_DADOS = get_data_filepath()
    
    if agendamentos:
        try:
            df = pd.DataFrame(agendamentos)
            
            for col in COLUNAS_ESPERADAS:
                if col not in df.columns:
                    df[col] = None
                    
            df[COLUNAS_ESPERADAS].to_csv(ARQUIVO_DADOS, index=False)
            
        except Exception as e:
            st.error(f"Erro ao salvar dados: {e}")
            
    else:
        if os.path.exists(ARQUIVO_DADOS):
             df_vazio = pd.DataFrame(columns=COLUNAS_ESPERADAS)
             df_vazio.to_csv(ARQUIVO_DADOS, index=False)