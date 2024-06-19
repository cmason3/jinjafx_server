#!/usr/bin/env python3

import sys, os, re, requests

libraries = {
  'bootstrap': '5.3.3',
  'codemirror': '5.65.16',
  'firacode': '6.2.0',
  'split.js': '1.6.5',
  'js-yaml': '4.1.0',
  'dayjs': '1.11.11',
  'pako': '2.1.0',
  'jszip': '3.10.1',
  'github-markdown-css': '5.6.1'
}

def update_file(cdnjs_url, sri, f):
  data = []

  with open(f, 'rt') as fh:
    for ln in fh.readlines():
      if m := cdnjs_url.search(ln):
        if m.group(2) in sri:
          if m.group(1) != libraries[lib]:
            ln = cdnjs_url.sub('https://cdnjs.cloudflare.com/ajax/libs/' + lib + '/' + libraries[lib] + '/' + m.group(2) + '"', ln)
            ln = re.sub(r'integrity=".+?"', 'integrity="' + sri[m.group(2)] + '"', ln)
            print(os.path.basename(f) + ' - updated ' + lib + '/' + m.group(2) + ' to ' + libraries[lib])

          else:
            print(os.path.basename(f) + ' - skipping ' + lib + '/' + m.group(2) + ' - already at ' + libraries[lib])

        else:
          print('warning: can\'t find resource "' + m.group(2) + '" on cdnjs', file=sys.stderr)

      data.append(ln)

  if len(data) > 0:
    with open(f, 'wt') as fh:
      fh.writelines(data)


for lib in libraries:
  www = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + '/../www/')
  cdnjs = re.compile(r'https://cdnjs.cloudflare.com/ajax/libs/' + re.escape(lib) + '/(.+?)/(.+?)"')

  api_url = 'https://api.cdnjs.com/libraries/' + lib + '/' + libraries[lib]
  r = requests.get(api_url + '?fields=sri').json()

  if 'sri' in r:
    update_file(cdnjs, r['sri'], os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + '/../jinjafx_server.py'))

    for fn in os.listdir(www):
      if fn.endswith('.html'):
        update_file(cdnjs, r['sri'], www + '/' + fn)

  elif 'error' in r:
    print('error: ' + r['message'], file=sys.stderr)

