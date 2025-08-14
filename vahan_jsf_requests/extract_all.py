import os
import re
import csv
import logging
from typing import List, Tuple, Optional
from bs4 import BeautifulSoup

RAW_DIR = os.path.join(os.path.dirname(__file__), 'raw_responses')
OUT_AGG = os.path.join(RAW_DIR, 'all_data.csv')
LOG_FILE = os.path.join(os.path.dirname(__file__), 'errors.log')

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

TARGET_UPDATE_IDS = {"combTablePnl","groupingTable"}


def read_fragments(path: str) -> List[str]:
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    frags: List[str] = []
    if '<partial-response' in text:
        try:
            xml = BeautifulSoup(text, 'xml')
            for upd in xml.find_all('update'):
                uid = upd.get('id') or ''
                if any(t in uid for t in TARGET_UPDATE_IDS):
                    frags.append(upd.text)
            if not frags:  # fallback all updates
                frags = [u.text for u in xml.find_all('update')]
        except Exception as e:
            logging.error(f"XML parse failed {path}: {e}")
            frags = [text]
    else:
        frags = [text]
    return frags


def clean_cell(txt: str) -> str:
    txt = txt.replace('\xa0', ' ').strip()
    # Remove multiple spaces and commas in numbers (keep internal spaces in labels)
    if re.fullmatch(r'[0-9,]+', txt):
        return txt.replace(',', '')
    return re.sub(r'\s+', ' ', txt)


def parse_table(html: str) -> Tuple[List[str], List[List[str]]]:
    """Robust parser for PrimeFaces scrollable DataTable.
    Handles separated header/body tables and infers Maker Month Wise headers.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Locate body tbody first (most reliable for data)
    tbody = soup.find('tbody', id=re.compile(r'_data$'))
    data_rows: List[List[str]] = []
    if tbody:
        for tr in tbody.find_all('tr', attrs={'role': 'row'}):
            cells = tr.find_all(['td','th'])
            if not cells:
                continue
            row = [clean_cell(c.get_text()) for c in cells]
            if any(cell.strip() for cell in row):
                data_rows.append(row)
    else:
        # Fallback: any tbody
        generic_tbody = soup.find('tbody')
        if generic_tbody:
            for tr in generic_tbody.find_all('tr'):
                cells = tr.find_all(['td','th'])
                row = [clean_cell(c.get_text()) for c in cells]
                if any(cell.strip() for cell in row):
                    data_rows.append(row)

    # Collect header cells
    headers: List[str] = []
    thead = soup.find('thead', id=re.compile(r'_head$')) or soup.find('thead')
    if thead:
        # Prefer explicit role=columnheader spans
        role_headers = thead.find_all(['th','td'], attrs={'role': 'columnheader'})
        if role_headers:
            headers = [clean_cell(h.get_text()) for h in role_headers]
        if not headers:
            # Flatten last header row with maximum cells
            rows = thead.find_all('tr')
            if rows:
                max_row = max(rows, key=lambda r: len(r.find_all(['th','td'])))
                headers = [clean_cell(th.get_text()) for th in max_row.find_all(['th','td'])]

    # Infer Maker Month Wise headers if blank/empty
    if (not headers or all(h == '' for h in headers)) and data_rows:
        first = data_rows[0]
        if len(first) >= 5 and re.fullmatch(r'\d+', first[0]):
            maker_like = not re.fullmatch(r'[0-9,]+', first[1])
            if maker_like:
                # Usually: S No, Maker, 12 months, TOTAL => 15 columns
                if len(first) >= 14:
                    headers = ['S No', 'Maker'] + MONTHS + ['TOTAL']
                else:
                    # Partial months - assume last is TOTAL
                    numeric_tail = len(first) - 2
                    if numeric_tail >= 2:
                        months_so_far = numeric_tail - 1
                        headers = ['S No', 'Maker'] + MONTHS[:months_so_far] + ['TOTAL']
                    else:
                        headers = ['S No', 'Maker'] + [f'M{i+1}' for i in range(numeric_tail)]

    # Normalize sizes
    if headers:
        width = len(headers)
        for r in data_rows:
            if len(r) < width:
                r.extend([''] * (width - len(r)))
            elif len(r) > width:
                del r[width:]
    else:
        width = max((len(r) for r in data_rows), default=0)
        headers = [f'col_{i}' for i in range(width)]
        for r in data_rows:
            if len(r) < width:
                r.extend([''] * (width - len(r)))
    return headers, data_rows


def detect_monthwise(head_rows) -> List[str]:
    if len(head_rows) < 2:
        return []
    all_text = [clean_cell(th.get_text()).upper() for r in head_rows for th in r.find_all(['th','td'])]
    month_hits = [t for t in all_text if t in MONTHS]
    if len(month_hits) >= 5:  # heuristic
        ordered_months = [m for m in MONTHS if m in month_hits]
        # Determine presence of Maker / S No
        return ['S No','Maker'] + ordered_months + ['TOTAL']
    return []


def derive_output_name(html_file: str) -> str:
    base = os.path.splitext(os.path.basename(html_file))[0]
    return base + '.csv'


def process_file(path: str) -> List[Tuple[str,List[str],List[List[str]]]]:
    frags = read_fragments(path)
    outputs = []
    for idx, frag in enumerate(frags):
        headers, rows = parse_table(frag)
        if rows:
            tag = '' if len(frags) == 1 else f'_{idx+1}'
            outputs.append((derive_output_name(path).replace('.csv', f'{tag}.csv'), headers, rows))
    return outputs


def write_csv(path: str, headers: List[str], rows: List[List[str]]):
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)


def main():
    if not os.path.isdir(RAW_DIR):
        print('Raw responses directory missing')
        return
    html_files = [os.path.join(RAW_DIR, f) for f in os.listdir(RAW_DIR) if f.lower().endswith('.html')]
    aggregated_rows: List[List[str]] = []
    aggregated_headers: Optional[List[str]] = None
    for fp in html_files:
        try:
            table_sets = process_file(fp)
            for out_name, headers, rows in table_sets:
                out_path = os.path.join(RAW_DIR, out_name)
                write_csv(out_path, headers, rows)
                # aggregate
                if not aggregated_headers:
                    aggregated_headers = ['SourceFile'] + headers
                for r in rows:
                    aggregated_rows.append([os.path.basename(out_name)] + r)
                print(f'Parsed {fp} -> {out_name} ({len(rows)} rows)')
        except Exception as e:
            logging.error(f'Failed processing {fp}: {e}')
    if aggregated_headers:
        write_csv(OUT_AGG, aggregated_headers, aggregated_rows)
        print(f'Wrote aggregated {OUT_AGG} ({len(aggregated_rows)} rows)')
    else:
        print('No tables extracted.')

if __name__ == '__main__':
    main()
