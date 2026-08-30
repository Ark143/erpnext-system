import urllib.request
routes = ["pos-terminal","vehicle-pos","executive-dashboard","executive-automan-car-care-center",
 "executive-san-fernando-warehouse","executive-the-wheelhub","executive-ultra-mrf","executive-ultra-mrf-dau-annex",
 "executive","executive-ultra-mrf-warehouse-dau","executive-wheel-core","executive-ultra-mrf-dau-main",
 "executive-ultra-mrf-mexico-warehouse","executive-ultra-mrf-san-fernando","executive-ultra-mrf-telebastagan",
 "executive-ultra-mrf-telebastagan-2","vm-dashboard","vm-company-dashboard"]
for r in routes:
    try:
        req = urllib.request.Request(f"http://localhost/{r}", headers={"User-Agent":"curl"})
        resp = urllib.request.urlopen(req, timeout=15)
        body = resp.read().decode("utf-8","ignore")
        # check it's not an error page
        err = "error" in body.lower()[:500] and "404" in body[:500]
        print(f"{resp.status} {r}: len={len(body)}")
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} {r}")
    except Exception as e:
        print(f"ERR {r}: {type(e).__name__} {str(e)[:60]}")
