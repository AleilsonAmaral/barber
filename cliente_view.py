# cliente_view.py
import streamlit as st
import datetime
import pandas as pd
import time 

# A função AGORA ENGLOBA TODO O CÓDIGO
def render_cliente_view(SERVICOS, HORARIOS, formatar_moeda, gerar_link_whatsapp, salvar_dados):
    """
    Renderiza a interface de agendamento e cancelamento para o cliente.
    """
    st.title("✂️ Viking Cuts")
    st.write("Agende o seu corte em segundos.")
    st.divider()

    # Passo 1: Escolher Serviço
    st.subheader("1. Escolha o Serviço")
    
    servico_escolhido = st.selectbox(
        "Selecione o tipo de corte:",
        options=list(SERVICOS.keys()),
        format_func=lambda x: f"{x} - {formatar_moeda(SERVICOS[x])}"
    )

    # Passo 2: Escolher Data e Horário
    st.subheader("2. Escolha a Data e Horário")
    
    # --- CÁLCULO DE LIMITES ---
    hoje = datetime.date.today()
    limite_maximo = hoje + datetime.timedelta(days=7)
    # -------------------------

    # Seletor de Data
    data_escolhida = st.date_input(
        "Selecione a Data:",
        min_value=hoje,
        max_value=limite_maximo,
        value=hoje
    )
    
    data_str = data_escolhida.strftime("%Y-%m-%d")

    # --- Lógica de Filtragem de Horários ---
    agendamentos_hoje = [
        a for a in st.session_state.agendamentos
        if a.get('data') == data_str
    ]
    
    horarios_ocupados = [a['horario'] for a in agendamentos_hoje]
    horarios_livres = [h for h in HORARIOS if h not in horarios_ocupados]

    submissao_habilitada = bool(horarios_livres)
    
    if not horarios_livres:
        st.error(f"Desculpe, não há mais horários disponíveis para {data_escolhida.strftime('%d/%m/%Y')}!")
    
    horario_escolhido = None
    if horarios_livres:
        horario_escolhido = st.selectbox(f"Horários Disponíveis em {data_escolhida.strftime('%d/%m/%Y')}:", horarios_livres)

    # -------------------------------------------------------------
    # Passo 3: Dados Pessoais e Escolha do Método
    st.subheader("3. Seus Dados e Ação")
    
    # CAMPOS FORA DO FORMULÁRIO para serem usados por ambos os botões
    nome_cliente = st.text_input("Seu Nome:")
    telemovel = st.text_input("Telemóvel (Opcional):")
    
    # Verifica se os dados mínimos estão preenchidos para habilitar os botões
    pode_agir = bool(nome_cliente.strip()) and bool(horario_escolhido)

    st.markdown("---")
    st.markdown("#### Escolha como deseja Agendar:")
    
    col_app, col_wpp = st.columns(2)

    # Lógica para o Agendamento Direto no App
    with col_app:
        btn_app = st.button("✅ Agendar pelo App (Recomendado)", use_container_width=True, disabled=not pode_agir)

    # Lógica para o Agendamento via WhatsApp
    with col_wpp:
        # Link do WhatsApp
        if pode_agir:
            confirmacao_wpp = f"{servico_escolhido} para {data_escolhida.strftime('%d/%m/%Y')} às {horario_escolhido}"
            link_wpp = gerar_link_whatsapp(confirmacao_wpp, horario_escolhido, nome_cliente.strip())
            
            # Adiciona o link ao botão do WhatsApp usando Markdown/HTML
            st.markdown(f"""
                <a href="{link_wpp}" target="_blank">
                    <button style="background-color:#25D366; color:white; border:none; padding:10px 20px; border-radius:5px; cursor:pointer; width:100%; height:38px;">
                        📱 Agendar pelo WhatsApp
                    </button>
                </a>
            """, unsafe_allow_html=True)
        else:
            st.button("📱 Agendar pelo WhatsApp", disabled=True, use_container_width=True) # Botão desabilitado

    # --- EXECUÇÃO DA LÓGICA DO APP (SALVAR) ---
    if btn_app:
        # Salvar no "Banco de Dados" (Session State)
        novo_agendamento = {
            "cliente": nome_cliente.strip(),
            "telemovel": telemovel,
            "servico": servico_escolhido,
            "preco": SERVICOS[servico_escolhido],
            "horario": horario_escolhido,
            "data": data_str,
            "data_hora_registro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        st.session_state.agendamentos.append(novo_agendamento)
        
        # Ação de Persistência
        salvar_dados(st.session_state.agendamentos)

        # Feedback e Recarregamento
        st.success(f"Agendado com sucesso para {data_escolhida.strftime('%d/%m/%Y')} às **{horario_escolhido}**!")
        st.balloons()
        time.sleep(1)
        st.rerun() # Recarrega para limpar o formulário e atualizar os horários

    # -------------------------------------------------------------
    # --- 4. CANCELAMENTO DE AGENDAMENTO (VISÃO CLIENTE) ---
    st.divider()
    st.subheader("🗓️ Cancelar Agendamento Existente")
    st.write("Para cancelar um agendamento, digite seu nome e clique em 'Buscar Meus Agendamentos'.")

    with st.form("form_cancelamento"):
        nome_cliente_cancelar = st.text_input("Seu Nome Completo:", key="nome_cancelar")
        btn_buscar = st.form_submit_button("Buscar Meus Agendamentos", type="secondary")

    if btn_buscar and nome_cliente_cancelar:
        nome_cliente_cancelar = nome_cliente_cancelar.strip()
        hoje_str = datetime.date.today().strftime("%Y-%m-%d")

        # 1. Filtra agendamentos futuros para o cliente
        meus_agendamentos = [
            a for a in st.session_state.agendamentos
            if (a.get('cliente', '').strip().lower() == nome_cliente_cancelar.lower()) and
               (a.get('data') >= hoje_str)
        ]
        
        if not meus_agendamentos:
            st.info(f"Nenhum agendamento futuro encontrado para {nome_cliente_cancelar}.")
        else:
            st.success(f"Encontrados {len(meus_agendamentos)} agendamento(s) futuro(s).")
            df_meus_agendamentos = pd.DataFrame(meus_agendamentos)
            
            # Adicionar um ID temporário para seleção
            df_meus_agendamentos['ID_Canc'] = range(1, len(df_meus_agendamentos) + 1)
            
            # Cria a string de exibição para o selectbox
            df_meus_agendamentos['Exibir'] = df_meus_agendamentos.apply(
                lambda row: f"{row['data']} às {row['horario']} ({row['servico']})", axis=1
            )
            
            with st.form("confirm_cancel"):
                agendamento_selecionado_id = st.selectbox(
                    "Qual agendamento deseja cancelar?",
                    options=df_meus_agendamentos['ID_Canc'],
                    format_func=lambda x: df_meus_agendamentos[df_meus_agendamentos['ID_Canc'] == x]['Exibir'].iloc[0]
                )
                
                confirm_btn = st.form_submit_button("Sim, Cancelar Agendamento Selecionado", type="primary")

                if confirm_btn:
                    # 1. Localizar o agendamento no DataFrame de exibição para obter as chaves
                    agendamento_remover_df = df_meus_agendamentos[df_meus_agendamentos['ID_Canc'] == agendamento_selecionado_id].iloc[0].to_dict()
                    
                    # 2. Chaves únicas para localizar na lista original
                    data_alvo = agendamento_remover_df.get('data')
                    horario_alvo = agendamento_remover_df.get('horario')
                    servico_alvo = agendamento_remover_df.get('servico')

                    indice_original = -1
                    for i, item in enumerate(st.session_state.agendamentos):
                        if (item.get('data') == data_alvo) and \
                           (item.get('horario') == horario_alvo) and \
                           (item.get('servico') == servico_alvo) and \
                           (item.get('cliente', '').strip().lower() == nome_cliente_cancelar.lower()):
                            indice_original = i
                            break

                    if indice_original != -1:
                        st.session_state.agendamentos.pop(indice_original)
                        # Ação de Persistência
                        salvar_dados(st.session_state.agendamentos)
                        st.success(f"Cancelamento de {servico_alvo} em {data_alvo} às {horario_alvo} efetuado com sucesso!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Erro ao localizar o agendamento para cancelamento. Tente novamente.")