"""Avaliação em lote do Sky Pixel no conjunto de teste e nos casos difíceis."""

import argparse
import csv
import json
import re
from dataclasses import asdict
from pathlib import Path

from classifier import CALIBRATION_STATUS, THRESHOLDS, classify, extract_features, load_image, save_diagnostics

RULES = ("blue", "combined")
CLASSES = ("ceu_encoberto", "ceu_limpo")
OUTPUTS = (*CLASSES, "indeterminado")


def natural_key(path: Path) -> list:
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", path.name)]


def run_photo(path: Path, expected: str | None, diagnostics: Path | None) -> dict:
    features = extract_features(load_image(path))
    if diagnostics is not None:
        save_diagnostics(features, diagnostics / path.stem)
    row = {
        "image": path.as_posix(),
        "expected": expected,
        "blue_percent": features.blue_ratio * 100,
        "bright_percent": features.bright_ratio * 100,
    }
    for rule in RULES:
        decision = classify(features, rule)
        row[rule] = decision.label
        row[f"{rule}_condition"] = decision.condition
    return row


def summarize(rows: list[dict], rule: str) -> dict:
    matrix = {exp: {out: 0 for out in OUTPUTS} for exp in CLASSES}
    for row in rows:
        matrix[row["expected"]][row[rule]] += 1
    total = len(rows)
    correct = sum(matrix[c][c] for c in CLASSES)
    abstentions = sum(matrix[c]["indeterminado"] for c in CLASSES)
    decided = total - abstentions
    return {
        "matrix": matrix,
        "total": total,
        "correct": correct,
        "wrong": decided - correct,
        "abstentions": abstentions,
        "accuracy": correct / total if total else 0.0,
        "coverage": decided / total if total else 0.0,
        "accuracy_when_decided": correct / decided if decided else None,
    }


def pct(value: float) -> str:
    return f"{value:.2f}%".replace(".", ",")


def ratio(value: float | None) -> str:
    return "—" if value is None else pct(value * 100)


def markdown_report(test_rows: list[dict], hard_rows: list[dict], summaries: dict) -> str:
    lines = [f"Limiares: `{CALIBRATION_STATUS}`", "", "### Resultados por foto do teste", ""]
    lines += ["| Foto | Esperado | Azul | Claros | Referência | Combinada |", "| --- | --- | ---: | ---: | --- | --- |"]
    for r in test_rows:
        lines.append(f"| `{Path(r['image']).name}` | {r['expected']} | {pct(r['blue_percent'])} | {pct(r['bright_percent'])} | {r['blue']} | {r['combined']} |")
    for rule, title in (("blue", "Referência (só azul)"), ("combined", "Combinada")):
        s = summaries[rule]
        lines += ["", f"### Matriz de confusão — {title}", "", "| Esperado \\ Saída | " + " | ".join(OUTPUTS) + " |", "| --- |" + " ---: |" * len(OUTPUTS)]
        for exp in CLASSES:
            lines.append(f"| {exp} | " + " | ".join(str(s["matrix"][exp][out]) for out in OUTPUTS) + " |")
        lines += [
            "",
            f"Acurácia geral: {s['correct']}/{s['total']} ({ratio(s['accuracy'])}) · erros: {s['wrong']} · "
            f"abstenções: {s['abstentions']} · cobertura: {ratio(s['coverage'])} · "
            f"acurácia quando decide: {ratio(s['accuracy_when_decided'])}",
        ]
    lines += ["", "### Casos difíceis (análise qualitativa, sem rótulo esperado)", ""]
    lines += ["| Foto | Azul | Claros | Referência | Combinada |", "| --- | ---: | ---: | --- | --- |"]
    for r in hard_rows:
        lines.append(f"| `{Path(r['image']).name}` | {pct(r['blue_percent'])} | {pct(r['bright_percent'])} | {r['blue']} | {r['combined']} |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Avalia as duas regras no conjunto de teste e nos casos difíceis.")
    parser.add_argument("--refs", default="refs", help="Pasta com teste/ e caso_dificil/ (padrão: refs)")
    parser.add_argument("--csv", metavar="ARQUIVO", help="Salva os resultados por foto em CSV")
    parser.add_argument("--json", metavar="ARQUIVO", help="Salva resultados e resumo em JSON")
    parser.add_argument("--diagnostics", metavar="DIRETORIO", help="Salva recorte e máscaras de cada foto em subpastas")
    args = parser.parse_args()

    refs = Path(args.refs)
    test_dir, hard_dir = refs / "teste", refs / "caso_dificil"
    diag = Path(args.diagnostics) if args.diagnostics else None
    try:
        test_rows = [
            run_photo(photo, label, diag / "teste" / label if diag else None)
            for label in CLASSES
            for photo in sorted((test_dir / label).glob("*.jpg"), key=natural_key)
        ]
        hard_rows = [
            run_photo(photo, None, diag / "caso_dificil" if diag else None)
            for photo in sorted(hard_dir.glob("*.jpg"), key=natural_key)
        ]
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Erro: {exc}\n")
    if not test_rows:
        parser.exit(2, f"Erro: nenhuma foto encontrada em {test_dir}/<classe>/\n")

    summaries = {rule: summarize(test_rows, rule) for rule in RULES}
    print(markdown_report(test_rows, hard_rows, summaries))

    if args.csv:
        fields = ["set", *test_rows[0].keys()]
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fields)
            writer.writeheader()
            writer.writerows({"set": "teste", **r} for r in test_rows)
            writer.writerows({"set": "caso_dificil", **r} for r in hard_rows)
    if args.json:
        payload = {
            "calibration_status": CALIBRATION_STATUS,
            "thresholds": asdict(THRESHOLDS),
            "summary": summaries,
            "test": test_rows,
            "hard_cases": hard_rows,
        }
        Path(args.json).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
