# Trabalho AV2 — Sistemas de Apoio à Decisão  
## Data Lake e Data Warehouse: Hospital privado rumo ao credenciamento SUS

> **Visualização no GitHub:** o conteúdo completo e atualizado está em [README.md](../README.md) na raiz do repositório.

**Disciplina:** Sistemas de Apoio à Decisão  
**Curso:** Sistemas de Informação  
**Referência analítica:** Hospital Universitário Onofre Lopes (HUOL/UFRN), Natal/RN  
**Banco de dados:** PostgreSQL local, base **`SUS_HUOL`** (usuário `postgres`, senha `123456`)  
**Repositório:** https://github.com/valterleao/SUS_HUOL

---

Este documento reproduz o relatório do trabalho. Para instruções de clone, pipeline e estrutura de pastas, consulte o [README.md](../README.md).

---

## 1. Introdução e contexto

Um hospital privado de Natal (RN) avalia credenciar-se ao SUS. A análise usa o **HUOL/UFRN** como referência de demanda (internações) e a percepção pública no **Instagram @huol_ufrn**.

Solução: Data Lake (bronze/prata/ouro) + DW PostgreSQL **`SUS_HUOL`** + Power BI.

---

## 2. Perguntas de negócio

| # | Pergunta | Resposta (dados reais) |
|---|----------|------------------------|
| 1 | Especialidades | Cardiologia (1.253), Urologia (1.185), Cirurgia Geral (932) |
| 2 | Perfil | Predomínio faixa **60+** (~37%) |
| 3 | Municípios | **Natal** ~35%; interior e RM |
| 4 | Sazonalidade | ~526–770/mês, estável |
| 5 | O que dizem | Atendimento, equipe, estrutura, SUS |
| 6 | Sentimento | Positivo 44%, neutro 32%, negativo 24% |

---

## 3. Fontes de dados

- **SUS:** 8 CSV em `data/raw/sus/` (dados.gov.br), 15.884 linhas brutas, **13.964** em 2024–2025.
- **Instagram:** amostra de 25 comentários (Caminho B documentado).

---

## 4. a 9. Arquitetura, Lake, DW, análises e recomendação

Ver seções detalhadas, tabelas e diagramas em **[README.md](../README.md)** (seções 4 a 9).

**Recomendação SAD:** credenciamento viável e condicionado; piloto em especialidades selecionadas com monitoramento no `SUS_HUOL`.

---

## 10. Conclusão

Pipeline integrado com dados reais do gov.br, respondendo às seis perguntas e apoiando decisão de credenciamento SUS.

---

## 11. Referências

- https://dados.gov.br/dados/conjuntos-dados/06-internacoes-hospitalares  
- https://www.instagram.com/huol_ufrn/  
- https://developers.facebook.com/docs/instagram-api/  

---

## Anexo — Execução

```powershell
cd SUS_HUOL
pip install -r requirements.txt
copy .env.example .env
python scripts\run_pipeline.py
```

Coloque CSV em `data/raw/sus/` antes de executar.
