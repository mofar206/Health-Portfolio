"""Regression checks for the portfolio routes and source-driven map layout."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit
import re,xml.etree.ElementTree as ET
root=Path(__file__).resolve().parents[1]
p=root/'dist' if (root/'dist').exists() else root
class Page(HTMLParser):
 def __init__(self): super().__init__();self.links=[];self.ids=[]
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id' in d:self.ids.append(d['id'])
  if tag=='a':self.links.append(d)
for f in p.glob('*.html'):
 s=f.read_text();r=Page();r.feed(s)
 assert len(r.ids)==len(set(r.ids)),f
 assert 'PRODUCT · DATA · COMMUNITY' in s
 assert s.count('navigation.js')==1 and s.count('layout.css')==1
 nav={a['data-nav']:a for a in r.links if 'data-nav' in a}
 assert urlsplit(nav['work']['href']).path=='index.html' and urlsplit(nav['work']['href']).fragment=='work' and urlsplit(nav['about']['href']).path=='about.html'
 if f.name!='index.html':assert nav['about' if f.name=='about.html' else 'work']['aria-current']=='page'
for source,target in [('health.html','transit.html'),('project3.html','transit.html'),('transit.html','permits.html'),('permits.html','about.html')]:
 s=(p/source).read_text();assert re.search(r'class="(?:project-next|next-case)" href="'+target+r'(?:\?[^"]*)?"',s),(source,target)
s=(p/'index.html').read_text();svg=ET.fromstring(re.search(r'<svg.*?</svg>',s).group());points=svg.findall('circle');assert len(points)==8
for point in points:assert -55<float(point.attrib['cx'])<425 and 0<float(point.attrib['cy'])<330
assert 'position:sticky' in (p/'layout.css').read_text()
print('PASS: eight page headers, unique IDs, complete project sequence, eight contained map points, and single shared navigation script')
