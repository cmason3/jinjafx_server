# JinjaFx Lambda - Jinja2 Templating Tool
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

import sys, os, re, hashlib

def lambda_handler(event, context):
  method = event['requestContext']['http']['method']
  pathname = event['rawPath']

  if method == 'OPTIONS':
    return {
      "headers": {
        "allow": "OPTIONS, GET, POST"
      },
      "statusCode": 204
    }

  elif method == 'GET':
    if pathname == '/':
      pathname = '/index.html'
  
    if re.search(r'^/[A-Z0-9_-]+\.[A-Z0-9]+$', pathname, re.IGNORECASE) and os.path.isfile(os.environ['LAMBDA_TASK_ROOT'] + '/www' + pathname):
      with open(os.environ['LAMBDA_TASK_ROOT'] + '/www' + pathname, 'rb') as f:
        isBase64Encoded = False
        headers = {}
        
        data = f.read()

        if pathname == '/index.html':
          from jinja2 import __version__ as jinja2_version
          from jinjafx import __version__ as jinjafx_version
          data = data.decode('utf-8').replace('{{ jinjafx.version }}', jinjafx_version + ' / Jinja2 v' + jinja2_version).replace('{{ get_link }}', 'false').encode('utf-8')

        etag = hashlib.sha256(data).hexdigest()
        headers['cache-control'] = 'max-age=0, must-revalidate'
        headers['etag'] = etag

        if pathname.endswith('.js'):
          headers['content-type'] = 'text/javascript'

        elif pathname.endswith('.css'):
          headers['content-type'] = 'text/css'

        elif pathname.endswith('.png'):
          import base64
          headers['content-type'] = 'image/png'
          data = base64.b64encode(data)
          isBase64Encoded = True

        else:
          headers['content-type'] = 'text/html'

        if 'if-none-match' in event['headers'] and event['headers']['if-none-match'] == etag:
          return {
            "headers": headers,
            "statusCode": 304
          }

        else:
          return {
            "headers": headers,
            "statusCode": 200,
            "isBase64Encoded": isBase64Encoded,
            "body": data.decode('utf-8')
          }
    
    return {
      "statusCode": 404,
      "body": "Not Found - " + str(event)
    }

  elif method == 'POST':
    if pathname == '/jinjafx':
      import json, yaml, base64, time, traceback, jinjafx

      try:
        gvars = {}

        dt = json.loads(event['body'])
        template = base64.b64decode(dt['template']) if 'template' in dt and len(dt['template'].strip()) > 0 else b''
        data = base64.b64decode(dt['data']) if 'data' in dt and len(dt['data'].strip()) > 0 else b''

        if 'vars' in dt and len(dt['vars'].strip()) > 0:
          gyaml = base64.b64decode(dt['vars'])

          y = yaml.load(gyaml, Loader=yaml.SafeLoader)
          if y != None:
            gvars.update(y)

        st = round(time.time() * 1000)
        outputs = jinjafx.JinjaFx().jinjafx(template.decode('utf-8'), data.decode('utf-8'), gvars, 'Output')
        ocount = 0

        jsr = {
          'status': 'ok',
          'elapsed': round(time.time() * 1000) - st,
          'outputs': {}
        }

        for o in outputs:
          output = '\n'.join(outputs[o]) + '\n'
          if len(output.strip()) > 0:
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
      
      return {
        "headers": {
          "content-type": "application/json"
        },
        "statusCode": 200,
        "body": json.dumps(jsr)
      }

    elif pathname == '/download':
      import json, io, zipfile, datetime, base64

      try:
        outputs = json.loads(event['body'])

        zfile = io.BytesIO()
        z = zipfile.ZipFile(zfile, 'w', zipfile.ZIP_DEFLATED)

        for o in outputs:
          ofile = re.sub(r'_+', '_', re.sub(r'[^A-Za-z0-9_. -/]', '_', os.path.normpath(o)))
          outputs[o] = base64.b64decode(outputs[o]).decode('utf-8')

          if '.' not in ofile:
            if '<html' in outputs[o].lower() and '<\/html>' in outputs[o].lower():
              ofile += '.html'
            else:
              ofile += '.txt'

          z.writestr(ofile, outputs[o])

        z.close()

        return {
          "headers": {
            "content-type": "application/zip",
            "x-download-filename": "Outputs." + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".zip"
          },
          "statusCode": 200,
          "isBase64Encoded": True,
          "body": base64.b64encode(zfile.getvalue()).decode('utf-8')
        }

      except:
        return {
          "statusCode": 400,
          "body": "Bad Request"
        }
 
    return {
      "statusCode": 404,
      "body": "Not Found"
    }
   
  return {
    "statusCode": 501,
    "body": "Not Implemented"
  }

