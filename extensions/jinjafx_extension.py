from jinja2.ext import Extension

import hashlib

class JinjaFxExtension(Extension):
  def __init__(self, environment):
    Extension.__init__(self, environment)
    environment.filters['cisco_snmpv3_key'] = self.__cisco_snmpv3_key

  def __cisco_snmpv3_key(self, password, engineid, algorithm='sha1'):
    h1 = hashlib.new(algorithm)
    h1.update(((password * (1048576 // len(password))) + password[:1048576 % len(password)]).encode('utf-8'))

    h2 = hashlib.new(algorithm)
    h2.update(h1.digest() + bytearray.fromhex(engineid) + h1.digest())
    return ':'.join([h2.hexdigest()[i:i + 2] for i in range(0, len(h2.hexdigest()), 2)])
