#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


__app__ = "owntracks Gateway"
__VERSION__ = "0.3"
__DATE__ = "03.09.2017"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2017 Markus Schiesser"
__license__ = 'GPL v3'

import time
import os
import glob
import json
import cherrypy
from configobj import ConfigObj
from library.logger import Logger
from library.mqttclient import mqttclient
from library.httpd import gateway


class owntrackGW(object):

    def __init__(self,configfile):
        self._configfile = configfile

        self._storage = {}

        self._storageCard = {}

        self._mqttc = None

        self._logCfg = None
        self._brokerCfg = None
        self._owntracksCfg = None
        self._httpdCfg = None

    def readConfig(self):
        _cfg = ConfigObj(self._configfile)

        self._brokerCfg = _cfg.get('BROKER')
        self._logCfg = _cfg.get('LOGGING')
        self._httpdCfg = _cfg.get('HTTPD')
        self._owntracksCfg = _cfg.get('OWNTRACKS')

        print(_cfg)
        self._tempfile = 'test'
        self._dirCard = './card'

    def startLogging(self):
        print('Logging',self._logCfg)
        self._log = Logger('OWNTRACKSGW')
        self._log.handle(self._logCfg.get('LOGMODE'),self._logCfg)
        self._log.level(self._logCfg.get('LOGLEVEL','DEBUG'))
        return True

    def readCard(self):
        print('OWntracks cfg',self._owntracksCfg)
        _dirCard = self._owntracksCfg['CARDS']

        for _file in glob.glob(os.path.join(_dirCard, '*.json')):
            print(_file)
            _base = os.path.basename(_file)
            _filename = os.path.splitext(_base)[0]
            try:
                with open(_file)as fh:
                    data = json.load(fh)
                    print('test',data)
                    part = _filename.split('-')
                    self._storageCard[part[0]+'/'+part[1]]=data
                    fh.close()

            except IOError:
                data = None
        #for filename in os.listdir(self._dirCard):

         #   script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
          #  rel_path = "2091/data.txt"
           # abs_file_path = os.path.join(script_dir, rel_path)
        print(self._storageCard)

        return True

    def publishCards(self):
        print('card Storage',self._storageCard)
        for key, item in self._storageCard.items():
            self._mqttc.publish(key,item,0,True)

        return

    def httpd(self):
        _httpdCfg = {}
        _httpdCfg['server.socket_host'] = str(self._httpdCfg.get('SOCKET','0.0.0.0'))
        _httpdCfg['server.socket_port'] = int(self._httpdCfg.get('PORT', 9888))

        cherrypy.config.update(_httpdCfg)

      #  cherrypy.config.socket_host = str(self._httpdCfg.get('SOCKET','0.0.0.0'))
       # cherrypy.config.socket_port  = int(self._httpdCfg.get('PORT', 9888))
       # cherrypy.config.update['server.socket_port'] = str(self._httpdCfg.get('PORT', 9888))
      #  _gw = gateway(self.frontend)
        USERS = {"admin": "2Sec4You", "test": "test", "test": "mobil"}

        conf = {
            '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
               # 'tools.sessions.on': True,
                'tools.response_headers.on': True,
                'tools.response_headers.headers': [('Content-Type', 'application/json')],
                'tools.encode.on': True,
                'tools.encode.encoding': 'utf-8'
             #   'tools.auth_basic.on': True,
              #  'tools.auth_basic.realm': 'localhost'
               # 'tools.auth_basic.checkpassword': validate_password
            }

        }

        #  cherrypy.quickstart(gateway(sample), '/', conf)

       # print('START')
        #cherrypy.config.update('server.conf')
      #  _s = sample()
      #  print('TEST')
        _gw = gateway(self.frontend)
        print('config', cherrypy.config)
        cherrypy.tree.mount(_gw,'/',conf)
        cherrypy.engine.start()

        return True



    def mqttclient(self):
        print('connect mqtt')
        _host = str(self._brokerCfg.get('HOST','192.168.2.254'))
        _port = int(self._brokerCfg.get('PORT',1883))
        _user = str(self._brokerCfg.get('USER','mqtt'))
        _passwd = str(self._brokerCfg.get('PASSWD','2Sec4You'))
        self._mqttc = mqttclient(self._brokerCfg)


       # self._mqttc.callback('owntracks/+/#')

        self._mqttc.register_callback('owntracks/+/+',self._updatePossition)
      #  self._mqttc.register_callback('owntracks/+/+/card', self._updateCard)
       # self._mqttc.register_callback('owntracks/#', self._updatePossition)
        self._mqttc.connect()
        self._mqttc.run()

        self._mqttc.subscribe('owntracks/#')
        return True


    def _updatePossition(self,_client,_data,_msg):
        _topic = _msg.topic
        _payload = _msg.payload
        print('update possition',_topic, _payload)
#        _timestamp = _payload['tst']
        self._storage[_topic]=_payload

        return

    def _updateCard(self,_topic,_payload):

        return

    def frontend(self,_user,_device,_msg):
       # print('Type',type(_msg))
        _cardUpdateFlag = False
        _msgList = []
        _tempStorage = {}
        _strTopic = 'owntracks/'+_user+'/'+_device

        self._mqttc.publish(_strTopic, _msg,0,True)

       # _newClient = self._storage.get(_strTopic,False)
        if _strTopic not in self._storage:
            _cardUpdateFlag = True


        self._storage[_strTopic] = _msg
       # _tempStorage['Date'] = time.time()

        #self._storage[_strTopic] = _tempStorage

        #print('print Storage',self._storage)

        for key, item in self._storage.items():
       #     print('for loop',key, item,_strTopic)

            if not _strTopic in key:
               _msgList.append(json.loads(item))

            if _cardUpdateFlag:
                for name, card in self._storageCard.items():
                    _msgList.append(json.loads(card))


        return _msgList

    def run(self):
        self.readConfig()
     #   self.startLogging()
        self.readCard()
        self.mqttclient()
        self.httpd()
        self.publishCards()

if __name__ == '__main__':

    owntracks = owntrackGW('owntracksGW.cfg')
    owntracks.run()