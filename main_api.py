import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("A variável GEMINI_API_KEY não foi encontrada no arquivo .env!")

# Inicializa o cliente do Google Gemini
gemini_client = genai.Client(api_key=API_KEY)

# Inicializa a aplicação FastAPI
app = FastAPI(
    title="InsideWork API - Inteligência de Produtividade Sustentável",
    version="1.0.0",
    description="Backend para monitoramento humanizado, cálculo do SPS e recomendações preditivas via IA."
)

# -------------------------------------------------------------------
# MODELOS DE DADOS (Pydantic)
# -------------------------------------------------------------------

class DadosEntradaColaborador(BaseModel):
    nome_colaborador: str = Field(..., example="Lanes")
    horas_trabalhadas: float = Field(..., example=8.0, description="Total de horas logadas no dia")
    minutos_pausa: int = Field(..., example=15, description="Tempo total de pausas em minutos")
    qtd_pausas: int = Field(..., example=1, description="Quantidade de intervalos realizados")
    nivel_atividade_fisica: float = Field(..., example=85.0, description="Porcentagem de tempo com uso de teclado/mouse")
    tarefas_concluidas_jira: int = Field(..., example=2, description="Tarefas finalizadas no Jira/Trello")
    pergunta_gestor: str = Field(..., example="Notei que as pausas estão baixas. O que sugerir?")

class RespostaSPS(BaseModel):
    colaborador: str
    sps_score: int
    classificacao: str
    alerta_desengajamento: bool
    recomendacao_ia: str


# -------------------------------------------------------------------
# LÓGICA DE NEGÓCIO: Cálculo do SPS (Score de Produtividade Sustentável)
# -------------------------------------------------------------------

def calcular_sps_base(dados: DadosEntradaColaborador) -> tuple[int, str, bool]:
    """
    Aplica as regras de negócio do InsideWork:
    - Cruza atividade física com entregas no Jira/Trello.
    - Avalia equilíbrio entre trabalho e pausas (NR 1 / NR 17).
    - Premia produtividade saudável e sinaliza alertas.
    """
    score = 100
    alerta_desengajamento = False

    # Regra 1: Atividade baixa + Nenhuma entrega no Jira = Desengajamento
    if dados.nivel_atividade_fisica < 30.0 and dados.tarefas_concluidas_jira == 0:
        alerta_desengajamento = True
        score -= 40

    # Regra 2: Alta atividade contínua sem pausas suficientes = Risco de Burnout / NR 17
    if dados.horas_trabalhadas >= 7.0 and dados.minutos_pausa < 30:
        score -= 30  # Penaliza sobrecarga para incentivar descanso

    # Regra 3: Produtividade equilibrada (Altas entregas + pausas adequadas) = SPS Máximo
    if dados.tarefas_concluidas_jira >= 3 and dados.minutos_pausa >= 45:
        score = min(100, score + 10)

    # Limita o score entre 0 e 100
    score = max(0, min(100, score))

    # Classificação visual
    if score >= 80:
        classificacao = "SPS Máximo (Produtividade Saudável)"
    elif score >= 50:
        classificacao = "SPS Moderado (Atenção às Pausas)"
    else:
        classificacao = "SPS Crítico (Risco de Sobrecarga ou Desengajamento)"

    return score, classificacao, alerta_desengajamento


# -------------------------------------------------------------------
# INTEGRAÇÃO COM GOOGLE AI STUDIO (GEMINI)
# -------------------------------------------------------------------

def gerar_recomendacao_gemini(dados: DadosEntradaColaborador, sps_score: int, classificacao: str, desengajado: bool) -> str:
    """
    Chama a API do Google Gemini para gerar um parecer consultivo humanizado.
    """
    # System Prompt com as diretrizes éticas e de negócio do InsideWork
    system_instruction = """
    Você é a Inteligência Consultiva do InsideWork, um assistente focado em produtividade sustentável, ergonomia (NR 17/NR 1) e saúde mental.
    
    Diretrizes Fundamentais:
    1. Seja estritamente empático, humano, direto e consultivo.
    2. NUNCA adote um tom punitivo, de vigilância ou de acusação.
    3. Trate dados de teclado e mouse apenas como metadados físicos de esforço, respeitando a LGPD.
    4. Sugira ações práticas para o gestor cuidar do bem-estar da equipe sem invadir a privacidade.
    """

    prompt_contexto = f"""
    Analise os seguintes dados do colaborador e responda à dúvida do gestor:

    - Nome do Colaborador: {dados.nome_colaborador}
    - Horas Logadas: {dados.horas_trabalhadas}h
    - Pausas Realizadas: {dados.minutos_pausa} min ({dados.qtd_pausas} intervalo(s))
    - Nível de Atividade Física (Mouse/Teclado): {dados.nivel_atividade_fisica}%
    - Entregas no Jira/Trello: {dados.tarefas_concluidas_jira} tarefa(s) concluída(s)
    - Score SPS Calculado: {sps_score}/100 ({classificacao})
    - Alerta de Desengajamento Ativo? {'Sim' if desengajado else 'Não'}

    Pergunta do Gestor: "{dados.pergunta_gestor}"

    Elabore uma recomendação prática, simples e humana em até 3 parágrafos.
    """

    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_contexto,
            config={
                'system_instruction': system_instruction,
                'temperature': 0.6
            }
        )
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar a IA do Google Gemini: {str(e)}")


# -------------------------------------------------------------------
# ENDPOINTS DA API
# -------------------------------------------------------------------

@app.get("/")
def home():
    return {
        "sistema": "InsideWork API",
        "status": "Online",
        "versao": "BMC_IW_2026.1",
        "mensagem": "API de Produtividade Sustentável pronta para processamento."
    }

@app.post("/api/sps/analisar", response_model=RespostaSPS)
def analisar_produtividade(dados: DadosEntradaColaborador):
    """
    Endpoint principal: Recebe métricas do agente/Jira, calcula o SPS e gera recomendação via IA.
    """
    # 1. Calcula as regras de negócio
    sps_score, classificacao, desengajado = calcular_sps_base(dados)
    
    # 2. Chama o Google AI Studio (Gemini) para a recomendação
    recomendacao = gerar_recomendacao_gemini(dados, sps_score, classificacao, desengajado)

    return RespostaSPS(
        colaborador=dados.nome_colaborador,
        sps_score=sps_score,
        classificacao=classificacao,
        alerta_desengajamento=desengajado,
        recomendacao_ia=recomendacao
    )