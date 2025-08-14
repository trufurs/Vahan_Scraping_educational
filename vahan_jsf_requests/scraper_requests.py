import os
import re
import time
import logging
from typing import Dict, List, Tuple, Optional
import requests
from bs4 import BeautifulSoup
import csv
import sys
import math
import argparse

BASE_URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": BASE_URL,
    "Origin": "https://vahan.parivahan.gov.in"
}

AJAX_HEADERS = {
    **HEADERS,
    "Faces-Request": "partial/ajax",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}

RAW_DIR = os.path.join(os.path.dirname(__file__), "raw_responses")
LOG_FILE = os.path.join(os.path.dirname(__file__), "errors.log")
os.makedirs(RAW_DIR, exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def get_view_state(soup: BeautifulSoup) -> str:
    """Extract current JSF ViewState token."""
    vs = soup.find('input', {'name': 'javax.faces.ViewState'})
    if not vs:
        raise RuntimeError("ViewState input not found")
    return vs.get('value')


def get_dropdown_options(soup: BeautifulSoup, select_id: str) -> List[Tuple[str, str]]:
    """Return list of (value,label) for given select id (plain <select> only)."""
    sel = soup.find('select', id=select_id)
    out: List[Tuple[str, str]] = []
    if not sel:
        return out
    for opt in sel.find_all('option'):
        val = opt.get('value')
        if val is None or val == '':
            continue
        out.append((val, opt.text.strip()))
    return out


def send_ajax_request(session: requests.Session,
                      form_id: str,
                      view_state: str,
                      source: str,
                      execute: str,
                      render: str,
                      extra_fields: Dict[str, str],
                      retries: int = 3) -> Tuple[str, BeautifulSoup]:
    """Send a PrimeFaces/JSF partial ajax POST and return (new_view_state, xml_soup)."""
    data = {
        'javax.faces.partial.ajax': 'true',
        'javax.faces.source': source,
        'javax.faces.partial.execute': execute,
        'javax.faces.partial.render': render,
        form_id: form_id,
        'javax.faces.ViewState': view_state,
    }
    data.update(extra_fields)

    for attempt in range(1, retries + 1):
        try:
            r = session.post(BASE_URL, headers=AJAX_HEADERS, data=data, timeout=40)
            if r.status_code == 200:
                xml = BeautifulSoup(r.text, 'xml')
                vs_update = xml.find('update', id=re.compile(r'ViewState$'))
                if vs_update and vs_update.text:
                    view_state = vs_update.text
                return view_state, xml
            logging.error(f"Attempt {attempt} status {r.status_code} for source={source}")
        except Exception as e:
            logging.error(f"Attempt {attempt} exception source={source}: {e}")
        time.sleep(1.2 * attempt)
    raise RuntimeError(f"Failed ajax after {retries} attempts for source {source}")


def save_html(vehicle: str, manufacturer: str, year: str, html_fragment: str):
    fname = f"{vehicle}_{manufacturer}_{year}.html".replace(' ', '_')
    path = os.path.join(RAW_DIR, fname)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html_fragment)
    logging.info(f"Saved {path}")


def parse_datatable_fragment(fragment_html: str) -> Tuple[List[str], List[List[str]]]:
    """Parse PrimeFaces scrollable DataTable fragment.
    - Header table (scrollable header) separate from body table.
    - Body tbody id typically ends with _data.
    - Infer month-wise headers when blank.
    """
    soup = BeautifulSoup(fragment_html, 'html.parser')
    # Find header thead
    thead = soup.find('thead', id=re.compile(r'_head$')) or soup.find('thead')
    headers: List[str] = []
    if thead:
        head_rows = thead.find_all('tr')
        if head_rows:
            # choose row with maximum cells
            max_row = max(head_rows, key=lambda r: len(r.find_all(['th','td'])))
            headers = [clean_cell_text(th.get_text()) for th in max_row.find_all(['th','td'])]
    # Gather body rows
    tbody = soup.find('tbody', id=re.compile(r'_data$')) or soup.find('tbody')
    rows: List[List[str]] = []
    if tbody:
        for tr in tbody.find_all('tr'):
            cells = tr.find_all(['td','th'])
            if not cells:
                continue
            row = [clean_cell_text(c.get_text()) for c in cells]
            if any(val.strip() for val in row):
                rows.append(row)
    # Infer Maker Month Wise header pattern if blank headers
    if (not headers or all(h == '' for h in headers)) and rows:
        first = rows[0]
        if len(first) >= 5 and re.fullmatch(r'\d+', first[0]) and not re.fullmatch(r'[0-9,]+', first[1]):
            # Typically S No, Maker, 12 months, TOTAL
            if len(first) >= 15:
                headers = ['S No','Maker','JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC','TOTAL']
            else:
                # Partial months (last is total)
                tail = len(first) - 2
                if tail >= 2:
                    months = tail - 1
                    month_names = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'][:months]
                    headers = ['S No','Maker'] + month_names + ['TOTAL']
    # Normalize
    max_cols = max((len(r) for r in rows), default=0)
    if headers and len(headers) < max_cols:
        headers.extend([f"col_{i}" for i in range(len(headers), max_cols)])
    elif not headers and max_cols:
        headers = [f"col_{i}" for i in range(max_cols)]
    return headers, rows


def clean_cell_text(txt: str) -> str:
    return ' '.join(txt.replace('\xa0', ' ').split())


def save_csv(base_name: str, year: str, headers: List[str], rows: List[List[str]]):
    if not headers or not rows:
        return
    fname = f"{base_name}_{year}.csv".replace(' ', '_')
    path = os.path.join(RAW_DIR, fname)
    try:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        logging.info(f"Saved {path}")
    except Exception as e:
        logging.error(f"CSV save failed {path}: {e}")


class VahanAjaxScraper:
    """Scrape the dashboard by iterating Y-Axis, X-Axis and Year (Calendar) and saving HTML + CSV."""

    def __init__(self):
        self.session = requests.Session()
        self.view_state: Optional[str] = None
        self.form_id: Optional[str] = None

    # ---------------- Core helpers -----------------
    def bootstrap(self) -> BeautifulSoup:
        r = self.session.get(BASE_URL, headers=HEADERS, timeout=40)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        self.view_state = get_view_state(soup)
        # pick the main form (contains ViewState)
        form = soup.find('form')
        if not form or not form.get('id'):
            raise RuntimeError('Main form id not found')
        self.form_id = form.get('id')
        return soup

    def run(self):
        try:
            soup = self.bootstrap()
        except Exception as e:
            logging.error(f"Initial bootstrap failed: {e}")
            return

        # Collect initial axis/year options (may be partially populated)
        yaxis_options = get_dropdown_options(soup, 'yaxisVar_input')
        xaxis_options = get_dropdown_options(soup, 'xaxisVar_input')
        year_options = get_dropdown_options(soup, 'selectedYear_input')

        # Filter & clean
        yaxis_options = [(v,l) for v,l in yaxis_options if v]
        xaxis_options = [(v,l) for v,l in xaxis_options if v]
        year_options = [(v,l) for v,l in year_options if v and 'Select' not in l]

        if not yaxis_options:
            logging.error("No Y-Axis options found (yaxisVar_input). Aborting.")
            return
        if not xaxis_options:
            logging.error("No X-Axis options found (xaxisVar_input). Aborting.")
            return
        if not year_options:
            logging.error("No Year options found (selectedYear_input). Aborting.")
            return

        # Maintain current state values
        current = {
            'j_idt26_input': 'A',              # Value display type: Absolute
            'j_idt34_input': '-1',             # All States
            'selectedRto_input': '-1',         # All RTO
            'selectedYearType_input': 'C',     # Calendar Year
            'yaxisVar_input': None,
            'xaxisVar_input': None,
            'selectedYear_input': None
        }

        def change_select(source_base: str, input_id: str, value: str, render: str):
            current[input_id] = value
            extra = {k.replace(':','%3A'): v for k,v in current.items() if v is not None}
            for k in list(current.keys()):
                extra[k.replace('_input','_focus')] = ''
            self.view_state, _xml = send_ajax_request(
                self.session,
                self.form_id,
                self.view_state,
                source=source_base,
                execute=source_base,
                render=render,
                extra_fields=extra
            )

        def build_html_table(headers: List[str], rows: List[List[str]]) -> str:
            head_html = ''.join(f"<th>{h}</th>" for h in headers)
            body_html = ''.join('<tr>' + ''.join(f"<td>{(c if c is not None else '')}</td>" for c in r) + '</tr>' for r in rows)
            return f"<table id='combinedFull'><thead><tr>{head_html}</tr></thead><tbody>{body_html}</tbody></table>"

        def refresh_and_save(y_label: str, x_label: str, year_label: str):
            extra = {k.replace(':','%3A'): v for k,v in current.items() if v is not None}
            for k in list(current.keys()):
                extra[k.replace('_input','_focus')] = ''
            extra['j_idt66'] = 'j_idt66'
            # PrimeFaces datatable baseline fields
            extra['groupingTable_scrollState'] = '0,0'
            self.view_state, xml = send_ajax_request(
                self.session,
                self.form_id,
                self.view_state,
                source='j_idt66',
                execute='@all',
                render='combTablePnl groupingTable msg',
                extra_fields=extra
            )
            fragment = extract_update_fragment([xml], 'combTablePnl') or extract_update_fragment([xml], 'groupingTable')
            if fragment:
                base = f"{y_label}_{x_label}".replace(' ', '_')
                headers, rows = parse_datatable_fragment(fragment)
                total_rows, page_size = extract_table_pagination_meta(fragment)
                fetched_pages = 1
                if total_rows and page_size and total_rows > len(rows):
                    total_pages = math.ceil(total_rows / page_size)
                    for page_index in range(1, total_pages):
                        try:
                            page_rows = self.fetch_page(page_index, page_size, current)
                            if not page_rows:
                                break
                            rows.extend(page_rows)
                            fetched_pages += 1
                            time.sleep(0.25)
                        except Exception as pe:
                            logging.error(f"Pagination fetch failed page {page_index+1}/{total_pages}: {pe}")
                            break
                elif page_size and page_size > 0:
                    # Fallback: iterate pages until no growth (when rowCount missing)
                    for page_index in range(1, 500):  # safety cap
                        try:
                            page_rows = self.fetch_page(page_index, page_size, current)
                            if not page_rows:
                                break
                            before = len(rows)
                            rows.extend(page_rows)
                            if len(rows) == before:
                                break
                            fetched_pages += 1
                            # Stop early if last page smaller than page_size
                            if len(page_rows) < page_size:
                                break
                            time.sleep(0.25)
                        except Exception as pe:
                            logging.error(f"Fallback pagination failed page {page_index+1}: {pe}")
                            break
                # Save first page raw fragment
                save_html(base, 'NA', year_label, fragment)
                # Save combined HTML synthesized so extract_all can parse all rows
                if headers and rows:
                    combined_html = build_html_table(headers, rows)
                    save_html(base + '_ALLPAGES', 'NA', year_label, combined_html)
                    save_csv(base + '_ALLPAGES', year_label, headers, rows)
                    logging.info(f"Saved combined {len(rows)} rows over {fetched_pages} pages")
            else:
                logging.error(f"No table fragment for {y_label} | {x_label} | {year_label}")

        # ------------- Interactive selection -------------
        def choose(prompt: str, options: List[Tuple[str,str]]) -> Tuple[str,str]:
            print(f"\n{prompt}:")
            for idx, (_val, _lab) in enumerate(options, start=1):
                print(f"  {idx}. {_lab}  (value={_val})")
            while True:
                sel = input(f"Enter number (1-{len(options)}): ").strip()
                if not sel.isdigit():
                    print("Please enter a number.")
                    continue
                i = int(sel)
                if 1 <= i <= len(options):
                    return options[i-1]
                print("Out of range.")

        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument('--y', dest='y_label')
        parser.add_argument('--x', dest='x_label')
        parser.add_argument('--year', dest='year_label')
        args, _ = parser.parse_known_args()

        def match_option(label: Optional[str], opts: List[Tuple[str,str]]):
            if not label:
                return None
            label_norm = label.strip().lower()
            for val, lab in opts:
                if lab.strip().lower() == label_norm:
                    return (val, lab)
            # partial contains
            for val, lab in opts:
                if label_norm in lab.strip().lower():
                    return (val, lab)
            return None

        auto = False
        if args.y_label and args.x_label and args.year_label:
            y_sel = match_option(args.y_label, yaxis_options)
            x_sel = match_option(args.x_label, xaxis_options)
            yr_sel = match_option(args.year_label, year_options)
            if y_sel and x_sel and yr_sel:
                y_val, y_label = y_sel
                x_val, x_label = x_sel
                year_val, year_label = yr_sel
                auto = True
                change_select('yaxisVar', 'yaxisVar_input', y_val, 'xaxisVar')
                change_select('xaxisVar', 'xaxisVar_input', x_val, 'multipleYear')
                change_select('selectedYear', 'selectedYear_input', year_val, 'selectedYear')
            else:
                print("Provided labels not matched; falling back to interactive mode.")

        if not auto:
            print("Starting interactive selection for Vahan dashboard scrape.")
            print("You will be asked to pick one Y-Axis, one X-Axis and one Year. Only that combination will be fetched.")

            y_val, y_label = choose("Select Y-Axis", yaxis_options)
            change_select('yaxisVar', 'yaxisVar_input', y_val, 'xaxisVar')
            x_val, x_label = choose("Select X-Axis", xaxis_options)
            change_select('xaxisVar', 'xaxisVar_input', x_val, 'multipleYear')
            year_val, year_label = choose("Select Year", year_options)
            change_select('selectedYear', 'selectedYear_input', year_val, 'selectedYear')

        print(f"Fetching table for: Y={y_label} | X={x_label} | Year={year_label} ...")
        try:
            refresh_and_save(y_label, x_label, year_label)
            print("Done. Check raw_responses folder for *_ALLPAGES files for full data.")
        except Exception as e:
            logging.error(f"Refresh failed {y_label} | {x_label} | {year_label}: {e}")
            print(f"Failed to fetch data: {e}")
        logging.info("Completed single combination extraction.")

    def fetch_page(self, page_index: int, page_size: int, current_state: Dict[str,str]):
        """Fetch a specific DataTable page (0-based) and return its rows (without headers)."""
        first = page_index * page_size
        extra = {k.replace(':','%3A'): v for k,v in current_state.items() if v is not None}
        for k in list(current_state.keys()):
            extra[k.replace('_input','_focus')] = ''
        # PrimeFaces DataTable pagination parameters
        extra.update({
            'groupingTable': 'groupingTable',
            'groupingTable_pagination': 'true',
            'groupingTable_first': str(first),
            'groupingTable_rows': str(page_size),
            'groupingTable_skipChildren': 'true',
            'groupingTable_encodeFeature': 'true',
            'groupingTable_scrollState': '0,0'
        })
        self.view_state, xml = send_ajax_request(
            self.session,
            self.form_id,
            self.view_state,
            source='groupingTable',
            execute='groupingTable',
            render='groupingTable',
            extra_fields=extra
        )
        fragment = extract_update_fragment([xml], 'groupingTable')
        if not fragment:
            return []
        # Extract just body rows
        soup = BeautifulSoup(fragment, 'html.parser')
        tbody = soup.find('tbody', id=lambda x: x and x.endswith('_data')) or soup.find('tbody')
        page_rows = []
        if tbody:
            for tr in tbody.find_all('tr'):
                cells = tr.find_all(['td','th'])
                row = [clean_cell_text(c.get_text()) for c in cells]
                if any(v.strip() for v in row):
                    page_rows.append(row)
        return page_rows

def extract_table_pagination_meta(fragment_html: str) -> Tuple[Optional[int], Optional[int]]:
    """Parse the PrimeFaces widget script to get total rowCount and page size."""
    try:
        row_count = None
        page_size = None
        # Look for script containing rowCount and rows
        m = re.search(r'rowCount:\s*(\d+)', fragment_html)
        if m:
            row_count = int(m.group(1))
        m2 = re.search(r'rows:\s*(\d+)', fragment_html)
        if m2:
            page_size = int(m2.group(1))
        return row_count, page_size
    except Exception:
        return None, None


def extract_update_fragment(xml_soups: List[BeautifulSoup], update_id: str) -> Optional[str]:
    for xml in xml_soups:
        if not xml:
            continue
        upd = xml.find('update', {'id': update_id})
        if upd:
            return upd.text
    return None


def get_view_state_from_xml(xml: BeautifulSoup, current: str) -> str:
    vs_update = xml.find('update', id=re.compile(r'ViewState$')) if xml else None
    if vs_update and vs_update.text:
        return vs_update.text
    return current


if __name__ == '__main__':
    scraper = VahanAjaxScraper()
    scraper.run()
