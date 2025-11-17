# parser/excel_loader.py

import pandas as pd
from pathlib import Path


def load_excel(path: str, sheet_name=None) -> pd.DataFrame:
    """
    Generic Excel loader.
    - Hem .xls hem .xlsx dosyalarını destekler
    - Tarih formatına burada dokunmuyoruz, sadece okuyoruz
    """
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Excel dosyası bulunamadı: {file_path}")

    suffix = file_path.suffix.lower()

    if suffix == ".xls":
        # Eski Excel formatı – xlrd gerekiyor
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine="xlrd")
    elif suffix in (".xlsx", ".xlsm"):
        df = pd.read_excel(file_path, sheet_name=sheet_name)
    else:
        raise ValueError(f"Desteklenmeyen dosya uzantısı: {suffix}")

    return df
