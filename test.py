import urllib.request, json, urllib.error
data=json.dumps({'prompt':'test', 'domain':'general'}).encode()
req=urllib.request.Request('https://prompt-optimizer-nts1.onrender.com/api/evaluate', data=data, headers={'Content-Type': 'application/json'})
try:
    print(urllib.request.urlopen(req).read().decode())
except urllib.error.HTTPError as e:
    print(e.read().decode())
