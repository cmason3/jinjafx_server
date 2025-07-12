#!/usr/bin/env python3

# JinjaFx Server - Jinja2 Templating Tool
# Copyright (c) 2020-2025 Chris Mason <chris@netnix.org>
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import sys
if sys.version_info < (3, 9):
  sys.exit('Requires Python >= 3.9')

from http.server import HTTPServer, BaseHTTPRequestHandler
from jinja2 import __version__ as jinja2_version
from jinja2 import TemplateError

import jinjafx, os, io, socket, signal, threading, yaml, json, base64, time, datetime, resource
import re, argparse, hashlib, traceback, glob, hmac, uuid, struct, binascii, gzip, requests, ctypes, subprocess
import cmarkgfm, emoji

__version__ = '25.7.12'

llock = threading.RLock()
rlock = threading.RLock()
base = os.path.abspath(os.path.dirname(__file__))

aws_s3_url = None
aws_access_key = None
aws_secret_key = None
github_url = None
github_token = None
jfx_weblog_key = None
repository = None
verbose = False
nocache = False
pandoc = None

rtable = {}
rl_rate = 0
rl_limit = 0
logfile = None
timelimit = 0
n_threads = 4
logring = []


class JinjaFxServer(HTTPServer):
  def handle_error(self, request, client_address):
    pass


class ArgumentParser(argparse.ArgumentParser):
  def error(self, message):
    print('URL:\n  https://github.com/cmason3/jinjafx_server\n', file=sys.stderr)
    print('Usage:\n  ' + self.format_usage()[7:], file=sys.stderr)
    raise Exception(message)


class JinjaFxRequest(BaseHTTPRequestHandler):
  server_version = 'JinjaFx/' + __version__
  protocol_version = 'HTTP/1.1'

  def format_bytes(self, b):
    for u in [ '', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y' ]:
      if b >= 1000:
        b /= 1000
      else:
        return '{:.2f}'.format(b).rstrip('0').rstrip('.') + u + 'B'

  def log_message(self, format, *args):
    path = self.path if hasattr(self, 'path') else ''
    path = path.replace('/jinjafx.html', '/')

    if not self.hide or verbose:
      if not isinstance(args[0], int) and path != '/ping':
        if self.error is not None:
          ansi = '31'
        elif args[1] == '200' or args[1] == '204':
          ansi = '32'
        elif args[1] == '304':
          ansi = '33'
        else:
          ansi = '31'

        if (args[1] != '204' and args[1] != '404' and args[1] != '501' and not path.startswith('/output.html') and not '/dt/' in path and (path != '/get_logs' or (args[1] != '200' and args[1] != '304'))) or self.critical or verbose:
          src = str(self.client_address[0])
          proto_ver = ''
          ctype = ''

          if path == '/get_logs' and args[1] == '302':
            ansi = '32'

          if hasattr(self, 'headers'):
            if 'X-Forwarded-For' in self.headers:
              src = self.headers['X-Forwarded-For']

            if 'X-Forwarded-ProtoVer' in self.headers:
              proto_ver = ' HTTP/' + re.sub(r'([23]).0', '\\1', self.headers['X-Forwarded-ProtoVer'])

            if 'Content-Type' in self.headers:
              if 'Content-Encoding' in self.headers:
                ctype = ' (' + self.headers['Content-Type'] + ':' + self.headers['Content-Encoding'] + ')'
              else:
                ctype = ' (' + self.headers['Content-Type'] + ')'

          if self.command == 'POST':
            if self.error is not None:
              ae = ' ->\033[1;' + ansi + 'm ' + str(self.error)[5:] + '\033[0m'
            else:
              ae = ''

            if self.elapsed is not None:
              log('[' + src + '] [\033[1;' + ansi + 'm' + str(args[1]) + '\033[0m]' + ' \033[1;33m' + self.command + '\033[0m ' + path + proto_ver + ctype + ' [' + self.format_bytes(self.length) + '] in ' + str(self.elapsed) + 'ms', ae)
            else:
              log('[' + src + '] [\033[1;' + ansi + 'm' + str(args[1]) + '\033[0m]' + ' \033[1;33m' + self.command + '\033[0m ' + path + proto_ver + ctype + ' [' + self.format_bytes(self.length) + ']', ae)

          elif self.command != None:
            if (args[1] != '200' and args[1] != '304') or (not path.endswith('.js') and not path.endswith('.css') and not path.endswith('.png')) or verbose:
              log('[' + src + '] [\033[1;' + ansi + 'm' + str(args[1]) + '\033[0m]' + ' ' + self.command + ' ' + path + proto_ver)


  def encode_link(self, bhash):
    alphabet = b'rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz'
    string = ''
    i = 0

    for offset, byte in enumerate(reversed(bytearray(bhash))):
      i += byte << (offset * 8)

    while i:
      i, idx = divmod(i, len(alphabet))
      string = alphabet[idx:idx + 1].decode('utf') + string

    return string


  def derive_key(self, password, salt=None, version=1):
    pbkdf2_iterations = 251001
    if salt == None:
      salt = os.urandom(32)
    return struct.pack('B', version) + struct.pack('B', len(salt)) + salt + hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, pbkdf2_iterations)


  def rot47(self, data):
    std_rot47chars = b" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}"
    mod_rot47chars = b"OPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|} !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMN"
    return data.translate(bytes.maketrans(std_rot47chars, mod_rot47chars))


  def e(self, data):
    return base64.b64encode(self.rot47(data))


  def d(self, data):
    return self.rot47(base64.b64decode(data))


  def ratelimit(self, remote_addr, n=0, check_only=False):
    if rl_rate != 0:
      rl_duration = rl_limit * 2
      key = f'{remote_addr}:{n}'
      t = int(time.time())

      with rlock:
        if key in rtable:
          if isinstance(rtable[key], int):
            if t > rtable[key]:
              del rtable[key]

            else:
              if not check_only:
                rtable[key] = min(rtable[key] + rl_duration, t + (rl_duration * 2))
              return True

          else:
            rtable[key] = list(filter(lambda s: s >= (t - rl_limit), rtable[key][-(rl_rate + 1):]))

        if not check_only:
          rtable.setdefault(key, []).append(t)

        if key in rtable:
          if len(rtable[key]) > rl_rate:
            if (rtable[key][-1] - rtable[key][0]) <= rl_limit:
              rtable[key] = t + rl_duration
              return True

    return False


  def do_GET(self, head=False, cache=True, versioned=False):
    try:
      self.critical = False
      self.hide = False
      self.error = None
      cheaders = {}

      fpath = self.path.split('?', 1)[0]

      if hasattr(self, 'headers') and 'X-Forwarded-For' in self.headers:
        remote_addr = self.headers['X-Forwarded-For']
      else:
        remote_addr = str(self.client_address[0])

      r = [ 'text/plain', 500, '500 Internal Server Error\r\n', sys._getframe().f_lineno ]

      if fpath == '/ping':
        cache = False
        r = [ 'text/plain', 200, 'OK\r\n'.encode('utf-8'), sys._getframe().f_lineno ]

      elif fpath == '/logs' and jfx_weblog_key is not None:
        self.path = re.sub(r'key=[^&]*', 'key', self.path, flags=re.IGNORECASE)

        with open(base + '/www/logs.html', 'rb') as f:
          r = [ 'text/html', 200, f.read(), sys._getframe().f_lineno ]

      elif fpath == '/get_logs' and jfx_weblog_key is not None:
        if hasattr(self, 'headers') and 'X-WebLog-Password' in self.headers:
          if self.headers['X-WebLog-Password'] == jfx_weblog_key:
            with llock:
              logs = '\r\n'.join(logring)

            logs = logs.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            logs = logs.replace('\033[1;31m', '<span class="text-danger">')
            logs = logs.replace('\033[1;32m', '<span class="text-success">')
            logs = logs.replace('\033[1;33m', '<span class="text-warning">')
            logs = logs.replace('\033[0m', '</span>')
            r = [ 'text/plain', 200, logs.encode('utf-8'), sys._getframe().f_lineno ]

          else:
            if not self.ratelimit(remote_addr, 3, False):
              r = [ 'text/plain', 401, '401 Unauthorized\r\n'.encode('utf-8'), sys._getframe().f_lineno ]
            else:
              r = [ 'text/plain', 429, '429 Too Many Requests\r\n'.encode('utf-8'), sys._getframe().f_lineno ]

        else:
          r = [ 'text/plain', 401, '401 Unauthorized\r\n'.encode('utf-8'), sys._getframe().f_lineno ]

      else:
        if fpath == '/':
          fpath = '/index.html'
          self.hide = not verbose

        if re.search(r'^/dt/[A-Za-z0-9_-]{1,24}(?:/[A-Za-z][A-Za-z0-9_ %-]*)?$', fpath):
          fpath = '/index.html'

        if re.search(r'^/[a-f0-9]{8}/', fpath):
          fpath = fpath[fpath[1:].index('/') + 1:]
          versioned = True

        if re.search(r'^/get_dt/[A-Za-z0-9_-]{1,24}$', fpath):
          dt = ''
          self.critical = True

          def sanitise_dt(dt):
            fields = ('dt_password:', 'dt_mpassword:', 'remote_addr:')
            dt = '\n'.join([ln for ln in dt.splitlines() if not ln.startswith(fields)])
            return dt.encode('utf-8')

          if aws_s3_url or github_url or repository:
            if not self.ratelimit(remote_addr, 2, False):
              if aws_s3_url:
                rr = aws_s3_get(aws_s3_url, 'jfx_' + fpath[8:] + '.yml')

                if rr.status_code == 200:
                  r = [ 'application/json', 200, json.dumps({ 'dt': self.e(sanitise_dt(rr.text)).decode('utf-8') }).encode('utf-8'), sys._getframe().f_lineno ]

                  dt = rr.text

                elif rr.status_code == 403:
                  r = [ 'text/plain', 403, '403 Forbidden\r\n'.encode('utf-8'), sys._getframe().f_lineno ]

                elif rr.status_code == 404:
                  r = [ 'text/plain', 404, '404 Not Found\r\n'.encode('utf-8'), sys._getframe().f_lineno ]

              elif github_url:
                rr = github_get(github_url, 'jfx_' + fpath[8:] + '.yml')

                if rr.status_code == 200:
                  jobj = rr.json()
                  content = jobj['content']

                  if jobj.get('encoding') and jobj.get('encoding') == 'base64':
                    content = base64.b64decode(content).decode('utf-8')

                  r = [ 'application/json', 200, json.dumps({ 'dt': self.e(sanitise_dt(content)).decode('utf-8') }).encode('utf-8'), sys._getframe().f_lineno ]

                  dt = content

                elif rr.status_code == 401:
                  r = [ 'text/plain', 403, '403 Forbidden\r\n'.encode('utf-8'), sys._getframe().f_lineno ]

                elif rr.status_code == 404:
                  r = [ 'text/plain', 404, '404 Not Found\r\n'.encode('utf-8'), sys._getframe().f_lineno ]

              else:
                fpath = os.path.normpath(repository + '/jfx_' + fpath[8:] + '.yml')

                if os.path.isfile(fpath):
                  with open(fpath, 'rb') as f:
                    dt = f.read().decode('utf-8')

                    r = [ 'application/json', 200, json.dumps({ 'dt': self.e(sanitise_dt(dt)).decode('utf-8') }).encode('utf-8'), sys._getframe().f_lineno ]

                else:
                  r = [ 'text/plain', 404, '404 Not Found\r\n'.encode('utf-8'), sys._getframe().f_lineno ]

              if r[1] == 200:
                if dt.lstrip().startswith('$VAULTY;'):
                  if 'X-Dt-Password' in self.headers:
                    try:
                      dt = jinjafx.Vaulty().decrypt(dt, self.headers['X-Dt-Password'])
                      r = [ 'application/json', 200, json.dumps({ 'dt': self.e(sanitise_dt(dt)).decode('utf-8') }).encode('utf-8'), sys._getframe().f_lineno ]

                    except Exception:
                      cheaders['X-Dt-Authentication'] = 'Open'
                      r = [ 'text/plain', 401, '401 Unauthorized\r\n'.encode('utf-8'), sys._getframe().f_lineno ]

                  else:
                    cheaders['X-Dt-Authentication'] = 'Open'
                    r = [ 'text/plain', 401, '401 Unauthorized\r\n'.encode('utf-8'), sys._getframe().f_lineno ]

              if r[1] == 200:
                mo = re.search(r'dt_password: "(\S+)"', dt)
                if mo != None:
                  if 'X-Dt-Password' in self.headers:
                    t = binascii.unhexlify(mo.group(1).encode('utf-8'))
                    if t != self.derive_key(self.headers['X-Dt-Password'], t[2:int(t[1]) + 2], t[0]):
                      mm = re.search(r'dt_mpassword: "(\S+)"', dt)
                      if mm != None:
                        t = binascii.unhexlify(mm.group(1).encode('utf-8'))
                        if t != self.derive_key(self.headers['X-Dt-Password'], t[2:int(t[1]) + 2], t[0]):
                          cheaders['X-Dt-Authentication'] = 'Modify'
                          r = [ 'text/plain', 401, '401 Unauthorized\r\n'.encode('utf-8'), sys._getframe().f_lineno ]

                      else:
                        cheaders['X-Dt-Authentication'] = 'Open'
                        r = [ 'text/plain', 401, '401 Unauthorized\r\n'.encode('utf-8'), sys._getframe().f_lineno ]

                  else:
                    cheaders['X-Dt-Authentication'] = 'Open'
                    r = [ 'text/plain', 401, '401 Unauthorized\r\n'.encode('utf-8'), sys._getframe().f_lineno ]

            else:
              r = [ 'text/plain', 429, '429 Too Many Requests\r\n'.encode('utf-8'), sys._getframe().f_lineno ]

        elif re.search(r'^/[A-Z0-9_-]+\.[A-Z0-9]+$', fpath, re.IGNORECASE) and (os.path.isfile(base + '/www' + fpath) or fpath == '/jinjafx.html'):
          if fpath.endswith('.js'):
            ctype = 'text/javascript'
          elif fpath.endswith('.css'):
            ctype = 'text/css'
          elif fpath.endswith('.png'):
            ctype = 'image/png'
          else:
            ctype = 'text/html'

          if fpath == '/jinjafx.html':
            r = [ 'text/plain', 200, 'OK\r\n'.encode('utf-8'), sys._getframe().f_lineno ]
            self.hide = verbose

          else:
            with open(base + '/www' + fpath, 'rb') as f:
              r = [ ctype, 200, f.read(), sys._getframe().f_lineno ]

              if fpath == '/index.html':
                if repository or aws_s3_url or github_url:
                  get_link = 'true'
                else:
                  get_link = 'false'

                r[2] = r[2].decode('utf-8').replace('{{ jinjafx.version }}', jinjafx.__version__ + ' / Jinja2 v' + jinja2_version).replace('{{ get_link }}', get_link).encode('utf-8')

              elif fpath == '/output.html':
                if pandoc:
                  r[2] = r[2].decode('utf-8').replace('{{ pandoc_class }}', '').encode('utf-8')
                else:
                  r[2] = r[2].decode('utf-8').replace('{{ pandoc_class }}', ' hide').encode('utf-8')

        else:
          r = [ 'text/plain', 404, '404 Not Found\r\n'.encode('utf-8'), sys._getframe().f_lineno ]

      script_src = "'self' https://cdnjs.cloudflare.com"

      if allowjs:
        script_src += " 'unsafe-inline'"

      headers = {
        'X-Content-Type-Options': 'nosniff',
        'Referrer-Policy': 'strict-origin-when-cross-origin'
      }

      if not nocsp:
        headers['Content-Security-Policy'] = "default-src 'self'; style-src 'self' https://cdnjs.cloudflare.com 'unsafe-inline'; script-src " + script_src + "; img-src data: *; frame-ancestors 'none'"

      etag = '"' + hashlib.sha224(repr(headers).encode('utf-8') + b'|' + r[0].encode('utf-8') + b'; ' + r[2]).hexdigest() + '"'

      if 'If-None-Match' in self.headers:
        if self.headers['If-None-Match'] == etag:
          head = True
          r = [ None, 304, None, sys._getframe().f_lineno ]

      self.send_response(r[1])

      if r[1] != 304:
        if len(r[2]) > 1024 and 'Accept-Encoding' in self.headers and r[0] != 'image/png':
          if 'gzip' in self.headers['Accept-Encoding']:
            self.send_header('Content-Encoding', 'gzip')
            r[2] = gzip.compress(r[2])

        self.send_header('Content-Type', r[0])
        self.send_header('Content-Length', str(len(r[2])))

      if versioned and not nocache:
        self.send_header('Cache-Control', 'public, max-age=31536000')

      elif not cache:
        self.send_header('Cache-Control', 'no-store, max-age=0')

      elif r[1] == 200 or r[1] == 304:
        if r[1] == 200:
          for h in headers:
            self.send_header(h, headers[h])

        self.send_header('Cache-Control', 'max-age=0, must-revalidate')
        self.send_header('ETag', etag)

      for k in cheaders:
        self.send_header(k, cheaders[k])

      self.end_headers()
      if not head:
        self.wfile.write(r[2])

    except Exception as e:
      log(traceback.format_exc())


  def do_OPTIONS(self):
    self.critical = False
    self.hide = False
    self.error = None
    self.send_response(204)
    self.send_header('Allow', 'OPTIONS, HEAD, GET, POST')
    self.end_headers()


  def do_HEAD(self):
    self.error = None
    self.do_GET(True)


  def do_POST(self):
    self.critical = False
    self.hide = False
    self.elapsed = None
    self.error = None

    cheaders = {}

    uc = self.path.split('?', 1)
    params = { x[0]: x[1] for x in [x.split('=') for x in uc[1].split('&') ] } if len(uc) > 1 else { }
    fpath = uc[0]

    if hasattr(self, 'headers') and 'X-Forwarded-For' in self.headers:
      remote_addr = self.headers['X-Forwarded-For']
    else:
      remote_addr = str(self.client_address[0])

    r = [ 'text/plain', 500, '500 Internal Server Error\r\n', sys._getframe().f_lineno ]

    if 'Content-Length' in self.headers:
      if int(self.headers['Content-Length']) < (25 * 1024 * 1024):
        postdata = self.rfile.read(int(self.headers['Content-Length']))
        self.length = len(postdata)

        if 'Content-Encoding' in self.headers and self.headers['Content-Encoding'] == 'gzip':
          postdata = gzip.decompress(postdata)

        if fpath == '/jinjafx':
          if self.headers['Content-Type'] == 'application/json':
            try:
              gvars = {}

              dt = json.loads(postdata.decode('utf-8'))
              data = self.d(dt['data']) if 'data' in dt and len(dt['data'].strip()) > 0 else b''

              if isinstance(dt['template'], dict):
                for t in dt['template']:
                  dt['template'][t] = self.d(dt['template'][t]).decode('utf-8') if len(dt['template'][t].strip()) > 0 else ''

              else:
                dt['template'] = self.d(dt['template']).decode('utf-8') if len(dt['template'].strip()) > 0 else ''

              template = dt['template']

              if 'vars' in dt and len(dt['vars'].strip()) > 0:
                gyaml = self.d(dt['vars']).decode('utf-8')
                vpw = self.d(dt['vpw']).decode('utf-8') if 'vpw' in dt else ''
                vault_undef = False

                if 'jinjafx_vault_undefined' in gyaml:
                  yaml.add_constructor('!vault', lambda x, y: None, yaml.SafeLoader)
                  if y := yaml.load(gyaml, Loader=yaml.SafeLoader):
                    vault_undef = y.get('jinjafx_vault_undefined', vault_undef)

                if vpw.strip():
                  vault_undef = False

                def yaml_vault_tag(loader, node):
                  x = jinjafx.AnsibleVault().decrypt(node.value.encode('utf-8'), vpw, vault_undef)
                  if x is not None:
                    return x.decode('utf-8')

                  else:
                    return '_undef'

                yaml.add_constructor('!vault', yaml_vault_tag, yaml.SafeLoader)

                if y := yaml.load(gyaml, Loader=yaml.SafeLoader):
                  if isinstance(y, list):
                    y = {'_': y}

                  s = [y]

                  while s:
                    c = s.pop()
                    for key in list(c.keys()):
                      if c[key] == '_undef':
                        del c[key]
                      elif isinstance(c[key], dict):
                        s.append(c[key])
                      elif isinstance(c[key], list):
                        for item in c[key]:
                          if isinstance(item, dict):
                            s.append(item)

                  gvars.update(y)

              st = round(time.time() * 1000)
              ocount = 0
              ret = [0, None]

              t = StoppableJinjaFx(jinjafx.JinjaFx()._jinjafx, template, data.decode('utf-8'), gvars, ret)

              if timelimit > 0:
                while t.is_alive() and ((time.time() * 1000) - st) <= (timelimit * 1000):
                  time.sleep(0.1)

                if t.is_alive():
                  t.stop()

              t.join()

              if ret[0] == 1:
                outputs = ret[1]

              elif ret[0] == -1:
                raise ret[1]

              else:
                raise Exception("execution time limit of " + str(timelimit) + "s exceeded")

              jsr = {
                'status': 'ok',
                'elapsed': round(time.time() * 1000) - st,
                'outputs': {}
              }

              self.elapsed = jsr['elapsed']

              def html_escape(text):
                text = text.replace("'", "&apos;")
                text = text.replace('"', "&quot;")
                return text

              for o in outputs:
                (oname, oformat) = o.rsplit(':', 1) if ':' in o else (o, 'text')
                oname = re.sub(r' */[ /]+', '/', oname.lstrip(' /').rstrip())
                output = '\n'.join(outputs[o]) + '\n'

                if oname.endswith('/') or (len(oname) == 0):
                  oname += 'Output'

                if len(output.strip()) > 0:
                  o = oname + ':' + oformat

                  if oformat == 'markdown' or oformat == 'md':
                    o = oname + ':html'
                    options = (cmarkgfm.cmark.Options.CMARK_OPT_GITHUB_PRE_LANG | cmarkgfm.cmark.Options.CMARK_OPT_SMART | cmarkgfm.cmark.Options.CMARK_OPT_UNSAFE)
                    output = cmarkgfm.github_flavored_markdown_to_html(html_escape(output), options).replace('&amp;amp;', '&amp;').replace('&amp;', '&')

                    for style in ['red', 'green', 'blue', 'highlight']:
                      output = re.sub('{(' + style + ')}(.+?){/\\1}', r'<span class="\1">\2</span>', output, flags=re.DOTALL | re.IGNORECASE)

                    head = '<!DOCTYPE html>\n<html>\n<head>\n'
                    head += '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.8.1/github-markdown.min.css" crossorigin="anonymous">\n'
                    head += '<style>\n  pre, code { white-space: pre-wrap !important; word-wrap: break-word !important; }\n'
                    head += '  .red { color: red; }\n  .green { color: green; }\n  .blue { color: blue; }\n  .highlight { background: yellow !important; print-color-adjust: exact; }\n</style>\n</head>\n'
                    output = emoji.emojize(output, language='alias').encode('ascii', 'xmlcharrefreplace').decode('utf-8')
                    output = head + '<body>\n<div class="markdown-body">\n' + output + '</div>\n</body>\n</html>\n'

                  elif oformat == 'html':
                    output = output.encode('ascii', 'xmlcharrefreplace').decode('utf-8')

                  elif oformat != 'text':
                    raise Exception('unknown output format "' + oformat + '" specified for output "' + oname + '"')

                  jsr['outputs'].update({ o: self.e(output.encode('utf-8')).decode('utf-8') })
                  if o != '_stderr_':
                    ocount += 1

              if ocount == 0:
                raise Exception('nothing to output')

            except TemplateError as e:
              if hasattr(e, 'name') and e.name and hasattr(e, 'lineno') and e.lineno:
                error = f'error[{e.name}:{e.lineno}]: {type(e).__name__}: {e}'

              else:
                error = jinjafx._format_error(e, 'template code')
                error = error.replace('__init__.py:', 'jinjafx_server.py:')

              jsr = {
                'status': 'error',
                'error': error
              }
              self.error = error

            except Exception as e:
              error = jinjafx._format_error(e, 'template code', '_jinjafx')
              error = error.replace('__init__.py:', 'jinjafx_server.py:')

              jsr = {
                'status': 'error',
                'error': error
              }
              self.error = error

            r = [ 'application/json', 200, json.dumps(jsr), sys._getframe().f_lineno ]

          else:
            r = [ 'text/plain', 400, '400 Bad Request\r\n', sys._getframe().f_lineno ]

        else:
          if fpath == '/html2docx':
            if pandoc:
              if self.headers['Content-Type'] == 'application/json':
                try:
                  if not self.ratelimit(remote_addr, 4, False):
                    html = self.d(json.loads(postdata.decode('utf-8')))
                    p = subprocess.run([pandoc, '-f', 'html', '-t', 'docx', '-o', '-', '--sandbox', '--standalone', '--embed-resources', '--reference-doc=' + base + '/pandoc/reference.docx'], input=html, stdout=subprocess.PIPE, check=True)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                    self.send_header('Content-Length', str(len(p.stdout)))
                    self.send_header('X-Download-Filename', 'Output.' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '.docx')
                    self.end_headers()
                    self.wfile.write(p.stdout)
                    return

                  else:
                    r = [ 'text/plain', 429, '429 Too Many Requests\r\n', sys._getframe().f_lineno ]

                except Exception as e:
                  log(traceback.format_exc())
                  r = [ 'text/plain', 400, '400 Bad Request\r\n', sys._getframe().f_lineno ]

              else:
                r = [ 'text/plain', 400, '400 Bad Request\r\n', sys._getframe().f_lineno ]

          elif fpath == '/get_link' or fpath == '/delete_link':
            if aws_s3_url or github_url or repository:
              if self.headers['Content-Type'] == 'application/json':
                try:
                  dt_yml = ''
                  dt_password = ''
                  dt_opassword = ''
                  dt_mpassword = ''
                  dt_epassword = ''
                  dt_revision = 1
                  dt_protected = 0
                  dt_encrypted = 0

                  if hasattr(self, 'headers'):
                    if 'X-Dt-Protected' in self.headers:
                      dt_protected = int(self.headers['X-Dt-Protected'])
                    if 'X-Dt-Password' in self.headers:
                      dt_password = self.headers['X-Dt-Password']
                    if 'X-Dt-Open-Password' in self.headers:
                      dt_opassword = self.headers['X-Dt-Open-Password']
                    if 'X-Dt-Encrypted' in self.headers:
                      dt_encrypted = int(self.headers['X-Dt-Encrypted'])
                    if 'X-Dt-Modify-Password' in self.headers:
                      dt_mpassword = self.headers['X-Dt-Modify-Password']
                    if 'X-Dt-Encrypt-Password' in self.headers:
                      dt_epassword = self.headers['X-Dt-Encrypt-Password']
                    if 'X-Dt-Revision' in self.headers:
                      dt_revision = int(self.headers['X-Dt-Revision'])

                  if not self.ratelimit(remote_addr, 1, False):
                    def authenticate_dt(rdt, r):
                      mm = re.search(r'dt_mpassword: "(\S+)"', rdt)
                      mo = re.search(r'dt_password: "(\S+)"', rdt)

                      if mm != None or mo != None:
                        if dt_password != '':
                          rpassword = mm.group(1) if mm != None else mo.group(1)
                          t = binascii.unhexlify(rpassword.encode('utf-8'))
                          if t != self.derive_key(dt_password, t[2:int(t[1]) + 2], t[0]):
                            cheaders['X-Dt-Authentication'] = 'Modify' if (mm != None) else 'Open'
                            r = [ 'text/plain', 401, '401 Unauthorized\r\n', sys._getframe().f_lineno ]

                        else:
                          cheaders['X-Dt-Authentication'] = 'Modify' if (mm != None) else 'Open'
                          r = [ 'text/plain', 401, '401 Unauthorized\r\n', sys._getframe().f_lineno ]

                      return mm, mo, r

                    if fpath == '/get_link':
                      dt = json.loads(postdata.decode('utf-8'))

                      vdt = {}
                      dt_yml += '---\n'
                      dt_yml += 'dt:\n'

                      if 'datasets' in dt:
                        if 'global' in dt:
                          vdt['global'] = self.d(dt['global']).decode('utf-8') if 'global' in dt and len(dt['global'].strip()) > 0 else ''

                          if vdt['global'] == '':
                            dt_yml += '  global: ""\n\n'
                          else:
                            dt_yml += '  global: |2\n'
                            dt_yml += re.sub('^', ' ' * 4, vdt['global'].rstrip(), flags=re.MULTILINE) + '\n\n'

                        dt_yml += '  datasets:\n'

                        for ds in dt['datasets']:
                          vdt['data'] = self.d(dt['datasets'][ds]['data']).decode('utf-8') if 'data' in dt['datasets'][ds] and len(dt['datasets'][ds]['data'].strip()) > 0 else ''
                          vdt['vars'] = self.d(dt['datasets'][ds]['vars']).decode('utf-8') if 'vars' in dt['datasets'][ds] and len(dt['datasets'][ds]['vars'].strip()) > 0 else ''

                          dt_yml += '    "' + ds + '":\n'

                          if vdt['data'] == '':
                            dt_yml += '      data: ""\n'
                          else:
                            dt_yml += '      data: |2\n'
                            dt_yml += re.sub('^', ' ' * 8, vdt['data'].rstrip(), flags=re.MULTILINE) + '\n\n'

                          if vdt['vars'] == '':
                            dt_yml += '      vars: ""\n\n'
                          else:
                            dt_yml += '      vars: |2\n'
                            dt_yml += re.sub('^', ' ' * 8, vdt['vars'].rstrip(), flags=re.MULTILINE) + '\n\n'

                      else :
                        vdt['data'] = self.d(dt['data']).decode('utf-8') if 'data' in dt and len(dt['data'].strip()) > 0 else ''
                        vdt['vars'] = self.d(dt['vars']).decode('utf-8') if 'vars' in dt and len(dt['vars'].strip()) > 0 else ''

                        if vdt['data'] == '':
                          dt_yml += '  data: ""\n'
                        else:
                          dt_yml += '  data: |2\n'
                          dt_yml += re.sub('^', ' ' * 4, vdt['data'].rstrip(), flags=re.MULTILINE) + '\n\n'

                        if vdt['vars'] == '':
                          dt_yml += '  vars: ""\n\n'
                        else:
                          dt_yml += '  vars: |2\n'
                          dt_yml += re.sub('^', ' ' * 4, vdt['vars'].rstrip(), flags=re.MULTILINE) + '\n\n'

                      if isinstance(dt['template'], dict):
                        dt_yml += '  template:\n'

                        for t in dt['template']:
                          te = self.d(dt['template'][t]).decode('utf-8') if len(dt['template'][t].strip()) > 0 else ''

                          if te == '':
                            dt_yml += '    "' + t + '": ""\n'
                          else:
                            dt_yml += '    "' + t + '": |2\n'
                            dt_yml += re.sub('^', ' ' * 6, te, flags=re.MULTILINE) + '\n\n'

                      else:
                        te = self.d(dt['template']).decode('utf-8') if len(dt['template'].strip()) > 0 else ''

                        if te == '':
                          dt_yml += '  template: ""\n'
                        else:
                          dt_yml += '  template: |2\n'
                          dt_yml += re.sub('^', ' ' * 4, te, flags=re.MULTILINE) + '\n\n'

                      if not dt_yml.endswith('\n\n'):
                        dt_yml += '\n'

                      dt_yml += 'revision: ' + str(dt_revision) + '\n'
                      dt_yml += 'dataset: "' + dt['dataset'] + '"\n'

                      if 'show_global' in dt:
                        dt_yml += 'show_global: ' + dt['show_global'] + '\n'

                      if dt_encrypted:
                        dt_yml += 'encrypted: 1\n'

                      if dt_protected:
                        dt_yml += 'protected: 1\n'

                      def update_dt(rdt, dt_yml, r):
                        mm, mo, r = authenticate_dt(rdt, r)

                        if r[1] != 401:
                          if dt_protected:
                            if dt_opassword != '' or dt_mpassword != '':
                              if dt_opassword != '':
                                dt_yml += 'dt_password: "' + binascii.hexlify(self.derive_key(dt_opassword)).decode('utf-8') + '"\n'

                              if dt_mpassword != '':
                                dt_yml += 'dt_mpassword: "' + binascii.hexlify(self.derive_key(dt_mpassword)).decode('utf-8') + '"\n'

                            else:
                              if mo != None:
                                dt_yml += 'dt_password: "' + mo.group(1) + '"\n'

                              if mm != None:
                                dt_yml += 'dt_mpassword: "' + mm.group(1) + '"\n'

                        return dt_yml, r

                      def add_client_fields(dt_yml, remote_addr):
                        dt_yml += 'remote_addr: "' + remote_addr + '"\n'
                        dt_yml += 'updated: "' + str(int(time.time()))  + '"\n'
                        return dt_yml

                    if 'id' in params:
                      if re.search(r'^[A-Za-z0-9_-]{1,24}$', params['id']):
                        dt_link = params['id']

                      else:
                        raise Exception("invalid link format")

                    elif fpath == '/delete_link':
                      raise Exception("link id is required")

                    else:
                      dt_link = self.encode_link(hashlib.sha256((str(uuid.uuid1()) + ':' + dt_yml).encode('utf-8')).digest()[:6])

                    dt_filename = 'jfx_' + dt_link + '.yml'

                    if aws_s3_url:
                      rr = aws_s3_get(aws_s3_url, dt_filename)
                      if rr.status_code == 200:
                        if rr.text.lstrip().startswith('$VAULTY;'):
                          if dt_epassword != '':
                            try:
                              content = jinjafx.Vaulty().decrypt(rr.text, dt_epassword)

                            except Exception:
                              r = [ 'text/plain', 403, '403 Forbidden\r\n', sys._getframe().f_lineno ]

                          else:
                            r = [ 'text/plain', 403, '403 Forbidden\r\n', sys._getframe().f_lineno ]

                        else:
                          content = rr.text

                        if r[1] != 403:
                          m = re.search(r'revision: (\d+)', rr.text)
                          if m != None:
                            if dt_revision <= int(m.group(1)):
                              r = [ 'text/plain', 409, '409 Conflict\r\n', sys._getframe().f_lineno ]

                          if r[1] != 409:
                            if fpath == '/get_link':
                              dt_yml, r = update_dt(rr.text, dt_yml, r)

                            elif fpath == '/delete_link':
                              mm, mo, r = authenticate_dt(rr.text, r)

                              if r[1] != 401:
                                rr = aws_s3_delete(aws_s3_url, dt_filename)

                                if rr.status_code == 204:
                                  r = [ 'text/plain', 200, '200 OK\r\n', sys._getframe().f_lineno ]

                                elif rr.status_code == 403:
                                  r = [ 'text/plain', 403, '403 Forbidden\r\n', sys._getframe().f_lineno ]

                      if fpath != '/delete_link' and (r[1] == 500 or r[1] == 200):
                        dt_yml = add_client_fields(dt_yml, remote_addr)

                        if dt_encrypted:
                          if dt_opassword != '':
                            dt_yml = jinjafx.Vaulty().encrypt(dt_yml, dt_opassword) + '\n'

                          elif dt_epassword != '':
                            dt_yml = jinjafx.Vaulty().encrypt(dt_yml, dt_epassword) + '\n'

                          else:
                            r = [ 'text/plain', 400, '400 Bad Request\r\n', sys._getframe().f_lineno ]

                        if r[1] != 400:
                          if dt_encrypted:
                            rr = aws_s3_put(aws_s3_url, dt_filename, dt_yml, 'application/vaulty')

                          else:
                            rr = aws_s3_put(aws_s3_url, dt_filename, dt_yml, 'application/yaml')

                          if rr.status_code == 200:
                            r = [ 'text/plain', 200, dt_link + '\r\n', sys._getframe().f_lineno ]

                          elif rr.status_code == 403:
                            r = [ 'text/plain', 403, '403 Forbidden\r\n', sys._getframe().f_lineno ]

                    elif github_url:
                      sha = None

                      rr = github_get(github_url, dt_filename)
                      if rr.status_code == 200:
                        jobj = rr.json()
                        content = jobj['content']
                        sha = jobj['sha']

                        if jobj.get('encoding') and jobj.get('encoding') == 'base64':
                          content = base64.b64decode(content).decode('utf-8')

                        if content.lstrip().startswith('$VAULTY;'):
                          if dt_epassword != '':
                            try:
                              content = jinjafx.Vaulty().decrypt(content, dt_epassword)

                            except Exception:
                              r = [ 'text/plain', 403, '403 Forbidden\r\n', sys._getframe().f_lineno ]

                          else:
                            r = [ 'text/plain', 403, '403 Forbidden\r\n', sys._getframe().f_lineno ]

                        if r[1] != 403:
                          m = re.search(r'revision: (\d+)', content)
                          if m != None:
                            if dt_revision <= int(m.group(1)):
                              r = [ 'text/plain', 409, '409 Conflict\r\n', sys._getframe().f_lineno ]

                          if r[1] != 409:
                            if fpath == '/get_link':
                              dt_yml, r = update_dt(content, dt_yml, r)

                            elif fpath == '/delete_link':
                              mm, mo, r = authenticate_dt(content, r)

                              if r[1] != 401:
                                rr = github_delete(github_url, dt_filename, sha)

                                if str(rr.status_code).startswith('2'):
                                  r = [ 'text/plain', 200, '200 OK\r\n', sys._getframe().f_lineno ]

                                elif rr.status_code == 401:
                                  r = [ 'text/plain', 403, '403 Forbidden\r\n', sys._getframe().f_lineno ]

                      if fpath != '/delete_link' and (r[1] == 500 or r[1] == 200):
                        dt_yml = add_client_fields(dt_yml, remote_addr)

                        if dt_encrypted:
                          if dt_opassword != '':
                            dt_yml = jinjafx.Vaulty().encrypt(dt_yml, dt_opassword) + '\n'

                          elif dt_epassword != '':
                            dt_yml = jinjafx.Vaulty().encrypt(dt_yml, dt_epassword) + '\n'

                          else:
                            r = [ 'text/plain', 400, '400 Bad Request\r\n', sys._getframe().f_lineno ]

                        if r[1] != 400:
                          rr = github_put(github_url, dt_filename, dt_yml, sha)

                          if str(rr.status_code).startswith('2'):
                            r = [ 'text/plain', 200, dt_link + '\r\n', sys._getframe().f_lineno ]

                          elif rr.status_code == 401:
                            r = [ 'text/plain', 403, '403 Forbidden\r\n', sys._getframe().f_lineno ]

                    else:
                      dt_filename = os.path.normpath(repository + '/' + dt_filename)

                      if os.path.isfile(dt_filename):
                        with open(dt_filename, 'rb') as f:
                          rr = f.read().decode('utf-8')

                        if rr.lstrip().startswith('$VAULTY'):
                          if dt_epassword != '':
                            try:
                              rr = jinjafx.Vaulty().decrypt(rr, dt_epassword)

                            except Exception:
                              r = [ 'text/plain', 403, '403 Forbidden\r\n', sys._getframe().f_lineno ]

                          else:
                            r = [ 'text/plain', 403, '403 Forbidden\r\n', sys._getframe().f_lineno ]

                        if r[1] != 403:
                          m = re.search(r'revision: (\d+)', rr)
                          if m != None:
                            if dt_revision <= int(m.group(1)):
                              r = [ 'text/plain', 409, '409 Conflict\r\n', sys._getframe().f_lineno ]

                          if r[1] != 409:
                            if fpath == '/get_link':
                              dt_yml, r = update_dt(rr, dt_yml, r)

                            elif fpath == '/delete_link':
                              mm, mo, r = authenticate_dt(rr, r)

                              if r[1] != 401:
                                os.remove(dt_filename)
                                r = [ 'text/plain', 200, '200 OK\r\n', sys._getframe().f_lineno ]

                      if fpath != '/delete_link' and (r[1] == 500 or r[1] == 200):
                        dt_yml = add_client_fields(dt_yml, remote_addr)

                        if dt_encrypted:
                          if dt_opassword != '':
                            dt_yml = jinjafx.Vaulty().encrypt(dt_yml, dt_opassword) + '\n'

                          elif dt_epassword != '':
                            dt_yml = jinjafx.Vaulty().encrypt(dt_yml, dt_epassword) + '\n'

                          else:
                            r = [ 'text/plain', 400, '400 Bad Request\r\n', sys._getframe().f_lineno ]

                        if r[1] != 400:
                          with open(dt_filename, 'w') as f:
                            f.write(dt_yml)

                            r = [ 'text/plain', 200, dt_link + '\r\n', sys._getframe().f_lineno ]

                  else:
                    r = [ 'text/plain', 429, '429 Too Many Requests\r\n', sys._getframe().f_lineno ]

                except Exception as e:
                  log(traceback.format_exc())
                  r = [ 'text/plain', 400, '400 Bad Request\r\n', sys._getframe().f_lineno ]

              else:
                r = [ 'text/plain', 400, '400 Bad Request\r\n', sys._getframe().f_lineno ]

            else:
              r = [ 'text/plain', 503, '503 Service Unavailable\r\n', sys._getframe().f_lineno ]

          else:
            r = [ 'text/plain', 404, '404 Not Found\r\n', sys._getframe().f_lineno ]

      else:
        r = [ 'text/plain', 413, '413 Request Entity Too Large\r\n', sys._getframe().f_lineno ]

    else:
      r = [ 'text/plain', 400, '400 Bad Request\r\n', sys._getframe().f_lineno ]

    self.send_response(r[1])

    r[2] = r[2].encode('utf-8')

    if r[1] == 200:
      self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')

      if len(r[2]) > 1024 and 'Accept-Encoding' in self.headers:
        if 'gzip' in self.headers['Accept-Encoding']:
          self.send_header('Content-Encoding', 'gzip')
          r[2] = gzip.compress(r[2])

    self.send_header('Content-Type', r[0])
    self.send_header('Content-Length', str(len(r[2])))
    self.send_header('X-Content-Type-Options', 'nosniff')

    for k in cheaders:
      self.send_header(k, cheaders[k])

    self.end_headers()
    self.wfile.write(r[2])


class JinjaFxThread(threading.Thread):
  def __init__(self, s, addr):
    threading.Thread.__init__(self)
    self.s = s
    self.addr = addr
    self.daemon = True
    self.start()

  def run(self):
    httpd = JinjaFxServer(self.addr, JinjaFxRequest, False)
    httpd.socket = self.s
    httpd.server_bind = self.server_close = lambda self: None
    httpd.serve_forever()


class StoppableJinjaFx(threading.Thread):
  def __init__(self, jinjafx, template, data, gvars, ret):
    threading.Thread.__init__(self)
    self.jinjafx = jinjafx
    self.template = template
    self.data = data
    self.gvars = gvars
    self.ret = ret
    self.start()

  def run(self):
    try:
      self.ret[1] = self.jinjafx(self.template, self.data, self.gvars, 'Output', [], True, True)
      self.ret[0] = 1

    except Exception as e:
      self.ret[1] = e
      self.ret[0] = -1

  def stop(self):
    ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.ident), ctypes.py_object(SystemExit))


def main(rflag=[0]):
  global aws_s3_url
  global aws_access_key
  global aws_secret_key
  global github_url
  global github_token
  global jfx_weblog_key
  global repository
  global rl_rate
  global rl_limit
  global timelimit
  global logfile
  global allowjs
  global nocsp
  global nocache
  global verbose
  global pandoc

  try:
    if not os.getenv('JOURNAL_STREAM'):
      print('JinjaFx Server v' + __version__ + ' - Jinja2 Templating Tool')
      print('Copyright (c) 2020-2025 Chris Mason <chris@netnix.org>\n')

    parser = ArgumentParser(add_help=False)
    parser.add_argument('-s', action='store_true', required=True)
    parser.add_argument('-l', metavar='<address>', default='127.0.0.1', type=str)
    parser.add_argument('-p', metavar='<port>', default=8080, type=int)
    group_ex = parser.add_mutually_exclusive_group()
    group_ex.add_argument('-r', metavar='<directory>', type=w_directory)
    group_ex.add_argument('-s3', metavar='<aws s3 url>', type=str)
    group_ex.add_argument('-github', metavar='<owner>/<repo>[:<branch>]', type=str)
    parser.add_argument('-rl', metavar='<rate/limit>', type=rlimit)
    parser.add_argument('-tl', metavar='<time limit>', type=int, default=0)
    parser.add_argument('-ml', metavar='<memory limit>', type=int, default=0)
    parser.add_argument('-logfile', metavar='<logfile>', type=str)
    parser.add_argument('-weblog', action='store_true', default=False)
    parser.add_argument('-pandoc', action='store_true', default=False)
    group2_ex = parser.add_mutually_exclusive_group()
    group2_ex.add_argument('-allowjs', action='store_true', default=False)
    group2_ex.add_argument('-nocsp', action='store_true', default=False)
    parser.add_argument('-nocache', action='store_true', default=False)
    parser.add_argument('-v', action='store_true', default=False)
    args = parser.parse_args()
    allowjs = args.allowjs
    nocsp = args.nocsp
    nocache = args.nocache
    verbose = args.v

    if args.pandoc:
      from shutil import which
      pandoc = which('pandoc')

      if not pandoc:
        parser.error("argument -pandoc: unable to find pandoc within the path")

    if args.weblog:
      jfx_weblog_key = os.getenv('JFX_WEBLOG_KEY')

      if jfx_weblog_key is None:
        parser.error("argument -weblog: environment variable 'JFX_WEBLOG_KEY' is mandatory")

    if args.s3 is not None:
      aws_s3_url = args.s3
      aws_access_key = os.getenv('AWS_ACCESS_KEY')
      aws_secret_key = os.getenv('AWS_SECRET_KEY')

      if aws_access_key == None or aws_secret_key == None:
        parser.error("argument -s3: environment variables 'AWS_ACCESS_KEY' and 'AWS_SECRET_KEY' are mandatory")

    if args.github is not None:
      github_url = args.github
      github_token = os.getenv('GITHUB_TOKEN')

      if github_token == None:
        parser.error("argument -github: environment variable 'GITHUB_TOKEN' is mandatory")

    if args.logfile is not None:
      logfile = args.logfile

    if args.rl is not None:
      args.rl = args.rl.lower().split('/', 1)

      if args.rl[1].endswith('s'):
        rl_limit = int(args.rl[1][:-1])
      elif args.rl[1].endswith('m'):
        rl_limit = int(args.rl[1][:-1]) * 60
      elif args.rl[1].endswith('h'):
        rl_limit = int(args.rl[1][:-1]) * 3600
      else:
        rl_limit = int(args.rl[1][:-1])

      rl_rate = int(args.rl[0])

    timelimit = args.tl

    def signal_handler(*args):
      rflag[0] = 2

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    if args.ml:
      soft, hard = resource.getrlimit(resource.RLIMIT_AS)
      resource.setrlimit(resource.RLIMIT_AS, (args.ml * 1024 * 1024, hard))

    update_versioned_links(base + '/www')
    log(f'Starting JinjaFx Server (PID is {os.getpid()}) on http://{args.l}:{args.p}...')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((args.l, args.p))
    s.listen()

    rflag[0] = 1
    threads = []
    repository = args.r

    for i in range(n_threads):
      threads.append(JinjaFxThread(s, (args.l, args.p)))

    while rflag[0] < 2:
      time.sleep(0.1)

    log(f'Terminating JinjaFx Server...')


  except Exception as e:
    error = jinjafx._format_error(e)
    print(error.replace('__init__.py:', 'jinjafx_server.py:'), file=sys.stderr)
    sys.exit(-2)

  finally:
    if rflag[0] > 0:
      s.close()


def log(t, ae=''):
  global logring

  with llock:
    timestamp = datetime.datetime.now().strftime('%b %d %H:%M:%S.%f')[:19]

    if os.getenv('JOURNAL_STREAM'):
      print(re.sub(r'\033\[(?:1;[0-9][0-9]|0)m', '', t + ae))

    else:
      print('[' + timestamp + '] ' + t + ae)

    logring.append('[' + timestamp + '] ' + t + ae)
    logring = logring[-1024:]

    if logfile is not None:
      try:
        with open(logfile, 'at') as f:
          f.write('[' + timestamp + '] ' + re.sub(r'\033\[(?:1;[0-9][0-9]|0)m', '', t + ae) + '\n')

      except Exception as e:
        traceback.print_exc()
        print('[' + timestamp + '] ' + str(e))


def update_versioned_links(d):
  for fn in os.listdir(d):
    if fn.endswith('.html'):
      changed = False
      html = []

      with open(d + '/' + fn, 'rt') as fh:
        for ln in fh:
          m = re.search(r'(?:href|src)="/([a-f0-9]{8})/(.+?)"', ln)
          if m:
            if nocache:
              if m.group(1) != '00000000':
                ln = re.sub(m.group(1), '00000000', ln)
                changed = True
            else:
              with open(d + '/' + m.group(2), 'rb') as fh2:
                h = hashlib.sha256(fh2.read()).hexdigest()[:8]

                if h != m.group(1):
                  ln = re.sub(m.group(1), h, ln)
                  changed = True

          html.append(ln)

      if changed:
        with open(d + '/' + fn, 'wt') as fh:
          fh.writelines(html)


def w_directory(d):
  if not os.path.isdir(d):
    raise argparse.ArgumentTypeError("repository directory '" + d + "' must exist")
  elif not os.access(d, os.W_OK):
    raise argparse.ArgumentTypeError("repository directory '" + d + "' must be writable")
  return d


def rlimit(rl):
  if not re.match(r'(?i)^\d+/\d+[smh]$', rl):
    raise argparse.ArgumentTypeError("value must be rate/limit, e.g. 5/30s or 30/1h")
  return rl


def aws_s3_authorization(method, fname, region, headers):
  sheaders = ';'.join(map(lambda k: k.lower(), sorted(headers.keys())))
  srequest = headers['x-amz-date'][:8] + '/' + region + '/s3/aws4_request'
  cr = method.upper() + '\n/' + fname + '\n\n' + '\n'.join([ k.lower() + ':' + v for k, v in sorted(headers.items()) ]) + '\n\n' + sheaders + '\n' + headers['x-amz-content-sha256']
  s2s = 'AWS4-HMAC-SHA256\n' + headers['x-amz-date'] + '\n' + srequest + '\n' + hashlib.sha256(cr.encode('utf-8')).hexdigest()

  dkey = hmac.new(('AWS4' + aws_secret_key).encode('utf-8'), headers['x-amz-date'][:8].encode('utf-8'), hashlib.sha256).digest()
  drkey = hmac.new(dkey, region.encode('utf-8'), hashlib.sha256).digest()
  drskey = hmac.new(drkey, b's3', hashlib.sha256).digest()
  skey = hmac.new(drskey, b'aws4_request', hashlib.sha256).digest()

  signature = hmac.new(skey, s2s.encode('utf-8'), hashlib.sha256).hexdigest()
  headers['Authorization'] = 'AWS4-HMAC-SHA256 Credential=' + aws_access_key + '/' + srequest + ', SignedHeaders=' + sheaders + ', Signature=' + signature
  return headers


def aws_s3_delete(s3_url, fname):
  headers = {
    'Host': s3_url,
    'Content-Type': 'text/plain',
    'x-amz-content-sha256': hashlib.sha256(b'').hexdigest(),
    'x-amz-date': datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
  }
  headers = aws_s3_authorization('DELETE', fname, s3_url.split('.')[2], headers)
  return requests.delete('https://' + s3_url + '/' + fname, headers=headers)


def aws_s3_put(s3_url, fname, content, ctype):
  content = gzip.compress(content.encode('utf-8'))
  headers = {
    'Host': s3_url,
    'Content-Length': str(len(content)),
    'Content-Type': ctype,
    'Content-Encoding': 'gzip',
    'x-amz-content-sha256': hashlib.sha256(content).hexdigest(),
    'x-amz-date': datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
  }
  headers = aws_s3_authorization('PUT', fname, s3_url.split('.')[2], headers)
  return requests.put('https://' + s3_url + '/' + fname, headers=headers, data=content)


def aws_s3_get(s3_url, fname):
  headers = {
    'Host': s3_url,
    'Accept-Encoding': 'gzip',
    'x-amz-content-sha256': hashlib.sha256(b'').hexdigest(),
    'x-amz-date': datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
  }
  headers = aws_s3_authorization('GET', fname, s3_url.split('.')[2], headers)
  return requests.get('https://' + s3_url + '/' + fname, headers=headers)


def github_delete(github_url, fname, sha=None):
  headers = {
    'Authorization': 'Token ' + github_token,
    'Content-Type': 'application/json'
  }

  data = {
    'message': 'Delete ' + fname
  }

  if ':' in github_url:
    github_url, data['branch'] = github_url.split(':', 1)

  if sha is not None:
    data['sha'] = sha

  return requests.delete('https://api.github.com/repos/' + github_url + '/contents/' + fname, headers=headers, data=json.dumps(data))


def github_put(github_url, fname, content, sha=None):
  headers = {
    'Authorization': 'Token ' + github_token,
    'Content-Type': 'application/json'
  }

  data = {
    'message': 'Update ' + fname,
    'content': base64.b64encode(content.encode('utf-8')).decode('utf-8')
  }

  if ':' in github_url:
    github_url, data['branch'] = github_url.split(':', 1)

  if sha is not None:
    data['sha'] = sha

  return requests.put('https://api.github.com/repos/' + github_url + '/contents/' + fname, headers=headers, data=json.dumps(data))


def github_get(github_url, fname):
  headers = {
    'Authorization': 'Token ' + github_token
  }

  if ':' in github_url:
    github_url, branch = github_url.split(':', 1)
    return requests.get('https://api.github.com/repos/' + github_url + '/contents/' + fname + '?ref=' + branch, headers=headers)

  else:
    return requests.get('https://api.github.com/repos/' + github_url + '/contents/' + fname, headers=headers)


if __name__ == '__main__':
  main()
