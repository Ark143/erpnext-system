#!/bin/bash
# verify login page assets all resolve (run on VPS host)
for a in $(curl -s http://localhost/login | grep -oE '(href|src)="[^"]*\.(css|js)[^"]*"' | sed 's/href="//;s/src="//;s/"//'); do
  code=$(curl -s -o /dev/null -w '%{http_code}' "http://localhost$a")
  echo "$code  $a"
done
