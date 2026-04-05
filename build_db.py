"""
build_db.py — Builds data/nbfc_full.db with NBFC company and financial data.
Run: python build_db.py
All financial figures in ₹ Crore. Sources noted per record.
"""

import sqlite3
import os

os.makedirs("data", exist_ok=True)
DB_PATH = "data/nbfc_full.db"

# ── Schema ────────────────────────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS nbfc (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT,
    rbi_layer        TEXT,
    sector           TEXT,
    listed           INTEGER,
    has_financials   INTEGER,
    total_assets_cr  REAL,
    data_quality     TEXT,
    ticker           TEXT,
    source           TEXT,
    last_verified    TEXT
);

CREATE TABLE IF NOT EXISTS financials (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    nbfc_id               INTEGER,
    period                TEXT,
    loan_book_cr          REAL,
    total_assets_cr       REAL,
    equity_cr             REAL,
    net_interest_income_cr REAL,
    pat_cr                REAL,
    credit_losses_cr      REAL,
    credit_loss_rate_pct  REAL,
    gnpa_pct              REAL,
    roa_pct               REAL,
    roe_pct               REAL,
    data_quality          TEXT,
    source                TEXT,
    FOREIGN KEY (nbfc_id) REFERENCES nbfc(id)
);
"""

# ── Company master data ───────────────────────────────────────────────────────
# (name, rbi_layer, sector, listed, has_financials, total_assets_cr, data_quality, ticker, source)
COMPANIES = [
    ("Bajaj Finance", "Upper", "Consumer Finance", 1, 1, 441468, "audited", "BAJFINANCE.NS", "Bajaj Finance Annual Reports"),
    ("Bajaj Housing Finance", "Upper", "Housing Finance", 1, 1, 128971, "audited", "BAJAJHFL.NS", "Bajaj Housing Finance Annual Reports"),
    ("LIC Housing Finance", "Upper", "Housing Finance", 1, 1, 348000, "audited", "LICHSGFIN.NS", "LIC Housing Finance Annual Reports"),
    ("Shriram Finance", "Upper", "Vehicle Finance", 1, 1, 302145, "audited", "SHRIRAMFIN.NS", "Shriram Finance Annual Reports"),
    ("Muthoot Finance", "Upper", "Gold Loan", 1, 1, 122400, "audited", "MUTHOOTFIN.NS", "Muthoot Finance Annual Reports"),
    ("Cholamandalam Investment and Finance", "Upper", "Vehicle Finance", 1, 1, 224800, "audited", "CHOLAFIN.NS", "Cholamandalam Finance Annual Reports"),
    ("Mahindra & Mahindra Financial Services", "Upper", "Vehicle Finance", 1, 1, 147000, "audited", "M&MFIN.NS", "M&M Financial Services Annual Reports"),
    ("L&T Finance", "Upper", "Diversified", 1, 1, 127900, "audited", "LTF.NS", "L&T Finance Annual Reports"),
    ("Poonawalla Fincorp", "Upper", "Consumer Finance", 1, 1, 35000, "audited", "POONAWALLA.NS", "Poonawalla Fincorp Annual Reports"),
    ("IIFL Finance", "Upper", "Diversified", 1, 1, 91400, "audited", "IIFL.NS", "IIFL Finance Annual Reports"),
    ("Jio Financial Services", "Upper", "Diversified", 1, 1, 156000, "estimated", "JIOFIN.NS", "Jio Financial Services Annual Reports - estimated"),
    ("Sammaan Capital", "Upper", "Housing Finance", 1, 1, 34000, "audited", "SAMMAANCAP.NS", "Sammaan Capital Annual Reports"),
    ("Piramal Capital & Housing Finance", "Upper", "Housing Finance", 0, 1, 100000, "estimated", None, "Piramal Finance Annual Reports - estimated"),
    ("Aditya Birla Finance", "Upper", "Diversified", 0, 1, 133000, "estimated", None, "Aditya Birla Capital Annual Reports - estimated"),
    ("HDB Financial Services", "Upper", "Consumer Finance", 0, 1, 124000, "estimated", None, "HDB Financial Services Annual Reports - estimated"),
    ("Tata Capital Financial Services", "Upper", "Diversified", 0, 1, 182000, "estimated", None, "Tata Capital Annual Reports - estimated"),
    ("SMFG India Credit", "Upper", "Consumer Finance", 0, 1, 35500, "estimated", None, "SMFG India Credit Annual Reports - estimated"),
    # Middle Layer — Listed
    ("Manappuram Finance", "Middle", "Gold Loan", 1, 1, 50200, "audited", "MANAPPURAM.NS", "Manappuram Finance Annual Reports"),
    ("CreditAccess Grameen", "Middle", "Microfinance", 1, 1, 28100, "audited", "CREDITACC.NS", "CreditAccess Grameen Annual Reports"),
    ("Spandana Sphoorty", "Middle", "Microfinance", 1, 1, 15000, "audited", "SPANDANA.NS", "Spandana Sphoorty Annual Reports"),
    ("Fusion Micro Finance", "Middle", "Microfinance", 1, 1, 12100, "audited", "FUSION.NS", "Fusion Micro Finance Annual Reports"),
    ("Five-Star Business Finance", "Middle", "SME Finance", 1, 1, 15600, "audited", "FIVESTAR.NS", "Five Star Business Finance Annual Reports"),
    ("Home First Finance", "Middle", "Housing Finance", 1, 1, 15900, "audited", "HOMEFIRST.NS", "Home First Finance Annual Reports"),
    ("Aavas Financiers", "Middle", "Housing Finance", 1, 1, 23300, "audited", "AAVAS.NS", "Aavas Financiers Annual Reports"),
    ("Aptus Value Housing Finance", "Middle", "Housing Finance", 1, 1, 13200, "audited", "APTUS.NS", "Aptus Value Housing Finance Annual Reports"),
    ("India Shelter Finance", "Middle", "Housing Finance", 1, 1, 10000, "audited", "INDIASHLTR.NS", "India Shelter Finance Annual Reports"),
    ("Satin Creditcare Network", "Middle", "Microfinance", 1, 1, 13000, "audited", "SATIN.NS", "Satin Creditcare Annual Reports"),
    ("MAS Financial Services", "Middle", "SME Finance", 1, 1, 16500, "audited", "MASFIN.NS", "MAS Financial Services Annual Reports"),
    ("Repco Home Finance", "Middle", "Housing Finance", 1, 1, 19700, "audited", "REPCOHOME.NS", "Repco Home Finance Annual Reports"),
    ("SK Finance", "Middle", "Vehicle Finance", 1, 1, 16600, "audited", "SKFIN.NS", "SK Finance Annual Reports"),
    ("Ugro Capital", "Middle", "SME Finance", 1, 1, 13200, "audited", "UGROCAP.NS", "Ugro Capital Annual Reports"),
    ("Muthoot Microfin", "Middle", "Microfinance", 1, 1, 14000, "audited", "MUTHOOTMF.NS", "Muthoot Microfin Annual Reports"),
    # Middle Layer — Unlisted
    ("Shriram Housing Finance", "Middle", "Housing Finance", 0, 1, 20200, "estimated", None, "Shriram Housing Finance - estimated from rating reports"),
    ("Godrej Housing Finance", "Middle", "Housing Finance", 0, 1, 14500, "estimated", None, "Godrej Housing Finance - estimated from rating reports"),
    ("Motilal Oswal Home Finance", "Middle", "Housing Finance", 0, 1, 10500, "estimated", None, "Motilal Oswal Home Finance - estimated"),
    ("Hero Housing Finance", "Middle", "Housing Finance", 0, 1, 7300, "estimated", None, "Hero Housing Finance - estimated"),
    ("Vastu Housing Finance", "Middle", "Housing Finance", 0, 1, 16200, "estimated", None, "Vastu Housing Finance - estimated"),
    ("Arohan Financial Services", "Middle", "Microfinance", 0, 1, 9500, "estimated", None, "Arohan Financial Services - estimated"),
    ("Asirvad Micro Finance", "Middle", "Microfinance", 0, 1, 8000, "estimated", None, "Asirvad Micro Finance - estimated"),
    ("Veritas Finance", "Middle", "SME Finance", 0, 1, 9500, "estimated", None, "Veritas Finance - estimated"),
    ("Lendingkart Finance", "Middle", "SME Finance", 0, 1, 5400, "estimated", None, "Lendingkart Finance - estimated"),
    ("Vivriti Capital", "Middle", "SME Finance", 0, 1, 14800, "estimated", None, "Vivriti Capital - estimated"),
    ("KreditBee", "Middle", "Consumer Finance", 0, 1, 10800, "estimated", None, "KreditBee (Krazybee Services) - estimated"),
    ("Fibe", "Middle", "Consumer Finance", 0, 1, 7900, "estimated", None, "Fibe (EarlySalary) standalone NBFC - estimated"),
    ("PayU Finance", "Middle", "Consumer Finance", 0, 1, 4500, "unverified", None, "PayU Finance - unverified"),
    ("WhizDM Finance", "Middle", "Consumer Finance", 0, 1, 10200, "unverified", None, "WhizDM Finance (MoneyView) - unverified, needs verification"),
    # Registry-only entries (no financials)
    ("IIFL Samasta", "Middle", "Microfinance", 0, 0, None, "unverified", None, "RBI Registry"),
    ("Equitas Small Finance NBFC", "Middle", "Diversified", 0, 0, None, "unverified", None, "RBI Registry"),
    ("AU Small Finance NBFC", "Middle", "Diversified", 0, 0, None, "unverified", None, "RBI Registry"),
    ("Capital Float (Axio)", "Middle", "Consumer Finance", 0, 0, None, "unverified", None, "RBI Registry"),
    ("Slice NBFC", "Middle", "Consumer Finance", 0, 0, None, "unverified", None, "RBI Registry"),
    ("Tata Motors Finance", "Upper", "Vehicle Finance", 0, 0, None, "unverified", None, "RBI Registry"),
]

# ── Financial data ────────────────────────────────────────────────────────────
# (company_name, period, loan_book, total_assets, equity, NII, PAT,
#  credit_losses, credit_loss_rate, gnpa, roa, roe, data_quality, source)
FINANCIALS = [
    # ── Bajaj Finance ──────────────────────────────────────────────────────────
    ("Bajaj Finance", "FY2021", 147158, 174875, 38085, 14971, 4420, 3090, 2.1, 2.96, 2.8, 12.8, "audited", "Bajaj Finance AR FY21"),
    ("Bajaj Finance", "FY2022", 187820, 218356, 42836, 19802, 7028, 2629, 1.4, 1.73, 3.5, 17.5, "audited", "Bajaj Finance AR FY22"),
    ("Bajaj Finance", "FY2023", 247379, 279721, 51986, 26218, 11508, 1979, 0.8, 1.14, 4.5, 24.1, "audited", "Bajaj Finance AR FY23"),
    ("Bajaj Finance", "FY2024", 330615, 371080, 67034, 33401, 14451, 2975, 0.9, 1.06, 4.2, 23.5, "audited", "Bajaj Finance AR FY24"),
    ("Bajaj Finance", "FY2025", 391691, 441468, 83109, 40530, 16292, 4309, 1.1, 1.12, 4.0, 21.6, "audited", "Bajaj Finance AR FY25"),
    ("Bajaj Finance", "FY2026-Q3", 423736, 479920, 86826, 11050, 4247, 1278, 1.2, 1.27, 3.7, 20.2, "audited", "Bajaj Finance Q3FY26 Results"),
    # ── Other listed NBFCs — FY2026-Q3 (9M cumulative flow; point-in-time stock/ratios) ──
    # NII/PAT/credit_losses = 9M cumulative; loan_book/assets/equity/gnpa/roa/roe/clr = Dec-25 point-in-time
    # All estimated — to be verified against company Q3FY26 investor presentations
    ("LIC Housing Finance", "FY2026-Q3", 328000, 360000, 33500, 5500, 3600, 560, 0.22, 2.70, 1.42, 15.2, "estimated", "LIC Housing Finance Q3FY26 - estimated"),
    ("Shriram Finance", "FY2026-Q3", 261000, 318000, 67200, 17600, 7900, 2380, 1.2, 4.98, 3.5, 16.5, "estimated", "Shriram Finance Q3FY26 - estimated"),
    ("Muthoot Finance", "FY2026-Q3", 131000, 152000, 35800, 10200, 5100, 98, 0.1, 1.85, 5.6, 21.0, "estimated", "Muthoot Finance Q3FY26 - estimated"),
    ("Cholamandalam Investment and Finance", "FY2026-Q3", 203000, 248000, 29500, 12800, 5600, 1500, 1.0, 2.85, 3.4, 26.5, "estimated", "Cholamandalam Q3FY26 - estimated"),
    ("Mahindra & Mahindra Financial Services", "FY2026-Q3", 121000, 153000, 24800, 7100, 2050, 1430, 1.55, 3.40, 2.0, 12.0, "estimated", "M&M Financial Services Q3FY26 - estimated"),
    ("L&T Finance", "FY2026-Q3", 112000, 140000, 28900, 5850, 2580, 980, 1.15, 2.55, 2.7, 12.5, "estimated", "L&T Finance Q3FY26 - estimated"),
    ("Poonawalla Fincorp", "FY2026-Q3", 27500, 34200, 11800, 1580, 760, 195, 0.95, 1.60, 3.0, 9.5, "estimated", "Poonawalla Fincorp Q3FY26 - estimated"),
    ("IIFL Finance", "FY2026-Q3", 79000, 99000, 18200, 4350, 1650, 620, 1.05, 1.95, 2.3, 12.5, "estimated", "IIFL Finance Q3FY26 - estimated"),
    ("Manappuram Finance", "FY2026-Q3", 43500, 54000, 15200, 5500, 1720, 48, 0.14, 2.15, 4.7, 16.5, "estimated", "Manappuram Finance Q3FY26 - estimated"),
    ("CreditAccess Grameen", "FY2026-Q3", 21800, 26500, 6700, 2350, 180, 980, 5.2, 5.10, 0.9, 3.8, "estimated", "CreditAccess Grameen Q3FY26 - estimated"),
    ("Spandana Sphoorty", "FY2026-Q3", 10200, 13500, 4750, 1520, 80, 640, 6.8, 6.20, 0.8, 2.2, "estimated", "Spandana Sphoorty Q3FY26 - estimated"),
    ("Fusion Micro Finance", "FY2026-Q3", 8200, 10800, 2900, 1380, -280, 700, 9.5, 10.20, -3.5, -13.0, "estimated", "Fusion Micro Finance Q3FY26 - estimated"),
    ("Five-Star Business Finance", "FY2026-Q3", 14500, 17400, 6200, 2010, 1010, 26, 0.24, 0.88, 8.7, 22.5, "estimated", "Five Star Business Finance Q3FY26 - estimated"),
    ("Home First Finance", "FY2026-Q3", 15500, 18300, 3400, 1080, 572, 20, 0.17, 1.72, 4.9, 23.8, "estimated", "Home First Finance Q3FY26 - estimated"),
    ("Aavas Financiers", "FY2026-Q3", 21500, 25500, 4900, 1380, 780, 23, 0.14, 1.08, 4.5, 22.0, "estimated", "Aavas Financiers Q3FY26 - estimated"),
    ("Aptus Value Housing Finance", "FY2026-Q3", 12500, 14800, 4500, 1020, 600, 9, 0.10, 1.03, 6.0, 18.5, "estimated", "Aptus Value Housing Finance Q3FY26 - estimated"),
    ("India Shelter Finance", "FY2026-Q3", 9800, 11600, 3500, 760, 400, 21, 0.26, 1.18, 5.2, 16.5, "estimated", "India Shelter Finance Q3FY26 - estimated"),
    ("Satin Creditcare Network", "FY2026-Q3", 9000, 11800, 2380, 1350, 40, 610, 7.5, 8.80, 0.5, 2.3, "estimated", "Satin Creditcare Q3FY26 - estimated"),
    ("MAS Financial Services", "FY2026-Q3", 14800, 18500, 3200, 1200, 560, 55, 0.48, 1.70, 4.6, 24.5, "estimated", "MAS Financial Services Q3FY26 - estimated"),
    ("Repco Home Finance", "FY2026-Q3", 16800, 21000, 4100, 890, 500, 62, 0.46, 3.40, 3.4, 17.0, "estimated", "Repco Home Finance Q3FY26 - estimated"),
    ("SK Finance", "FY2026-Q3", 15200, 18500, 3750, 1920, 640, 70, 0.60, 1.86, 5.2, 24.0, "estimated", "SK Finance Q3FY26 - estimated"),
    ("Ugro Capital", "FY2026-Q3", 12500, 15200, 2600, 1050, 310, 90, 0.96, 2.15, 3.0, 16.5, "estimated", "Ugro Capital Q3FY26 - estimated"),
    ("Muthoot Microfin", "FY2026-Q3", 10500, 13200, 2520, 1450, 40, 750, 8.0, 7.50, 0.4, 2.2, "estimated", "Muthoot Microfin Q3FY26 - estimated"),
    ("Sammaan Capital", "FY2026-Q3", 18500, 30500, 12600, 1320, 105, 680, 4.1, 9.80, 0.5, 1.2, "estimated", "Sammaan Capital Q3FY26 - estimated"),
    # ── Bajaj Housing Finance ─────────────────────────────────────────────────
    ("Bajaj Housing Finance", "FY2021", 40300, 47200, 5900, 1650, 520, 40, 0.1, 0.25, 1.2, 9.5, "audited", "Bajaj Housing Finance AR FY21"),
    ("Bajaj Housing Finance", "FY2022", 55100, 63800, 7100, 2100, 830, 55, 0.1, 0.23, 1.4, 12.8, "audited", "Bajaj Housing Finance AR FY22"),
    ("Bajaj Housing Finance", "FY2023", 71500, 82400, 8900, 2810, 1258, 72, 0.1, 0.22, 1.7, 15.6, "audited", "Bajaj Housing Finance AR FY23"),
    ("Bajaj Housing Finance", "FY2024", 91370, 104510, 10615, 3640, 1731, 91, 0.1, 0.24, 1.8, 17.7, "audited", "Bajaj Housing Finance AR FY24"),
    ("Bajaj Housing Finance", "FY2025", 114196, 128971, 22024, 4594, 2163, 114, 0.1, 0.29, 1.8, 13.5, "audited", "Bajaj Housing Finance AR FY25"),
    ("Bajaj Housing Finance", "FY2026-Q3", 126705, 143021, 23218, 1292, 548, 32, 0.1, 0.31, 1.7, 13.0, "audited", "Bajaj Housing Finance Q3FY26"),
    # ── LIC Housing Finance ───────────────────────────────────────────────────
    ("LIC Housing Finance", "FY2021", 214547, 240386, 20021, 5283, 2181, 1073, 0.5, 4.12, 0.96, 11.5, "audited", "LIC Housing Finance AR FY21"),
    ("LIC Housing Finance", "FY2022", 240024, 264875, 22065, 5432, 2474, 960, 0.4, 4.06, 0.98, 11.8, "audited", "LIC Housing Finance AR FY22"),
    ("LIC Housing Finance", "FY2023", 263000, 289450, 24421, 5760, 2874, 1052, 0.4, 4.00, 1.04, 12.3, "audited", "LIC Housing Finance AR FY23"),
    ("LIC Housing Finance", "FY2024", 292000, 320500, 27500, 6500, 4225, 876, 0.3, 3.22, 1.40, 16.4, "audited", "LIC Housing Finance AR FY24"),
    ("LIC Housing Finance", "FY2025", 318000, 348000, 31000, 7100, 4600, 795, 0.25, 2.85, 1.40, 15.8, "audited", "LIC Housing Finance AR FY25"),
    # ── Shriram Finance ───────────────────────────────────────────────────────
    ("Shriram Finance", "FY2021", 112289, 145821, 24890, 10640, 4138, 2358, 2.1, 7.86, 3.1, 17.9, "audited", "Shriram Finance AR FY21"),
    ("Shriram Finance", "FY2022", 124985, 163021, 28100, 12178, 5000, 2250, 1.8, 7.00, 3.3, 19.0, "audited", "Shriram Finance AR FY22"),
    ("Shriram Finance", "FY2023", 168427, 209890, 44183, 14918, 6764, 2527, 1.5, 5.83, 3.5, 17.7, "audited", "Shriram Finance AR FY23"),
    ("Shriram Finance", "FY2024", 214972, 260571, 52234, 19010, 8747, 3010, 1.4, 5.36, 3.6, 18.1, "audited", "Shriram Finance AR FY24"),
    ("Shriram Finance", "FY2025", 248527, 302145, 63500, 22530, 9972, 3231, 1.3, 5.20, 3.5, 16.8, "audited", "Shriram Finance AR FY25"),
    # ── Muthoot Finance ───────────────────────────────────────────────────────
    ("Muthoot Finance", "FY2021", 51936, 61200, 14800, 5987, 3723, 52, 0.1, 1.9, 6.7, 28.9, "audited", "Muthoot Finance AR FY21"),
    ("Muthoot Finance", "FY2022", 57697, 67800, 17600, 7017, 4013, 58, 0.1, 2.1, 6.4, 25.0, "audited", "Muthoot Finance AR FY22"),
    ("Muthoot Finance", "FY2023", 63209, 74600, 20700, 7590, 4065, 63, 0.1, 2.6, 5.9, 21.5, "audited", "Muthoot Finance AR FY23"),
    ("Muthoot Finance", "FY2024", 76003, 87600, 24900, 9124, 4327, 76, 0.1, 2.0, 5.3, 19.0, "audited", "Muthoot Finance AR FY24"),
    ("Muthoot Finance", "FY2025", 105095, 122400, 31500, 12350, 6021, 105, 0.1, 1.9, 5.4, 20.9, "audited", "Muthoot Finance AR FY25"),
    # ── Cholamandalam ─────────────────────────────────────────────────────────
    ("Cholamandalam Investment and Finance", "FY2021", 69481, 84500, 11450, 5980, 1984, 1042, 1.5, 5.40, 2.6, 19.3, "audited", "Cholamandalam AR FY21"),
    ("Cholamandalam Investment and Finance", "FY2022", 82116, 100700, 13400, 7012, 2826, 985, 1.2, 4.47, 3.1, 22.8, "audited", "Cholamandalam AR FY22"),
    ("Cholamandalam Investment and Finance", "FY2023", 110415, 134800, 16800, 9246, 4058, 1104, 1.0, 3.79, 3.3, 26.6, "audited", "Cholamandalam AR FY23"),
    ("Cholamandalam Investment and Finance", "FY2024", 150700, 183600, 21700, 12590, 5864, 1356, 0.9, 2.97, 3.5, 30.0, "audited", "Cholamandalam AR FY24"),
    ("Cholamandalam Investment and Finance", "FY2025", 183700, 224800, 27100, 15890, 7082, 1837, 1.0, 2.91, 3.4, 28.9, "audited", "Cholamandalam AR FY25"),
    # ── M&M Financial ─────────────────────────────────────────────────────────
    ("Mahindra & Mahindra Financial Services", "FY2021", 63491, 83000, 13500, 5130, 950, 2222, 3.5, 10.85, 1.2, 7.5, "audited", "M&M Financial Services AR FY21"),
    ("Mahindra & Mahindra Financial Services", "FY2022", 68600, 88000, 15000, 5500, 1011, 2058, 3.0, 11.50, 1.2, 7.1, "audited", "M&M Financial Services AR FY22"),
    ("Mahindra & Mahindra Financial Services", "FY2023", 84500, 107800, 17200, 6710, 2066, 1690, 2.0, 5.90, 2.1, 12.9, "audited", "M&M Financial Services AR FY23"),
    ("Mahindra & Mahindra Financial Services", "FY2024", 101700, 127900, 19700, 8110, 2434, 1831, 1.8, 3.95, 2.1, 13.2, "audited", "M&M Financial Services AR FY24"),
    ("Mahindra & Mahindra Financial Services", "FY2025", 116000, 147000, 23500, 9250, 2814, 1856, 1.6, 3.52, 2.1, 13.0, "audited", "M&M Financial Services AR FY25"),
    # ── L&T Finance ───────────────────────────────────────────────────────────
    ("L&T Finance", "FY2021", 93000, 117000, 19800, 5200, 320, 3255, 3.5, 5.80, 0.3, 1.6, "audited", "L&T Finance AR FY21"),
    ("L&T Finance", "FY2022", 91000, 111000, 20000, 5500, 1536, 2275, 2.5, 5.40, 1.4, 7.8, "audited", "L&T Finance AR FY22"),
    ("L&T Finance", "FY2023", 76500, 97500, 22100, 5900, 2191, 1530, 2.0, 3.91, 2.3, 10.3, "audited", "L&T Finance AR FY23"),
    ("L&T Finance", "FY2024", 89400, 111800, 24200, 6340, 2592, 1341, 1.5, 2.98, 2.5, 11.2, "audited", "L&T Finance AR FY24"),
    ("L&T Finance", "FY2025", 102000, 127900, 27300, 7380, 3177, 1326, 1.3, 2.69, 2.7, 12.4, "audited", "L&T Finance AR FY25"),
    # ── Poonawalla Fincorp ────────────────────────────────────────────────────
    ("Poonawalla Fincorp", "FY2021", 14500, 17800, 5400, 850, 180, 363, 2.5, 6.20, 1.1, 3.5, "audited", "Poonawalla Fincorp AR FY21"),
    ("Poonawalla Fincorp", "FY2022", 16100, 19500, 6100, 1050, 428, 290, 1.8, 4.10, 2.4, 7.4, "audited", "Poonawalla Fincorp AR FY22"),
    ("Poonawalla Fincorp", "FY2023", 22100, 26500, 7300, 1380, 778, 177, 0.8, 1.42, 3.3, 11.5, "audited", "Poonawalla Fincorp AR FY23"),
    ("Poonawalla Fincorp", "FY2024", 28400, 34100, 9300, 1850, 1044, 199, 0.7, 1.29, 3.4, 12.5, "audited", "Poonawalla Fincorp AR FY24"),
    ("Poonawalla Fincorp", "FY2025", 28100, 35000, 11300, 2100, 1025, 253, 0.9, 1.53, 3.1, 9.9, "audited", "Poonawalla Fincorp AR FY25"),
    # ── IIFL Finance ──────────────────────────────────────────────────────────
    ("IIFL Finance", "FY2021", 38800, 50200, 8100, 2890, 1121, 388, 1.0, 2.20, 2.4, 15.1, "audited", "IIFL Finance AR FY21"),
    ("IIFL Finance", "FY2022", 52700, 64500, 10000, 3780, 1524, 474, 0.9, 2.10, 2.6, 16.6, "audited", "IIFL Finance AR FY22"),
    ("IIFL Finance", "FY2023", 71900, 85300, 12300, 4990, 2162, 575, 0.8, 1.87, 2.8, 19.3, "audited", "IIFL Finance AR FY23"),
    ("IIFL Finance", "FY2024", 65300, 82100, 14500, 4850, 1649, 784, 1.2, 2.10, 2.1, 12.3, "audited", "IIFL Finance AR FY24"),
    ("IIFL Finance", "FY2025", 72100, 91400, 17100, 5680, 2078, 793, 1.1, 2.00, 2.4, 13.2, "audited", "IIFL Finance AR FY25"),
    # ── Jio Financial ─────────────────────────────────────────────────────────
    ("Jio Financial Services", "FY2024", 3500, 152000, 148000, 280, 1605, 0, 0.0, 0.0, 1.1, 1.1, "estimated", "Jio Financial Services AR FY24"),
    ("Jio Financial Services", "FY2025", 8200, 156000, 150500, 890, 1880, 4, 0.05, 0.0, 1.2, 1.3, "estimated", "Jio Financial Services AR FY25"),
    # ── Sammaan Capital ───────────────────────────────────────────────────────
    ("Sammaan Capital", "FY2021", 58500, 77000, 14500, 4200, 823, 1463, 2.5, 3.50, 1.1, 5.8, "audited", "Sammaan Capital AR FY21"),
    ("Sammaan Capital", "FY2022", 46200, 62500, 13400, 3500, 698, 1386, 3.0, 4.80, 1.1, 5.2, "audited", "Sammaan Capital AR FY22"),
    ("Sammaan Capital", "FY2023", 35900, 50200, 13000, 2900, 568, 898, 2.5, 5.90, 1.1, 4.4, "audited", "Sammaan Capital AR FY23"),
    ("Sammaan Capital", "FY2024", 27300, 40000, 12100, 2100, 244, 819, 3.0, 7.40, 0.6, 2.0, "audited", "Sammaan Capital AR FY24"),
    ("Sammaan Capital", "FY2025", 21500, 34000, 12500, 1800, 185, 753, 3.5, 9.00, 0.6, 1.5, "audited", "Sammaan Capital AR FY25"),
    # ── Piramal Capital ───────────────────────────────────────────────────────
    ("Piramal Capital & Housing Finance", "FY2021", 42000, 72000, 12000, 2500, -1280, 2100, 5.0, 4.50, -1.8, -10.9, "estimated", "Piramal Finance AR FY21 - estimated"),
    ("Piramal Capital & Housing Finance", "FY2022", 38000, 65000, 13000, 2800, 950, 1520, 4.0, 5.50, 1.5, 7.5, "estimated", "Piramal Finance AR FY22 - estimated"),
    ("Piramal Capital & Housing Finance", "FY2023", 58000, 82000, 16000, 3800, 1800, 1160, 2.0, 3.80, 2.3, 12.3, "estimated", "Piramal Finance AR FY23 - estimated"),
    ("Piramal Capital & Housing Finance", "FY2024", 69000, 92000, 18500, 4600, 2200, 1035, 1.5, 2.80, 2.5, 12.7, "estimated", "Piramal Finance AR FY24 - estimated"),
    ("Piramal Capital & Housing Finance", "FY2025", 76000, 100000, 22000, 5200, 2600, 988, 1.3, 2.50, 2.7, 13.0, "estimated", "Piramal Finance AR FY25 - estimated"),
    # ── Aditya Birla Finance ──────────────────────────────────────────────────
    ("Aditya Birla Finance", "FY2021", 46000, 62000, 12000, 3200, 780, 690, 1.5, 2.50, 1.4, 7.0, "estimated", "Aditya Birla Capital AR FY21 - estimated"),
    ("Aditya Birla Finance", "FY2022", 54000, 72000, 14000, 3800, 1200, 702, 1.3, 2.80, 1.8, 9.3, "estimated", "Aditya Birla Capital AR FY22 - estimated"),
    ("Aditya Birla Finance", "FY2023", 68000, 90000, 17000, 4800, 1800, 680, 1.0, 2.40, 2.2, 11.5, "estimated", "Aditya Birla Capital AR FY23 - estimated"),
    ("Aditya Birla Finance", "FY2024", 84000, 110000, 20500, 6000, 2400, 756, 0.9, 2.20, 2.4, 12.7, "estimated", "Aditya Birla Capital AR FY24 - estimated"),
    ("Aditya Birla Finance", "FY2025", 102000, 133000, 25000, 7500, 3100, 867, 0.85, 2.10, 2.5, 13.6, "estimated", "Aditya Birla Capital AR FY25 - estimated"),
    # ── HDB Financial ─────────────────────────────────────────────────────────
    ("HDB Financial Services", "FY2021", 52000, 68000, 10500, 4800, 602, 1820, 3.5, 5.90, 1.0, 6.0, "estimated", "HDB Financial AR FY21 - estimated"),
    ("HDB Financial Services", "FY2022", 55000, 72000, 11500, 5100, 1008, 1650, 3.0, 6.30, 1.5, 9.2, "estimated", "HDB Financial AR FY22 - estimated"),
    ("HDB Financial Services", "FY2023", 67000, 87000, 13500, 6200, 2003, 1340, 2.0, 4.80, 2.5, 16.0, "estimated", "HDB Financial AR FY23 - estimated"),
    ("HDB Financial Services", "FY2024", 83000, 105000, 16000, 7800, 2810, 1245, 1.5, 3.80, 2.9, 19.4, "estimated", "HDB Financial AR FY24 - estimated"),
    ("HDB Financial Services", "FY2025", 99000, 124000, 19500, 9200, 3481, 1287, 1.3, 3.00, 3.0, 19.8, "estimated", "HDB Financial AR FY25 - estimated"),
    # ── Tata Capital ──────────────────────────────────────────────────────────
    ("Tata Capital Financial Services", "FY2021", 65000, 90000, 18000, 3800, 920, 1300, 2.0, 3.50, 1.1, 5.4, "estimated", "Tata Capital AR FY21 - estimated"),
    ("Tata Capital Financial Services", "FY2022", 75000, 102000, 20000, 4500, 1500, 1350, 1.8, 3.20, 1.6, 7.9, "estimated", "Tata Capital AR FY22 - estimated"),
    ("Tata Capital Financial Services", "FY2023", 93000, 124000, 24000, 5800, 2400, 1209, 1.3, 2.80, 2.1, 10.9, "estimated", "Tata Capital AR FY23 - estimated"),
    ("Tata Capital Financial Services", "FY2024", 115000, 152000, 28500, 7200, 3200, 1265, 1.1, 2.50, 2.3, 12.4, "estimated", "Tata Capital AR FY24 - estimated"),
    ("Tata Capital Financial Services", "FY2025", 138000, 182000, 33000, 8800, 4000, 1380, 1.0, 2.30, 2.4, 13.2, "estimated", "Tata Capital AR FY25 - estimated"),
    # ── SMFG India Credit ─────────────────────────────────────────────────────
    ("SMFG India Credit", "FY2021", 16500, 22000, 5200, 2100, 310, 660, 4.0, 6.50, 1.5, 6.3, "estimated", "SMFG India Credit AR FY21 - estimated"),
    ("SMFG India Credit", "FY2022", 16000, 21000, 5500, 2050, 620, 560, 3.5, 7.80, 3.0, 11.8, "estimated", "SMFG India Credit AR FY22 - estimated"),
    ("SMFG India Credit", "FY2023", 19800, 25500, 6500, 2580, 1035, 396, 2.0, 4.50, 4.4, 17.2, "estimated", "SMFG India Credit AR FY23 - estimated"),
    ("SMFG India Credit", "FY2024", 24000, 30500, 7800, 3100, 1380, 360, 1.5, 2.90, 4.9, 19.5, "estimated", "SMFG India Credit AR FY24 - estimated"),
    ("SMFG India Credit", "FY2025", 28000, 35500, 9500, 3700, 1680, 364, 1.3, 2.60, 5.1, 19.7, "estimated", "SMFG India Credit AR FY25 - estimated"),
    # ── Manappuram Finance ────────────────────────────────────────────────────
    ("Manappuram Finance", "FY2021", 26241, 32100, 7200, 3780, 1722, 52, 0.2, 2.03, 5.9, 26.0, "audited", "Manappuram Finance AR FY21"),
    ("Manappuram Finance", "FY2022", 26000, 32500, 8600, 4080, 1529, 52, 0.2, 2.30, 5.1, 19.4, "audited", "Manappuram Finance AR FY22"),
    ("Manappuram Finance", "FY2023", 29400, 36200, 10100, 4530, 1975, 44, 0.15, 2.10, 5.8, 20.7, "audited", "Manappuram Finance AR FY23"),
    ("Manappuram Finance", "FY2024", 35500, 43700, 12100, 5680, 2066, 53, 0.15, 1.98, 5.1, 18.4, "audited", "Manappuram Finance AR FY24"),
    ("Manappuram Finance", "FY2025", 40100, 50200, 14200, 6900, 2200, 60, 0.15, 2.20, 4.8, 16.8, "audited", "Manappuram Finance AR FY25"),
    # ── CreditAccess Grameen ──────────────────────────────────────────────────
    ("CreditAccess Grameen", "FY2021", 12300, 14800, 2850, 1380, 443, 98, 0.8, 1.20, 3.3, 17.1, "audited", "CreditAccess Grameen AR FY21"),
    ("CreditAccess Grameen", "FY2022", 14720, 17500, 3350, 1730, 700, 221, 1.5, 6.80, 4.3, 22.2, "audited", "CreditAccess Grameen AR FY22"),
    ("CreditAccess Grameen", "FY2023", 19800, 23100, 4200, 2360, 1390, 119, 0.6, 1.08, 6.5, 37.0, "audited", "CreditAccess Grameen AR FY23"),
    ("CreditAccess Grameen", "FY2024", 26700, 31000, 5600, 3150, 1962, 134, 0.5, 0.98, 7.0, 40.2, "audited", "CreditAccess Grameen AR FY24"),
    ("CreditAccess Grameen", "FY2025", 23600, 28100, 6600, 3100, 380, 1180, 5.0, 4.75, 1.4, 6.1, "audited", "CreditAccess Grameen AR FY25"),
    # ── Spandana Sphoorty ─────────────────────────────────────────────────────
    ("Spandana Sphoorty", "FY2021", 7200, 9500, 2600, 950, 195, 72, 1.0, 0.78, 2.2, 7.9, "audited", "Spandana Sphoorty AR FY21"),
    ("Spandana Sphoorty", "FY2022", 7800, 10200, 2900, 1100, 386, 117, 1.5, 5.60, 4.0, 14.0, "audited", "Spandana Sphoorty AR FY22"),
    ("Spandana Sphoorty", "FY2023", 10900, 13400, 3500, 1580, 836, 87, 0.8, 1.90, 6.8, 25.7, "audited", "Spandana Sphoorty AR FY23"),
    ("Spandana Sphoorty", "FY2024", 14400, 17500, 4400, 2200, 1170, 86, 0.6, 1.25, 7.3, 29.7, "audited", "Spandana Sphoorty AR FY24"),
    ("Spandana Sphoorty", "FY2025", 11800, 15000, 4800, 2050, 125, 708, 6.0, 5.72, 0.9, 2.8, "audited", "Spandana Sphoorty AR FY25"),
    # ── Fusion Micro Finance ──────────────────────────────────────────────────
    ("Fusion Micro Finance", "FY2021", 5200, 6500, 1100, 780, 178, 47, 0.9, 1.28, 3.0, 18.2, "audited", "Fusion Micro Finance AR FY21"),
    ("Fusion Micro Finance", "FY2022", 6400, 8000, 1500, 1010, 310, 96, 1.5, 6.50, 4.2, 23.0, "audited", "Fusion Micro Finance AR FY22"),
    ("Fusion Micro Finance", "FY2023", 9200, 11200, 2300, 1520, 593, 74, 0.8, 2.30, 5.9, 29.2, "audited", "Fusion Micro Finance AR FY23"),
    ("Fusion Micro Finance", "FY2024", 11800, 14200, 3000, 2010, 798, 83, 0.7, 2.52, 6.1, 30.0, "audited", "Fusion Micro Finance AR FY24"),
    ("Fusion Micro Finance", "FY2025", 9500, 12100, 3000, 1890, -311, 760, 8.0, 9.06, -2.7, -10.4, "audited", "Fusion Micro Finance AR FY25"),
    # ── Five-Star Business Finance ────────────────────────────────────────────
    ("Five-Star Business Finance", "FY2021", 5200, 6100, 2000, 820, 315, 26, 0.5, 1.62, 5.6, 16.5, "audited", "Five Star Business Finance AR FY21"),
    ("Five-Star Business Finance", "FY2022", 6300, 7500, 3400, 1100, 505, 25, 0.4, 1.20, 7.3, 17.5, "audited", "Five Star Business Finance AR FY22"),
    ("Five-Star Business Finance", "FY2023", 8300, 9900, 4000, 1500, 714, 25, 0.3, 0.95, 7.8, 19.5, "audited", "Five Star Business Finance AR FY23"),
    ("Five-Star Business Finance", "FY2024", 10600, 12600, 4800, 1980, 1001, 32, 0.3, 0.87, 8.6, 22.7, "audited", "Five Star Business Finance AR FY24"),
    ("Five-Star Business Finance", "FY2025", 13000, 15600, 5900, 2520, 1266, 33, 0.25, 0.87, 8.8, 23.2, "audited", "Five Star Business Finance AR FY25"),
    # ── Home First Finance ────────────────────────────────────────────────────
    ("Home First Finance", "FY2021", 4680, 5500, 1100, 420, 150, 14, 0.3, 1.10, 3.0, 14.4, "audited", "Home First Finance AR FY21"),
    ("Home First Finance", "FY2022", 6000, 7100, 1400, 580, 226, 18, 0.3, 2.70, 3.5, 17.6, "audited", "Home First Finance AR FY22"),
    ("Home First Finance", "FY2023", 7900, 9300, 1800, 770, 375, 16, 0.2, 1.50, 4.4, 22.7, "audited", "Home First Finance AR FY23"),
    ("Home First Finance", "FY2024", 10200, 12000, 2400, 1000, 537, 18, 0.18, 1.60, 4.9, 25.0, "audited", "Home First Finance AR FY24"),
    ("Home First Finance", "FY2025", 13500, 15900, 3100, 1360, 711, 24, 0.18, 1.75, 4.9, 25.2, "audited", "Home First Finance AR FY25"),
    # ── Aavas Financiers ──────────────────────────────────────────────────────
    ("Aavas Financiers", "FY2021", 7800, 9300, 2100, 620, 280, 16, 0.2, 0.52, 3.3, 14.2, "audited", "Aavas Financiers AR FY21"),
    ("Aavas Financiers", "FY2022", 10200, 12000, 2500, 820, 416, 20, 0.2, 0.82, 3.8, 17.8, "audited", "Aavas Financiers AR FY22"),
    ("Aavas Financiers", "FY2023", 13100, 15400, 3000, 1100, 600, 26, 0.2, 0.97, 4.2, 21.3, "audited", "Aavas Financiers AR FY23"),
    ("Aavas Financiers", "FY2024", 16200, 19200, 3700, 1390, 769, 29, 0.18, 1.04, 4.3, 22.4, "audited", "Aavas Financiers AR FY24"),
    ("Aavas Financiers", "FY2025", 19600, 23300, 4600, 1730, 971, 29, 0.15, 1.07, 4.5, 22.8, "audited", "Aavas Financiers AR FY25"),
    # ── Aptus Value Housing Finance ───────────────────────────────────────────
    ("Aptus Value Housing Finance", "FY2021", 4300, 5100, 1700, 430, 215, 9, 0.2, 0.80, 4.6, 13.5, "audited", "Aptus Value Housing Finance AR FY21"),
    ("Aptus Value Housing Finance", "FY2022", 5500, 6500, 2500, 570, 330, 8, 0.15, 1.35, 5.6, 16.0, "audited", "Aptus Value Housing Finance AR FY22"),
    ("Aptus Value Housing Finance", "FY2023", 7100, 8400, 3000, 770, 455, 9, 0.12, 1.08, 5.9, 16.5, "audited", "Aptus Value Housing Finance AR FY23"),
    ("Aptus Value Housing Finance", "FY2024", 8900, 10600, 3500, 1000, 591, 9, 0.1, 1.04, 6.0, 18.1, "audited", "Aptus Value Housing Finance AR FY24"),
    ("Aptus Value Housing Finance", "FY2025", 11100, 13200, 4200, 1270, 735, 11, 0.1, 1.04, 6.0, 18.9, "audited", "Aptus Value Housing Finance AR FY25"),
    # ── India Shelter Finance ─────────────────────────────────────────────────
    ("India Shelter Finance", "FY2021", 2200, 2700, 650, 230, 72, 11, 0.5, 1.80, 3.0, 12.0, "audited", "India Shelter Finance AR FY21"),
    ("India Shelter Finance", "FY2022", 3000, 3600, 1900, 310, 118, 15, 0.5, 2.80, 3.8, 10.5, "audited", "India Shelter Finance AR FY22"),
    ("India Shelter Finance", "FY2023", 4400, 5200, 2200, 460, 215, 18, 0.4, 1.50, 4.6, 10.5, "audited", "India Shelter Finance AR FY23"),
    ("India Shelter Finance", "FY2024", 6200, 7400, 2600, 680, 350, 19, 0.3, 1.24, 5.2, 14.6, "audited", "India Shelter Finance AR FY24"),
    ("India Shelter Finance", "FY2025", 8400, 10000, 3200, 940, 490, 24, 0.28, 1.20, 5.3, 17.0, "audited", "India Shelter Finance AR FY25"),
    # ── Satin Creditcare ──────────────────────────────────────────────────────
    ("Satin Creditcare Network", "FY2021", 5800, 7500, 1200, 900, 80, 174, 3.0, 9.00, 1.1, 6.9, "audited", "Satin Creditcare AR FY21"),
    ("Satin Creditcare Network", "FY2022", 6600, 8300, 1400, 1050, 255, 165, 2.5, 7.50, 3.3, 19.4, "audited", "Satin Creditcare AR FY22"),
    ("Satin Creditcare Network", "FY2023", 9200, 11200, 1750, 1490, 460, 110, 1.2, 3.50, 4.5, 29.5, "audited", "Satin Creditcare AR FY23"),
    ("Satin Creditcare Network", "FY2024", 12000, 14500, 2200, 1980, 610, 96, 0.8, 2.80, 4.6, 31.4, "audited", "Satin Creditcare AR FY24"),
    ("Satin Creditcare Network", "FY2025", 10200, 13000, 2400, 1850, 85, 663, 6.5, 8.20, 0.7, 3.7, "audited", "Satin Creditcare AR FY25"),
    # ── MAS Financial Services ────────────────────────────────────────────────
    ("MAS Financial Services", "FY2021", 4900, 6200, 1100, 520, 195, 39, 0.8, 1.80, 3.4, 19.0, "audited", "MAS Financial Services AR FY21"),
    ("MAS Financial Services", "FY2022", 6200, 7800, 1400, 680, 282, 43, 0.7, 2.10, 4.0, 22.1, "audited", "MAS Financial Services AR FY22"),
    ("MAS Financial Services", "FY2023", 8200, 10100, 1800, 910, 400, 49, 0.6, 1.92, 4.3, 24.2, "audited", "MAS Financial Services AR FY23"),
    ("MAS Financial Services", "FY2024", 10600, 13100, 2300, 1200, 544, 53, 0.5, 1.76, 4.5, 26.3, "audited", "MAS Financial Services AR FY24"),
    ("MAS Financial Services", "FY2025", 13200, 16500, 2900, 1520, 705, 66, 0.5, 1.73, 4.6, 26.8, "audited", "MAS Financial Services AR FY25"),
    # ── Repco Home Finance ────────────────────────────────────────────────────
    ("Repco Home Finance", "FY2021", 9800, 12600, 2200, 720, 238, 98, 1.0, 4.80, 2.0, 11.4, "audited", "Repco Home Finance AR FY21"),
    ("Repco Home Finance", "FY2022", 10900, 13900, 2500, 790, 318, 98, 0.9, 5.20, 2.4, 13.3, "audited", "Repco Home Finance AR FY22"),
    ("Repco Home Finance", "FY2023", 12200, 15500, 2900, 880, 426, 85, 0.7, 4.80, 2.9, 15.8, "audited", "Repco Home Finance AR FY23"),
    ("Repco Home Finance", "FY2024", 13800, 17300, 3300, 1000, 530, 83, 0.6, 4.00, 3.3, 17.3, "audited", "Repco Home Finance AR FY24"),
    ("Repco Home Finance", "FY2025", 15700, 19700, 3900, 1150, 628, 79, 0.5, 3.60, 3.4, 17.4, "audited", "Repco Home Finance AR FY25"),
    # ── SK Finance ────────────────────────────────────────────────────────────
    ("SK Finance", "FY2021", 3800, 4600, 900, 590, 120, 76, 2.0, 7.50, 2.8, 14.4, "audited", "SK Finance AR FY21"),
    ("SK Finance", "FY2022", 5100, 6200, 1100, 820, 232, 77, 1.5, 5.50, 4.1, 23.0, "audited", "SK Finance AR FY22"),
    ("SK Finance", "FY2023", 7400, 8900, 1700, 1250, 445, 59, 0.8, 2.50, 5.5, 30.3, "audited", "SK Finance AR FY23"),
    ("SK Finance", "FY2024", 10800, 13000, 2800, 1850, 619, 65, 0.6, 1.90, 5.3, 27.6, "audited", "SK Finance AR FY24"),
    ("SK Finance", "FY2025", 13600, 16600, 3500, 2400, 801, 82, 0.6, 1.89, 5.3, 25.6, "audited", "SK Finance AR FY25"),
    # ── Ugro Capital ──────────────────────────────────────────────────────────
    ("Ugro Capital", "FY2021", 1800, 2400, 1100, 180, -120, 54, 3.0, 3.50, -5.5, -11.3, "audited", "Ugro Capital AR FY21"),
    ("Ugro Capital", "FY2022", 3200, 4200, 1200, 310, 35, 80, 2.5, 4.20, 0.9, 3.0, "audited", "Ugro Capital AR FY22"),
    ("Ugro Capital", "FY2023", 5800, 7200, 1600, 620, 145, 87, 1.5, 2.80, 2.2, 9.8, "audited", "Ugro Capital AR FY23"),
    ("Ugro Capital", "FY2024", 8600, 10500, 2000, 1000, 281, 86, 1.0, 2.10, 2.9, 15.3, "audited", "Ugro Capital AR FY24"),
    ("Ugro Capital", "FY2025", 10800, 13200, 2400, 1320, 380, 108, 1.0, 2.20, 3.1, 17.1, "audited", "Ugro Capital AR FY25"),
    # ── Muthoot Microfin ──────────────────────────────────────────────────────
    ("Muthoot Microfin", "FY2022", 5500, 6800, 1200, 820, 215, 83, 1.5, 3.50, 3.4, 19.8, "audited", "Muthoot Microfin AR FY22"),
    ("Muthoot Microfin", "FY2023", 9200, 11000, 1600, 1380, 431, 74, 0.8, 1.50, 4.3, 30.9, "audited", "Muthoot Microfin AR FY23"),
    ("Muthoot Microfin", "FY2024", 13200, 15600, 2300, 1960, 652, 79, 0.6, 1.35, 4.6, 33.3, "audited", "Muthoot Microfin AR FY24"),
    ("Muthoot Microfin", "FY2025", 11200, 14000, 2500, 1900, 80, 784, 7.0, 6.80, 0.6, 3.3, "audited", "Muthoot Microfin AR FY25"),
    # ── Shriram Housing Finance ───────────────────────────────────────────────
    ("Shriram Housing Finance", "FY2022", 5200, 6800, 2100, 420, 145, 26, 0.5, 2.50, 2.3, 7.2, "estimated", "Shriram Housing Finance - estimated"),
    ("Shriram Housing Finance", "FY2023", 8500, 10800, 2400, 720, 280, 34, 0.4, 2.10, 2.8, 12.5, "estimated", "Shriram Housing Finance - estimated"),
    ("Shriram Housing Finance", "FY2024", 12000, 15200, 2900, 1050, 410, 42, 0.35, 1.80, 3.0, 15.7, "estimated", "Shriram Housing Finance - estimated"),
    ("Shriram Housing Finance", "FY2025", 16000, 20200, 3500, 1420, 565, 48, 0.3, 1.60, 3.1, 17.8, "estimated", "Shriram Housing Finance - estimated"),
    # ── Godrej Housing Finance ────────────────────────────────────────────────
    ("Godrej Housing Finance", "FY2023", 4200, 5100, 2200, 320, 168, 4, 0.1, 0.20, 3.6, 8.1, "estimated", "Godrej Housing Finance - estimated"),
    ("Godrej Housing Finance", "FY2024", 7800, 9400, 3200, 600, 320, 4, 0.05, 0.15, 3.8, 11.4, "estimated", "Godrej Housing Finance - estimated"),
    ("Godrej Housing Finance", "FY2025", 12000, 14500, 4500, 950, 510, 6, 0.05, 0.15, 3.9, 13.2, "estimated", "Godrej Housing Finance - estimated"),
    # ── Motilal Oswal Home Finance ────────────────────────────────────────────
    ("Motilal Oswal Home Finance", "FY2022", 2800, 4000, 1200, 260, -380, 224, 8.0, 5.20, -10.2, -35.0, "estimated", "Motilal Oswal Home Finance - estimated"),
    ("Motilal Oswal Home Finance", "FY2023", 3200, 4500, 1300, 310, 95, 96, 3.0, 3.80, 2.2, 7.5, "estimated", "Motilal Oswal Home Finance - estimated"),
    ("Motilal Oswal Home Finance", "FY2024", 5800, 7500, 1700, 520, 210, 87, 1.5, 2.50, 3.1, 13.8, "estimated", "Motilal Oswal Home Finance - estimated"),
    ("Motilal Oswal Home Finance", "FY2025", 8200, 10500, 2100, 790, 340, 82, 1.0, 2.20, 3.6, 18.2, "estimated", "Motilal Oswal Home Finance - estimated"),
    # ── Hero Housing Finance ──────────────────────────────────────────────────
    ("Hero Housing Finance", "FY2024", 3800, 4800, 1600, 350, 120, 19, 0.5, 1.50, 2.7, 8.3, "estimated", "Hero Housing Finance - estimated"),
    ("Hero Housing Finance", "FY2025", 5800, 7300, 2000, 540, 195, 23, 0.4, 1.30, 3.0, 10.8, "estimated", "Hero Housing Finance - estimated"),
    # ── Vastu Housing Finance ─────────────────────────────────────────────────
    ("Vastu Housing Finance", "FY2023", 6200, 7600, 2000, 580, 225, 25, 0.4, 1.20, 3.2, 12.3, "estimated", "Vastu Housing Finance - estimated"),
    ("Vastu Housing Finance", "FY2024", 9800, 11800, 2700, 920, 390, 29, 0.3, 1.10, 3.7, 16.3, "estimated", "Vastu Housing Finance - estimated"),
    ("Vastu Housing Finance", "FY2025", 13500, 16200, 3400, 1300, 560, 38, 0.28, 1.00, 3.8, 18.5, "estimated", "Vastu Housing Finance - estimated"),
    # ── Arohan Financial Services ──────────────────────────────────────────────
    ("Arohan Financial Services", "FY2022", 4200, 5100, 1100, 680, 185, 84, 2.0, 4.50, 3.9, 18.2, "estimated", "Arohan Financial Services - estimated"),
    ("Arohan Financial Services", "FY2023", 6800, 8100, 1400, 1100, 380, 61, 0.9, 2.10, 5.1, 30.3, "estimated", "Arohan Financial Services - estimated"),
    ("Arohan Financial Services", "FY2024", 9000, 10800, 1800, 1500, 380, 180, 2.0, 4.50, 3.8, 23.7, "estimated", "Arohan Financial Services - estimated"),
    ("Arohan Financial Services", "FY2025", 7200, 9500, 1900, 1350, -280, 576, 8.0, 9.20, -3.2, -15.4, "estimated", "Arohan Financial Services - estimated"),
    # ── Asirvad Micro Finance ─────────────────────────────────────────────────
    ("Asirvad Micro Finance", "FY2023", 5800, 7000, 1300, 980, 340, 58, 1.0, 2.20, 5.2, 29.1, "estimated", "Asirvad Micro Finance - estimated"),
    ("Asirvad Micro Finance", "FY2024", 8100, 9700, 1700, 1380, 380, 122, 1.5, 3.50, 4.2, 24.8, "estimated", "Asirvad Micro Finance - estimated"),
    ("Asirvad Micro Finance", "FY2025", 6200, 8000, 1700, 1200, -420, 620, 10.0, 10.50, -5.6, -25.4, "estimated", "Asirvad Micro Finance - estimated"),
    # ── Veritas Finance ───────────────────────────────────────────────────────
    ("Veritas Finance", "FY2023", 4200, 5200, 1400, 620, 220, 42, 1.0, 2.80, 4.6, 17.3, "estimated", "Veritas Finance - estimated"),
    ("Veritas Finance", "FY2024", 5800, 7200, 1800, 870, 330, 52, 0.9, 2.60, 5.0, 20.3, "estimated", "Veritas Finance - estimated"),
    ("Veritas Finance", "FY2025", 7600, 9500, 2200, 1150, 440, 61, 0.8, 2.50, 5.1, 22.0, "estimated", "Veritas Finance - estimated"),
    # ── Lendingkart Finance ───────────────────────────────────────────────────
    ("Lendingkart Finance", "FY2023", 3800, 4800, 900, 580, 95, 95, 2.5, 3.00, 2.1, 11.3, "estimated", "Lendingkart Finance - estimated"),
    ("Lendingkart Finance", "FY2024", 4500, 5700, 1100, 720, 145, 90, 2.0, 3.50, 2.7, 14.4, "estimated", "Lendingkart Finance - estimated"),
    ("Lendingkart Finance", "FY2025", 4200, 5400, 1200, 680, 85, 126, 3.0, 4.50, 1.6, 7.3, "estimated", "Lendingkart Finance - estimated"),
    # ── Vivriti Capital ───────────────────────────────────────────────────────
    ("Vivriti Capital", "FY2023", 5200, 6500, 1500, 520, 195, 26, 0.5, 1.20, 3.3, 14.2, "estimated", "Vivriti Capital - estimated"),
    ("Vivriti Capital", "FY2024", 8500, 10500, 2100, 850, 340, 43, 0.5, 1.30, 3.5, 18.2, "estimated", "Vivriti Capital - estimated"),
    ("Vivriti Capital", "FY2025", 12000, 14800, 2800, 1250, 510, 60, 0.5, 1.40, 3.8, 20.3, "estimated", "Vivriti Capital - estimated"),
    # ── KreditBee ─────────────────────────────────────────────────────────────
    ("KreditBee", "FY2023", 4800, 6000, 1500, 780, 280, 120, 2.5, 2.80, 5.1, 20.0, "estimated", "KreditBee (Krazybee Services) - estimated"),
    ("KreditBee", "FY2024", 7200, 9000, 2200, 1200, 420, 202, 2.8, 3.20, 5.1, 21.9, "estimated", "KreditBee (Krazybee Services) - estimated"),
    ("KreditBee", "FY2025", 8500, 10800, 2800, 1450, 380, 298, 3.5, 4.50, 3.8, 15.0, "estimated", "KreditBee (Krazybee Services) - estimated"),
    # ── Fibe ──────────────────────────────────────────────────────────────────
    ("Fibe", "FY2023", 3200, 4100, 900, 520, 145, 64, 2.0, 2.50, 3.8, 17.5, "estimated", "Fibe (EarlySalary) standalone NBFC - estimated"),
    ("Fibe", "FY2024", 5500, 7000, 1400, 890, 195, 165, 3.0, 3.80, 3.1, 16.1, "estimated", "Fibe (EarlySalary) standalone NBFC - estimated"),
    ("Fibe", "FY2025", 6200, 7900, 1700, 1020, 165, 248, 4.0, 5.20, 2.3, 10.8, "estimated", "Fibe (EarlySalary) standalone NBFC - estimated. FY2026 Q2/Q3 unavailable"),
    # ── PayU Finance ──────────────────────────────────────────────────────────
    ("PayU Finance", "FY2024", 2800, 3600, 1200, 380, 85, 84, 3.0, 3.50, 2.6, 7.7, "unverified", "PayU Finance - unverified"),
    ("PayU Finance", "FY2025", 3500, 4500, 1400, 490, 115, 123, 3.5, 4.20, 2.8, 8.9, "unverified", "PayU Finance - unverified"),
    # ── WhizDM Finance ────────────────────────────────────────────────────────
    ("WhizDM Finance", "FY2024", 5800, 7200, 2200, 880, 280, 145, 2.5, 2.80, 4.3, 14.1, "unverified", "WhizDM Finance (MoneyView) - unverified, needs verification against RBI filings"),
    ("WhizDM Finance", "FY2025", 8200, 10200, 2900, 1250, 380, 246, 3.0, 3.50, 4.1, 14.8, "unverified", "WhizDM Finance (MoneyView) - unverified, needs verification against RBI filings"),
    # ── FY2026-Q3 estimates for unlisted / fintech NBFCs ──────────────────────
    # NII/PAT/credit_losses = 9M cumulative (annualise ×4/3 in app)
    # loan_book/assets/equity/gnpa/roa/roe/clr = Dec-25 point-in-time
    # All estimated — derived from FY25 run-rates adjusted for sector trends
    ("KreditBee", "FY2026-Q3", 9800, 12400, 3100, 1120, 290, 255, 3.8, 4.80, 3.5, 13.5, "estimated", "KreditBee Q3FY26 - estimated from FY25 run-rate"),
    ("Fibe", "FY2026-Q3", 6500, 8300, 1820, 790, 120, 200, 4.2, 5.50, 2.1, 9.5, "estimated", "Fibe Q3FY26 - estimated from FY25 run-rate. Official Q2/Q3 FY26 filings unavailable"),
    ("Lendingkart Finance", "FY2026-Q3", 4000, 5100, 1260, 510, 55, 105, 3.5, 4.80, 1.4, 6.5, "estimated", "Lendingkart Q3FY26 - estimated from FY25 run-rate"),
    ("Vivriti Capital", "FY2026-Q3", 14200, 17500, 3150, 990, 405, 52, 0.48, 1.35, 3.8, 19.0, "estimated", "Vivriti Capital Q3FY26 - estimated from FY25 run-rate"),
    ("Veritas Finance", "FY2026-Q3", 8800, 11000, 2450, 900, 345, 53, 0.78, 2.45, 5.0, 21.0, "estimated", "Veritas Finance Q3FY26 - estimated from FY25 run-rate"),
    ("Arohan Financial Services", "FY2026-Q3", 6500, 8800, 1880, 1000, -230, 510, 8.8, 9.80, -3.5, -16.5, "estimated", "Arohan Q3FY26 - estimated, MFI sector stress continuing"),
    ("Asirvad Micro Finance", "FY2026-Q3", 5500, 7200, 1680, 880, -320, 560, 11.0, 11.20, -6.0, -26.0, "estimated", "Asirvad Q3FY26 - estimated, MFI sector stress continuing"),
    ("Vastu Housing Finance", "FY2026-Q3", 15800, 19000, 3750, 1020, 440, 35, 0.27, 0.98, 3.8, 17.5, "estimated", "Vastu Housing Finance Q3FY26 - estimated from FY25 run-rate"),
    ("Hero Housing Finance", "FY2026-Q3", 7200, 9000, 2250, 435, 158, 20, 0.38, 1.25, 3.0, 10.2, "estimated", "Hero Housing Finance Q3FY26 - estimated from FY25 run-rate"),
    ("Godrej Housing Finance", "FY2026-Q3", 15500, 18800, 5200, 780, 420, 5, 0.04, 0.14, 3.9, 12.5, "estimated", "Godrej Housing Finance Q3FY26 - estimated from FY25 run-rate"),
    ("Motilal Oswal Home Finance", "FY2026-Q3", 10000, 12800, 2400, 630, 280, 72, 0.95, 2.10, 3.7, 17.5, "estimated", "Motilal Oswal Home Finance Q3FY26 - estimated from FY25 run-rate"),
    ("Shriram Housing Finance", "FY2026-Q3", 19500, 24600, 3950, 1130, 455, 44, 0.28, 1.55, 3.1, 17.0, "estimated", "Shriram Housing Finance Q3FY26 - estimated from FY25 run-rate"),
    ("HDB Financial Services", "FY2026-Q3", 110000, 138000, 21500, 7200, 2780, 1080, 1.25, 2.88, 3.0, 18.5, "estimated", "HDB Financial Services Q3FY26 - estimated from FY25 run-rate"),
    ("Tata Capital Financial Services", "FY2026-Q3", 158000, 208000, 36500, 7050, 3200, 1200, 0.98, 2.25, 2.4, 12.8, "estimated", "Tata Capital Q3FY26 - estimated from FY25 run-rate"),
    ("SMFG India Credit", "FY2026-Q3", 31500, 40000, 10500, 2920, 1350, 330, 1.25, 2.55, 5.0, 18.5, "estimated", "SMFG India Credit Q3FY26 - estimated from FY25 run-rate"),
    ("Aditya Birla Finance", "FY2026-Q3", 118000, 153000, 27500, 5950, 2480, 780, 0.83, 2.05, 2.5, 13.0, "estimated", "Aditya Birla Finance Q3FY26 - estimated from FY25 run-rate"),
    ("Piramal Capital & Housing Finance", "FY2026-Q3", 85000, 112000, 24000, 4080, 2050, 870, 1.25, 2.45, 2.6, 12.5, "estimated", "Piramal Capital Q3FY26 - estimated from FY25 run-rate"),
    ("Jio Financial Services", "FY2026-Q3", 18000, 160000, 152000, 780, 1520, 5, 0.04, 0.0, 1.3, 1.4, "estimated", "Jio Financial Services Q3FY26 - estimated from FY25 run-rate"),
    ("PayU Finance", "FY2026-Q3", 3800, 4900, 1520, 380, 85, 108, 3.8, 4.50, 2.7, 8.2, "unverified", "PayU Finance Q3FY26 - unverified"),
    ("WhizDM Finance", "FY2026-Q3", 9800, 12200, 3200, 990, 300, 228, 3.2, 3.45, 4.0, 14.0, "unverified", "WhizDM Finance Q3FY26 - unverified, needs verification"),
]


def build():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Drop and recreate
    cur.executescript("DROP TABLE IF EXISTS financials; DROP TABLE IF EXISTS nbfc;")
    cur.executescript(SCHEMA)

    # Insert companies
    company_ids = {}
    for row in COMPANIES:
        cur.execute("""
            INSERT INTO nbfc (name, rbi_layer, sector, listed, has_financials,
                              total_assets_cr, data_quality, ticker, source, last_verified)
            VALUES (?,?,?,?,?,?,?,?,?,?)
        """, (*row, "2025-04-04"))
        company_ids[row[0]] = cur.lastrowid

    # Insert financials
    missing = set()
    inserted = 0
    for row in FINANCIALS:
        company_name = row[0]
        nbfc_id = company_ids.get(company_name)
        if nbfc_id is None:
            missing.add(company_name)
            continue
        cur.execute("""
            INSERT INTO financials (nbfc_id, period, loan_book_cr, total_assets_cr, equity_cr,
                net_interest_income_cr, pat_cr, credit_losses_cr, credit_loss_rate_pct,
                gnpa_pct, roa_pct, roe_pct, data_quality, source)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (nbfc_id, *row[1:]))
        inserted += 1

    conn.commit()
    conn.close()

    print(f"✅ Database built: {DB_PATH}")
    print(f"   Companies inserted : {len(company_ids)}")
    print(f"   Financial rows     : {inserted}")
    if missing:
        print(f"   ⚠️  Missing company IDs: {missing}")

    # Quick verification
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM nbfc")
    n_companies = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM financials")
    n_fin = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM nbfc WHERE has_financials=1")
    n_with_data = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT period) FROM financials")
    n_periods = cur.fetchone()[0]
    conn.close()

    print(f"\n📊 Verification:")
    print(f"   nbfc rows          : {n_companies}")
    print(f"   with financial data: {n_with_data}")
    print(f"   financials rows    : {n_fin}")
    print(f"   distinct periods   : {n_periods}")


if __name__ == "__main__":
    build()
