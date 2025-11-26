# admin_view.py
import streamlit as st
import pandas as pd
import datetime
import time 

# A função AGORA espera o novo argumento: config_barbearia
def render_admin_view(SERVICOS, formatar_moeda, gerar_link_whatsapp, salvar_dados, config_barbearia):
    """
    Renderiza a interface de gestão, visualização e exportação (sem cancelamento)
    para o administrador, usando as configurações dinâmicas da barbearia.
    """
    
    # --- Extrair Configurações Dinâmicas ---
    nome_barbearia = config_barbearia.get('name', 'BARBEARIA') # Obtém o nome ou usa BARBEARIA como fallback
    # Logo URL não é exibida na visão admin, mas o nome é.
    
    st.title(f"👑 Gestão {nome_barbearia}") # Título agora é dinâmico
    st.divider()

    # --- VISUALIZAÇÃO DA AGENDA DO DIA ---
    data_visao_admin = st.date_input(
        "Selecione a Data para Visualização da Agenda:",
        value=datetime.date.today(),
        key='admin_date_picker'
    )
    data_str_admin = data_visao_admin.strftime("%Y-%m-%d")
    
    st.subheader(f"Agenda para {data_visao_admin.strftime('%d/%m/%Y')}")
    
    # 1. Filtrar Agendamentos pela Data Escolhida para Visualização
    # Nota: st.session_state.agendamentos já está carregada isoladamente pelo app.py
    agendamentos_filtrados = [
        a for a in st.session_state.agendamentos 
        if a.get('data') == data_str_admin
    ]

    if not agendamentos_filtrados:
        st.info(f"Nenhum agendamento para {data_visao_admin.strftime('%d/%m/%Y')} ainda!")
    else:
        # Converter a lista de dicionários filtrada para um DataFrame do pandas
        df_agendamentos = pd.DataFrame(agendamentos_filtrados)

        # Adicionar uma coluna de ID temporário para seleção
        df_agendamentos['ID'] = range(1, len(df_agendamentos) + 1)
        
        # Reorganizar e Formatar para visualização
        df_agendamentos = df_agendamentos[['ID', 'horario', 'cliente', 'servico', 'preco', 'telemovel', 'data', 'data_hora_registro']]
        df_agendamentos_display = df_agendamentos.copy()
        df_agendamentos_display['preco'] = df_agendamentos_display['preco'].apply(formatar_moeda)
        
        # --- EXIBIÇÃO DA TABELA ---
        st.markdown("### Agendamentos Confirmados")
        st.dataframe(
            df_agendamentos_display, 
            hide_index=True, 
            use_container_width=True,
            column_config={
                "ID": st.column_config.Column("ID", width="small"),
                "horario": st.column_config.Column("Horário ⏰", width="small"),
                "cliente": st.column_config.Column("Cliente 👤"),
                "servico": st.column_config.Column("Serviço"),
                "preco": st.column_config.Column("Preço 💰", width="small"),
                "telemovel": st.column_config.Column("Telemóvel 📞"),
                "data": st.column_config.Column("Data", disabled=True),
                "data_hora_registro": st.column_config.Column("Registro", disabled=True)
            }
        )

        st.divider()

        # Estatísticas (Resumo)
        st.subheader("Resumo do Dia")
        
        total_agendamentos = len(df_agendamentos)
        valor_total_bruto = df_agendamentos['preco'].astype(float).sum()

        col_count, col_sum = st.columns(2)
        
        with col_count:
            st.metric("Total de Agendamentos", f"**{total_agendamentos}**")
        
        with col_sum:
            st.metric("Receita Prevista", formatar_moeda(valor_total_bruto), delta_color="off")
    
    # --- FILTRO E EXPORTAÇÃO DE DADOS (Mantido) ---
    st.divider()
    st.subheader("📊 Exportar Agenda por Período")
    
    if st.session_state.agendamentos:
        col_start, col_end = st.columns(2)
        
        hoje = datetime.date.today()
        
        # Tenta encontrar a data mais antiga na base de dados, senão usa hoje
        try:
            # Garante que as datas sejam tratadas como objetos date antes de min()
            data_minima = pd.to_datetime(pd.DataFrame(st.session_state.agendamentos)['data']).min().date()
        except:
            data_minima = hoje 
        
        with col_start:
            data_inicio = st.date_input("Data Inicial:", 
                                         value=data_minima,
                                         min_value=data_minima)
        
        with col_end:
            data_fim = st.date_input("Data Final:", 
                                         value=hoje, 
                                         min_value=data_inicio)

        # Filtra a base de dados completa (session_state) pelo período
        df_completo = pd.DataFrame(st.session_state.agendamentos)
        
        # Garante que a coluna 'data' seja do tipo data para comparação
        df_completo['data'] = pd.to_datetime(df_completo['data']).dt.date
        
        df_exportar = df_completo[
            (df_completo['data'] >= data_inicio) & 
            (df_completo['data'] <= data_fim)
        ].copy()
        
        # Prepara o DataFrame para download
        if not df_exportar.empty:
            df_exportar = df_exportar.rename(columns={
                'data_hora_registro': 'Registro_do_Sistema',
                'data': 'Data_Agendada',
                'horario': 'Horario',
                'cliente': 'Cliente',
                'telemovel': 'Telemovel',
                'servico': 'Servico',
                'preco': 'Preco'
            })
            
            df_exportar['Preco'] = df_exportar['Preco'].apply(formatar_moeda)

            csv_data = df_exportar.to_csv(index=False, sep=';').encode('utf-8')
            
            st.success(f"Total de {len(df_exportar)} agendamentos encontrados no período.")
            st.download_button(
                label="⬇️ Baixar CSV Filtrado",
                data=csv_data,
                file_name=f'agenda_{nome_barbearia.lower().replace(" ", "_")}_{data_inicio.strftime("%Y%m%d")}_a_{data_fim.strftime("%Y%m%d")}.csv', # Nome do arquivo de exportação dinâmico
                mime='text/csv',
                use_container_width=True
            )
        else:
            st.warning("Nenhum agendamento encontrado no período selecionado.")

    else:
        st.info("Não há dados de agendamento salvos para exportar.")