# admin_view.py
import streamlit as st
import pandas as pd
import datetime
import time 

def render_admin_view(SERVICOS, formatar_moeda, gerar_link_whatsapp, salvar_dados, config_barbearia):
    """Renderiza a interface de gestão, visualização e exportação para o administrador."""
    
    nome_barbearia = config_barbearia.get('name', 'BARBEARIA VIKING') 
    
    st.title(f"👑 Gestão {nome_barbearia}")
    st.divider()

    # --- VISUALIZAÇÃO DA AGENDA DO DIA ---
    st.subheader("Agenda do Dia")
    
    data_visao_admin = st.date_input(
        "Selecione a Data para Visualização da Agenda:",
        value=datetime.date.today(),
        key='admin_date_picker'
    )
    data_str_admin = data_visao_admin.strftime("%Y-%m-%d")
    
    st.subheader(f"Agenda para {data_visao_admin.strftime('%d/%m/%Y')}")
    
    agendamentos_filtrados = [
        a for a in st.session_state.agendamentos 
        if a.get('data') == data_str_admin
    ]

    if not agendamentos_filtrados:
        st.info(f"Nenhum agendamento para {data_visao_admin.strftime('%d/%m/%Y')} ainda!")
    else:
        df_agendamentos = pd.DataFrame(agendamentos_filtrados)

        df_agendamentos = df_agendamentos.sort_values(by='horario').reset_index(drop=True)
        
        df_agendamentos['ID'] = range(1, len(df_agendamentos) + 1)
        
        if 'telemovel' in df_agendamentos.columns:
            df_agendamentos.rename(columns={'telemovel': 'celular'}, inplace=True)
        
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
                "celular": st.column_config.Column("Celular 📞"), 
                "codigo_cancelamento": st.column_config.Column("Cód. Cancel. 🔑", width="small"), 
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
    
    # --- FILTRO E EXPORTAÇÃO DE DADOS ---
    st.divider()
    st.subheader("📊 Exportar Agenda por Período")
    
    if st.session_state.agendamentos:
        col_start, col_end = st.columns(2)
        
        hoje = datetime.date.today()
        
        try:
            data_minima = pd.to_datetime(pd.DataFrame(st.session_state.agendamentos)['data']).min().date()
        except:
            data_minima = hoje 
        
        with col_start:
            data_inicio = st.date_input("Data Inicial:", 
                                         value=data_minima,
                                         min_value=data_minima,
                                         key='export_start')
        
        with col_end:
            data_fim = st.date_input("Data Final:", 
                                         value=hoje, 
                                         min_value=data_inicio,
                                         key='export_end')

        df_completo = pd.DataFrame(st.session_state.agendamentos)
        
        df_completo['data'] = pd.to_datetime(df_completo['data']).dt.date
        
        df_exportar = df_completo[
            (df_completo['data'] >= data_inicio) & 
            (df_completo['data'] <= data_fim)
        ].copy()
        
        # Prepara o DataFrame para download
        if not df_exportar.empty:
            
            if 'telemovel' in df_exportar.columns:
                df_exportar.rename(columns={'telemovel': 'celular'}, inplace=True)
            
            df_exportar = df_exportar.rename(columns={
                'data_hora_registro': 'Registro_do_Sistema',
                'data': 'Data_Agendada',
                'horario': 'Horario',
                'cliente': 'Cliente',
                'celular': 'Celular', 
                'servico': 'Servico',
                'preco': 'Preco',
                'codigo_cancelamento': 'Codigo_Cancelamento'
            })
            
            df_exportar['Preco'] = df_exportar['Preco'].apply(formatar_moeda) 

            csv_data = df_exportar.to_csv(index=False, sep=';').encode('utf-8')
            
            st.success(f"Total de {len(df_exportar)} agendamentos encontrados no período.")
            st.download_button(
                label="⬇️ Baixar CSV Filtrado",
                data=csv_data,
                file_name=f'agenda_{nome_barbearia.lower().replace(" ", "_")}_{data_inicio.strftime("%Y%m%d")}_a_{data_fim.strftime("%Y%m%d")}.csv', 
                mime='text/csv',
                use_container_width=True
            )
        else:
            st.warning("Nenhum agendamento encontrado no período selecionado.")

    else:
        st.info("Não há dados de agendamento salvos para exportar.")