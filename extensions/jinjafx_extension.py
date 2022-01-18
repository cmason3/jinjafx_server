from jinja2.ext import Extension

import hashlib, re

class JinjaFxExtension(Extension):
  def __init__(self, environment):
    Extension.__init__(self, environment)
    environment.filters['cisco_snmpv3_key'] = self.__cisco_snmpv3_key
    environment.filters['junos_snmpv3_key'] = self.__junos_snmpv3_key

  def __expand_snmpv3_key(self, password, algorithm):
    h = hashlib.new(algorithm)
    h.update(((password * (1048576 // len(password))) + password[:1048576 % len(password)]).encode('utf-8'))
    return h.digest()

  def __cisco_snmpv3_key(self, password, engineid, algorithm='sha1'):
    ekey = self.__expand_snmpv3_key(password, algorithm)

    h = hashlib.new(algorithm)
    h.update(ekey + bytearray.fromhex(engineid) + ekey)
    return ':'.join([h.hexdigest()[i:i + 2] for i in range(0, len(h.hexdigest()), 2)])

  def __junos_snmpv3_key(self, password, engineid, algorithm='sha1', prefix = '80000a4c'):
    ekey = self.__expand_snmpv3_key(password, algorithm)

    if re.match(r'^(?:[a-f0-9]{2}:){5}[a-f0-9]{2}$', engineid):
      engineid = prefix + '03' + ''.join(engineid.split(':'))

    elif re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$', engineid):
      engineid = prefix + '01' + ''.join("{:02x}".format(int(o), 2) for o in engineid.split('.'))

    else:
      engineid = prefix + '04' + ''.join("{:02x}".format(ord(c)) for c in engineid)

    h = hashlib.new(algorithm)
    h.update(ekey + bytearray.fromhex(engineid) + ekey)
    return h.hexdigest()
