# 6E Gamma Exposure Engine

A manual-run Python tool that reads structured 6E options data from Google Sheets, calculates per-strike gamma exposure (GEX), and writes the results back into Google Sheets.

## Purpose

This project is designed to:

- read call and put option inputs from separate Google Sheets tabs
- validate the workbook structure and input data
- calculate call GEX, put GEX, and net GEX by strike
- generate a summary of total gamma exposure
- write clean output tables back into Google Sheets
- preserve header rows and overwrite only data rows on each run

This is a manual workflow. You update the input tabs, set the current futures price, then run the script.

---

## Formula

### Call GEX
```python
call_gex = gamma * contract_size * open_interest * futures_price * 0.0001
```

### Put GEX
```python
put_gex = gamma * contract_size * open_interest * futures_price * 0.0001 * -1
```

### Net GEX
```python
net_gex = call_gex + put_gex
```

### Confirmed assumptions
- instrument: 6E
- contract size: 125000
- scalar: 0.0001
- calls are positive
- puts are negative

---

## Project Structure

```text
gamma_engine/
├── app.py
├── calculations.py
├── models.py
├── README.md
├── requirements.txt
├── service_account.json
├── settings.py
├── sheets_service.py
└── validators.py
```

---

## Google Sheets Workbook Structure

The Google Sheet must contain these tabs exactly:

1. `Call_Input`
2. `Put_Input`
3. `Config`
4. `Per_Strike_GEX`
5. `Summary`

### 1. `Call_Input`
Headers in row 1:

```text
volatility	strike	call_price	delta	gamma	vega	theta	open_interest
```

### 2. `Put_Input`
Headers in row 1:

```text
volatility	strike	put_price	delta	gamma	vega	theta	open_interest
```

### 3. `Config`
Headers in row 1:

```text
key	value
```

Required rows:

```text
futures_price	1.1803
contract_size	125000
```

### 4. `Per_Strike_GEX`
Headers in row 1:

```text
timestamp	strike	call_iv	call_gamma	call_oi	call_gex	put_iv	put_gamma	put_oi	put_gex	net_gex	futures_price
```

### 5. `Summary`
Headers in row 1:

```text
timestamp	futures_price	total_call_gex	total_put_gex	net_total_gex	max_positive_strike	max_negative_strike	largest_absolute_gex_strike
```

---

## Setup

## 1. Create the project folder
Create a folder such as:

```text
gamma_engine
```

## 2. Place Google credentials in the folder
Put your Google service account JSON file in the project folder and name it exactly:

```text
service_account.json
```

## 3. Install Python dependencies
From inside the project folder, run:

```bash
pip install -r requirements.txt
```

or:

```bash
python3 -m pip install -r requirements.txt
```

## 4. Confirm `settings.py`
`settings.py` must contain the correct Google Sheet ID and exact worksheet names.

---

## Running the tool

From inside the project folder, run:

```bash
python3 app.py
```

The script will:

1. connect to Google Sheets
2. validate required tabs
3. validate required headers
4. validate config values
5. parse input rows
6. calculate per-strike GEX
7. calculate summary metrics
8. overwrite data rows in:
   - `Per_Strike_GEX`
   - `Summary`

---

## Daily Workflow

1. Update `Call_Input`
2. Update `Put_Input`
3. Update `futures_price` in `Config`
4. Run:

```bash
python3 app.py
```

5. Review:
- `Per_Strike_GEX`
- `Summary`

---

## Output Definitions

## `Per_Strike_GEX`
Each row represents one strike.

Columns:

- `timestamp`: run timestamp
- `strike`: strike price
- `call_iv`: call volatility
- `call_gamma`: call gamma
- `call_oi`: call open interest
- `call_gex`: positive call gamma exposure
- `put_iv`: put volatility
- `put_gamma`: put gamma
- `put_oi`: put open interest
- `put_gex`: negative put gamma exposure
- `net_gex`: `call_gex + put_gex`
- `futures_price`: current 6E futures price from `Config`

## `Summary`
One row per run.

Columns:

- `timestamp`
- `futures_price`
- `total_call_gex`
- `total_put_gex`
- `net_total_gex`
- `max_positive_strike`
- `max_negative_strike`
- `largest_absolute_gex_strike`

---

## Validation Rules

The script will stop with an error if:

- a required tab is missing
- a required header is missing or out of order
- `futures_price` is missing or invalid
- `contract_size` is missing or not `125000`
- a required numeric field is blank or invalid
- duplicate strikes exist on the same side
- negative gamma is found
- negative open interest is found

The script will continue but warn if:

- a strike exists only in `Call_Input`
- a strike exists only in `Put_Input`

In later calculation stages, the missing side is treated as zero.

---

## Formatting Notes

Google Sheets may visually round numbers if the cell format is too coarse.

Recommended formatting for input tabs:

- `gamma`: `0.0000`
- `strike`: `0.0000`
- `call_price` / `put_price`: `0.0000`
- `delta`: `0.00`
- `vega`: `0.0000`
- `theta`: `0.0000`
- `open_interest`: integer

Recommended formatting for outputs:

- GEX columns: `#,##0`
- strike / futures price: `0.0000`

---

## Common Issues

### 1. Credentials file not found
Make sure the file exists in the project folder and is named exactly:

```text
service_account.json
```

### 2. Google Sheets access error
Make sure the Google Sheet has been shared with the service account email from the JSON credentials file.

### 3. Header mismatch error
Check that the tab names and row 1 headers exactly match the documented structure.

### 4. Config value error
Check that:
- `futures_price` is numeric and greater than 0
- `contract_size` is exactly `125000`

### 5. Rounded display in Google Sheets
This is usually a formatting issue, not a data-loss issue. Adjust the column number format to show more decimal places.

---

## Current Status

Implemented:

- Google Sheets authentication
- workbook validation
- input parsing
- call/put merge by strike
- GEX calculations
- summary calculations
- output writing to Google Sheets
- output formatting

Not yet implemented:

- historical summary logging
- chart generation
- automated scheduling
- raw QuickStrike paste parsing
- advanced analytics

---

## Notes

This tool is intentionally designed as a clean manual-run workflow:
- update inputs
- run once
- review outputs

That keeps the process transparent and easy to audit.
