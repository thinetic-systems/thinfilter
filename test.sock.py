



import httplib
conn = httplib.HTTPConnection("localhost:3128")
print conn
conn.request("GET", "cache_object://localhost/active_requests")
r1 = conn.getresponse()
print r1  
a=r1.read()
conn.close()

data={}

print len(a)
c=None
for line in a.split('\n'):
  print "line=%s"%line
  if line.startswith('Connection:'):
    c=line.split()[1]
    data[c]={}
  if c and "me:" in line:
    data[c]['me']=line.split()[1]
  elif c and "peer:" in line:
    data[c]['peer']=line.split()[1]
  elif c and line.startswith('uri '):
    data[c]['uri']=line.split()[1]
  elif c and line.startswith('start '):
    data[c]['seconds']=float(line.split()[2].replace('(',''))
  elif c and line.startswith('out.offset '):
    data[c]['bytes']=float( int(line.split()[1].replace(',','')) / 1024.0)

import pprint
pprint.pprint(data)
