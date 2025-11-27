# cliente_view.py
import streamlit as st
import datetime
import pandas as pd
import time 
import re 
import random 
import string 

# --- FUNÇÕES DE UTILIDADE ---

def gerar_codigo_confirmacao(length=6):
    """Gera um código alfanumérico único para cancelamento."""
    caracteres = string.ascii_uppercase + string.digits 
    return ''.join(random.choice(caracteres) for i in range(length))

def validar_celular(celular):
    """Verifica se o celular (no formato brasileiro com DDD) é válido e o retorna limpo."""
    limpo = re.sub(r'[\D]', '', celular)
    
    if len(limpo) == 11:
        return True, limpo
    return False, None

# --- FUNÇÕES DE NAVEGAÇÃO INTERNA ---

def inicializar_estado_agendamento():
    """Inicializa as variáveis de sessão para o fluxo de agendamento."""
    if 'agendamento_data' not in st.session_state:
        st.session_state.agendamento_data = {} 
    if 'agendamento_step' not in st.session_state:
        st.session_state.agendamento_step = 1

def proximo_passo():
    st.session_state.agendamento_step += 1
    st.rerun()

def passo_anterior():
    st.session_state.agendamento_step -= 1
    st.rerun()

# --- FUNÇÃO PRINCIPAL ---

def render_cliente_view(SERVICOS, HORARIOS, formatar_moeda, gerar_link_whatsapp, salvar_dados, config_barbearia, cliente_action):
    """Renderiza a interface de agendamento e cancelamento para o cliente."""
    
    # --- Extrair Configurações Dinâmicas ---
    nome_barbearia = config_barbearia.get('name', 'BARBEARI Angels') 
    whatsapp_barbearia = config_barbearia.get('whatsapp', '351999999999') 
    
    st.divider()

    # --- LÓGICA DE REDIRECIONAMENTO BASEADA NA AÇÃO ---
    if cliente_action == 'AGENDAR':
        render_agendamento(SERVICOS, HORARIOS, formatar_moeda, gerar_link_whatsapp, salvar_dados, whatsapp_barbearia)
    
    elif cliente_action == 'MEUS_AGENDAMENTOS':
        render_cancelamento_seguro(salvar_dados)
        
    elif cliente_action == 'HOME':
        pass
        
# --- MÓDULO DE AGENDAMENTO EM 3 PASSOS ---
def render_agendamento(SERVICOS, HORARIOS, formatar_moeda, gerar_link_whatsapp, salvar_dados, whatsapp_barbearia):
    
    inicializar_estado_agendamento()
    
    progress_value = min(st.session_state.agendamento_step / 3.0, 1.0) 

    st.progress(progress_value, text=f"Progresso: Passo {st.session_state.agendamento_step} de 3")

    # --- PASSO 1: SERVIÇO ---
    if st.session_state.agendamento_step == 1:
        st.subheader("1. ✂️ Serviço")
        st.markdown("---")
        
        cols = st.columns(2)
        
        servico_selecionado = st.session_state.agendamento_data.get('servico')

        for i, (servico, preco) in enumerate(SERVICOS.items()):
            col = cols[i % 2]
            with col:
                if st.button(
                    f"{servico} - {formatar_moeda(preco)}", 
                    key=f"servico_{i}", 
                    use_container_width=True,
                    type="primary" if servico == servico_selecionado else "secondary"
                ):
                    st.session_state.agendamento_data['servico'] = servico
                    st.session_state.agendamento_data['preco'] = preco
                    proximo_passo()
        
        if servico_selecionado:
            st.success(f"Serviço Selecionado: **{servico_selecionado}**")

    # --- PASSO 2: HORÁRIO ---
    elif st.session_state.agendamento_step == 2:
        st.subheader("2. 🗓️ Data e Horário")
        st.markdown("---")

        hoje = datetime.date.today()
        limite_maximo = hoje + datetime.timedelta(days=7)

        data_escolhida = st.date_input(
            "Selecione a Data:",
            min_value=hoje,
            max_value=limite_maximo,
            value=st.session_state.agendamento_data.get('data_obj', hoje),
            key="data_picker"
        )
        
        st.session_state.agendamento_data['data_obj'] = data_escolhida
        data_str = data_escolhida.strftime("%Y-%m-%d")
        
        barber_id_atual = st.session_state.get('barber_id', 'GERAL')
        
        agendamentos_hoje = [
            a for a in st.session_state.agendamentos
            if a.get('data') == data_str and a.get('barber_id') == barber_id_atual
        ]
        
        horarios_ocupados = [a['horario'] for a in agendamentos_hoje]
        horarios_livres = [h for h in HORARIOS if h not in horarios_ocupados]

        horario_selecionado = st.session_state.agendamento_data.get('horario')

        st.markdown(f"#### Horários Livres para {data_escolhida.strftime('%d/%m/%Y')}:")
        
        if not horarios_livres:
            st.error("❌ Não há horários disponíveis para este dia.")
        else:
            COLUNAS_GRID = 4 
            cols = st.columns(COLUNAS_GRID)
            
            for i, horario in enumerate(horarios_livres):
                col = cols[i % COLUNAS_GRID]
                with col:
                    if st.button(
                        horario, 
                        key=f"hora_{horario}", 
                        use_container_width=True,
                        type="primary" if horario == horario_selecionado else "secondary"
                    ):
                        st.session_state.agendamento_data['horario'] = horario
                        st.session_state.agendamento_data['data'] = data_str
                        proximo_passo() 
        
        st.markdown("---")
        if st.button("⬅️ Voltar ao Serviço", key="btn_back_step2"):
            passo_anterior()

    # --- PASSO 3: DADOS PESSOAIS ---
    elif st.session_state.agendamento_step == 3:
        st.subheader("3. 🧑 Seus Dados")
        st.markdown("---")
        
        servico = st.session_state.agendamento_data['servico']
        data_hora = f"{st.session_state.agendamento_data['data_obj'].strftime('%d/%m')} às {st.session_state.agendamento_data['horario']}"

        st.info(f"Confirmação: **{servico}** em **{data_hora}**")

        with st.form("form_dados_cliente"):
            nome_cliente = st.text_input("Seu Nome Completo:", value=st.session_state.agendamento_data.get('nome', ''))
            celular_input = st.text_input("Seu Celular (Apenas números, Ex: 11987654321):", value=st.session_state.agendamento_data.get('celular', ''))
            
            st.markdown("---")
            col_back, col_submit = st.columns(2)
            
            with col_back:
                if st.form_submit_button("⬅️ Voltar ao Horário", type="secondary"):
                    passo_anterior()

            with col_submit:
                btn_confirmar = st.form_submit_button("✅ Confirmar Agendamento", type="primary")

        if btn_confirmar:
            # 1. Validação
            valido, celular_limpo = validar_celular(celular_input)
            
            if not nome_cliente.strip():
                st.error("Por favor, preencha o Nome Completo.")
            elif not valido:
                st.error("O número de Celular é inválido. Digite 11 dígitos (com DDD e sem pontuação).")
            else:
                # 2. Geração do Código de Segurança
                codigo = gerar_codigo_confirmacao()

                # 3. Salvar no "Banco de Dados"
                novo_agendamento = {
                    "barber_id": st.session_state.barber_id,
                    "cliente": nome_cliente.strip(),
                    "celular": celular_limpo, 
                    "servico": servico,
                    "preco": st.session_state.agendamento_data['preco'],
                    "horario": st.session_state.agendamento_data['horario'],
                    "data": st.session_state.agendamento_data['data'],
                    "codigo_cancelamento": codigo, 
                    "data_hora_registro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.agendamentos.append(novo_agendamento)
                salvar_dados(st.session_state.agendamentos)

                # 4. Feedback e Ação Final
                st.session_state.agendamento_step = 4 
                
                st.session_state.agendamento_data['nome'] = nome_cliente.strip()
                st.session_state.agendamento_data['celular'] = celular_limpo
                st.session_state.agendamento_data['codigo'] = codigo
                
                st.rerun()

    # --- PASSO 4: SUCESSO E LINK DE WHATSAPP ---
    elif st.session_state.agendamento_step == 4:
        st.success("🎉 Agendamento Confirmado com Sucesso!")
        st.balloons()
        
        dados = st.session_state.agendamento_data
        
        st.markdown(f"""
        ### Detalhes do Seu Agendamento:
        * **Cliente:** **{dados['nome']}**
        * **Serviço:** **{dados['servico']}**
        * **Data/Hora:** **{dados['data_obj'].strftime('%d/%m/%Y')} às {dados['horario']}**
        * **Código de Cancelamento:** **{dados['codigo']}**
        """)
        
        confirmacao_wpp = f"{dados['servico']} em {dados['data_obj'].strftime('%d/%m/%Y')}"
        
        link_wpp = gerar_link_whatsapp(
            whatsapp_barbearia, 
            confirmacao_wpp, 
            dados['horario'], 
            dados['nome'], 
            dados['codigo']
        )
        
        st.markdown("---")
        st.subheader("Ação Sugerida:")
        
        st.markdown(f"""
            <a href="{link_wpp}" target="_blank">
                <button style="background-color: #D4A657; color: #1C1C1C; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 600; width: 100%;">
                    💬 Enviar Confirmação via WhatsApp
                </button>
            </a>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        if st.button("Novo Agendamento"):
            st.session_state.agendamento_step = 1 
            st.session_state.agendamento_data = {} 
            st.rerun()

# --- MÓDULO DE CANCELAMENTO SEGURO (Ação: MEUS_AGENDAMENTOS) ---

def render_cancelamento_seguro(salvar_dados):
    st.subheader("📝 Meus Agendamentos")
    st.markdown("---")
    st.write("Cancele seu agendamento buscando por **Nome e Celular** ou usando o **Código de Confirmação**.")
    
    tab_nome_celular, tab_codigo = st.tabs(["🔑 Nome e Celular", "🔢 Código de Confirmação"])
    
    agendamento_encontrado = None
    
    # --- 1. Busca por Nome + Celular ---
    with tab_nome_celular:
        with st.form("form_cancel_nc"):
            nome_cancel = st.text_input("Seu Nome Completo:", key="nome_cancel_nc")
            celular_input_cancel = st.text_input("Seu Celular (11 dígitos):", key="cel_cancel_nc")
            btn_buscar_nc = st.form_submit_button("Buscar Agendamento", type="primary")

        if btn_buscar_nc:
            valido, celular_limpo = validar_celular(celular_input_cancel)
            
            if not nome_cancel.strip() or not valido:
                st.error("Preencha o Nome e um Celular válido (11 dígitos, sem pontuação).")
            else:
                hoje_str = datetime.date.today().strftime("%Y-%m-%d")
                
                agendamentos_match = [
                    a for a in st.session_state.agendamentos
                    if (a.get('cliente', '').strip().lower() == nome_cancel.strip().lower()) and
                       (a.get('celular') == celular_limpo) and
                       (a.get('data') >= hoje_str) 
                ]

                if agendamentos_match:
                    st.session_state.agendamentos_match = agendamentos_match
                    st.session_state.cancel_method = 'NC'
                    st.rerun() 
                else:
                    st.info(f"Nenhum agendamento futuro encontrado para {nome_cancel.strip()}.")

    # --- 2. Busca por Código de Confirmação ---
    with tab_codigo:
        with st.form("form_cancel_cod"):
            codigo_cancel = st.text_input("Código de Confirmação (Ex: 123ABC):", key="cod_cancel_cod")
            btn_buscar_cod = st.form_submit_button("Buscar Agendamento por Código", type="primary")

        if btn_buscar_cod and codigo_cancel.strip():
            codigo_cancel = codigo_cancel.strip().upper()
            hoje_str = datetime.date.today().strftime("%Y-%m-%d")
            
            agendamentos_match = [
                a for a in st.session_state.agendamentos
                if (a.get('codigo_cancelamento', '').upper() == codigo_cancel) and
                   (a.get('data') >= hoje_str) 
            ]
            
            if agendamentos_match:
                st.session_state.agendamentos_match = agendamentos_match
                st.session_state.cancel_method = 'CODIGO'
                st.rerun()
            else:
                st.error("Código de confirmação inválido ou agendamento já passou/foi cancelado.")

    # --- 3. Confirmação de Cancelamento (Exibida após a busca) ---
    if 'agendamentos_match' in st.session_state and st.session_state.agendamentos_match:
        
        st.divider()
        st.subheader("⚠️ Confirme o Cancelamento")
        
        agendamentos_match = st.session_state.agendamentos_match
        
        df_match = pd.DataFrame(agendamentos_match)
        df_match['Exibir'] = df_match.apply(
            lambda row: f"{row['data']} às {row['horario']} ({row['servico']}) - Cliente: {row['cliente']}", axis=1
        )
        
        df_match['ID_temp'] = df_match.index
        
        with st.container(): 
            agendamento_selecionado_id = st.selectbox(
                "Agendamento(s) Encontrado(s):",
                options=df_match['ID_temp'],
                format_func=lambda x: df_match[df_match['ID_temp'] == x]['Exibir'].iloc[0],
                key="select_cancel_match"
            )
            
            agendamento_a_cancelar = df_match[df_match['ID_temp'] == agendamento_selecionado_id].iloc[0].to_dict()

            if st.button(f"🔴 Cancelar Agendamento de {agendamento_a_cancelar['cliente']} em {agendamento_a_cancelar['data']}", type="primary"):
                
                # --- Lógica de Remoção ---
                data_alvo = agendamento_a_cancelar.get('data')
                horario_alvo = agendamento_a_cancelar.get('horario')
                cliente_alvo = agendamento_a_cancelar.get('cliente', '').strip().lower()
                celular_alvo = agendamento_a_cancelar.get('celular')
                codigo_alvo = agendamento_a_cancelar.get('codigo_cancelamento', '').upper()
                
                indice_original = -1
                for i, item in enumerate(st.session_state.agendamentos):
                    is_match = (
                        (item.get('data') == data_alvo) and
                        (item.get('horario') == horario_alvo) and
                        (item.get('cliente', '').strip().lower() == cliente_alvo) and
                        (item.get('celular') == celular_alvo)
                    )
                    
                    if st.session_state.cancel_method == 'CODIGO':
                         is_match = is_match and (item.get('codigo_cancelamento', '').upper() == codigo_alvo)

                    if is_match:
                        indice_original = i
                        break

                if indice_original != -1:
                    st.session_state.agendamentos.pop(indice_original)
                    salvar_dados(st.session_state.agendamentos)
                    
                    st.success(f"Agendamento de {agendamento_a_cancelar['cliente']} cancelado com sucesso!")
                    
                    del st.session_state.agendamentos_match
                    del st.session_state.cancel_method
                    
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Erro interno ao cancelar. Tente buscar novamente.")