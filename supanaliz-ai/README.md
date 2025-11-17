# supanaliz-ai

Project scaffold for `supanaliz-ai`.

Structure

```
supanaliz-ai/
│
├── parser/
│   ├── __init__.py
│   ├── excel_loader.py
│   ├── sales_parser.py
│   └── purchase_parser.py
│
├── features/
│   ├── __init__.py
│   ├── sales_features.py
│   └── purchase_features.py
│
├── agents/
│   ├── __init__.py
│   ├── sales_agent.py
│   ├── purchase_agent.py
│   └── decision_agent.py
│
├── api/
│   └── main.py
│
├── requirements.txt
└── README.md
```

Quick start

1. Create a virtual environment (PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the API (from project root):

```powershell
uvicorn api.main:app --reload --port 8000
```

Notes

- The parsers and agents are placeholders — extend parsing, validation, and decision logic to match your real data schemas.
- The `api/main.py` saves uploaded files into the current directory temporarily. Consider saving to a secure temp folder and cleaning up after processing.
# SUPANALİZ AI – Offline Decision Lab

Satış ve satınalma Excel verilerini okuyup:

- Feature seti çıkaran,
- Satış ve satınalma için ayrı ajanlar çalıştıran,
- Malzeme eşleştirme motoru ile DecisionAgent üreten,
- FastAPI backend üzerinden JSON I/O ile çalışan

tamamen offline bir Python projesi.

---

## 1. Kurulum

```bash
git clone <bu repo>
cd supanaliz-ai

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
