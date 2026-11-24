"""Validação da regra "céu aberto" sem usar a foto avaliada na escolha dos parâmetros.

Os parâmetros da máscara (saturação mínima, brilho mínimo e textura máxima) e o
limiar de decisão são escolhidos por busca em grade: vence a combinação que
deixa a maior folga entre a foto limpa com menos céu aberto e a foto encoberta
com mais céu aberto. O limiar fica no meio dessa folga.

Dois protocolos:
1. Calibração -> teste: escolhe tudo só com refs/calibracao e mede em refs/teste.
2. Leave-one-out: para cada uma das 34 fotos rotuladas, escolhe tudo com as
   outras 33 e classifica a foto que ficou de fora.
"""

from dataclasses import replace
from itertools import product
from pathlib import Path

import numpy as np

from classifier import OPEN_SKY, load_image, open_sky_mask

CLASSES = ("ceu_encoberto", "ceu_limpo")
GRID = list(product((20, 30, 40, 50), (80, 100, 120, 140), (3.0, 4.0, 5.0, 6.0, 8.0)))


def measure(image: np.ndarray) -> dict:
    out = {}
    for s_min, v_min, texture_max in GRID:
        mask = open_sky_mask(image, replace(OPEN_SKY, s_min=s_min, v_min=v_min, texture_max=texture_max))
        out[(s_min, v_min, texture_max)] = np.count_nonzero(mask) / mask.size
    return out


def fit(rows: list[dict]) -> tuple[float, tuple, float]:
    best = None
    for key in GRID:
        most_open_overcast = max(r["m"][key] for r in rows if r["label"] == "ceu_encoberto")
        least_open_clear = min(r["m"][key] for r in rows if r["label"] == "ceu_limpo")
        candidate = (least_open_clear - most_open_overcast, key, (least_open_clear + most_open_overcast) / 2)
        if best is None or candidate[0] > best[0]:
            best = candidate
    return best


def predict(row: dict, key: tuple, threshold: float) -> str:
    return "ceu_limpo" if row["m"][key] >= threshold else "ceu_encoberto"


def main() -> None:
    rows = [
        {"split": split, "label": label, "name": photo.name, "m": measure(load_image(photo))}
        for split in ("calibracao", "teste")
        for label in CLASSES
        for photo in sorted(Path("refs", split, label).glob("*.jpg"))
    ]
    calibration = [r for r in rows if r["split"] == "calibracao"]
    test = [r for r in rows if r["split"] == "teste"]

    margin, key, threshold = fit(calibration)
    hits = [predict(r, key, threshold) == r["label"] for r in test]
    print("1) Calibração -> teste")
    print(f"   parâmetros escolhidos: S >= {key[0]}, V >= {key[1]}, textura < {key[2]}; limiar {threshold:.1%} (folga {margin:.1%})")
    print(f"   teste: {sum(hits)}/{len(test)} acertos")
    for r, ok in zip(test, hits):
        if not ok:
            print(f"   erro: {r['label']}/{r['name']} ({r['m'][key]:.1%} de céu aberto)")

    hits = []
    for i, row in enumerate(rows):
        _, key, threshold = fit(rows[:i] + rows[i + 1:])
        ok = predict(row, key, threshold) == row["label"]
        hits.append(ok)
        if not ok:
            print(f"   erro LOO: {row['split']}/{row['label']}/{row['name']}")
    print("2) Leave-one-out nas 34 fotos rotuladas")
    print(f"   {sum(hits)}/{len(rows)} acertos")


if __name__ == "__main__":
    main()
