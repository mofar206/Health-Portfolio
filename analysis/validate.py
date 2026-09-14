"""Offline snapshot and internal-link checks. Run from either static layout."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
from collections import Counter
import json,datetime as dt
root=Path(__file__).resolve().parents[1]; site=root/'dist' if (root/'dist').exists() else root
p=json.loads((site/'datasets/permits.json').read_text());t=json.loads((site/'datasets/transit.json').read_text())
assert len(p['records'])==p['meta']['distinctPermits']==2983
assert len({r['id'] for r in p['records']})==2983
assert Counter(r['status'] for r in p['records'])=={r['status']:r['count'] for r in p['statusSummary']}
for r in p['records']:
 if r['daysToIssue'] is not None: assert r['daysToIssue']==(dt.date.fromisoformat(r['issued'])-dt.date.fromisoformat(r['applied'])).days>=0
assert len(t['hubs'])==8
for hub in t['hubs']:
 assert 47<hub['lat']<48 and -123<hub['lon']<-122
 for day,events in hub['days'].items():
  assert all(0<=e[0]<1800 and e[1] in t['routes'] and e[3] in {s['id'] for s in hub['stops']} for e in events)
assert [len(x) for x in t['hubs'][0]['days'].values()]==[132,133,134]
class Links(HTMLParser):
 def handle_starttag(self,tag,attrs):
  for key,v in attrs:
   if key in ('href','src') and v:
    u=urlsplit(v)
    if not u.scheme and u.path: assert (site/u.path).exists(),v
for page in site.glob('*.html'):Links().feed(page.read_text())
print('PASS: snapshot reconciliation, date intervals, transit references, geography, and all local page/asset links')
