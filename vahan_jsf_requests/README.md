# Vahan Dashboard Requests Scraper

This scraper simulates JSF + PrimeFaces AJAX interactions on the Vahan dashboard without using Selenium.

It:
- Initiates a session and parses initial ViewState and dropdown options.
- Iteratively selects vehicle type (2W,3W,4W) -> manufacturer -> year via JSF partial AJAX POSTs.
- Captures the updated table panel fragment (update id="tablePnl") from each response XML and saves raw HTML under `raw_responses/<vehicle>_<manufacturer>_<year>.html`.
- Retries failed requests up to 3 times and logs errors in `errors.log`.

## Run
```
python scraper_requests.py
```

## Notes
Manufacturers list is dependent on selected vehicle type, so after changing vehicle type, the script fetches fresh manufacturer options before looping.
