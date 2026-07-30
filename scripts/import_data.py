from __future__ import annotations

import os
from pathlib import Path

import mysql.connector
import pandas as pd
from dotenv import load_dotenv
from mysql.connector import Error


# =========================================================
# CONFIGURAÇÕES DO PROJETO
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "raw" / "space_missions.csv"
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH)


# =========================================================
# FUNÇÕES DE LIMPEZA
# =========================================================

def limpar_texto(valor: object) -> str | None:
    """Remove espaços extras e transforma valores vazios em None."""
    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if not texto:
        return None

    return texto


def limpar_preco(valor: object) -> float | None:
    """Converte o preço do CSV para número decimal."""
    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if not texto:
        return None

    texto = (
        texto
        .replace("$", "")
        .replace(",", "")
        .replace(" ", "")
    )

    try:
        return float(texto)
    except ValueError:
        return None


def limpar_data(valor: object):
    """Converte a data para o formato aceito pelo MariaDB."""
    if pd.isna(valor):
        return None

    data = pd.to_datetime(
        valor,
        errors="coerce"
    )

    if pd.isna(data):
        return None

    return data.date()


def limpar_hora(valor: object):
    """Converte o horário para o formato aceito pelo MariaDB."""
    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if not texto:
        return None

    hora = pd.to_datetime(
        texto,
        format="mixed",
        errors="coerce"
    )

    if pd.isna(hora):
        return None

    return hora.time()


# =========================================================
# CONEXÃO COM O BANCO
# =========================================================

def conectar_banco():
    """Cria e retorna uma conexão com o MariaDB."""
    variaveis_obrigatorias = [
        "DB_HOST",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    ]

    ausentes = [
        variavel
        for variavel in variaveis_obrigatorias
        if not os.getenv(variavel)
    ]

    if ausentes:
        raise ValueError(
            f"Variáveis ausentes no arquivo .env: {', '.join(ausentes)}"
        )

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


# =========================================================
# EXTRAÇÃO E VALIDAÇÃO
# =========================================================

def carregar_csv() -> pd.DataFrame:
    """Lê e valida o arquivo CSV."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {CSV_PATH}"
        )

    df = pd.read_csv(
        CSV_PATH,
        encoding="latin-1"
    )

    colunas_obrigatorias = {
        "Company",
        "Location",
        "Date",
        "Time",
        "Rocket",
        "Mission",
        "RocketStatus",
        "Price",
        "MissionStatus",
    }

    colunas_ausentes = colunas_obrigatorias.difference(df.columns)

    if colunas_ausentes:
        raise ValueError(
            f"Colunas ausentes no CSV: {sorted(colunas_ausentes)}"
        )

    print("✅ CSV carregado com sucesso!")
    print(f"Linhas encontradas: {len(df)}")
    print(f"Colunas encontradas: {len(df.columns)}")

    return df


# =========================================================
# TRANSFORMAÇÃO
# =========================================================

def transformar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """Limpa e converte os dados antes da carga."""
    df = df.copy()

    colunas_texto = [
        "Company",
        "Location",
        "Rocket",
        "Mission",
        "RocketStatus",
        "MissionStatus",
    ]

    for coluna in colunas_texto:
        df[coluna] = df[coluna].apply(limpar_texto)

    df["Date"] = df["Date"].apply(limpar_data)
    df["Time"] = df["Time"].apply(limpar_hora)
    df["Price"] = df["Price"].apply(limpar_preco)

    antes = len(df)

    # Uma missão precisa ter ao menos um nome para ser carregada.
    df = df.dropna(subset=["Mission"])

    removidas = antes - len(df)

    print("\n✅ Transformação concluída!")

    if removidas:
        print(f"Linhas removidas por falta do nome da missão: {removidas}")

    return df


# =========================================================
# CARGA DAS DIMENSÕES
# =========================================================

def limpar_tabelas(cursor) -> None:
    """Limpa as tabelas para permitir nova execução do ETL."""
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    cursor.execute("TRUNCATE TABLE missions")
    cursor.execute("TRUNCATE TABLE rockets")
    cursor.execute("TRUNCATE TABLE locations")
    cursor.execute("TRUNCATE TABLE companies")

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")


def carregar_empresas(cursor, df: pd.DataFrame) -> dict[str, int]:
    """Insere empresas únicas e retorna um mapa nome → ID."""
    empresas = sorted(
        df["Company"]
        .dropna()
        .unique()
        .tolist()
    )

    cursor.executemany(
        """
        INSERT INTO companies (company_name)
        VALUES (%s)
        """,
        [(empresa,) for empresa in empresas],
    )

    cursor.execute(
        """
        SELECT id_company, company_name
        FROM companies
        """
    )

    mapa = {
        nome: id_company
        for id_company, nome in cursor.fetchall()
    }

    return mapa


def carregar_locais(cursor, df: pd.DataFrame) -> dict[str, int]:
    """Insere locais únicos e retorna um mapa nome → ID."""
    locais = sorted(
        df["Location"]
        .dropna()
        .unique()
        .tolist()
    )

    cursor.executemany(
        """
        INSERT INTO locations (location_name)
        VALUES (%s)
        """,
        [(local,) for local in locais],
    )

    cursor.execute(
        """
        SELECT id_location, location_name
        FROM locations
        """
    )

    mapa = {
        nome: id_location
        for id_location, nome in cursor.fetchall()
    }

    return mapa


def carregar_foguetes(
    cursor,
    df: pd.DataFrame
) -> dict[tuple[str, str | None], int]:
    """Insere foguetes únicos e retorna um mapa (nome, status) → ID."""
    foguetes_df = (
        df[["Rocket", "RocketStatus"]]
        .dropna(subset=["Rocket"])
        .drop_duplicates()
        .sort_values(by=["Rocket", "RocketStatus"], na_position="last")
    )

    registros = [
        (linha.Rocket, linha.RocketStatus)
        for linha in foguetes_df.itertuples(index=False)
    ]

    cursor.executemany(
        """
        INSERT INTO rockets (
            rocket_name,
            rocket_status
        )
        VALUES (%s, %s)
        """,
        registros,
    )

    cursor.execute(
        """
        SELECT
            id_rocket,
            rocket_name,
            rocket_status
        FROM rockets
        """
    )

    mapa = {
        (nome, status): id_rocket
        for id_rocket, nome, status in cursor.fetchall()
    }

    return mapa


# =========================================================
# CARGA DAS MISSÕES
# =========================================================

def carregar_missoes(
    cursor,
    df: pd.DataFrame,
    empresas_ids: dict[str, int],
    locais_ids: dict[str, int],
    foguetes_ids: dict[tuple[str, str | None], int],
) -> int:
    """Insere todas as missões utilizando as chaves estrangeiras."""
    registros = []

    for linha in df.itertuples(index=False):
        id_company = empresas_ids.get(linha.Company)
        id_location = locais_ids.get(linha.Location)

        chave_foguete = (
            linha.Rocket,
            linha.RocketStatus,
        )

        id_rocket = foguetes_ids.get(chave_foguete)

        registros.append(
            (
                linha.Mission,
                linha.Date,
                linha.Time,
                linha.MissionStatus,
                linha.Price,
                id_company,
                id_rocket,
                id_location,
            )
        )

    cursor.executemany(
        """
        INSERT INTO missions (
            mission_name,
            mission_date,
            mission_time,
            mission_status,
            price,
            id_company,
            id_rocket,
            id_location
        )
        VALUES (
            %s, %s, %s, %s,
            %s, %s, %s, %s
        )
        """,
        registros,
    )

    return len(registros)


# =========================================================
# EXECUÇÃO PRINCIPAL
# =========================================================

def main() -> None:
    conexao = None
    cursor = None

    try:
        print("========== INÍCIO DO ETL ==========\n")

        # EXTRACT
        df = carregar_csv()

        # TRANSFORM
        df = transformar_dados(df)

        # LOAD
        conexao = conectar_banco()
        cursor = conexao.cursor()

        print("✅ Conexão com o MariaDB realizada!")

        limpar_tabelas(cursor)

        empresas_ids = carregar_empresas(cursor, df)
        locais_ids = carregar_locais(cursor, df)
        foguetes_ids = carregar_foguetes(cursor, df)

        total_missoes = carregar_missoes(
            cursor=cursor,
            df=df,
            empresas_ids=empresas_ids,
            locais_ids=locais_ids,
            foguetes_ids=foguetes_ids,
        )

        conexao.commit()

        print("\n========== ETL CONCLUÍDO ==========")
        print(f"Empresas inseridas: {len(empresas_ids)}")
        print(f"Locais inseridos: {len(locais_ids)}")
        print(f"Foguetes inseridos: {len(foguetes_ids)}")
        print(f"Missões inseridas: {total_missoes}")
        print("✅ Dados carregados no MariaDB com sucesso!")

    except (
        Error,
        ValueError,
        FileNotFoundError,
    ) as erro:
        if conexao and conexao.is_connected():
            conexao.rollback()

        print(f"\n❌ Erro durante o ETL: {erro}")

    except Exception as erro:
        if conexao and conexao.is_connected():
            conexao.rollback()

        print(f"\n❌ Erro inesperado: {erro}")

    finally:
        if cursor:
            cursor.close()

        if conexao and conexao.is_connected():
            conexao.close()
            print("\n🔒 Conexão com o banco encerrada.")


if __name__ == "__main__":
    main()