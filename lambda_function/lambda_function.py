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

import sys, os, re, logging
sys.path.append(os.environ['LAMBDA_TASK_ROOT'] + '/lib')

def lambda_handler(event, context):
  logger = logging.getLogger()
  method = event['requestContext']['http']['method']
  pathname = event['rawPath']

  logger.info("IN FUNCTION")
  logger.info("SYSPATH is " + str(sys.path))
  
  if method == 'GET':
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

        if pathname.endswith('.js'):
          headers['content-type'] = 'text/javascript'

        elif pathname.endswith('.css'):
          headers['content-type'] = 'text/css'

        elif pathname.endswith('.png'):
          import base64
          headers['content-type'] = 'image/png'
          data = base64.b64encode(data).decode('utf-8')
          isBase64Encoded = True

        else:
          headers['content-type'] = 'text/html'
    
        return {
          "headers": headers,
          "statusCode": 200,
          "isBase64Encoded": isBase64Encoded,
          "body": data
        }
    
    return {
      "statusCode": 404,
      "body": "Not Found"
    }

  elif method == 'POST':
    if pathname == '/jinjafx':
      pass
 
    return {
      "statusCode": 404,
      "body": "Not Found"
    }
   
  return {
    "statusCode": 501,
    "body": "Not Implemented"
  }

