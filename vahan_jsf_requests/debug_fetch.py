import requests, os
from bs4 import BeautifulSoup

BASE_URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

s = requests.Session()
r = s.get(BASE_URL, headers=HEADERS, timeout=40)
print('Status:', r.status_code)
print('Length:', len(r.text))
open(os.path.join(os.path.dirname(__file__), 'initial.html'), 'w', encoding='utf-8').write(r.text)

soup = BeautifulSoup(r.text, 'lxml')
print('Form IDs:')
for f in soup.find_all('form'):
    print(' -', f.get('id'))
print('Select elements:')
for sel in soup.find_all('select'):
    print(sel.get('id'))
    for opt in sel.find_all('option')[:5]:
        print('   opt', opt.get('value'), opt.text.strip()[:50])
    print('   ... total options', len(sel.find_all('option')))

print('Hidden inputs (first 5):')
for hi in soup.find_all('input', type='hidden')[:5]:
    print(hi.get('name'))
