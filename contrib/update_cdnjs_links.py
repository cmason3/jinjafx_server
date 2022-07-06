#!/usr/bin/env python3

import sys, os, re, requests

if len(sys.argv) == 3:
  www = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + '/../www')
  cdnjs = re.compile(r'https://cdnjs.cloudflare.com/ajax/libs/' + re.escape(sys.argv[1]) + '/(.+?)/(.+?)"')

  api_url = 'https://api.cdnjs.com/libraries/' + sys.argv[1] + '/' + sys.argv[2]
  r = requests.get(api_url + '?fields=sri').json()

  if 'sri' in r:
    for fn in ('index.html', 'output.html'):
      html = []

      with open(www + '/' + fn, 'r') as fh:
        for ln in fh.readlines():
          m = cdnjs.search(ln)
          if m:
            if m.group(2) in r['sri']:
              if m.group(1) != sys.argv[2]:
                ln = cdnjs.sub('https://cdnjs.cloudflare.com/ajax/libs/' + sys.argv[1] + '/' + sys.argv[2] + '/' + m.group(2) + '"', ln)
                ln = re.sub(r'integrity=".+?"', 'integrity="' + r['sri'][m.group(2)] + '"', ln)
                print(fn + ' - updated ' + sys.argv[1] + '/' + m.group(2) + ' to ' + sys.argv[2])

              else:
                print(fn + ' - skipping ' + sys.argv[1] + '/' + m.group(2) + ' - already at ' + sys.argv[2])

            else:
              print('warning: can\'t find resource "' + m.group(2) + '" on cdnjs', file=sys.stderr)

              

          html.append(ln)

      if len(html) > 0:
        with open(www + '/' + fn, 'w') as fh:
          fh.writelines(html)

  elif 'error' in r:
    print('error: ' + r['message'], file=sys.stderr)

else:
  print('usage: ' + os.path.basename(sys.argv[0]) + ' <library> <version>', file=sys.stderr)

