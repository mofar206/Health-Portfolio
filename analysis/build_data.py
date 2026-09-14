"""Build auditable, browser-sized snapshots from official Metro and Renton data.

Run from the repository root with Python 3.12+. Uses only the standard library.
Download Metro's zip separately to work/raw/metro.zip; pass --raw-dir to change it.
The data is historical/scheduled, not live operations or an equity ranking.
"""
import argparse, collections, csv, datetime as dt, hashlib, io, json, math
import sqlite3, urllib.parse, urllib.request, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=(ROOT/'dist' if (ROOT/'dist').exists() else ROOT)/'datasets'; OUT.mkdir(parents=True,exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--raw-dir',type=Path,default=ROOT.parent/'raw')
args=parser.parse_args();raw=args.raw_dir;raw.mkdir(exist_ok=True,parents=True)
NOW=dt.datetime.now(dt.timezone.utc).isoformat()
def save(name,data):
 (OUT/name).write_text(json.dumps(data,separators=(',',':'),ensure_ascii=False))
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
HUBS=[
 ('skyway','Skyway','Renton Ave S & S 126th St','Unincorporated community'),
 ('white-center','White Center','SW Roxbury St & 15th Ave SW','Unincorporated community / Seattle boundary'),
 ('burien','Burien','Burien Transit Center','City transit center'),
 ('tukwila','Tukwila','Tukwila International Blvd Station','Station bus bays'),
 ('seatac','SeaTac','International Blvd & S 176th St','Airport-area bus stops'),
 ('renton','Renton','Renton Transit Center','City transit center'),
 ('kent','Kent','Kent Sounder Station','Station bus bays'),
 ('auburn','Auburn','Auburn Transit Center','City transit center')]
DATES=['20260915','20260919','20260920']
with zipfile.ZipFile(raw/'metro.zip') as z:
 def read(name):return list(csv.DictReader(io.TextIOWrapper(z.open(name),encoding='utf-8-sig')))
 feed=read('feed_info.txt')[0];stops=read('stops.txt');routes=read('routes.txt');cal=read('calendar.txt');exceptions=read('calendar_dates.txt');trips=read('trips.txt')
 assert all(feed['feed_start_date']<=d<=feed['feed_end_date'] for d in DATES)
 services={}
 for date in DATES:
  weekday=dt.datetime.strptime(date,'%Y%m%d').strftime('%A').lower()
  ids={r['service_id'] for r in cal if r[weekday]=='1' and r['start_date']<=date<=r['end_date']}
  for ex in exceptions:
   if ex['date']==date:
    if ex['exception_type']=='1':ids.add(ex['service_id'])
    else:ids.discard(ex['service_id'])
  services[date]=ids
 bus_routes={r['route_id']:r for r in routes if r['route_type']=='3'}
 use_services=set.union(*services.values())
 trip_index={r['trip_id']:r for r in trips if r['route_id'] in bus_routes and r['service_id'] in use_services}
 hubdata=[];stop_hub={}
 for key,name,prefix,context in HUBS:
  selected=[s for s in stops if s['stop_name'].startswith(prefix) and s.get('location_type','0') in ['','0']]
  assert selected,(key,prefix)
  info={'id':key,'name':name,'anchor':prefix,'context':context,'lat':sum(float(s['stop_lat']) for s in selected)/len(selected),'lon':sum(float(s['stop_lon']) for s in selected)/len(selected),'stops':[{'id':s['stop_id'],'name':s['stop_name'],'lat':float(s['stop_lat']),'lon':float(s['stop_lon']),'wheelchair':s.get('wheelchair_boarding','0')} for s in selected],'days':{}}
  hubdata.append(info)
  for s in selected:stop_hub[s['stop_id']]=key
 # One boarding opportunity per trip per selected hub; no repeated-bay inflation.
 events={};scanned=0
 for row in csv.DictReader(io.TextIOWrapper(z.open('stop_times.txt'),encoding='utf-8-sig')):
  scanned+=1
  if row['stop_id'] not in stop_hub or row['trip_id'] not in trip_index or row.get('pickup_type')=='1':continue
  value=row.get('departure_time') or row.get('arrival_time')
  if not value:continue
  h,m,s=map(int,value.split(':'));minute=h*60+m+s/60
  trip=trip_index[row['trip_id']];key=(stop_hub[row['stop_id']],row['trip_id'])
  event=[round(minute,2),trip['route_id'],trip.get('direction_id','0'),row['stop_id'],trip['service_id']]
  if key not in events or minute<events[key][0]:events[key]=event
 used_routes=set()
 for hub in hubdata:
  for date in DATES:
   rows=[v[:4] for (key,tid),v in events.items() if key==hub['id'] and v[4] in services[date]]
   rows.sort();hub['days'][date]=rows;used_routes.update(r[1] for r in rows)
  assert hub['days'][DATES[0]],hub['name']
 transit={'meta':{'retrievedAt':NOW,'source':'https://metro.kingcounty.gov/GTFS/google_transit.zip','documentation':'https://kingcounty.gov/en/dept/metro/rider-tools/mobile-and-web-apps','sha256':digest(raw/'metro.zip'),'feed':feed,'dates':DATES,'stopTimeRowsScanned':scanned,'method':'Bus routes only. Exact named stop groups, not city-wide coverage. Calendar exceptions applied. No-pickup events removed. One earliest departure per trip per hub. Times after midnight retain their service-day hour.'},'hubs':hubdata,'routes':{k:{'name':bus_routes[k]['route_short_name'] or bus_routes[k]['route_long_name'],'description':bus_routes[k]['route_long_name'],'color':bus_routes[k].get('route_color','')} for k in used_routes}}
 save('transit.json',transit)
 print('Transit:',len(hubdata),'hubs;',len(used_routes),'routes;',scanned,'stop-time rows scanned',flush=True)

BASE='https://gismaps.rentonwa.gov/as03/rest/services/Operational/PermitsAndConstruction/MapServer/41'
FIELDS='OBJECTID,PERMITNUMBER,APPLYDATE,ISSUEDATE,EXPIREDATE,FINALIZEDATE,PERMITTYPE,STATUS,WORKCLASS,CATEGORY,PMPERMITID'
def query(params):
 url=BASE+'/query?'+urllib.parse.urlencode(dict(params,f='json'))
 with urllib.request.urlopen(url,timeout=45) as r:d=json.load(r)
 if 'error' in d:raise RuntimeError(d['error'])
 return d
ids=query({'where':'1=1','returnIdsOnly':'true'})['objectIds'];features=[]
for offset in range(0,len(ids),500):
 d=query({'objectIds':','.join(map(str,ids[offset:offset+500])),'outFields':FIELDS,'returnGeometry':'false'})
 assert not d.get('exceededTransferLimit'),offset
 features += [f['attributes'] for f in d['features']]
assert len(features)==len(ids),(len(features),len(ids))
(raw/'renton-permits.json').write_text(json.dumps(features))
def iso(value):
 return dt.datetime.fromtimestamp(value/1000,dt.timezone.utc).date().isoformat() if value is not None else None
# Parcel layer may repeat a permit. Group by stable permit number; count disagreements.
grouped=collections.defaultdict(list)
for a in features:
 if a['PERMITNUMBER']:grouped[a['PERMITNUMBER']].append(a)
conflicts=0;records=[]
for number,rows in grouped.items():
 rows.sort(key=lambda r:r['OBJECTID']);a=rows[0]
 if any(any(r.get(k)!=a.get(k) for k in FIELDS.split(',') if k!='OBJECTID') for r in rows[1:]):conflicts+=1
 rec={'id':number,'type':a['PERMITTYPE'] or 'Unspecified','status':a['STATUS'] or 'Unspecified','workClass':a['WORKCLASS'] or 'Unspecified','category':a['CATEGORY'] or 'Unspecified','applied':iso(a['APPLYDATE']),'issued':iso(a['ISSUEDATE']),'expires':iso(a['EXPIREDATE']),'finalized':iso(a['FINALIZEDATE']),'parcelRows':len(rows)}
 if rec['applied'] and rec['issued']:
  days=(dt.date.fromisoformat(rec['issued'])-dt.date.fromisoformat(rec['applied'])).days
  rec['daysToIssue']=days if days>=0 else None
  rec['dateOrderFlag']=days<0
 else:rec['daysToIssue']=None;rec['dateOrderFlag']=False
 records.append(rec)
records.sort(key=lambda r:(r['applied'] or '',r['id']),reverse=True)
db=sqlite3.connect(':memory:')
db.execute('CREATE TABLE permits (id TEXT PRIMARY KEY, type TEXT, status TEXT, applied TEXT, issued TEXT, days_to_issue INTEGER)')
db.executemany('INSERT INTO permits VALUES (?,?,?,?,?,?)',[(r['id'],r['type'],r['status'],r['applied'],r['issued'],r['daysToIssue']) for r in records])
summary=[dict(zip(['status','count'],r)) for r in db.execute('SELECT status, COUNT(*) AS count FROM permits GROUP BY status ORDER BY count DESC')]
save('permits.json',{'meta':{'retrievedAt':NOW,'asOfDate':NOW[:10],'source':BASE,'rawRows':len(features),'distinctPermits':len(records),'duplicateParcelRows':len(features)-len(records),'conflictingDuplicateGroups':conflicts,'invalidDateOrder':sum(r['dateOrderFlag'] for r in records),'sha256':digest(raw/'renton-permits.json'),'method':'Complete set of object IDs from the active permit-parcel layer, fetched in batches. Deduplicated by permit number. UTC calendar dates. Negative issue intervals excluded. This active-layer snapshot is not a complete history of applications or completions.'},'statusSummary':summary,'records':records})
print('Permits:',len(features),'parcel rows;',len(records),'distinct;',conflicts,'conflicting groups;',summary,flush=True)
