"""Recompute the published case-study findings from the checked-in snapshots."""
from pathlib import Path
import json,statistics
root=Path(__file__).resolve().parents[1]
site=root/'dist' if (root/'dist').exists() else root
transit=json.loads((site/'datasets/transit.json').read_text())
permits=json.loads((site/'datasets/permits.json').read_text())
rows=permits['records'];valid=[r['daysToIssue'] for r in rows if r['daysToIssue'] is not None]
building=[r['daysToIssue'] for r in rows if r['type']=='BLD - BUILDING' and r['daysToIssue'] is not None]
findings={'transit':[], 'permits':{'records':len(rows),'validIntervals':len(valid),'medianDays':statistics.median(valid),'sameDayIntervals':sum(v==0 for v in valid),'buildingValidIntervals':len(building),'buildingMedianDays':statistics.median(building)}}
for h in transit['hubs']:
 tue=len(h['days']['20260915']);sun=len(h['days']['20260920'])
 findings['transit'].append({'anchor':h['name'],'tuesday':tue,'sunday':sun,'changePercent':round((sun/tue-1)*100,1)})
assert findings['permits']=={'records':2983,'validIntervals':2704,'medianDays':0.0,'sameDayIntervals':1832,'buildingValidIntervals':544,'buildingMedianDays':54.0}
a=next(r for r in findings['transit'] if r['anchor']=='Auburn');assert (a['tuesday'],a['sunday'],a['changePercent'])==(387,199,-48.6)
assert next(r for r in findings['transit'] if r['anchor']=='Skyway')['sunday']==134
out=site/'datasets/findings.json';out.write_text(json.dumps(findings,indent=2)+'\n')
print('PASS: all published findings independently recomputed from snapshots')
