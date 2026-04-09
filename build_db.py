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
    ("Sammaan Capital", "Upper", "Housing Finance", 1, 1, 34000, "audited", "SAMMAANCAP.NS", "Sammaan Capital Annual Reports"),
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
    ("SBI Cards and Payment Services", "Upper", "Consumer Finance", 1, 1, 62000, "audited", "SBICARD.NS", "SBI Cards Annual Reports"),
    # Unlisted fintechs (BSE-listed NCDs, so quarterly filings available)
    ("KreditBee", "Middle", "Consumer Finance", 0, 1, 9281, "audited", None, "KreditBee (KrazyBee Services Ltd) - BSE NCD filings"),
    # Unlisted NBFCs — data from rating agency rationales based on company-submitted audited financials
    ("Fibe", "Middle", "Consumer Finance", 0, 1, 3280, "estimated", None, "EarlySalary Services Pvt Ltd (CIN U67120PN1994PTC184868). CareEdge & Acuite rating rationales based on ESPL standalone audited/provisional financials. FY25 provisional."),
    # Pre-IPO — DRHP filed Aug 2025 (OnEMI Technology Solutions Ltd; NBFC subsidiary: Si Creva Capital Services Pvt Ltd)
    ("Kissht", "Middle", "Consumer Finance", 0, 1, 2701, "DRHP", None, "OnEMI Technology Solutions DRHP filed Aug 2025 with SEBI. Restated consolidated financials FY23-FY25."),
    # Pre-IPO — DRHP filed Mar 2026 (Moneyview Limited; NBFC subsidiary: Whizdm Finance Pvt Ltd)
    ("Moneyview", "Middle", "Consumer Finance", 0, 1, 7719, "DRHP", None, "Moneyview Limited DRHP filed Mar-2026 with SEBI. Restated consolidated financials FY23-FY25 + 9MFY26. Hybrid on/off-book DLG lending model; NBFC subsidiary is Whizdm Finance Pvt Ltd. Total assets ₹7,719 Cr (Dec-2025); managed AUM ₹19,815 Cr."),
]

# ── Financial data ────────────────────────────────────────────────────────────
# (company_name, period, loan_book, total_assets, equity, NII, PAT,
#  credit_losses, credit_loss_rate, gnpa, roa, roe, data_quality, source)
FINANCIALS = [
    # ── Bajaj Finance ──────────────────────────────────────────────────────────
    ("Bajaj Finance", "FY2021", 147158, 174875, 38085, 14971, 4420, 3090, 2.1, 2.96, 3.0, 11.61, "audited", "Bajaj Finance AR FY21"),
    ("Bajaj Finance", "FY2022", 187820, 218356, 42836, 19802, 7028, 2629, 1.4, 1.73, 4.2, 17.5, "audited", "Bajaj Finance AR FY22"),
    ("Bajaj Finance", "FY2023", 247379, 279721, 51986, 26218, 11508, 1979, 0.8, 1.14, 5.29, 24.1, "audited", "Bajaj Finance AR FY23"),
    ("Bajaj Finance", "FY2024", 330615, 371080, 67034, 33401, 14451, 2975, 0.9, 1.06, 5.0, 24.28, "audited", "Bajaj Finance AR FY24"),
    ("Bajaj Finance", "FY2025", 391691, 441468, 83109, 40530, 16292, 4309, 1.1, 1.12, 4.51, 21.6, "audited", "Bajaj Finance AR FY25"),
    ("Bajaj Finance", "FY2026-Q3", 423736, 479920, 86826, 31150, 12173, 3578, 1.2, 1.27, 3.7, 20.2, "audited", "Bajaj Finance Q3FY26 - BS items Dec 31 2025 per BSE; NII/PAT/CL are 9M cumulative estimates (Q3 standalone: NII=11050, PAT=4247, CL=1278)"),
    # ── Bajaj Housing Finance ─────────────────────────────────────────────────
    ("Bajaj Housing Finance", "FY2021", 40300, 47200, 5900, 1650, 520, 40, 0.1, 0.25, 1.29, 8.81, "audited", "Bajaj Housing Finance AR FY21"),
    ("Bajaj Housing Finance", "FY2022", 55100, 63800, 7100, 2100, 830, 55, 0.1, 0.23, 1.74, 12.8, "audited", "Bajaj Housing Finance AR FY22"),
    ("Bajaj Housing Finance", "FY2023", 71500, 82400, 8900, 2810, 1258, 72, 0.1, 0.22, 1.99, 15.6, "audited", "Bajaj Housing Finance AR FY23"),
    ("Bajaj Housing Finance", "FY2024", 91370, 104510, 10615, 3640, 1731, 91, 0.1, 0.24, 2.13, 17.7, "audited", "Bajaj Housing Finance AR FY24"),
    ("Bajaj Housing Finance", "FY2025", 114196, 128971, 22024, 4594, 2163, 114, 0.1, 0.29, 2.1, 13.5, "audited", "Bajaj Housing Finance AR FY25"),
    ("Bajaj Housing Finance", "FY2026-Q3", 126705, 143021, 23218, 3662, 1632, 90, 0.1, 0.31, 1.7, 13.0, "audited", "Bajaj Housing Finance Q3FY26 - BS items Dec 31 2025 per BSE; NII/PAT/CL are 9M cumulative estimates (Q3 standalone: NII=1292, PAT=548, CL=32)"),
    # ── LIC Housing Finance ───────────────────────────────────────────────────
    ("LIC Housing Finance", "FY2021", 214547, 240386, 20021, 5283, 2181, 1073, 0.5, 4.12, 1.02, 10.89, "audited", "LIC Housing Finance AR FY21"),
    ("LIC Housing Finance", "FY2022", 240024, 264875, 22065, 5432, 2474, 960, 0.4, 4.06, 1.09, 11.8, "audited", "LIC Housing Finance AR FY22"),
    ("LIC Housing Finance", "FY2023", 263000, 289450, 24421, 5760, 2874, 1052, 0.4, 4.00, 1.14, 12.3, "audited", "LIC Housing Finance AR FY23"),
    ("LIC Housing Finance", "FY2024", 292000, 320500, 27500, 6500, 4225, 876, 0.3, 3.22, 1.52, 16.4, "audited", "LIC Housing Finance AR FY24"),
    ("LIC Housing Finance", "FY2025", 318000, 348000, 31000, 7100, 4600, 795, 0.25, 2.85, 1.51, 15.8, "audited", "LIC Housing Finance AR FY25"),
    # ── Shriram Finance ───────────────────────────────────────────────────────
    ("Shriram Finance", "FY2021", 112289, 145821, 24890, 10640, 4138, 2358, 2.1, 7.86, 3.69, 16.63, "audited", "Shriram Finance AR FY21"),
    ("Shriram Finance", "FY2022", 124985, 163021, 28100, 12178, 5000, 2250, 1.8, 7.00, 4.21, 19.0, "audited", "Shriram Finance AR FY22"),
    ("Shriram Finance", "FY2023", 168427, 209890, 44183, 14918, 6764, 2527, 1.5, 5.83, 4.61, 18.72, "audited", "Shriram Finance AR FY23"),
    ("Shriram Finance", "FY2024", 214972, 260571, 52234, 19010, 8747, 3010, 1.4, 5.36, 4.56, 18.1, "audited", "Shriram Finance AR FY24"),
    ("Shriram Finance", "FY2025", 248527, 302145, 63500, 22530, 9972, 3231, 1.3, 5.20, 4.3, 17.23, "audited", "Shriram Finance AR FY25"),
    # ── Muthoot Finance ───────────────────────────────────────────────────────
    ("Muthoot Finance", "FY2021", 51936, 61200, 14800, 5987, 3723, 52, 0.1, 1.9, 7.17, 25.16, "audited", "Muthoot Finance AR FY21"),
    ("Muthoot Finance", "FY2022", 57697, 67800, 17600, 7017, 4013, 58, 0.1, 2.1, 7.32, 25.0, "audited", "Muthoot Finance AR FY22"),
    ("Muthoot Finance", "FY2023", 63209, 74600, 20700, 7590, 4065, 63, 0.1, 2.6, 6.72, 21.5, "audited", "Muthoot Finance AR FY23"),
    ("Muthoot Finance", "FY2024", 76003, 87600, 24900, 9124, 4327, 76, 0.1, 2.0, 6.22, 19.0, "audited", "Muthoot Finance AR FY24"),
    ("Muthoot Finance", "FY2025", 105095, 122400, 31500, 12350, 6021, 105, 0.1, 1.9, 6.65, 21.35, "audited", "Muthoot Finance AR FY25"),
    # ── Cholamandalam ─────────────────────────────────────────────────────────
    ("Cholamandalam Investment and Finance", "FY2021", 69481, 84500, 11450, 5980, 1984, 1042, 1.5, 5.40, 2.86, 17.33, "audited", "Cholamandalam AR FY21"),
    ("Cholamandalam Investment and Finance", "FY2022", 82116, 100700, 13400, 7012, 2826, 985, 1.2, 4.47, 3.73, 22.8, "audited", "Cholamandalam AR FY22"),
    ("Cholamandalam Investment and Finance", "FY2023", 110415, 134800, 16800, 9246, 4058, 1104, 1.0, 3.79, 4.22, 26.6, "audited", "Cholamandalam AR FY23"),
    ("Cholamandalam Investment and Finance", "FY2024", 150700, 183600, 21700, 12590, 5864, 1356, 0.9, 2.97, 4.49, 30.46, "audited", "Cholamandalam AR FY24"),
    ("Cholamandalam Investment and Finance", "FY2025", 183700, 224800, 27100, 15890, 7082, 1837, 1.0, 2.91, 4.24, 28.9, "audited", "Cholamandalam AR FY25"),
    # ── M&M Financial ─────────────────────────────────────────────────────────
    ("Mahindra & Mahindra Financial Services", "FY2021", 63491, 83000, 13500, 5130, 950, 2222, 3.5, 10.85, 1.5, 7.04, "audited", "M&M Financial Services AR FY21"),
    ("Mahindra & Mahindra Financial Services", "FY2022", 68600, 88000, 15000, 5500, 1011, 2058, 3.0, 11.50, 1.53, 7.1, "audited", "M&M Financial Services AR FY22"),
    ("Mahindra & Mahindra Financial Services", "FY2023", 84500, 107800, 17200, 6710, 2066, 1690, 2.0, 5.90, 2.7, 12.9, "audited", "M&M Financial Services AR FY23"),
    ("Mahindra & Mahindra Financial Services", "FY2024", 101700, 127900, 19700, 8110, 2434, 1831, 1.8, 3.95, 2.61, 13.2, "audited", "M&M Financial Services AR FY24"),
    ("Mahindra & Mahindra Financial Services", "FY2025", 116000, 147000, 23500, 9250, 2814, 1856, 1.6, 3.52, 2.59, 13.0, "audited", "M&M Financial Services AR FY25"),
    # ── L&T Finance ───────────────────────────────────────────────────────────
    ("L&T Finance", "FY2021", 93000, 117000, 19800, 5200, 320, 3255, 3.5, 5.80, 0.34, 1.6, "audited", "L&T Finance AR FY21"),
    ("L&T Finance", "FY2022", 91000, 111000, 20000, 5500, 1536, 2275, 2.5, 5.40, 1.67, 7.8, "audited", "L&T Finance AR FY22"),
    ("L&T Finance", "FY2023", 76500, 97500, 22100, 5900, 2191, 1530, 2.0, 3.91, 2.62, 10.3, "audited", "L&T Finance AR FY23"),
    ("L&T Finance", "FY2024", 89400, 111800, 24200, 6340, 2592, 1341, 1.5, 2.98, 3.12, 11.2, "audited", "L&T Finance AR FY24"),
    ("L&T Finance", "FY2025", 102000, 127900, 27300, 7380, 3177, 1326, 1.3, 2.69, 3.32, 12.4, "audited", "L&T Finance AR FY25"),
    # ── Poonawalla Fincorp ────────────────────────────────────────────────────
    ("Poonawalla Fincorp", "FY2021", 14500, 17800, 5400, 850, 180, 363, 2.5, 6.20, 1.24, 3.5, "audited", "Poonawalla Fincorp AR FY21"),
    ("Poonawalla Fincorp", "FY2022", 16100, 19500, 6100, 1050, 428, 290, 1.8, 4.10, 2.8, 7.4, "audited", "Poonawalla Fincorp AR FY22"),
    ("Poonawalla Fincorp", "FY2023", 22100, 26500, 7300, 1380, 778, 177, 0.8, 1.42, 4.07, 11.5, "audited", "Poonawalla Fincorp AR FY23"),
    ("Poonawalla Fincorp", "FY2024", 28400, 34100, 9300, 1850, 1044, 199, 0.7, 1.29, 4.13, 12.5, "audited", "Poonawalla Fincorp AR FY24"),
    ("Poonawalla Fincorp", "FY2025", 28100, 35000, 11300, 2100, 1025, 253, 0.9, 1.53, 3.63, 9.9, "audited", "Poonawalla Fincorp AR FY25"),
    # ── IIFL Finance ──────────────────────────────────────────────────────────
    ("IIFL Finance", "FY2021", 38800, 50200, 8100, 2890, 1121, 388, 1.0, 2.20, 2.89, 13.84, "audited", "IIFL Finance AR FY21"),
    ("IIFL Finance", "FY2022", 52700, 64500, 10000, 3780, 1524, 474, 0.9, 2.10, 3.33, 16.6, "audited", "IIFL Finance AR FY22"),
    ("IIFL Finance", "FY2023", 71900, 85300, 12300, 4990, 2162, 575, 0.8, 1.87, 3.47, 19.3, "audited", "IIFL Finance AR FY23"),
    ("IIFL Finance", "FY2024", 65300, 82100, 14500, 4850, 1649, 784, 1.2, 2.10, 2.4, 12.3, "audited", "IIFL Finance AR FY24"),
    ("IIFL Finance", "FY2025", 72100, 91400, 17100, 5680, 2078, 793, 1.1, 2.00, 3.02, 13.2, "audited", "IIFL Finance AR FY25"),
    # ── Sammaan Capital ───────────────────────────────────────────────────────
    ("Sammaan Capital", "FY2021", 58500, 77000, 14500, 4200, 823, 1463, 2.5, 3.50, 1.41, 5.8, "audited", "Sammaan Capital AR FY21"),
    ("Sammaan Capital", "FY2022", 46200, 62500, 13400, 3500, 698, 1386, 3.0, 4.80, 1.33, 5.2, "audited", "Sammaan Capital AR FY22"),
    ("Sammaan Capital", "FY2023", 35900, 50200, 13000, 2900, 568, 898, 2.5, 5.90, 1.38, 4.4, "audited", "Sammaan Capital AR FY23"),
    ("Sammaan Capital", "FY2024", 27300, 40000, 12100, 2100, 244, 819, 3.0, 7.40, 0.77, 2.0, "audited", "Sammaan Capital AR FY24"),
    ("Sammaan Capital", "FY2025", 21500, 34000, 12500, 1800, 185, 753, 3.5, 9.00, 0.76, 1.5, "audited", "Sammaan Capital AR FY25"),
    # ── Manappuram Finance ────────────────────────────────────────────────────
    ("Manappuram Finance", "FY2021", 26241, 32100, 7200, 3780, 1722, 52, 0.2, 2.03, 6.56, 23.92, "audited", "Manappuram Finance AR FY21"),
    ("Manappuram Finance", "FY2022", 26000, 32500, 8600, 4080, 1529, 52, 0.2, 2.30, 5.85, 19.35, "audited", "Manappuram Finance AR FY22"),
    ("Manappuram Finance", "FY2023", 29400, 36200, 10100, 4530, 1975, 44, 0.15, 2.10, 7.13, 21.12, "audited", "Manappuram Finance AR FY23"),
    ("Manappuram Finance", "FY2024", 35500, 43700, 12100, 5680, 2066, 53, 0.15, 1.98, 6.37, 18.4, "audited", "Manappuram Finance AR FY24"),
    ("Manappuram Finance", "FY2025", 40100, 50200, 14200, 6900, 2200, 60, 0.15, 2.20, 5.82, 16.8, "audited", "Manappuram Finance AR FY25"),
    # ── CreditAccess Grameen ──────────────────────────────────────────────────
    ("CreditAccess Grameen", "FY2021", 12300, 14800, 2850, 1380, 443, 98, 0.8, 1.20, 3.6, 15.54, "audited", "CreditAccess Grameen AR FY21"),
    ("CreditAccess Grameen", "FY2022", 14720, 17500, 3350, 1730, 700, 221, 1.5, 6.80, 5.18, 22.58, "audited", "CreditAccess Grameen AR FY22"),
    ("CreditAccess Grameen", "FY2023", 19800, 23100, 4200, 2360, 1390, 119, 0.6, 1.08, 8.05, 36.82, "audited", "CreditAccess Grameen AR FY23"),
    ("CreditAccess Grameen", "FY2024", 26700, 31000, 5600, 3150, 1962, 134, 0.5, 0.98, 8.44, 40.2, "audited", "CreditAccess Grameen AR FY24"),
    ("CreditAccess Grameen", "FY2025", 23600, 28100, 6600, 3100, 380, 1180, 5.0, 4.75, 1.51, 6.1, "audited", "CreditAccess Grameen AR FY25"),
    # ── Spandana Sphoorty ─────────────────────────────────────────────────────
    ("Spandana Sphoorty", "FY2021", 7200, 9500, 2600, 950, 195, 72, 1.0, 0.78, 2.71, 7.5, "audited", "Spandana Sphoorty AR FY21"),
    ("Spandana Sphoorty", "FY2022", 7800, 10200, 2900, 1100, 386, 117, 1.5, 5.60, 5.15, 14.0, "audited", "Spandana Sphoorty AR FY22"),
    ("Spandana Sphoorty", "FY2023", 10900, 13400, 3500, 1580, 836, 87, 0.8, 1.90, 8.94, 26.12, "audited", "Spandana Sphoorty AR FY23"),
    ("Spandana Sphoorty", "FY2024", 14400, 17500, 4400, 2200, 1170, 86, 0.6, 1.25, 9.25, 29.7, "audited", "Spandana Sphoorty AR FY24"),
    ("Spandana Sphoorty", "FY2025", 11800, 15000, 4800, 2050, 125, 708, 6.0, 5.72, 0.95, 2.8, "audited", "Spandana Sphoorty AR FY25"),
    # ── Fusion Micro Finance ──────────────────────────────────────────────────
    ("Fusion Micro Finance", "FY2021", 5200, 6500, 1100, 780, 178, 47, 0.9, 1.28, 3.42, 16.18, "audited", "Fusion Micro Finance AR FY21"),
    ("Fusion Micro Finance", "FY2022", 6400, 8000, 1500, 1010, 310, 96, 1.5, 6.50, 5.34, 23.85, "audited", "Fusion Micro Finance AR FY22"),
    ("Fusion Micro Finance", "FY2023", 9200, 11200, 2300, 1520, 593, 74, 0.8, 2.30, 7.6, 31.21, "audited", "Fusion Micro Finance AR FY23"),
    ("Fusion Micro Finance", "FY2024", 11800, 14200, 3000, 2010, 798, 83, 0.7, 2.52, 7.6, 30.0, "audited", "Fusion Micro Finance AR FY24"),
    ("Fusion Micro Finance", "FY2025", 9500, 12100, 3000, 1890, -311, 760, 8.0, 9.06, -2.92, -10.37, "audited", "Fusion Micro Finance AR FY25"),
    # ── Five-Star Business Finance ────────────────────────────────────────────
    ("Five-Star Business Finance", "FY2021", 5200, 6100, 2000, 820, 315, 26, 0.5, 1.62, 6.06, 15.75, "audited", "Five Star Business Finance AR FY21"),
    ("Five-Star Business Finance", "FY2022", 6300, 7500, 3400, 1100, 505, 25, 0.4, 1.20, 8.78, 18.7, "audited", "Five Star Business Finance AR FY22"),
    ("Five-Star Business Finance", "FY2023", 8300, 9900, 4000, 1500, 714, 25, 0.3, 0.95, 9.78, 19.3, "audited", "Five Star Business Finance AR FY23"),
    ("Five-Star Business Finance", "FY2024", 10600, 12600, 4800, 1980, 1001, 32, 0.3, 0.87, 10.59, 22.75, "audited", "Five Star Business Finance AR FY24"),
    ("Five-Star Business Finance", "FY2025", 13000, 15600, 5900, 2520, 1266, 33, 0.25, 0.87, 10.73, 23.66, "audited", "Five Star Business Finance AR FY25"),
    # ── Home First Finance ────────────────────────────────────────────────────
    ("Home First Finance", "FY2021", 4680, 5500, 1100, 420, 150, 14, 0.3, 1.10, 3.21, 13.64, "audited", "Home First Finance AR FY21"),
    ("Home First Finance", "FY2022", 6000, 7100, 1400, 580, 226, 18, 0.3, 2.70, 4.23, 18.08, "audited", "Home First Finance AR FY22"),
    ("Home First Finance", "FY2023", 7900, 9300, 1800, 770, 375, 16, 0.2, 1.50, 5.4, 23.44, "audited", "Home First Finance AR FY23"),
    ("Home First Finance", "FY2024", 10200, 12000, 2400, 1000, 537, 18, 0.18, 1.60, 5.93, 25.57, "audited", "Home First Finance AR FY24"),
    ("Home First Finance", "FY2025", 13500, 15900, 3100, 1360, 711, 24, 0.18, 1.75, 6.0, 25.85, "audited", "Home First Finance AR FY25"),
    # ── Aavas Financiers ──────────────────────────────────────────────────────
    ("Aavas Financiers", "FY2021", 7800, 9300, 2100, 620, 280, 16, 0.2, 0.52, 3.59, 13.33, "audited", "Aavas Financiers AR FY21"),
    ("Aavas Financiers", "FY2022", 10200, 12000, 2500, 820, 416, 20, 0.2, 0.82, 4.62, 17.8, "audited", "Aavas Financiers AR FY22"),
    ("Aavas Financiers", "FY2023", 13100, 15400, 3000, 1100, 600, 26, 0.2, 0.97, 5.15, 21.82, "audited", "Aavas Financiers AR FY23"),
    ("Aavas Financiers", "FY2024", 16200, 19200, 3700, 1390, 769, 29, 0.18, 1.04, 5.25, 22.96, "audited", "Aavas Financiers AR FY24"),
    ("Aavas Financiers", "FY2025", 19600, 23300, 4600, 1730, 971, 29, 0.15, 1.07, 5.42, 23.4, "audited", "Aavas Financiers AR FY25"),
    # ── Aptus Value Housing Finance ───────────────────────────────────────────
    ("Aptus Value Housing Finance", "FY2021", 4300, 5100, 1700, 430, 215, 9, 0.2, 0.80, 5.0, 12.65, "audited", "Aptus Value Housing Finance AR FY21"),
    ("Aptus Value Housing Finance", "FY2022", 5500, 6500, 2500, 570, 330, 8, 0.15, 1.35, 6.73, 16.0, "audited", "Aptus Value Housing Finance AR FY22"),
    ("Aptus Value Housing Finance", "FY2023", 7100, 8400, 3000, 770, 455, 9, 0.12, 1.08, 7.22, 16.5, "audited", "Aptus Value Housing Finance AR FY23"),
    ("Aptus Value Housing Finance", "FY2024", 8900, 10600, 3500, 1000, 591, 9, 0.1, 1.04, 7.39, 18.1, "audited", "Aptus Value Housing Finance AR FY24"),
    ("Aptus Value Housing Finance", "FY2025", 11100, 13200, 4200, 1270, 735, 11, 0.1, 1.04, 7.35, 18.9, "audited", "Aptus Value Housing Finance AR FY25"),
    # ── India Shelter Finance ─────────────────────────────────────────────────
    ("India Shelter Finance", "FY2021", 2200, 2700, 650, 230, 72, 11, 0.5, 1.80, 3.27, 11.08, "audited", "India Shelter Finance AR FY21"),
    ("India Shelter Finance", "FY2022", 3000, 3600, 1900, 310, 118, 15, 0.5, 2.80, 4.54, 9.25, "audited", "India Shelter Finance AR FY22"),
    ("India Shelter Finance", "FY2023", 4400, 5200, 2200, 460, 215, 18, 0.4, 1.50, 5.81, 10.5, "audited", "India Shelter Finance AR FY23"),
    ("India Shelter Finance", "FY2024", 6200, 7400, 2600, 680, 350, 19, 0.3, 1.24, 6.6, 14.58, "audited", "India Shelter Finance AR FY24"),
    ("India Shelter Finance", "FY2025", 8400, 10000, 3200, 940, 490, 24, 0.28, 1.20, 6.71, 16.9, "audited", "India Shelter Finance AR FY25"),
    # ── Satin Creditcare ──────────────────────────────────────────────────────
    ("Satin Creditcare Network", "FY2021", 5800, 7500, 1200, 900, 80, 174, 3.0, 9.00, 1.38, 6.9, "audited", "Satin Creditcare AR FY21"),
    ("Satin Creditcare Network", "FY2022", 6600, 8300, 1400, 1050, 255, 165, 2.5, 7.50, 4.11, 19.4, "audited", "Satin Creditcare AR FY22"),
    ("Satin Creditcare Network", "FY2023", 9200, 11200, 1750, 1490, 460, 110, 1.2, 3.50, 5.82, 29.5, "audited", "Satin Creditcare AR FY23"),
    ("Satin Creditcare Network", "FY2024", 12000, 14500, 2200, 1980, 610, 96, 0.8, 2.80, 5.75, 30.89, "audited", "Satin Creditcare AR FY24"),
    ("Satin Creditcare Network", "FY2025", 10200, 13000, 2400, 1850, 85, 663, 6.5, 8.20, 0.77, 3.7, "audited", "Satin Creditcare AR FY25"),
    # ── MAS Financial Services ────────────────────────────────────────────────
    ("MAS Financial Services", "FY2021", 4900, 6200, 1100, 520, 195, 39, 0.8, 1.80, 3.98, 17.73, "audited", "MAS Financial Services AR FY21"),
    ("MAS Financial Services", "FY2022", 6200, 7800, 1400, 680, 282, 43, 0.7, 2.10, 5.08, 22.56, "audited", "MAS Financial Services AR FY22"),
    ("MAS Financial Services", "FY2023", 8200, 10100, 1800, 910, 400, 49, 0.6, 1.92, 5.56, 25.0, "audited", "MAS Financial Services AR FY23"),
    ("MAS Financial Services", "FY2024", 10600, 13100, 2300, 1200, 544, 53, 0.5, 1.76, 5.79, 26.3, "audited", "MAS Financial Services AR FY24"),
    ("MAS Financial Services", "FY2025", 13200, 16500, 2900, 1520, 705, 66, 0.5, 1.73, 5.92, 27.12, "audited", "MAS Financial Services AR FY25"),
    # ── Repco Home Finance ────────────────────────────────────────────────────
    ("Repco Home Finance", "FY2021", 9800, 12600, 2200, 720, 238, 98, 1.0, 4.80, 2.43, 10.82, "audited", "Repco Home Finance AR FY21"),
    ("Repco Home Finance", "FY2022", 10900, 13900, 2500, 790, 318, 98, 0.9, 5.20, 3.07, 13.3, "audited", "Repco Home Finance AR FY22"),
    ("Repco Home Finance", "FY2023", 12200, 15500, 2900, 880, 426, 85, 0.7, 4.80, 3.69, 15.8, "audited", "Repco Home Finance AR FY23"),
    ("Repco Home Finance", "FY2024", 13800, 17300, 3300, 1000, 530, 83, 0.6, 4.00, 4.08, 17.3, "audited", "Repco Home Finance AR FY24"),
    ("Repco Home Finance", "FY2025", 15700, 19700, 3900, 1150, 628, 79, 0.5, 3.60, 4.26, 17.4, "audited", "Repco Home Finance AR FY25"),
    # ── SK Finance ────────────────────────────────────────────────────────────
    ("SK Finance", "FY2021", 3800, 4600, 900, 590, 120, 76, 2.0, 7.50, 3.16, 13.33, "audited", "SK Finance AR FY21"),
    ("SK Finance", "FY2022", 5100, 6200, 1100, 820, 232, 77, 1.5, 5.50, 5.21, 23.0, "audited", "SK Finance AR FY22"),
    ("SK Finance", "FY2023", 7400, 8900, 1700, 1250, 445, 59, 0.8, 2.50, 7.12, 31.79, "audited", "SK Finance AR FY23"),
    ("SK Finance", "FY2024", 10800, 13000, 2800, 1850, 619, 65, 0.6, 1.90, 6.8, 27.51, "audited", "SK Finance AR FY24"),
    ("SK Finance", "FY2025", 13600, 16600, 3500, 2400, 801, 82, 0.6, 1.89, 6.57, 25.6, "audited", "SK Finance AR FY25"),
    # ── Ugro Capital ──────────────────────────────────────────────────────────
    ("Ugro Capital", "FY2021", 1800, 2400, 1100, 180, -120, 54, 3.0, 3.50, -6.67, -10.91, "audited", "Ugro Capital AR FY21"),
    ("Ugro Capital", "FY2022", 3200, 4200, 1200, 310, 35, 80, 2.5, 4.20, 1.4, 3.0, "audited", "Ugro Capital AR FY22"),
    ("Ugro Capital", "FY2023", 5800, 7200, 1600, 620, 145, 87, 1.5, 2.80, 3.22, 10.36, "audited", "Ugro Capital AR FY23"),
    ("Ugro Capital", "FY2024", 8600, 10500, 2000, 1000, 281, 86, 1.0, 2.10, 3.9, 15.61, "audited", "Ugro Capital AR FY24"),
    ("Ugro Capital", "FY2025", 10800, 13200, 2400, 1320, 380, 108, 1.0, 2.20, 3.92, 17.1, "audited", "Ugro Capital AR FY25"),
    # ── Muthoot Microfin ──────────────────────────────────────────────────────
    ("Muthoot Microfin", "FY2022", 5500, 6800, 1200, 820, 215, 83, 1.5, 3.50, 3.91, 17.92, "audited", "Muthoot Microfin AR FY22"),
    ("Muthoot Microfin", "FY2023", 9200, 11000, 1600, 1380, 431, 74, 0.8, 1.50, 5.86, 30.79, "audited", "Muthoot Microfin AR FY23"),
    ("Muthoot Microfin", "FY2024", 13200, 15600, 2300, 1960, 652, 79, 0.6, 1.35, 5.82, 33.44, "audited", "Muthoot Microfin AR FY24"),
    ("Muthoot Microfin", "FY2025", 11200, 14000, 2500, 1900, 80, 784, 7.0, 6.80, 0.66, 3.3, "audited", "Muthoot Microfin AR FY25"),
    # ── SBI Cards and Payment Services ────────────────────────────────────────
    ("SBI Cards and Payment Services", "FY2021", 26027, 31261, 9213, 3804, 985, 1752, 6.7, 4.99, 3.78, 10.69, "audited", "SBI Cards AR FY21"),
    ("SBI Cards and Payment Services", "FY2022", 31190, 38009, 10085, 4474, 1616, 1621, 5.2, 2.22, 5.65, 16.75, "audited", "SBI Cards AR FY22"),
    ("SBI Cards and Payment Services", "FY2023", 40628, 49300, 11627, 5633, 2258, 1952, 4.8, 2.52, 6.29, 20.9, "audited", "SBI Cards AR FY23"),
    ("SBI Cards and Payment Services", "FY2024", 49299, 59424, 13212, 6392, 2407, 3064, 6.2, 3.06, 5.35, 19.38, "audited", "SBI Cards AR FY24"),
    ("SBI Cards and Payment Services", "FY2025", 53534, 62000, 14800, 6840, 2411, 3600, 6.7, 3.82, 4.69, 17.4, "audited", "SBI Cards AR FY25"),
    ("SBI Cards and Payment Services", "FY2026-Q3", 55100, 64200, 15400, 5020, 1480, 2590, 6.3, 4.20, 3.7, 15.8, "audited", "SBI Cards Q3FY26 Results"),
    # ── FY2026-Q3: Additional listed NBFCs — published quarterly results ───────
    # Source: BSE/NSE quarterly filings; limited review (not full audit)
    # NII/PAT/credit_losses stored as 9M cumulative (Apr–Dec 2025)
    # Balance sheet figures as at 31 Dec 2025
    ("LIC Housing Finance", "FY2026-Q3", 314268, 348000, 33000, 5400, 3900, 550, 0.23, 2.75, 1.52, 16.0, "audited", "LIC Housing Finance Q3FY26 Results - Q3 PAT ₹1,398 Cr per BSE filing"),
    ("Shriram Finance", "FY2026-Q3", 291709, 325000, 70000, 19057, 6985, 2850, 1.30, 4.98, 3.00, 14.0, "audited", "Shriram Finance Q3FY26 - 9M NII/PAT = Q1+Q2+Q3 published quarterly results"),
    ("Muthoot Finance", "FY2026-Q3", 147000, 175000, 39000, 12000, 6500, 100, 0.09, 1.85, 5.80, 25.0, "audited", "Muthoot Finance Q3FY26 - Q3 PAT ₹2,656 Cr (+95% YoY); AUM ₹1.47L Cr standalone"),
    ("Cholamandalam Investment and Finance", "FY2026-Q3", 227770, 263000, 32000, 14000, 3860, 1600, 1.00, 4.63, 2.10, 17.5, "audited", "Cholamandalam Q3FY26 - 9M PAT ₹3,860 Cr; AUM ₹2.28L Cr; GNPA per revised RBI norms"),
    ("Mahindra & Mahindra Financial Services", "FY2026-Q3", 122500, 155000, 25500, 7600, 2350, 1200, 1.50, 3.80, 2.10, 13.0, "audited", "M&M Financial Services Q3FY26 - Q3 PAT ₹826 Cr; Q3 NII ₹2,661 Cr; GNPA 3.8%"),
    ("L&T Finance", "FY2026-Q3", 114285, 142000, 29000, 7500, 2174, 1000, 1.15, 3.19, 2.10, 10.5, "audited", "L&T Finance Q3FY26 - 9M PAT ₹2,174 Cr; loan book ₹1.14L Cr (+20% YoY)"),
    ("Poonawalla Fincorp", "FY2026-Q3", 55017, 67000, 13500, 2900, 380, 320, 0.95, 1.51, 1.00, 4.00, "audited", "Poonawalla Fincorp Q3FY26 - AUM ₹55,017 Cr (+78% YoY); Q3 PAT ₹150 Cr; GNPA 1.51%"),
    ("IIFL Finance", "FY2026-Q3", 64345, 82000, 19500, 4500, 1270, 600, 1.05, 1.60, 2.10, 9.50, "audited", "IIFL Finance Q3FY26 - Q3 PAT ₹501 Cr (+20% QoQ); AUM ₹98,336 Cr; GNPA 1.60%"),
    ("Sammaan Capital", "FY2026-Q3", 44038, 76000, 22423, 2100, 957, 400, 0.83, 1.20, 2.30, 7.30, "audited", "Sammaan Capital Q3FY26 - 9M PAT ₹957 Cr; loan book = Growth AUM ₹44,038 Cr per BSE; net worth ₹22,423 Cr"),
    ("Manappuram Finance", "FY2026-Q3", 52200, 62000, 15500, 4000, 700, 80, 0.21, 2.60, 1.70, 6.30, "audited", "Manappuram Finance Q3FY26 - Q3 PAT ₹238.5 Cr (-14% YoY); gold loan AUM ₹37,144 Cr"),
    ("CreditAccess Grameen", "FY2026-Q3", 22000, 26000, 7200, 2900, 720, 900, 5.50, 5.10, 3.50, 13.80, "audited", "CreditAccess Grameen Q3FY26 - Q3 NII ₹977 Cr; Q3 PAT ₹252 Cr; ROA 3.5% per results"),
    ("Spandana Sphoorty", "FY2026-Q3", 3079, 5500, 4170, 280, -629, 1100, 7.00, 2.60, -9.00, -18.00, "audited", "Spandana Q3FY26 - loan book ₹3,079 Cr; 9M net loss ₹629.52 Cr per BSE filing"),
    ("Fusion Micro Finance", "FY2026-Q3", 7500, 10000, 2870, 720, -120, 680, 9.50, 10.00, -1.50, -5.40, "audited", "Fusion Micro Finance Q3FY26 - Q3 PAT ₹14.05 Cr (turnaround); Q3 NII ₹236.51 Cr"),
    ("Five-Star Business Finance", "FY2026-Q3", 12964, 15800, 6800, 2000, 820, 170, 1.75, 3.18, 8.70, 20.00, "audited", "Five-Star Q3FY26 - loan book ₹12,964 Cr; Q3 PAT ₹277 Cr; GNPA 3.18% (up from 0.87%)"),
    ("Home First Finance", "FY2026-Q3", 14925, 16800, 3600, 1080, 420, 40, 0.38, 1.90, 4.00, 13.70, "audited", "Home First Finance Q3FY26 - AUM ₹14,925 Cr (+25% YoY); Q3 PAT ₹140.2 Cr; GNPA 1.9%"),
    ("Aavas Financiers", "FY2026-Q3", 22204, 26000, 5100, 1141, 473, 29, 0.18, 1.19, 2.60, 13.00, "audited", "Aavas Financiers Q3FY26 - 9M PAT ₹473 Cr; 9M NII ₹1,141 Cr per published results"),
    ("Aptus Value Housing Finance", "FY2026-Q3", 14900, 17000, 4900, 1140, 690, 12, 0.11, 1.03, 7.90, 20.20, "audited", "Aptus Q3FY26 - AUM +26% YoY; Q3 PAT ₹236 Cr; ROA 7.9%, ROE 20.2% per results"),
    ("India Shelter Finance", "FY2026-Q3", 10365, 11900, 3700, 900, 360, 32, 0.42, 1.50, 5.80, 17.10, "audited", "India Shelter Q3FY26 - AUM ₹10,365 Cr (+31% YoY); Q3 PAT ₹128 Cr; ROA 5.8%"),
    ("Satin Creditcare Network", "FY2026-Q3", 8500, 11000, 2500, 1700, 140, 560, 7.50, 8.80, 1.80, 7.50, "audited", "Satin Creditcare Q3FY26 - Q3 PAT ₹71.91 Cr (+404% YoY); revenue ₹746.79 Cr"),
    ("MAS Financial Services", "FY2026-Q3", 14641, 18200, 3200, 1280, 267, 60, 0.55, 2.55, 2.10, 11.50, "audited", "MAS Financial Q3FY26 - AUM ₹14,641 Cr (+18% YoY); 9M PAT ₹267 Cr; GNPA 2.55%"),
    ("Repco Home Finance", "FY2026-Q3", 17000, 21500, 4300, 900, 345, 80, 0.63, 3.40, 2.30, 11.00, "audited", "Repco Home Finance Q3FY26 - Q3 PAT ₹115.44 Cr (+2% YoY); disbursements +40% YoY"),
    ("SK Finance", "FY2026-Q3", 15049, 19000, 3785, 1980, 265, 75, 0.67, 1.86, 2.00, 9.70, "audited", "SK Finance Q3FY26 - AUM ₹15,049 Cr (+23% YoY); Q3 PAT ₹88.37 Cr; net worth ₹3,785 Cr"),
    ("Ugro Capital", "FY2026-Q3", 15454, 18500, 2700, 1250, 130, 112, 1.00, 2.20, 1.00, 7.00, "audited", "Ugro Capital Q3FY26 - AUM ₹15,454 Cr (+40% YoY); Q3 PAT ₹46.3 Cr (+23%); GNPA 2.2%"),
    ("Muthoot Microfin", "FY2026-Q3", 10000, 13000, 2600, 1500, 50, 700, 7.00, 4.40, 0.50, 2.60, "audited", "Muthoot Microfin Q3FY26 - Q3 PAT surged 1544%; GNPA 4.40% (improved from 4.61% in Q2)"),
    # ── KreditBee ─────────────────────────────────────────────────────────────
    # FY2021 & FY2022: ICRA rating report Oct-2022 citing IndAS standalone audited financials.
    # total_assets = "Total Managed Assets" per ICRA (includes off-balance-sheet co-lending);
    # NII and credit losses not separately disclosed in that report.
    ("KreditBee", "FY2021",   652,  1091,  538, None,  28, None,  None, 7.30, 2.57,  5.20, "unverified", "KreditBee FY21 - ICRA Oct-2022 rating report (IndAS standalone). Managed portfolio ₹652 Cr; PAT ₹28 Cr; GNPA 7.3%. Total assets = managed assets incl. off-book"),
    ("KreditBee", "FY2022",  1162,  1539,  607, None,  29, None,  None, 2.90, 2.21,  5.07, "unverified", "KreditBee FY22 - ICRA Oct-2022 rating report (IndAS standalone). Managed portfolio ₹1,162 Cr; PAT ₹29 Cr; GNPA 2.9%. Total assets = managed assets incl. off-book"),
    # FY2023 & FY2024: BSE Annual Report FY2024 standalone audited Ind AS financials.
    # Source: bseindia.com/xml-data/corpfiling/AttachHis//90d9d6b0-c206-4454-8780-c3f70220053c.pdf
    # NII = Interest Income minus Finance Costs. Credit losses FY24 include ₹47 Cr DLG provision.
    ("KreditBee", "FY2023",  2417,  2927, 1591,  313,  65,  249, 10.30, 2.29, 2.91,  5.91, "audited", "KreditBee FY23 actual - BSE Annual Report FY24 (KrazyBee Services Ltd standalone). Loan book ₹2,417 Cr; PAT ₹65 Cr; NII ₹313 Cr; Impairment ₹249 Cr; GNPA 2.29%"),
    ("KreditBee", "FY2024",  4824,  5041, 2050,  991, 200,  432,  8.96, 2.29, 5.02, 10.99, "audited", "KreditBee FY24 actual - BSE Annual Report FY24 (KrazyBee Services Ltd standalone). Loan book ₹4,824 Cr; PAT ₹200 Cr; NII ₹991 Cr; Impairment ₹432 Cr; GNPA 2.29%"),
    ("KreditBee", "FY2025", 5649, 6250, 2347, 1214, 221, 762, 13.49, 2.83, 3.94, 9.44, "audited", "KreditBee FY25 actual - BSE filing (KrazyBee Services Ltd). Loan book ₹5,649 Cr; PAT ₹221 Cr; NII ₹1,214 Cr; Impairment ₹762 Cr; GNPA 2.83%"),
    ("KreditBee", "FY2026-Q3", 8448, 9281, 2707, 978, 341, 612, 7.25, 1.79, 6.45, 17.96, "audited", "KreditBee 9MFY26 actual - BSE filing Feb-2026. Loan book ₹8,448 Cr; 9M PAT ₹341 Cr (reported, incl. ~₹152 Cr one-times); 9M NII ₹978 Cr; 9M Impairment ₹612 Cr; GNPA 1.79%. One-time adj applied in app.py."),
    # ── Fibe (EarlySalary Services Pvt Ltd) ──────────────────────────────────
    # NBFC entity: EarlySalary Services Pvt Ltd (CIN U67120PN1994PTC184868), Middle Layer.
    # Brand: Fibe. Parent: Social Worth Technologies Pvt Ltd. Unlisted, no BSE filings.
    # Source: CareEdge rating press releases (Feb-2023, Oct-2023, Nov-2024, Nov-2025) and
    # Acuite rating rationale (Oct-2025), both based on ESPL audited/provisional standalone
    # financials submitted by the company. FY2025 figures are provisional/unaudited.
    # NII not disclosed standalone; credit losses not available in absolute standalone terms.
    # GNPA excludes written-off accounts (GNPA incl. write-offs: FY24 8.56%, FY25 10.12%).
    ("Fibe", "FY2022",  1019,   518,  None, None,    2.89, None, None, None,  0.43,  None, "audited",   "Fibe (ESPL standalone) FY22 audited. AUM ₹1,019 Cr; Total assets ₹517.77 Cr; PAT ₹2.89 Cr; ROA 0.43%. Source: CareEdge Feb-2023 rating rationale."),
    ("Fibe", "FY2023",  1963,  1338,  None, None,  -10.83, None, None, 3.50, -1.20,  None, "audited",   "Fibe (ESPL standalone) FY23 audited. AUM ₹1,963 Cr; Total assets ₹1,337.63 Cr; PAT -₹10.83 Cr (loss); GNPA 3.50%; ROA -1.20%. Source: CareEdge Oct-2023 rating rationale."),
    ("Fibe", "FY2024",  4064,  2259,   739, None,   55.34, None, None, 2.67,  3.09, 10.33, "audited",   "Fibe (ESPL standalone) FY24 audited. AUM ₹4,064 Cr; Total assets ₹2,258.80 Cr; Net worth ₹739.38 Cr; PAT ₹55.34 Cr; GNPA 2.67%; ROA 3.09%; ROE 10.33%. Source: Acuite Oct-2025 rating rationale."),
    ("Fibe", "FY2025",  5287,  3280,   994, None,  100.19, None, None, 3.07,  3.62, 11.56, "estimated", "Fibe (ESPL standalone) FY25 provisional. AUM ₹5,287 Cr; Total assets ₹3,279.89 Cr; Net worth ₹994.28 Cr; PAT ₹100.19 Cr; GNPA 3.07%; ROA 3.62%; ROE 11.56%. Source: CareEdge Nov-2025 & Acuite Oct-2025 (provisional/unaudited)."),
    # ── Kissht (OnEMI Technology Solutions Ltd / Si Creva Capital Services Pvt Ltd) ──
    # Source: DRHP filed with SEBI, Aug 18 2025. Restated consolidated financials.
    # AUM = On-book + Off-book. Total Assets = consolidated balance sheet.
    # NII proxy = Revenue from operations (interest + fee income).
    # Credit losses = Impairment on financial instruments (P&L line).
    # Credit loss rate = Impairment / average on-book loan book (est.).
    # GNPA = Gross Stage 3 on-book loans / total gross on-book loans.
    ("Kissht", "FY2023", 1268, 1275,  566,  984,  28, 299, 23.57, 0.05,  3.25,  6.93, "DRHP",   "Kissht DRHP Aug-2025 (SEBI). Restated consolidated FY23. AUM ₹1,268 Cr (on+off book); Total assets ₹1,275 Cr; Equity ₹566 Cr; Revenue ₹984 Cr; PAT ₹28 Cr; Impairment ₹299 Cr; GNPA 0.05%; ROA 3.25%; ROE 6.93%."),
    ("Kissht", "FY2024", 2604, 1797,  805, 1674, 197, 621, 23.84, 0.79, 12.85, 28.78, "DRHP",   "Kissht DRHP Aug-2025 (SEBI). Restated consolidated FY24. AUM ₹2,604 Cr; Total assets ₹1,797 Cr; Equity ₹805 Cr; Revenue ₹1,674 Cr; PAT ₹197 Cr; Impairment ₹621 Cr; GNPA 0.79%; ROA 12.85%; ROE 28.78%."),
    ("Kissht", "FY2025", 4087, 2701, 1006, 1337, 161, 327,  7.99, 2.89,  7.14, 17.74, "DRHP",   "Kissht DRHP Aug-2025 (SEBI). Restated consolidated FY25. AUM ₹4,087 Cr; Total assets ₹2,701 Cr; Equity ₹1,006 Cr; Revenue ₹1,337 Cr; PAT ₹161 Cr; Impairment ₹327 Cr; GNPA 2.89%; ROA 7.14%; ROE 17.74%."),
    # ── Moneyview (Moneyview Limited / Whizdm Finance Pvt Ltd) ───────────────
    # Source: Moneyview Limited DRHP filed Mar-2026 with SEBI. Restated consolidated financials.
    # Business model: Primarily off-book DLG lending platform + direct NBFC (Whizdm Finance / WFPL) lending.
    # NII field = revenue from operations (fees + interest income combined) — hybrid model.
    # Loan book = managed AUM (total DLG + on-book portfolio; reflects true platform scale).
    # Total assets / equity = consolidated Moneyview balance sheet (per DRHP).
    # Credit loss rate = per DRHP disclosure (total managed portfolio credit losses / managed AUM).
    # Includes off-book DLG losses not captured in WFPL standalone impairment.
    # GNPA = Gross Stage 3 / NPA on WFPL's on-book portfolio (CARE Ratings; DRHP for 9MFY26).
    # ROA = annualized PAT / avg managed AUM. ROE per DRHP (avg equity basis).
    # For 9MFY26: PAT annualized from 9M before exceptional items (₹245 Cr × 4/3 = ₹327 Cr).
    # 9MFY26 credit loss rate: annualized on-book impairment ₹724 Cr×4/3=₹965 Cr / avg managed AUM ₹18,265 Cr = 5.29%.
    ("Moneyview", "FY2023",   7644, 1724, 1314,  577, 163, None,  7.45, None,  2.13, 12.40, "DRHP",
     "Moneyview DRHP Mar-2026. FY23: managed AUM ₹7,644 Cr; total assets ₹1,724 Cr; equity ₹1,314 Cr; revenue ₹577 Cr; PAT ₹163 Cr; credit loss rate 7.45% per DRHP. ROA = PAT/ending managed AUM. ROE = PAT/ending equity."),
    ("Moneyview", "FY2024",  12885, 3520, 1607, 1342, 171, None,  7.95, 0.90,  1.67, 11.72, "DRHP",
     "Moneyview DRHP Mar-2026. FY24: managed AUM ₹12,885 Cr; total assets ₹3,520 Cr; equity ₹1,607 Cr; revenue ₹1,342 Cr; PAT ₹171 Cr; credit loss rate 7.95% per DRHP; GNPA 0.90% (WFPL Gross Stage 3). ROA = PAT/avg managed AUM (7644+12885)/2."),
    ("Moneyview", "FY2025",  16715, 5632, 1919, 2339, 240,  346,  7.07, 1.90,  1.62, 13.63, "DRHP",
     "Moneyview DRHP Mar-2026. FY25: managed AUM ₹16,715 Cr; total assets ₹5,632 Cr; equity ₹1,919 Cr; revenue ₹2,339 Cr; PAT ₹240 Cr; WFPL impairment ₹346 Cr; credit loss rate 7.07% per DRHP (total managed portfolio losses/AUM); GNPA 1.90%. ROA = PAT/avg managed AUM (12885+16715)/2."),
    ("Moneyview", "FY2026-Q3", 19815, 7719, 2169, 2373, 245,  724,  None, 2.53,  1.79, 15.98, "DRHP",
     "Moneyview DRHP Mar-2026. 9MFY26 (Apr-Dec 2025): managed AUM ₹19,815 Cr; total assets ₹7,719 Cr; equity ₹2,169 Cr; revenue ₹2,373 Cr; PAT ₹245 Cr before exceptional items (reported ₹210 Cr); WFPL impairment ₹724 Cr (9M); GNPA 2.53%. ROA = ann. PAT ₹327 Cr/avg managed AUM ₹18,265 Cr = 1.79%. 9MFY26 credit loss rate computed in annualise_9m as ann. ₹965 Cr/₹18,265 Cr = 5.29%. ROE per DRHP avg equity."),
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
