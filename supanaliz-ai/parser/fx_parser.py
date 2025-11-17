# parser/fx_parser.py

import pandas as pd
from pathlib import Path
from typing import Dict


def load_fx_rates(path: str) -> pd.Series:
    import pandas as pd
    from pathlib import Path

    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Kur dosyası bulunamadı: {file_path}")

    df = pd.read_excel(file_path)

    if "Tarih" not in df.columns or "Efektif Satış Kuru" not in df.columns:
        raise KeyError("Kur dosyasında 'Tarih' veya 'Efektif Satış Kuru' kolonu yok.")

    # Tarih
    df["Tarih"] = pd.to_datetime(df["Tarih"], dayfirst=True, errors="coerce")

    # Numerik
    fx_raw = (
        df["Efektif Satış Kuru"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )
    df["Efektif Satış Kuru"] = pd.to_numeric(fx_raw, errors="coerce")

    # 🔥 1) Duplicate tarihleri çözüyoruz — aynı gün varsa ortalamasını al!
    df = df.groupby("Tarih", as_index=True)["Efektif Satış Kuru"].mean().to_frame()

    # Artık duplicate tarihler YOK
    fx_series = df["Efektif Satış Kuru"].sort_index()

    # 🔥 2) Asfreq + ffill + bfill
    fx_daily = fx_series.asfreq("D").ffill().bfill()

    return fx_daily



def build_fx_lookup(path: str) -> Dict[pd.Timestamp, float]:
    """
    Tarih→kur mapping'i döner (günlük, ffill+bfill yapılmış).
    """
    fx_daily = load_fx_rates(path)
    return fx_daily.to_dict()
