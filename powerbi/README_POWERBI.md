# Power BI — Dashboard AV2 SUS HUOL

## Arquivo do relatório

| Arquivo | Descrição |
|---------|-----------|
| [AV2-SUS-TRB2.pbix](AV2-SUS-TRB2.pbix) | Dashboard Power BI (abrir no Power BI Desktop) |
| [../AV2-SUS-TRB2.pdf](../AV2-SUS-TRB2.pdf) | Exportação PDF com capturas das páginas |
| [../docs/images/dashboard/](../docs/images/dashboard/) | PNGs das 3 páginas (exibidas no README) |

**Páginas do dashboard:**

1. **Demanda SUS** — municípios, sazonalidade, perfil etário/gênero, top especialidades  
2. **Percepção social** — sentimento Instagram e nuvem de palavras  
3. **Internações por cidade e especialidades** — tabelas detalhadas  

## Conexão PostgreSQL

| Campo    | Valor        |
|----------|--------------|
| Servidor | localhost    |
| Porta    | 5432         |
| Banco    | **SUS_HUOL** |
| Usuário  | postgres     |
| Senha    | 123456       |

Modo: **Import** (recomendado para volumes deste trabalho).

## Tabelas e views a importar

Schema `olap`:

- `fato_internacao`
- `dim_tempo`, `dim_especialidade`, `dim_paciente`, `dim_municipio`
- `fato_sentimento_comentario`
- Views: `vw_top_especialidades`, `vw_perfil_paciente`, `vw_internacoes_municipio`, `vw_sazonalidade_mensal`, `vw_comentarios_amostra`, `vw_sentimento_distribuicao`, `vw_termos_frequentes`, `vw_resumo_decisao`

## Relacionamentos (modelo estrela)

```
dim_tempo[id_tempo] ----< fato_internacao[id_tempo]
dim_especialidade ----< fato_internacao[id_especialidade]
dim_paciente --------< fato_internacao[id_paciente]
dim_municipio -------< fato_internacao[id_municipio]
```

Comentários Instagram: tabela `fato_sentimento_comentario` isolada (sem FK para fato de internações).

## Página 1 — Demanda SUS

| Visual | Campo / View |
|--------|----------------|
| Barras horizontais | `vw_top_especialidades` — eixo: especialidade, valor: total_internacoes |
| Barras empilhadas | `vw_perfil_paciente` — faixa_etaria, sexo, total_internacoes |
| Tabela / mapa | `vw_internacoes_municipio` — municipio, capital_interior, total_internacoes |
| Linha | `vw_sazonalidade_mensal` — eixo: ano_mes, valor: total_internacoes |
| Cartões | `vw_resumo_decisao` — total_internacoes_huol, especialidade_lider, municipio_lider |

## Página 2 — Percepção social

| Visual | Campo |
|--------|--------|
| Donut / pizza | `vw_sentimento_distribuicao` — sentimento, qtd_comentarios |
| Barras | `vw_termos_frequentes` — termo por sentimento (filtro slicer) |
| Tabela | `vw_comentarios_amostra` — texto_resumo, sentimento, curtidas |

## Filtros sugeridos

- Ano (`dim_tempo[ano]`)
- Capital/Interior (`dim_municipio[capital_interior]`)
- Sentimento (página 2)

## Validação das 6 perguntas

1. Top especialidades → `vw_top_especialidades`
2. Perfil etário/gênero → `vw_perfil_paciente`
3. Municípios → `vw_internacoes_municipio`
4. Sazonalidade → `vw_sazonalidade_mensal`
5. O que dizem → `vw_comentarios_amostra` + `vw_termos_frequentes`
6. Sentimento → `vw_sentimento_distribuicao`
