import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date
import requests

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA & TEMA VISUAL (INSIDEWORK)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="InsideWork - Produzir com Consciência",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS personalizada com as cores da Logo (Azul #1E64EB, Verde #10B981, Dark #0F172A)
st.markdown("""
    <style>
    :root {
        --primary: #1E64EB;
        --success: #10B981;
        --warning: #F59E0B;
        --dark: #0F172A;
        --bg: #F8FAFC;
    }
    .stApp {
        background-color: var(--bg);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .header-card {
        background: linear-gradient(135deg, #1E64EB 0%, #1D4ED8 100%);
        color: white;
        padding: 28px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 10px 15px -3px rgba(30, 100, 235, 0.25);
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        text-align: center;
    }
    .badge-role {
        background-color: #DBEAFE;
        color: #1E64EB;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    div[data-testid="stSidebarNav"] {
        padding-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. GERENCIAMENTO DE SESSÃO & BASE DE USUÁRIOS
# -----------------------------------------------------------------------------
USERS = {
    "colaborador@insidework.com.br": {
        "password": "colab123",
        "name": "Carlos Silva",
        "role": "Colaborador",
        "cargo": "Desenvolvedor Full Stack Senior • Engenharia de Software"
    },
    "gestor@insidework.com.br": {
        "password": "rh123",
        "name": "Mariana Costa",
        "role": "Gestor de RH",
        "cargo": "Gerente de Pessoas & Cultura"
    },
    "diretoria@insidework.com.br": {
        "password": "admin123",
        "name": "Roberto Almeida",
        "role": "Diretoria / Admin",
        "cargo": "Diretor de Operações e Tecnologia"
    }
}

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "leave_requests" not in st.session_state:
    st.session_state.leave_requests = []
if "clock_records" not in st.session_state:
    st.session_state.clock_records = [
        {"data": "2026-10-21", "entrada": "08:00", "almoco": "12:00", "retorno": "13:00", "status": "Em Jornada"}
    ]

# -----------------------------------------------------------------------------
# 3. TELA DE LOGIN (AUTENTICAÇÃO ISOLADA)
# -----------------------------------------------------------------------------
def render_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-bottom: 24px;">
                <h1 style="color: #1E64EB; font-weight: 800; font-size: 2.5rem; margin-bottom: 0;">INSIDE WORK</h1>
                <p style="color: #64748B; font-size: 0.95rem; font-weight: 500;">
                    <span style="color: #10B981;">PRODUZIR COM CONSCIÊNCIA</span>, CRESCER COM CONSISTÊNCIA
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            st.subheader("Acesso à Plataforma")
            email_input = st.text_input("E-mail corporativo", placeholder="seu.email@empresa.com.br")
            password_input = st.text_input("Senha de acesso", type="password", placeholder="••••••••")
            
            submit_btn = st.form_submit_button("Entrar no Sistema", use_container_width=True, type="primary")
            
            if submit_btn:
                email_clean = email_input.strip().lower()
                if email_clean in USERS and USERS[email_clean]["password"] == password_input:
                    st.session_state.authenticated = True
                    st.session_state.user_data = USERS[email_clean]
                    st.session_state.user_data["email"] = email_clean
                    st.success("Autenticado com sucesso!")
                    st.rerun()
                else:
                    st.error("E-mail ou senha incorretos. Verifique suas credenciais de acesso.")

# -----------------------------------------------------------------------------
# 4. PAINEL EXCLUSIVO: COLABORADOR
# -----------------------------------------------------------------------------
def render_colaborador():
    user = st.session_state.user_data
    
    # Cabeçalho Principal
    st.markdown(f"""
        <div class="header-card">
            <span class="badge-role" style="background: rgba(255,255,255,0.2); color: white;">Perfil Colaborador</span>
            <h1 style="margin: 8px 0 4px 0; font-size: 2rem;">Olá, {user['name']}! 👋</h1>
            <p style="margin: 0; opacity: 0.9; font-size: 1rem;">{user['cargo']}</p>
        </div>
    """, unsafe_allow_html=True)

    # Botões de Ação Direta
    btn_col1, btn_col2, _ = st.columns([1, 1, 2])
    with btn_col1:
        modal_ponto = st.popover("⏱️ Registrar Ponto Agora", use_container_width=True)
    with btn_col2:
        modal_folga = st.popover("✈️ Solicitar Folga/Férias", use_container_width=True)

    # Modal / Popover de Ponto Eletrônico
    with modal_ponto:
        st.subheader("Registro de Ponto Eletrônico")
        st.write(f"**Data Atual:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        st.info("Localização GPS verificada: Escritório Central / Home Office Autenticado")
        
        tipo_ponto = st.selectbox("Selecione o evento", ["Entrada", "Saída para Almoço", "Retorno de Almoço", "Saída Definitiva"])
        if st.button("Confirmar Registro", type="primary", use_container_width=True):
            agora = datetime.now().strftime("%H:%M:%S")
            st.session_state.clock_records.append({
                "data": date.today().strftime("%Y-%m-%d"),
                "evento": tipo_ponto,
                "horario": agora
            })
            st.success(f"Ponto registrado com sucesso ({tipo_ponto} às {agora})!")

    # Modal / Popover de Solicitação de Folga/Férias
    with modal_folga:
        st.subheader("Nova Solicitação de Ausência / Férias")
        with st.form("leave_form"):
            tipo_ausencia = st.selectbox("Tipo de Solicitação", [
                "Férias Regulamentares", 
                "Folga por Banco de Horas", 
                "Licença Médica / Atestado"
            ])
            data_inicio = st.date_input("Data de Início", min_value=date.today())
            data_fim = st.date_input("Data do Término", min_value=data_inicio)
            justificativa = st.text_area("Justificativa ou Observações", placeholder="Descreva brevemente o motivo...")
            
            dias_totais = (data_fim - data_inicio).days + 1
            st.caption(f"📅 Total de dias solicitados: **{dias_totais} dia(s)**")
            
            enviar_solicitacao = st.form_submit_button("Enviar Solicitação ao RH", type="primary", use_container_width=True)
            
            if enviar_solicitacao:
                st.session_state.leave_requests.append({
                    "colaborador": user["name"],
                    "email": user["email"],
                    "tipo": tipo_ausencia,
                    "inicio": str(data_inicio),
                    "fim": str(data_fim),
                    "dias": dias_totais,
                    "status": "Pendente",
                    "justificativa": justificativa
                })
                st.success("Sua solicitação de folga/férias foi encaminhada para aprovação do Gestor de RH!")

    st.markdown("<br>", unsafe_allow_html=True)

    # Linha de Métricas
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Horas Trabalhadas", "154h / 168h", delta="Meta do mês")
    with m2:
        st.metric("Banco de Horas", "+12h 30m", delta="+2.5h esta semana")
    with m3:
        st.metric("Férias Acumuladas", "18 dias", delta="Próximo venc.: Out/2026")
    with m4:
        st.metric("Score de Produtividade (SPS)", "94%", delta="Excelente (NR-17 OK)")

    # Gráfico de Evolução de Horas
    st.subheader("Evolução de Horas Trabalhadas")
    df_horas = pd.DataFrame({
        "Dia": ["01/10", "02/10", "05/10", "06/10", "07/10", "08/10", "09/10", "12/10", "13/10", "14/10", "15/10", "16/10"],
        "Horas": [8.0, 8.5, 8.0, 9.0, 8.0, 8.0, 7.5, 8.0, 8.5, 9.0, 8.0, 8.0]
    })
    fig = px.bar(df_horas, x="Dia", y="Horas", color_discrete_sequence=["#1E64EB"])
    fig.add_hline(y=8.0, line_dash="dash", line_color="#10B981", annotation_text="Jornada Padrão (8h)")
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # Guia NR-17 & Pausas Ergonômicas
    st.info("💡 **Alerta Ergonômico NR-17:** Você está contínuo em atividade a 1h 45m. Recomendamos uma pausa ativa de 5 minutos para alongamento.")

# -----------------------------------------------------------------------------
# 5. PAINEL EXCLUSIVO: GESTOR DE RH / LÍDER
# -----------------------------------------------------------------------------
def render_gestor():
    user = st.session_state.user_data
    
    st.markdown(f"""
        <div class="header-card" style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);">
            <span class="badge-role" style="background: #F59E0B; color: white;">Perfil Gestor de RH</span>
            <h1 style="margin: 8px 0 4px 0; font-size: 2rem;">Painel de Gestão de Pessoas & Equipe</h1>
            <p style="margin: 0; opacity: 0.9;">Monitoramento de saúde laboral, carga preditiva e aprovações de ausências.</p>
        </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("SPS Média da Equipe", "86%", delta="+4% vs mês anterior")
    with m2:
        st.metric("Risco de Burnout (IA)", "2 Colaboradores", delta="-30% licenças médicas", delta_color="inverse")
    with m3:
        st.metric("Conformidade NR-1 / NR-17", "98%", delta="Auditado em Out/2026")
    with m4:
        st.metric("Solicitações Pendentes", len(st.session_state.leave_requests))

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 Solicitantes de Folga/Férias", "🧠 Padrões Preditivos de IA", "🔄 Integração Jira/Trello"])

    with tab1:
        st.subheader("Gestão de Folgas e Férias Solicitadas")
        if not st.session_state.leave_requests:
            st.write("Nenhuma solicitação pendente no momento.")
        else:
            for idx, req in enumerate(st.session_state.leave_requests):
                with st.expander(f"📌 {req['colaborador']} - {req['tipo']} ({req['dias']} dias)"):
                    st.write(f"**Período:** {req['inicio']} até {req['fim']}")
                    st.write(f"**Justificativa:** {req['justificativa']}")
                    st.write(f"**Status Atual:** {req['status']}")
                    
                    c1, c2, _ = st.columns([1, 1, 3])
                    with c1:
                        if st.button("Aprovar", key=f"app_{idx}", type="primary"):
                            req['status'] = "Aprovado"
                            st.success("Solicitação Aprovada!")
                            st.rerun()
                    with c2:
                        if st.button("Recusar", key=f"rec_{idx}"):
                            req['status'] = "Recusado"
                            st.error("Solicitação Recusada.")
                            st.rerun()

    with tab2:
        st.subheader("🧠 Central Consultiva de IA (Análise Preditiva & Ergonomia)")
        st.caption("Envie métricas do colaborador e pergunte à IA do InsideWork para obter orientações humanizadas (NR-17/LGPD).")

        # Formulário para enviar os dados
        with st.form("form_consulta_ia"):
            col_f1, col_f2 = st.columns(2)
            
            with col_f1:
                nome_colab = st.text_input("Nome do Colaborador", value="Lanes")
                horas_trab = st.number_input("Horas Trabalhadas (hoje)", value=8.0, step=0.5)
                min_pausa = st.number_input("Minutos de Pausa", value=10, step=5)
                qtd_pausas = st.number_input("Quantidade de Pausas", value=1, step=1)

            with col_f2:
                atividade_fisica = st.slider("Atividade Física (Teclado/Mouse %)", 0.0, 100.0, 90.0)
                tarefas_jira = st.number_input("Tarefas Concluídas (Jira/Trello)", value=4, step=1)
                pergunta = st.text_area("Pergunta do Gestor para a IA", 
                                        value="A Lanes entregou todas as tarefas, mas notamos que ela quase não fez pausas. Como devo abordar essa situação?")

            btn_analisar = st.form_submit_button("⚡ Processar Análise SPS & Consultar IA", type="primary", use_container_width=True)

        # Chamada para o backend em FastAPI quando o botão for clicado
        if btn_analisar:
            payload = {
                "nome_colaborador": nome_colab,
                "horas_trabalhadas": horas_trab,
                "minutos_pausa": min_pausa,
                "qtd_pausas": qtd_pausas,
                "nivel_atividade_fisica": atividade_fisica,
                "tarefas_concluidas_jira": tarefas_jira,
                "pergunta_gestor": pergunta
            }

            with st.spinner("Calculando SPS e gerando parecer da IA via Google Gemini..."):
                try:
                    response = requests.post("http://127.0.0.1:8000/api/sps/analisar", json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        resultado = response.json()

                        st.divider()
                        st.success("Análise concluída com sucesso!")

                        res_c1, res_c2, res_c3 = st.columns(3)
                        with res_c1:
                            st.metric("Score SPS Calculado", f"{resultado['sps_score']}/100")
                        with res_c2:
                            st.metric("Classificação", resultado['classificacao'])
                        with res_c3:
                            status_alerta = "⚠️ ATIVO" if resultado['alerta_desengajamento'] else "✅ Normal"
                            st.metric("Alerta Desengajamento", status_alerta)

                        st.markdown("### 🤖 Parecer Consultivo da IA (Gemini)")
                        st.info(resultado['recomendacao_ia'])

                    else:
                        st.error(f"Erro na API: {response.status_code} - {response.text}")

                except requests.exceptions.ConnectionError:
                    st.error("❌ Não foi possível conectar ao backend! Confirme se o servidor `main_api.py` está rodando em http://127.0.0.1:8000")

    with tab3:
        st.subheader("Sincronização API Jira & Trello")
        st.success("✅ Conexão via API ativa. Cruzando entregas de tarefas com esforço físico acumulado.")

# -----------------------------------------------------------------------------
# 6. PAINEL EXCLUSIVO: DIRETORIA / ADMIN
# -----------------------------------------------------------------------------
def render_diretoria():
    st.markdown("""
        <div class="header-card" style="background: linear-gradient(135deg, #10B981 0%, #047857 100%);">
            <span class="badge-role" style="background: rgba(255,255,255,0.2); color: white;">Perfil Diretoria / Admin</span>
            <h1 style="margin: 8px 0 4px 0; font-size: 2rem;">Painel Executivo & Calculadora de ROI</h1>
            <p style="margin: 0; opacity: 0.9;">Acompanhamento financeiro do modelo de assinatura e documentação estratégica.</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["💰 Calculadora de ROI & Assinatura", "📄 Documentação (5W2H & Canvas)"])

    with tab1:
        st.subheader("Simulador de Retorno sobre Investimento (ROI)")
        col_sim1, col_sim2 = st.columns(2)
        
        with col_sim1:
            num_usuarios = st.slider("Número de Colaboradores Ativos", min_value=10, max_value=1000, value=150, step=10)
            valor_por_usuario = 14.98
            custo_mensal = num_usuarios * valor_por_usuario
            
            st.metric("Investimento Mensal (Assinatura)", f"R$ {custo_mensal:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            st.caption("Valor fixo corporativo de **R$ 14,98 / colaborador / mês**")

        with col_sim2:
            economia_estimada = (num_usuarios * 350.00) # Economia média com prevenção de afastamentos
            roi_calculado = ((economia_estimada - custo_mensal) / custo_mensal) * 100
            
            st.metric("Economia Estimada por Mês (Redução de Burnout)", f"R$ {economia_estimada:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            st.metric("ROI Estimado do Projeto", f"{roi_calculado:.1f}%")

    with tab2:
        st.subheader("Documentação Oficial do Projeto InsideWork")
        
        with st.expander("📌 Matriz 5W2H", expanded=True):
            st.markdown("""
            * **WHAT (O que é):** Software de captura de metadados de desempenho com IA preditiva para evitar sobrecarga.
            * **WHO (Quem participa):** Colaboradores (Home office/presencial), Gestores de RH e Desenvolvedores.
            * **WHERE (Onde ocorre):** Ambientes corporativos de trabalho híbrido e escritórios.
            * **WHEN (Quando):** A partir da implementação do projeto.
            * **WHY (Propósito):** Promover produtividade sustentável, reduzindo em até 30% faltas por burnout e adequando às NRs (NR-1 e NR-17).
            * **HOW (Como será feito):** Coleta de metadados de atividade física (uso de teclado/mouse) sem gravar telas/conteúdos, gerando o Score SPS e conectando ao Jira/Trello.
            * **HOW MUCH (Preço):** Assinatura corporativa de **R$ 14,98 mensais por colaborador**.
            """)
            
        with st.expander("📊 Business Model Canvas (BM Canvas)", expanded=True):
            st.markdown("""
            * **Proposta de Valor:** Melhorar a produtividade humanizando relações e prevenindo riscos de burnout.
            * **Segmento de Clientes:** Empresas com colaboradores em computador e gestores buscando equilíbrio entre entrega e bem-estar.
            * **Fontes de Receita:** Assinatura mensal corporativa de R$ 14,98 por usuário ativo.
            * **Canais:** LinkedIn, vendas B2B e integrações nativas Jira/Trello.
            """)

# -----------------------------------------------------------------------------
# 7. ROTEAMENTO PRINCIPAL DA APLICAÇÃO
# -----------------------------------------------------------------------------
def main():
    if not st.session_state.authenticated:
        render_login()
    else:
        user = st.session_state.user_data
        
        with st.sidebar:
            st.markdown("### ⚡ **InsideWork**")
            st.caption("Produzir com consciência, crescer com consistência")
            st.divider()
            
            st.write(f"👤 **Usuário:** {user['name']}")
            st.write(f"🏷️ **Perfil:** {user['role']}")
            st.write(f"📧 **E-mail:** {user['email']}")
            
            st.divider()
            
            if st.button("🚪 Encerrar Sessão (Sair)", type="secondary", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_data = None
                st.rerun()

        if user["role"] == "Colaborador":
            render_colaborador()
        elif user["role"] == "Gestor de RH":
            render_gestor()
        elif user["role"] == "Diretoria / Admin":
            render_diretoria()

if __name__ == "__main__":
    main()