"""Extração de características e regras explicáveis para fotografias diurnas."""

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass(frozen=True)
class Thresholds:
    """Valores congelados em 2026-11-10; registro em calibration.json.

    HSV usa a escala OpenCV: H=0..179, S e V=0..255.
    As proporções usam a escala 0..1.
    """

    blue_h_min: int = 90
    blue_h_max: int = 130
    blue_s_min: int = 100
    blue_v_min: int = 50
    bright_s_max: int = 50
    bright_v_min: int = 180
    clear_blue_min: float = 0.70
    overcast_blue_max: float = 0.20
    overcast_bright_min: float = 0.35


THRESHOLDS = Thresholds()
CALIBRATION_STATUS = "congelado_2026-11-10_calibracao_v3"


@dataclass
class Features:
    crop: np.ndarray
    blue_mask: np.ndarray
    bright_mask: np.ndarray
    blue_ratio: float
    bright_ratio: float


@dataclass(frozen=True)
class Decision:
    label: str
    condition: str


def load_image(path: str | Path) -> np.ndarray:
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"Arquivo de imagem não encontrado: {path}")
    try:
        data = np.frombuffer(path.read_bytes(), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR) if data.size else None
    except (OSError, cv2.error) as exc:
        raise ValueError(f"Não foi possível ler a imagem: {path}") from exc
    if image is None:
        raise ValueError(f"Arquivo inválido ou formato de imagem não suportado: {path}")
    return image


def extract_features(image: np.ndarray, thresholds: Thresholds = THRESHOLDS) -> Features:
    if image.ndim != 3 or image.shape[2] != 3 or image.size == 0 or image.dtype != np.uint8:
        raise ValueError("A imagem deve ser uma matriz BGR uint8 não vazia com três canais.")
    crop = image[:max(1, image.shape[0] // 3)].copy()
    hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
    blue_mask = cv2.inRange(
        hsv,
        (thresholds.blue_h_min, thresholds.blue_s_min, thresholds.blue_v_min),
        (thresholds.blue_h_max, 255, 255),
    )
    bright_mask = cv2.inRange(
        hsv, (0, 0, thresholds.bright_v_min), (179, thresholds.bright_s_max, 255)
    )
    return Features(
        crop, blue_mask, bright_mask,
        float(np.count_nonzero(blue_mask) / blue_mask.size),
        float(np.count_nonzero(bright_mask) / bright_mask.size),
    )


def classify(features: Features, rule: str = "combined", thresholds: Thresholds = THRESHOLDS) -> Decision:
    blue, bright = features.blue_ratio, features.bright_ratio
    clear = blue >= thresholds.clear_blue_min
    low_blue = blue <= thresholds.overcast_blue_max
    cloudy = bright >= thresholds.overcast_bright_min
    if rule == "blue":
        if clear:
            return Decision("ceu_limpo", f"azul >= {thresholds.clear_blue_min:.0%}")
        if low_blue:
            return Decision("ceu_encoberto", f"azul <= {thresholds.overcast_blue_max:.0%}")
        return Decision("indeterminado", "proporção de azul entre os limiares de decisão")
    if rule != "combined":
        raise ValueError(f"Regra desconhecida: {rule}")
    if clear and not cloudy:
        return Decision("ceu_limpo", f"azul >= {thresholds.clear_blue_min:.0%} e claros < {thresholds.overcast_bright_min:.0%}")
    if low_blue and cloudy and not clear:
        return Decision("ceu_encoberto", f"azul <= {thresholds.overcast_blue_max:.0%} e claros >= {thresholds.overcast_bright_min:.0%}")
    return Decision("indeterminado", "sinais insuficientes ou conflitantes para as condições de céu limpo e encoberto")


def save_diagnostics(features: Features, directory: str | Path) -> None:
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for name, image in (("recorte.png", features.crop), ("mascara_azul.png", features.blue_mask), ("mascara_claros.png", features.bright_mask)):
        try:
            success, encoded = cv2.imencode(".png", image)
            if not success:
                raise ValueError(f"Não foi possível gerar {name}")
            (directory / name).write_bytes(encoded.tobytes())
        except cv2.error as exc:
            raise ValueError(f"Não foi possível salvar {name}") from exc
