# admin_view.py
import streamlit as st
import pandas as pd
import datetime
import time

def render_admin_view(SERVICOS, formatar_moeda, gerar_link_whatsapp, salvar_dados):
    """
    Renderiza a interface de gestão, cancelamento e exportação para o administrador.
    """
    st.title("👑 Gestão Viking Cuts")
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
    agendamentos_filtrados = [
        a for a in st.session_state.agendamentos 
        if a.get('data') == data_str_admin
    ]

    if not agendamentos_filtrados:
        st.info(f"Nenhum agendamento para {data_visao_admin.strftime('%d/%m/%Y')} ainda!")
    else:
        # Converter a lista de dicionários filtrada para um DataFrame do pandas
        df_agendamentos = pd.DataFrame(agendamentos_filtrados)

        # Adicionar uma coluna de ID temporário para seleção e exclusão
        df_agendamentos['ID'] = range(1, len(df_agendamentos) + 1)
        
        # Reorganizar e Formatar para visualização
        df_agendamentos = df_agendamentos[['ID', 'horario', 'cliente', 'servico', 'preco', 'telemovel', 'data', 'data_hora_registro']]
        df_agendamentos_display = df_agendamentos.copy()
        df_agendamentos_display['preco'] = df_agendamentos_display['preco'].apply(formatar_moeda)
        
        # --- Formulário de Exclusão (Com Confirmação) ---
        st.markdown("### Cancelar Agendamento")
        with st.form("form_excluir_agendamento"):
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

            col_input, col_confirm, col_btn = st.columns([0.5, 0.3, 0.2])

            with col_input:
                id_para_excluir = st.number_input(
                    "Digite o ID do agendamento a ser cancelado:", 
                    min_value=1, 
                    max_value=max(1, len(df_agendamentos)), # Max value seguro
                    step=1,
                    key='id_input_admin'
                )
            
            with col_confirm:
                # CHECKBOX DE CONFIRMAÇÃO
                st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                confirmacao = st.checkbox("Confirmar Exclusão?", key="confirm_delete")
            
            with col_btn:
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                
                # O botão agora tem um rótulo claro e usa a variável 'confirmacao'
                submitted_excluir = st.form_submit_button("🚨 FINALIZAR EXCLUSÃO", 
                                                         type="primary", 
                                                         use_container_width=True,
                                                         disabled=not confirmacao)


            if submitted_excluir:
                if confirmacao:
                    indice_a_remover_df = int(id_para_excluir) - 1 
                    
                    try:
                        # 1. IDENTIFICAR O ITEM NO DATAFRAME FILTRADO
                        agendamento_a_remover_parcial = df_agendamentos.iloc[indice_a_remover_df]
                        
                        # 🚀 CORREÇÃO DA LÓGICA DE BUSCA: Garante que a data seja uma STRING
                        data_alvo = str(agendamento_a_remover_parcial['data']) 
                        
                        if isinstance(data_alvo, datetime.date):
                             data_alvo = data_alvo.strftime("%Y-%m-%d")

                        horario_alvo = agendamento_a_remover_parcial['horario']
                        cliente_alvo = agendamento_a_remover_parcial['cliente']
                        
                        indice_original = -1
                        
                        # 2. PROCURAR O ITEM CORRETO NA LISTA ORIGINAL (st.session_state.agendamentos)
                        for i, item in enumerate(st.session_state.agendamentos):
                            # Compara as chaves únicas (Data, Horário e Cliente)
                            if (item.get('data') == data_alvo) and \
                               (item.get('horario') == horario_alvo) and \
                               (item.get('cliente') == cliente_alvo):
                                indice_original = i
                                break

                        if indice_original != -1:
                            # 3. REMOVER E SALVAR
                            st.session_state.agendamentos.pop(indice_original)
                            salvar_dados(st.session_state.agendamentos)

                            st.success(f"Agendamento (ID: {id_para_excluir}) de {cliente_alvo} cancelado com sucesso. Agenda atualizada!")
                            time.sleep(1) 
                            st.rerun() 
                        else:
                            st.error("Erro: Não foi possível localizar o agendamento na base de dados principal.")
                            
                    except IndexError:
                        st.error("Erro: ID de agendamento inválido. Por favor, verifique o número na tabela.")
                    except Exception as e:
                        st.error(f"Erro inesperado ao cancelar: {e}")

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
                file_name=f'agenda_viking_cuts_{data_inicio.strftime("%Y%m%d")}_a_{data_fim.strftime("%Y%m%d")}.csv',
                mime='text/csv',
                use_container_width=True
            )
        else:
             st.warning("Nenhum agendamento encontrado no período selecionado.")

    else:
        st.info("Não há dados de agendamento salvos para exportar.")