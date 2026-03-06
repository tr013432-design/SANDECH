# Arquitetura do SANDECH CRM

## Stack
- Front-end: Streamlit multipágina
- Persistência: SQLite
- Linguagem: Python
- Visual: cards, métricas e kanban inspirados em CRMs modernos, adaptados para engenharia consultiva

## Módulos
- Contas: cadastro de clientes, plantas e contas estratégicas
- Contatos: stakeholders e influência na compra
- Oportunidades: pipeline técnico-comercial com campos aderentes à SANDECH
- Propostas: revisões, valor, premissas, fora de escopo e entregáveis
- Atividades: follow-up e agenda operacional
- Biblioteca: base de premissas, exclusões e modelos
- Dashboard: pipeline, valor ponderado, aging, conversão e perdas

## Regras de negócio implementadas
- Probabilidade padrão por etapa do funil
- Histórico de mudança de etapa
- Criação automática de atividades em etapas críticas
- Motivo de perda automático quando marcado como perdida sem justificativa
- Proteção conceitual: sem posicionar a empresa como executora de obra, fornecimento ou montagem

## Próximas evoluções recomendadas
- Login por perfil
- Integração com e-mail e WhatsApp
- Exportação de proposta em PDF/Word
- Aprovação eletrônica de Go/No-Go
- Indicadores por vendedor, conta e segmento
- Integração com Power BI ou ERP
