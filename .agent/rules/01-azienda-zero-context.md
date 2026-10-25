---
trigger: always_on
description: Contesto Azienda Zero (Regione del Veneto) e regole obbligatorie di pricing in USD mensile per tabelle VM, OS e licenze MS SQL Server
---

# Regole Dominio Azienda Zero (Regione del Veneto) & Pricing Standard

## 1. Contesto Azienda Zero (Regione del Veneto)
- **Ente**: **Azienda Zero** (Passaggio Luigi Gaudenzio 1, Padova) — Ente di governance della Sanità della Regione del Veneto, Centrale Acquisti Regionale (**CRAV**) e coordinamento ICT per tutte le **9 ULSS Venete** (`ULSS 1 Dolomiti`, `ULSS 2 Marca Trevigiana`, `ULSS 3 Serenissima`, `ULSS 4 Veneto Orientale`, `ULSS 6 Euganea`, `ULSS 7 Pedemontana`, `ULSS 8 Berica`, `ULSS 9 Scaligera`) e le Aziende Ospedaliere (`AO Padova`, `AOUI Verona`, `IOV - Istituto Oncologico Veneto`).
- **Progetto GCP Demo**: `rootprj-377111` (Location `global` per Gemini Enterprise App / Discovery Engine; `us-central1` per Vertex AI Agent Engine / ADK).
- **Ambiti Applicativi della Demo**:
  1. **Gare CRAV & PNRR Sanità Digitale** (Capitolati Telemedicina, FSE 2.0, COT - Centrali Operative Territoriali, integrazione CTI `116117`).
  2. **PDTA Regionali (Percorsi Diagnostico-Terapeutici Assistenziali)** e monitoraggio SLA tempi di attesa sulle 9 ULSS.
  3. **Compliance Privacy GDPR, CDPA & Qualifica ACN** (inapplicabilità clausola USA HIPAA art. 3.3 viii ToS ai dati sanitari europei sotto GDPR, configurazione **Data Region = Europe** per storage + processing, distinzione ACN QC2 vs QC3).

## 2. Regola Tassativa di Pricing (`$ USD / Mese`)
Quando produci stime economiche, tabelle di sizing o output di tool di calcolo costi:
- Mantieni tutti i prezzi **sempre in dollari (`$ USD`) su base mensile (`Prezzo Mese`)**.
- Includi **sempre** le colonne dedicate:
  - **Prezzo Mese List (`$/mo`)**
  - **Prezzo Mese 1Y CUD (`$/mo`)**
  - **Prezzo Mese 3Y CUD (`$/mo`)**
- Per le **VM con sistema operativo**, mostra sempre il **Costo Mese con Sistema Operativo (`OS $/mo` e `Totale con OS $/mo`)** fornendo il costo licenza OS (`Windows Server`, `RHEL`, ecc.) **solo per gli OS supportati** (escludendo il costo licenza per gli OS fuori supporto / EOL).
- Per i database **MS SQL Server**, fornisci il costo licenza in una **colonna separata (`COSTO MESE LICENZA MSSQL $/MO`)** **solo per le istanze supportate su OS supportato** (non fornire il costo licenza DB se il DB è fuori supporto o se l'OS sottostante è fuori supporto).
