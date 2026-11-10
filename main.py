import argparse
from pathlib import Path

import cv2
import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(description="Abre uma imagem no Sky Pixel.")
    parser.add_argument("imagem", type=Path, help="Caminho da fotografia")
    args = parser.parse_args()

    try:
        contents = args.imagem.read_bytes()
    except FileNotFoundError:
        parser.error(f"Arquivo inexistente: {args.imagem}")
    except OSError:
        parser.error(f"Não foi possível ler o arquivo: {args.imagem}")

    try:
        image = cv2.imdecode(np.frombuffer(contents, dtype=np.uint8), cv2.IMREAD_COLOR)
    except cv2.error:
        image = None

    if image is None:
        parser.error(f"Imagem inválida ou formato não suportado: {args.imagem}")

    height, width = image.shape[:2]
    print(f"Imagem aberta: {args.imagem} ({width} x {height} px)")


if __name__ == "__main__":
    main()
