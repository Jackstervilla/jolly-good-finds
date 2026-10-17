#!/usr/bin/env python3
"""Check each ASIN's amazon.co.uk page responds and shows a product (title, availability, price for internal reference only).
Usage: check_asins.py ASIN... > results.json   (prices are NOT used on the site)"""
import json, re, subprocess, sys, time
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"
out = {}
for a in sys.argv[1:]:
    for attempt in range(3):
        r = subprocess.run(["curl", "-s", "--compressed", "-L", "-A", UA, "-H", "Accept-Language: en-GB,en;q=0.9",
                            "-w", "\n__CODE__%{http_code}", f"https://www.amazon.co.uk/dp/{a}"], capture_output=True, text=True, errors="ignore")
        h, code = r.stdout.rsplit("\n__CODE__", 1)
        if "captcha" in h.lower() or code in ("503",):
            time.sleep(5 + attempt * 5); continue
        break
    t = re.search(r'id="productTitle"[^>]*>\s*([^<]+)', h)
    av = re.search(r'id="availability"[\s\S]{0,600}?<span[^>]*>\s*([^<]+)', h)
    p = re.findall(r'class="a-offscreen">\s*(£[\d.,]+)', h)
    out[a] = {"code": code, "title": t.group(1).strip() if t else None,
              "availability": av.group(1).strip() if av else None, "price_ref": p[0] if p else None,
              "captcha": "captcha" in h.lower(), "dog_page": "Sorry! We couldn't find that page" in h or "Page Not Found" in h}
    print(a, out[a], file=sys.stderr)
    time.sleep(1.5)
json.dump(out, sys.stdout, indent=1)
