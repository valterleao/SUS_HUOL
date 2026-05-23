"""
Gera dados de amostra alinhados ao schema do trabalho (HUOL / jan-dez 2024-2025).
Substitua por CSV real em data/raw/sus/ após download no dados.gov.br.
"""
from datetime import date
from pathlib import Path
import random

import pandas as pd

from config import DATA_SAMPLE_DIR, HUOL_CNES, HUOL_NOME

random.seed(42)

ESPECIALIDADES = [
    "CLINICA MEDICA",
    "Clinica Medica",
    "CIRURGIA GERAL",
    "PEDIATRIA",
    "OBSTETRICIA",
    "ORTOPEDIA",
    "CARDIOLOGIA",
    "NEUROLOGIA",
    "UTI",
    "INFECTOLOGIA",
]

MUNICIPIOS = [
    ("2408102", "Natal"),
    ("2403251", "Parnamirim"),
    ("2408003", "Mossoro"),
    ("2401008", "Caico"),
    ("2400208", "Acari"),
    ("2402303", "Currais Novos"),
]

COMENTARIOS = [
    ("cmt_001", "post_101", "maria_silva", "2025-03-12", 12, "Excelente atendimento no HUOL, equipe muito atenciosa! #saude"),
    ("cmt_002", "post_101", "joao_rn", "2025-03-12", 3, "Demora na emergencia foi grande, mas o medico foi competente."),
    ("cmt_003", "post_102", "ana_costa", "2025-04-01", 8, "Hospital referencia em Natal, parabens aos profissionais."),
    ("cmt_004", "post_102", "pedro_123", "2025-04-02", 1, "Pessima experiencia, falta de leitos e atendimento lento."),
    ("cmt_005", "post_103", "lucia_m", "2025-04-15", 15, "Meu filho foi bem cuidado na pediatria, muito obrigada HUOL!"),
    ("cmt_006", "post_103", "carlos_ufrn", "2025-04-16", 5, "Estrutura antiga mas medicos excelentes."),
    ("cmt_007", "post_104", "renata_rn", "2025-05-02", 0, "Aguardando resultado de exame ha duas semanas."),
    ("cmt_008", "post_104", "felipe_h", "2025-05-03", 7, "Atendimento humanizado na maternidade, recomendo."),
    ("cmt_009", "post_105", "sandra_p", "2025-05-10", 2, "Nao gostei da limpeza do quarto."),
    ("cmt_010", "post_105", "miguel_t", "2025-05-11", 20, "O HUOL salvou minha mae, gratidao eterna!"),
    ("cmt_011", "post_106", "julia_f", "2025-06-01", 4, "Consulta marcada com atraso de 3 horas."),
    ("cmt_012", "post_106", "rafael_n", "2025-06-02", 9, "Bom hospital publico, SUS precisa de mais investimento."),
    ("cmt_013", "post_107", "patricia_l", "2025-06-15", 6, "Equipe da UTI muito preparada."),
    ("cmt_014", "post_107", "bruno_s", "2025-06-16", 1, "Horrivel, nunca mais volto."),
    ("cmt_015", "post_108", "camila_r", "2025-07-01", 11, "Educação em saude de qualidade na UFRN."),
    ("cmt_016", "post_108", "diego_m", "2025-07-02", 3, "Normal, nem bom nem ruim."),
    ("cmt_017", "post_109", "eliane_p", "2025-08-10", 14, "Residencia medica muito boa, aprendizado excelente."),
    ("cmt_018", "post_109", "gustavo_h", "2025-08-11", 2, "Fila enorme no pronto socorro."),
    ("cmt_019", "post_110", "helena_c", "2025-09-01", 18, "Melhor hospital universitario do RN!"),
    ("cmt_020", "post_110", "ivan_j", "2025-09-02", 0, "Sem comentarios adicionais."),
    ("cmt_021", "post_111", "katia_m", "2025-10-05", 7, "Cirurgia bem sucedida, equipe cirurgica impecavel."),
    ("cmt_022", "post_111", "leo_a", "2025-10-06", 1, "Desorganizacao no agendamento."),
    ("cmt_023", "post_112", "monica_s", "2025-11-01", 10, "Atendimento SUS eficiente neste hospital."),
    ("cmt_024", "post_112", "nelson_b", "2025-11-02", 4, "Precisa reformar instalacoes."),
    ("cmt_025", "post_113", "olivia_t", "2025-12-01", 16, "Profissionais dedicados mesmo com alta demanda."),
]


def gerar_internacoes(n_registros: int = 8000) -> pd.DataFrame:
    rows = []
    start = date(2024, 1, 1)
    end = date(2025, 12, 31)
    delta = (end - start).days

    for _ in range(n_registros):
        d = start.toordinal() + random.randint(0, delta)
        dt = date.fromordinal(d)
        cod_mun, mun = random.choice(MUNICIPIOS)
        esp = random.choice(ESPECIALIDADES)
        idade = random.randint(0, 90)
        sexo = random.choice(["M", "F", "M", "F", "NI"])
        qtd = random.choices([1, 1, 1, 2, 3], weights=[70, 15, 10, 4, 1], k=1)[0]
        rows.append(
            {
                "data_internacao": dt.isoformat(),
                "especialidade_hospitalar": esp,
                "numero_internacoes": qtd,
                "municipio_residencia": mun,
                "codigo_municipio_ibge": cod_mun,
                "idade": idade if random.random() > 0.02 else None,
                "sexo_paciente": sexo,
                "cnes_estabelecimento": HUOL_CNES,
                "nome_estabelecimento": HUOL_NOME,
                "uf_estabelecimento": "RN",
            }
        )
    return pd.DataFrame(rows)


def gerar_instagram() -> pd.DataFrame:
    return pd.DataFrame(
        COMENTARIOS,
        columns=["comment_id", "post_id", "autor", "data_comentario", "curtidas", "texto_comentario"],
    )


def main() -> None:
    out = DATA_SAMPLE_DIR
    out.mkdir(parents=True, exist_ok=True)
    sus_path = out / "internacoes_huol_2024_2025.csv"
    ig_path = out / "instagram_comentarios_huol.csv"
    gerar_internacoes().to_csv(sus_path, index=False, encoding="utf-8-sig", sep=";")
    gerar_instagram().to_csv(ig_path, index=False, encoding="utf-8-sig", sep=";")
    print(f"SUS: {sus_path} ({sus_path.stat().st_size} bytes)")
    print(f"Instagram: {ig_path} ({ig_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
