#!/usr/bin/env python3

import sys, os, re, requests

libraries = {
  'bootstrap': '5.3.1',
  'codemirror': '5.65.15',
  'firacode': '6.2.0',
  'split.js': '1.6.5',
  'js-yaml': '4.1.0',
  'dayjs': '1.11.9',
  'pako': '2.1.0',
  'jszip': '3.10.1'
}

for lib in libraries:
  www = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + '/../www')
  cdnjs = re.compile(r'https://cdnjs.cloudflare.com/ajax/libs/' + re.escape(lib) + '/(.+?)/(.+?)"')

  api_url = 'https://api.cdnjs.com/libraries/' + lib + '/' + libraries[lib]
  r = requests.get(api_url + '?fields=sri').json()

  if 'sri' in r:
    for fn in os.listdir(www):
      if fn.endswith('.html'):
        html = []

        with open(www + '/' + fn, 'rt') as fh:
          for ln in fh.readlines():
            m = cdnjs.search(ln)
            if m:
              if m.group(2) in r['sri']:
                if m.group(1) != libraries[lib]:
                  ln = cdnjs.sub('https://cdnjs.cloudflare.com/ajax/libs/' + lib + '/' + libraries[lib] + '/' + m.group(2) + '"', ln)
                  ln = re.sub(r'integrity=".+?"', 'integrity="' + r['sri'][m.group(2)] + '"', ln)
                  print(fn + ' - updated ' + lib + '/' + m.group(2) + ' to ' + libraries[lib])

                else:
                  print(fn + ' - skipping ' + lib + '/' + m.group(2) + ' - already at ' + libraries[lib])

              else:
                print('warning: can\'t find resource "' + m.group(2) + '" on cdnjs', file=sys.stderr)

            html.append(ln)

        if len(html) > 0:
          with open(www + '/' + fn, 'wt') as fh:
            fh.writelines(html)

  elif 'error' in r:
    print('error: ' + r['message'], file=sys.stderr)

