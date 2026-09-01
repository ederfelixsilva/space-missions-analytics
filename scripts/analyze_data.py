"""Gera tabelas analíticas, indicadores e gráficos a partir do CSV original."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw" / "space_missions.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
IMAGE_DIR = BASE_DIR / "images" / "dashboard"

COLORS = {
    "navy": "#172554",
    "blue": "#2563EB",
    "cyan": "#06B6D4",
    "orange": "#F97316",
    "red": "#DC2626",
    "gray": "#64748B",
}


def load_and_clean() -> pd.DataFrame:
    """Carrega uma cópia do CSV e padroniza tipos sem alterar o arquivo bruto."""
    df = pd.read_csv(RAW_PATH, encoding="latin-1")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Price"] = pd.to_numeric(
        df["Price"].astype("string").str.replace(",", "", regex=False),
        errors="coerce",
    )
    df["Year"] = df["Date"].dt.year.astype("Int64")
    return df


def build_tables(df: pd.DataFrame) -> dict[str, object]:
    """Calcula KPIs e salva tabelas usadas nas visualizações."""
    status = df["MissionStatus"].value_counts().rename_axis("status").reset_index(name="missions")
    status["percentage"] = (100 * status["missions"] / len(df)).round(2)

    annual = (
        df.groupby("Year", dropna=True)
        .agg(
            missions=("Mission", "size"),
            successes=("MissionStatus", lambda s: (s == "Success").sum()),
        )
        .reset_index()
    )
    annual["success_rate_pct"] = (100 * annual["successes"] / annual["missions"]).round(2)

    companies = (
        df.groupby("Company")
        .agg(
            missions=("Mission", "size"),
            successes=("MissionStatus", lambda s: (s == "Success").sum()),
        )
        .reset_index()
    )
    companies["success_rate_pct"] = (100 * companies["successes"] / companies["missions"]).round(2)
    companies = companies.sort_values(["missions", "success_rate_pct"], ascending=False)

    rockets = (
        df.groupby(["Rocket", "RocketStatus"])
        .agg(
            missions=("Mission", "size"),
            successes=("MissionStatus", lambda s: (s == "Success").sum()),
        )
        .reset_index()
    )
    rockets["success_rate_pct"] = (100 * rockets["successes"] / rockets["missions"]).round(2)
    rockets = rockets.sort_values(["missions", "success_rate_pct"], ascending=False)

    status.to_csv(PROCESSED_DIR / "missions_by_status.csv", index=False)
    annual.to_csv(PROCESSED_DIR / "missions_by_year.csv", index=False)
    companies.to_csv(PROCESSED_DIR / "companies_performance.csv", index=False)
    rockets.to_csv(PROCESSED_DIR / "rockets_performance.csv", index=False)

    metrics = {
        "records": int(len(df)),
        "period": [int(df["Year"].min()), int(df["Year"].max())],
        "companies": int(df["Company"].nunique()),
        "locations": int(df["Location"].nunique()),
        "rockets": int(df[["Rocket", "RocketStatus"]].drop_duplicates().shape[0]),
        "successes": int((df["MissionStatus"] == "Success").sum()),
        "success_rate_pct": round(100 * (df["MissionStatus"] == "Success").mean(), 2),
        "known_prices": int(df["Price"].notna().sum()),
        "price_coverage_pct": round(100 * df["Price"].notna().mean(), 2),
    }
    (PROCESSED_DIR / "summary.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return {"status": status, "annual": annual, "companies": companies, "metrics": metrics}


def plot_dashboard(tables: dict[str, object]) -> None:
    """Cria um painel estático com os quatro recortes principais."""
    status = tables["status"]
    annual = tables["annual"]
    companies = tables["companies"].head(10).sort_values("missions")
    metrics = tables["metrics"]

    sns.set_theme(style="whitegrid", font_scale=0.95)
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle("Space Missions Analytics | 1957–2022", fontsize=22, fontweight="bold", color=COLORS["navy"])

    axes[0, 0].plot(annual["Year"], annual["missions"], color=COLORS["blue"], linewidth=2.2)
    axes[0, 0].fill_between(annual["Year"], annual["missions"], alpha=0.15, color=COLORS["blue"])
    axes[0, 0].set_title("Evolução anual dos lançamentos", fontweight="bold")
    axes[0, 0].set_xlabel("Ano")
    axes[0, 0].set_ylabel("Missões")

    axes[0, 1].barh(companies["Company"], companies["missions"], color=COLORS["cyan"])
    axes[0, 1].set_title("Empresas com mais missões", fontweight="bold")
    axes[0, 1].set_xlabel("Missões")
    axes[0, 1].set_ylabel("")

    status_colors = [COLORS["blue"], COLORS["red"], COLORS["orange"], COLORS["gray"]]
    axes[1, 0].bar(status["status"], status["missions"], color=status_colors)
    axes[1, 0].set_title("Resultado das missões", fontweight="bold")
    axes[1, 0].set_xlabel("")
    axes[1, 0].set_ylabel("Missões")
    axes[1, 0].tick_params(axis="x", rotation=15)

    axes[1, 1].axis("off")
    summary = (
        f"{metrics['records']:,} missões\n"
        f"{metrics['success_rate_pct']:.2f}% de sucesso\n"
        f"{metrics['companies']} empresas\n"
        f"{metrics['locations']} locais\n"
        f"{metrics['price_coverage_pct']:.2f}% com preço informado"
    ).replace(",", ".")
    axes[1, 1].text(0.08, 0.55, summary, fontsize=21, linespacing=1.6, color=COLORS["navy"], va="center")
    axes[1, 1].set_title("Indicadores principais", fontweight="bold")

    fig.text(0.5, 0.01, "Fonte: Space Missions Dataset | Valores de preço na unidade original (milhões de USD)", ha="center", color=COLORS["gray"])
    plt.tight_layout(rect=[0, 0.04, 1, 0.95])
    fig.savefig(IMAGE_DIR / "space_missions_overview.png", dpi=180, bbox_inches="tight")
    fig.savefig(IMAGE_DIR / "space_missions_overview.svg", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    df = load_and_clean()
    tables = build_tables(df)
    plot_dashboard(tables)
    print("Análise concluída: tabelas e painel foram gerados com sucesso.")


if __name__ == "__main__":
    main()
