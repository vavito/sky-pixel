"""Interface de linha de comando do Sky Pixel."""

import argparse
from dataclasses import asdict
import json

from classifier import CALIBRATION_STATUS, OPEN_SKY, OPEN_SKY_STATUS, THRESHOLDS, classify, extract_features, load_image, save_diagnostics


def main() -> None:
    parser = argparse.ArgumentParser(description="Classifica a aparência do céu no terço superior de uma foto diurna.")
    parser.add_argument("image", help="Caminho da fotografia")
    parser.add_argument("--rule", choices=("blue", "combined", "open", "both", "all"), default="open", help="Regra de decisão (padrão: open; both = blue+combined; all = as três)")
    parser.add_argument("--diagnostics", metavar="DIRETORIO", help="Salva recorte e máscaras PNG; arquivos existentes com os mesmos nomes serão substituídos")
    parser.add_argument("--json", action="store_true", help="Exibe o resultado em JSON")
    args = parser.parse_args()
    try:
        features = extract_features(load_image(args.image))
        rules = {"both": ("blue", "combined"), "all": ("blue", "combined", "open")}.get(args.rule, (args.rule,))
        decisions = {rule: asdict(classify(features, rule)) for rule in rules}
        if args.diagnostics:
            save_diagnostics(features, args.diagnostics)
    except (ValueError, OSError) as exc:
        parser.exit(2, f"Erro: {exc}\n")
    result = {
        "image": args.image,
        "blue_percent": features.blue_ratio * 100,
        "bright_percent": features.bright_ratio * 100,
        "open_sky_percent": features.open_ratio * 100,
        "calibration_status": CALIBRATION_STATUS,
        "thresholds": asdict(THRESHOLDS),
        "open_sky_status": OPEN_SKY_STATUS,
        "open_sky_thresholds": asdict(OPEN_SKY),
        "decisions": decisions,
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Azul: {result['blue_percent']:.2f}% | Claros de baixa saturação: {result['bright_percent']:.2f}% | Céu aberto: {result['open_sky_percent']:.2f}%")
        print(f"Limiares: {CALIBRATION_STATUS} | {OPEN_SKY_STATUS}")
        for rule, decision in decisions.items():
            print(f"{rule}: {decision['label']} — {decision['condition']}")
        if args.diagnostics:
            print(f"Diagnósticos salvos em: {args.diagnostics}")


if __name__ == "__main__":
    main()
