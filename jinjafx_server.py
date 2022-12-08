#!/usr/bin/env python3

# JinjaFx Server - Jinja2 Templating Tool
# Copyright (c) 2020-2022 Chris Mason <chris@netnix.org>
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

from http.server import HTTPServer, BaseHTTPRequestHandler
from jinja2 import __version__ as jinja2_version
import jinjafx, os, io, sys, socket, signal, threading, yaml, json, base64, time, datetime, resource
import re, argparse, zipfile, hashlib, traceback, glob, hmac, uuid, struct, binascii, gzip, requests
import cmarkgfm, emoji, func_timeout

__version__ = '22.12.1'

lock = threading.RLock()
base = os.path.abspath(os.path.dirname(__file__))

aws_s3_url = None
aws_access_key = None
aws_secret_key = None
github_url = None
github_token = None
repository = None
verbose = False

rtable = {}
rl_rate = 0
rl_limit = 0
logfile = None
timelimit = 0

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
        if args[1] == '200' or args[1] == '204':
          ansi = '32'
        elif args[1] == '304':
          ansi = '33'
        else:
          ansi = '31'

        if (args[1] != '204' and args[1] != '404' and args[1] != '501') or self.critical or verbose:
          src = str(self.client_address[0])
          ctype = ''

          if hasattr(self, 'headers'):
            if 'X-Forwarded-For' in self.headers:
              src = self.headers['X-Forwarded-For']

            if 'Content-Type' in self.headers:
              if 'Content-Encoding' in self.headers:
                ctype = ' (' + self.headers['Content-Type'] + ':' + self.headers['Content-Encoding'] + ')'
              else:
                ctype = ' (' + self.headers['Content-Type'] + ')'

          if str(args[1]) == 'ERR':
            log('[' + src + '] [\033[1;' + ansi + 'm' + str(args[1]) + '\033[0m]' + ' \033[1;' + ansi + 'm' + str(args[2]) + '\033[0m')
        
          elif self.command == 'POST':
            if self.elapsed is not None:
              log('[' + src + '] [\033[1;' + ansi + 'm' + str(args[1]) + '\033[0m]' + ' \033[1;33m' + self.command + '\033[0m ' + path + ctype + ' [' + self.format_bytes(self.length) + '] in ' + str(self.elapsed) + 'ms')
            else:
              log('[' + src + '] [\033[1;' + ansi + 'm' + str(args[1]) + '\033[0m]' + ' \033[1;33m' + self.command + '\033[0m ' + path + ctype + ' [' + self.format_bytes(self.length) + ']')

          elif self.command != None:
            if (args[1] != '200' and args[1] != '304') or (not path.endswith('.js') and not path.endswith('.css') and not path.endswith('.png')) or verbose:
              log('[' + src + '] [\033[1;' + ansi + 'm' + str(args[1]) + '\033[0m]' + ' ' + self.command + ' ' + path)


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


  def do_GET(self, head=False, cache=True, versioned=False):
    try:
      self.critical = False
      self.hide = False

      fpath = self.path.split('?', 1)[0]
  
      r = [ 'text/plain', 500, '500 Internal Server Error\r\n', sys._getframe().f_lineno ]
  
      if fpath == '/ping':
        cache = False
        r = [ 'text/plain', 200, 'OK\r\n'.encode('utf-8'), sys._getframe().f_lineno ]
  
      else:
        if fpath == '/':
          fpath = '/index.html'
          self.hide = not verbose
  
        if re.search(r'^/dt/[A-Za-z0-9_-]{1,24}$', fpath):
          fpath = '/index.html'
  
        if re.search(r'^/[a-f0-9]{8}/', fpath):
          fpath = fpath[fpath[1:].index('/') + 1:]
          versioned = True
  
        if re.search(r'^/get_dt/[A-Za-z0-9_-]{1,24}$', fpath):
          dt = ''
          self.critical = True
  
          if aws_s3_url or github_url or repository:
            if aws_s3_url:
              rr = aws_s3_get(aws_s3_url, 'jfx_' + fpath[8:] + '.yml')
    
              if rr.status_code == 200:
                r = [ 'application/yaml', 200, rr.text.encode('utf-8'), sys._getframe().f_lineno ]
    
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
  
                r = [ 'application/yaml', 200, content.encode('utf-8'), sys._getframe().f_lineno ]
    
                dt = content
    
              elif rr.status_code == 401:
                r = [ 'text/plain', 403, '403 Forbidden\r\n'.encode('utf-8'), sys._getframe().f_lineno ]
    
              elif rr.status_code == 404:
                r = [ 'text/plain', 404, '404 Not Found\r\n'.encode('utf-8'), sys._getframe().f_lineno ]
    
            else:
              fpath = os.path.normpath(repository + '/jfx_' + fpath[8:] + '.yml')
    
              if os.path.isfile(fpath):
                with open(fpath, 'rb') as f:
                  rr = f.read()
                  dt = rr.decode('utf-8')
    
                  r = [ 'application/yaml', 200, rr, sys._getframe().f_lineno ]
  
                os.utime(fpath, None)
    
              else:
                r = [ 'text/plain', 404, '404 Not Found\r\n'.encode('utf-8'), sys._getframe().f_lineno ]
  
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
                        r = [ 'text/plain', 401, '401 Unauthorized\r\n'.encode('utf-8'), sys._getframe().f_lineno ]
  
                    else:
                      r = [ 'text/plain', 401, '401 Unauthorized\r\n'.encode('utf-8'), sys._getframe().f_lineno ]
  
                else:
                  r = [ 'text/plain', 401, '401 Unauthorized\r\n'.encode('utf-8'), sys._getframe().f_lineno ]
  
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
  
        else:
          r = [ 'text/plain', 404, '404 Not Found\r\n'.encode('utf-8'), sys._getframe().f_lineno ]
  
      etag = '"' + hashlib.sha256(r[2]).hexdigest() + '"'
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
        self.send_header('X-Content-Type-Options', 'nosniff')
  
      if versioned:
        self.send_header('Cache-Control', 'public, max-age=31536000')
  
      elif not cache:
        self.send_header('Cache-Control', 'no-store, max-age=0')
  
      elif r[1] == 200 or r[1] == 304:
        if r[1] == 200:
          self.send_header('Content-Security-Policy', "frame-ancestors 'none'")
          self.send_header('Referrer-Policy', 'strict-origin-when-cross-origin')
  
        self.send_header('Cache-Control', 'max-age=0, must-revalidate')
        self.send_header('ETag', etag)
  
      self.end_headers()
      if not head:
        self.wfile.write(r[2])

    except Exception as e:
      log('Exception: ' + str(e))


  def do_OPTIONS(self):
    self.critical = False
    self.hide = False
    self.send_response(204)
    self.send_header('Allow', 'OPTIONS, HEAD, GET, POST')
    self.end_headers()


  def do_HEAD(self):
    self.do_GET(True)


  def do_POST(self):
    self.critical = False
    self.hide = False
    self.elapsed = None

    uc = self.path.split('?', 1)
    params = { x[0]: x[1] for x in [x.split('=') for x in uc[1].split('&') ] } if len(uc) > 1 else { }
    fpath = uc[0]

    r = [ 'text/plain', 500, '500 Internal Server Error\r\n', sys._getframe().f_lineno ]

    if 'Content-Length' in self.headers:
      if int(self.headers['Content-Length']) < (2048 * 1024):
        postdata = self.rfile.read(int(self.headers['Content-Length']))
        self.length = len(postdata)

        if 'Content-Encoding' in self.headers and self.headers['Content-Encoding'] == 'gzip':
          postdata = gzip.decompress(postdata)

        if fpath == '/jinjafx':
          if self.headers['Content-Type'] == 'application/json':
            try:
              gvars = {}

              dt = json.loads(postdata.decode('utf-8'))
              template = base64.b64decode(dt['template']) if 'template' in dt and len(dt['template'].strip()) > 0 else b''
              data = base64.b64decode(dt['data']) if 'data' in dt and len(dt['data'].strip()) > 0 else b''
  
              if 'vars' in dt and len(dt['vars'].strip()) > 0:
                gyaml = base64.b64decode(dt['vars']).decode('utf-8')

                if 'vault_password' in dt:
                  vpw = base64.b64decode(dt['vault_password']).decode('utf-8')

                  if gyaml.lstrip().startswith('$ANSIBLE_VAULT;'):
                    gyaml = jinjafx.Vault().decrypt(gyaml.encode('utf-8'), vpw).decode('utf-8')

                  def yaml_vault_tag(loader, node):
                    return jinjafx.Vault().decrypt(node.value.encode('utf-8'), vpw).decode('utf-8')

                  yaml.add_constructor('!vault', yaml_vault_tag, yaml.SafeLoader)

                y = yaml.load(gyaml, Loader=yaml.SafeLoader)
                if y != None:
                  gvars.update(y)

              try:
                st = round(time.time() * 1000)
                ocount = 0

                if timelimit > 0:
                  outputs = func_timeout.func_timeout(timelimit, jinjafx.JinjaFx().jinjafx, args=(template.decode('utf-8'), data.decode('utf-8'), gvars, 'Output', [], True))
                else:
                  outputs = jinjafx.JinjaFx().jinjafx(template.decode('utf-8'), data.decode('utf-8'), gvars, 'Output', [], True)
                            
              except func_timeout.FunctionTimedOut:
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
                output = '\n'.join(outputs[o]) + '\n'
                if len(output.strip()) > 0:
                  if oformat == 'markdown' or oformat == 'md':
                    o = oname + ':html'
                    options = (cmarkgfm.cmark.Options.CMARK_OPT_GITHUB_PRE_LANG | cmarkgfm.cmark.Options.CMARK_OPT_SMART | cmarkgfm.cmark.Options.CMARK_OPT_UNSAFE)
                    output = cmarkgfm.github_flavored_markdown_to_html(html_escape(output), options).replace('&amp;amp;', '&amp;').replace('&amp;', '&')
                    head = '<!DOCTYPE html>\n<html>\n<head>\n'
                    head += '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.1.0/github-markdown.min.css" crossorigin="anonymous">\n'
                    head += '<style>\n  pre, code { white-space: pre-wrap !important; word-wrap: break-word !important; }\n</style>\n</head>\n'
                    output = emoji.emojize(output, language='alias').encode('ascii', 'xmlcharrefreplace').decode('utf-8')
                    output = head + '<body>\n<div class="markdown-body">\n' + output + '</div>\n</body>\n</html>\n'

                  elif oformat == 'html':
                    output = output.encode('ascii', 'xmlcharrefreplace').decode('utf-8')

                  jsr['outputs'].update({ o: base64.b64encode(output.encode('utf-8')).decode('utf-8') })
                  if o != '_stderr_':
                    ocount += 1
  
              if ocount == 0:
                raise Exception('nothing to output')
  
            except Exception as e:
              tb = traceback.format_exc()
              match = re.search(r'[\s\S]*File "<(?:template|unknown)>", line ([0-9]+), in.*template', tb, re.IGNORECASE)
              if match:
                error = 'error[template.j2:' + match.group(1) + ']: ' + type(e).__name__ + ': ' + str(e)
              elif 'yaml.SafeLoader' in tb:
                error = 'error[vars.yml]: ' + type(e).__name__ + ': ' + str(e)
              else:
                error = 'error[' + str(sys.exc_info()[2].tb_lineno) + ']: ' + type(e).__name__ + ': ' + str(e)

              jsr = {
                'status': 'error',
                'error': error
              }
              self.log_request('ERR', error);
  
            r = [ 'application/json', 200, json.dumps(jsr), sys._getframe().f_lineno ]
  
          else:
            r = [ 'text/plain', 400, '400 Bad Request\r\n', sys._getframe().f_lineno ]
  
        else:
          if fpath == '/download':
            if self.headers['Content-Type'] == 'application/json':
              lterminator = '\r\n' if 'User-Agent' in self.headers and 'windows' in self.headers['User-Agent'].lower() else '\n'

              try:
                outputs = json.loads(postdata.decode('utf-8'))

                zfile = io.BytesIO()
                z = zipfile.ZipFile(zfile, 'w', zipfile.ZIP_DEFLATED)

                for o in outputs:
                  (oname, oformat) = o.rsplit(':', 1) if ':' in o else (o, 'text')
                  ofile = re.sub(r'_+', '_', re.sub(r'[^A-Za-z0-9_. -/]', '_', os.path.normpath(oname)))
                  outputs[o] = re.sub(r'\r?\n', lterminator, base64.b64decode(outputs[o]).decode('utf-8'))

                  if '.' not in ofile:
                    if oformat == 'html':
                      ofile += '.html'
                    else:
                      ofile += '.txt'

                  z.writestr(ofile, outputs[o])

                z.close()

                self.send_response(200)
                self.send_header('Content-Type', 'application/zip')
                self.send_header('Content-Length', str(len(zfile.getvalue())))
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.send_header('X-Download-Filename', 'Outputs.' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S') + '.zip')
                self.end_headers()
                self.wfile.write(zfile.getvalue())
                return

              except Exception as e:
                log('Exception: ' + str(e))
                r = [ 'text/plain', 400, '400 Bad Request\r\n', sys._getframe().f_lineno ]

            else:
              r = [ 'text/plain', 400, '400 Bad Request\r\n', sys._getframe().f_lineno ]

          elif fpath == '/get_link':
            if aws_s3_url or github_url or repository:
              if self.headers['Content-Type'] == 'application/json':
                try:
                  remote_addr = str(self.client_address[0])
                  dt_password = ''
                  dt_opassword = ''
                  dt_mpassword = ''
                  dt_revision = 1

                  if hasattr(self, 'headers'):
                    if 'X-Forwarded-For' in self.headers:
                      remote_addr = self.headers['X-Forwarded-For']
                    if 'X-Dt-Password' in self.headers:
                      dt_password = self.headers['X-Dt-Password']
                    if 'X-Dt-Open-Password' in self.headers:
                      dt_opassword = self.headers['X-Dt-Open-Password']
                    if 'X-Dt-Modify-Password' in self.headers:
                      dt_mpassword = self.headers['X-Dt-Modify-Password']
                    if 'X-Dt-Revision' in self.headers:
                      dt_revision = int(self.headers['X-Dt-Revision'])

                  ratelimit = False
                  if rl_rate != 0:
                    rtable.setdefault(remote_addr, []).append(int(time.time()))

                    if len(rtable[remote_addr]) > rl_rate:
                      if (rtable[remote_addr][-1] - rtable[remote_addr][0]) <= rl_limit:
                        ratelimit = True

                      rtable[remote_addr] = rtable[remote_addr][-rl_rate:]

                  if not ratelimit:
                    dt = json.loads(postdata.decode('utf-8'))

                    vdt = {}

                    dt_yml = '---\n'
                    dt_yml += 'dt:\n'

                    if 'datasets' in dt:
                      dt_yml += '  datasets:\n'

                      for ds in dt['datasets']:
                        vdt['data'] = base64.b64decode(dt['datasets'][ds]['data']).decode('utf-8') if 'data' in dt['datasets'][ds] and len(dt['datasets'][ds]['data'].strip()) > 0 else ''
                        vdt['vars'] = base64.b64decode(dt['datasets'][ds]['vars']).decode('utf-8') if 'vars' in dt['datasets'][ds] and len(dt['datasets'][ds]['vars'].strip()) > 0 else ''

                        dt_yml += '    "' + ds + '":\n'

                        if vdt['data'] == '':
                          dt_yml += '      data: ""\n\n'
                        else:
                          dt_yml += '      data: |2\n'
                          dt_yml += re.sub('^', ' ' * 8, vdt['data'].rstrip(), flags=re.MULTILINE) + '\n\n'

                        if vdt['vars'] == '':
                          dt_yml += '      vars: ""\n\n'
                        else:
                          dt_yml += '      vars: |2\n'
                          dt_yml += re.sub('^', ' ' * 8, vdt['vars'].rstrip(), flags=re.MULTILINE) + '\n\n'

                    else :
                      vdt['data'] = base64.b64decode(dt['data']).decode('utf-8') if 'data' in dt and len(dt['data'].strip()) > 0 else ''
                      vdt['vars'] = base64.b64decode(dt['vars']).decode('utf-8') if 'vars' in dt and len(dt['vars'].strip()) > 0 else ''

                      if vdt['data'] == '':
                        dt_yml += '  data: ""\n\n'
                      else:
                        dt_yml += '  data: |2\n'
                        dt_yml += re.sub('^', ' ' * 4, vdt['data'].rstrip(), flags=re.MULTILINE) + '\n\n'

                      if vdt['vars'] == '':
                        dt_yml += '  vars: ""\n\n'
                      else:
                        dt_yml += '  vars: |2\n'
                        dt_yml += re.sub('^', ' ' * 4, vdt['vars'].rstrip(), flags=re.MULTILINE) + '\n\n'

                    vdt['template'] = base64.b64decode(dt['template']).decode('utf-8') if 'template' in dt and len(dt['template'].strip()) > 0 else ''

                    if vdt['template'] == '':
                      dt_yml += '  template: ""\n'
                    else:
                      dt_yml += '  template: |2\n'
                      dt_yml += re.sub('^', ' ' * 4, vdt['template'], flags=re.MULTILINE) + '\n'

                    dt_yml += '\nrevision: ' + str(dt_revision) + '\n'

                    dt_hash = hashlib.sha256(dt_yml.encode('utf-8')).hexdigest()
                    dt_yml += 'dt_hash: "' + dt_hash + '"\n'

                    if 'id' in params:
                      if re.search(r'^[A-Za-z0-9_-]{1,24}$', params['id']):
                        dt_link = params['id']

                      else:
                        raise Exception("invalid link format")

                    else:
                      dt_link = self.encode_link(hashlib.sha256((str(uuid.uuid1()) + ':' + dt_yml).encode('utf-8')).digest()[:6])

                    dt_filename = 'jfx_' + dt_link + '.yml'

                    def update_dt(rdt, dt_yml, r):
                      mm = re.search(r'dt_mpassword: "(\S+)"', rdt)
                      mo = re.search(r'dt_password: "(\S+)"', rdt)

                      if mm != None or mo != None:
                        if dt_password != '':
                          rpassword = mm.group(1) if mm != None else mo.group(1)
                          t = binascii.unhexlify(rpassword.encode('utf-8'))
                          if t != self.derive_key(dt_password, t[2:int(t[1]) + 2], t[0]):
                            r = [ 'text/plain', 401, '401 Unauthorized\r\n', sys._getframe().f_lineno ]

                        else:
                          r = [ 'text/plain', 401, '401 Unauthorized\r\n', sys._getframe().f_lineno ]

                      if r[1] != 401:
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

                    if aws_s3_url:
                      rr = aws_s3_get(aws_s3_url, dt_filename)
                      if rr.status_code == 200:
                        m = re.search(r'revision: (\d+)', rr.text)
                        if m != None:
                          if dt_revision <= int(m.group(1)):
                            r = [ 'text/plain', 409, '409 Conflict\r\n', sys._getframe().f_lineno ]

                        if r[1] != 409:
                          dt_yml, r = update_dt(rr.text, dt_yml, r)

                      if r[1] == 500 or r[1] == 200:
                        dt_yml = add_client_fields(dt_yml, remote_addr)
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

                        m = re.search(r'revision: (\d+)', content)
                        if m != None:
                          if dt_revision <= int(m.group(1)):
                            r = [ 'text/plain', 409, '409 Conflict\r\n', sys._getframe().f_lineno ]

                        if r[1] != 409:
                          dt_yml, r = update_dt(content, dt_yml, r)

                      if r[1] == 500 or r[1] == 200:
                        dt_yml = add_client_fields(dt_yml, remote_addr)
                        rr = github_put(github_url, dt_filename, dt_yml, sha)

                        if str(rr.status_code).startswith('2'):
                          r = [ 'text/plain', 200, dt_link + '\r\n', sys._getframe().f_lineno ]

                        elif rr.status_code == 401:
                          r = [ 'text/plain', 403, '403 Forbidden\r\n', sys._getframe().f_lineno ]

                        else:
                          print(rr.text)

                    else:
                      dt_filename = os.path.normpath(repository + '/' + dt_filename)

                      if os.path.isfile(dt_filename):
                        with open(dt_filename, 'rb') as f:
                          rr = f.read()

                        m = re.search(r'revision: (\d+)', rr.decode('utf-8'))
                        if m != None:
                          if dt_revision <= int(m.group(1)):
                            r = [ 'text/plain', 409, '409 Conflict\r\n', sys._getframe().f_lineno ]

                        if r[1] != 409:
                          dt_yml, r = update_dt(rr.decode('utf-8'), dt_yml, r)

                      if r[1] == 500 or r[1] == 200:
                        dt_yml = add_client_fields(dt_yml, remote_addr)
                        with open(dt_filename, 'w') as f:
                          f.write(dt_yml)

                          r = [ 'text/plain', 200, dt_link + '\r\n', sys._getframe().f_lineno ]

                  else:
                    r = [ 'text/plain', 429, '429 Too Many Requests\r\n', sys._getframe().f_lineno ]

                except Exception as e:
                  log('Exception: ' + str(e))
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


def main(rflag=[0]):
  global aws_s3_url
  global aws_access_key
  global aws_secret_key
  global github_url
  global github_token
  global repository
  global rl_rate
  global rl_limit
  global timelimit
  global logfile
  global verbose

  try:
    print('JinjaFx Server v' + __version__ + ' - Jinja2 Templating Tool')
    print('Copyright (c) 2020-2022 Chris Mason <chris@netnix.org>\n')

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
    parser.add_argument('-v', action='store_true', default=False)
    args = parser.parse_args()
    verbose = args.v
    
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

    log('Starting JinjaFx Server (PID is ' + str(os.getpid()) + ') on http://' + args.l + ':' + str(args.p) + '...')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((args.l, args.p))
    s.listen(16)

    rflag[0] = 1
    threads = []
    repository = args.r

    for i in range(16):
      threads.append(JinjaFxThread(s, (args.l, args.p)))

    while rflag[0] < 2:
      time.sleep(0.1)

    log('Terminating JinjaFx Server...')


  except Exception as e:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    print('error[' + str(exc_tb.tb_lineno) + ']: ' + str(e), file=sys.stderr)
    sys.exit(-2)

  finally:
    if rflag[0] > 0:
      s.shutdown(1)
      s.close()


def log(t):
  with lock:
    timestamp = datetime.datetime.now().strftime('%b %d %H:%M:%S.%f')[:19]
    print('[' + timestamp + '] ' + t)

    if logfile is not None:
      try:
        with open(logfile, 'at') as f:
          f.write('[' + timestamp + '] ' + re.sub(r'\033\[(?:1;[0-9][0-9]|0)m', '', t) + '\n')

      except Exception as e:
        traceback.print_exc()
        print('[' + timestamp + '] ' + str(e))


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


def aws_s3_put(s3_url, fname, content, ctype):
  content = gzip.compress(content.encode('utf-8'))
  headers = {
    'Host': s3_url,
    'Content-Length': str(len(content)),
    'Content-Type': ctype,
    'Content-Encoding': 'gzip',
    'x-amz-content-sha256': hashlib.sha256(content).hexdigest(),
    'x-amz-date': datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
  }
  headers = aws_s3_authorization('PUT', fname, s3_url.split('.')[2], headers)
  return requests.put('https://' + s3_url + '/' + fname, headers=headers, data=content)


def aws_s3_get(s3_url, fname):
  headers = {
    'Host': s3_url,
    'Accept-Encoding': 'gzip',
    'x-amz-content-sha256': hashlib.sha256(b'').hexdigest(),
    'x-amz-date': datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
  }
  headers = aws_s3_authorization('GET', fname, s3_url.split('.')[2], headers)
  return requests.get('https://' + s3_url + '/' + fname, headers=headers)


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
