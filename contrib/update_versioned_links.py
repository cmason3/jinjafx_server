#!/usr/bin/env python3

import os, re, hashlib

www = os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + '/../www')

for fn in os.listdir(www):
  if fn.endswith('.html'):
    html = []

    with open(www + '/' + fn, 'rt') as fh:
      for ln in fh.readlines():
        m = re.search(r'(?:href|src)="/([a-f0-9]{8})/(.+?)"', ln)
        if m:
          with open(www + '/' + m.group(2), 'rb') as fh2:
            h = hashlib.sha256(fh2.read()).hexdigest()[:8]

            if h != m.group(1):
              print(fn + ' - updated ' + m.group(2) + ' to ' + h)
              ln = re.sub(m.group(1), h, ln)

        html.append(ln)

    if len(html) > 0:
      with open(www + '/' + fn, 'wt') as fh:
        fh.writelines(html)

