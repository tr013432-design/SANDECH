from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "sandech_crm.db"

PIPELINE_STAGES = [
    "Lead identificado",
    "Qualificação inicial",
    "Entendimento do escopo",
    "Go / No-Go interno",
    "Em elaboração de proposta",
    "Proposta enviada",
    "Em negociação",
    "Aguardando decisão do cliente",
    "Ganha",
    "Perdida",
    "Stand-by",
]

OPEN_STAGES = [
    "Lead identificado",
    "Qualificação inicial",
    "Entendimento do escopo",
    "Go / No-Go interno",
    "Em elaboração de proposta",
    "Proposta enviada",
    "Em negociação",
    "Aguardando decisão do cliente",
    "Stand-by",
]

STAGE_PROBABILITIES = {
    "Lead identificado": 10,
    "Qualificação inicial": 20,
    "Entendimento do escopo": 35,
    "Go / No-Go interno": 45,
    "Em elaboração de proposta": 60,
    "Proposta enviada": 75,
    "Em negociação": 85,
    "Aguardando decisão do cliente": 90,
    "Ganha": 100,
    "Perdida": 0,
    "Stand-by": 15,
}

SEGMENTS = [
    "Óleo & Gás / Offshore / Onshore",
    "Petroquímico / Químico",
    "Energia",
    "Data Centers",
    "Infraestrutura / Logística / Portuário",
    "Farmacêutico",
    "Alimentício",
    "Agroindustrial",
    "Mineração",
    "Outros Industriais",
]

DISCIPLINES = [
    "Processos",
    "Tubulação",
    "Mecânica",
    "Elétrica",
    "Instrumentação",
    "Automação",
    "Civil",
    "Metálica",
    "Segurança",
    "HVAC",
    "Telecomunicações / CFTV",
    "Arquitetura / Geral",
]

SERVICE_TYPES = [
    "Projeto conceitual",
    "Projeto básico",
    "Projeto detalhado",
    "As Built",
    "Levantamento de campo",
    "Memorial / critério / relatório técnico",
    "Especificação técnica / requisição de material",
    "PATEC / parecer técnico",
    "EVTE",
    "Apoio técnico / body shop",
    "Revisão documental",
]

PROJECT_PHASES = ["Conceitual", "Básico", "Detalhado", "As Built", "Estudo / EVTE", "Suporte técnico"]
OPPORTUNITY_NATURES = ["Novo", "Aditivo", "Revisão", "Contrato contínuo", "Alocação"]
LOCATIONS = ["Onshore", "Offshore"]
LEAD_SOURCES = ["Relacionamento comercial", "Indicação", "Cliente recorrente", "Inbound", "Evento", "Site", "LinkedIn", "Parceiro", "Prospecção ativa"]
LOSS_REASONS = [
    "Preço acima do concorrente",
    "Projeto postergado",
    "Cliente decidiu fazer internamente",
    "Escopo fora do perfil da SANDECH",
    "Condição contratual inviável",
    "Prazo inexequível",
    "Sem retorno do cliente",
    "Sem capacidade interna",
    "Falta de documentação para proposta",
    "Outro, com justificativa",
]
TEAM_MEMBERS = ["Comercial", "Engenharia", "Jurídico", "Diretoria", "Financeiro / Cadastro"]
ACTIVITY_TYPES = ["Ligação", "E-mail", "Reunião", "Visita técnica", "Follow-up", "Análise TR/RFQ", "Validação interna", "Revisão de proposta", "Jurídico / minuta", "Outro"]
LIBRARY_CATEGORIES = ["Premissas", "Fora de escopo", "Modelo de proposta", "Lista de documentos", "Caso semelhante", "Compliance"]

BG_COLOR = "#F4F7FA"
CARD_COLOR = "#FFFFFF"
PRIMARY_COLOR = "#0F4C81"
SECONDARY_COLOR = "#16324F"
TEXT_COLOR = "#142230"
