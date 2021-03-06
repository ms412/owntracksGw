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
__VERSION__ = "0.4"
__DATE__ = "04.09.2017"
__author__ = "Markus Schiesser"
__contact__ = "M.Schiesser@gmail.com"
__copyright__ = "Copyright (C) 2017 Markus Schiesser"
__license__ = 'GPL v3'

import time
import os
import glob
import json
import cherrypy
from collections import defaultdict
from configobj import ConfigObj
from library.nesteddict import nesteddict
from library.filemanager import filemanager
from library.logger import Logger
from library.mqttclient import mqttclient
from library.httpd import gateway


class owntrackGw(object):

    def __init__(self,configfile):
        self._configfile = configfile

        self._storage = nesteddict()

        self._mqttc = None

        self._logCfg = None
        self._brokerCfg = None
        self._owntracksCfg = None
        self._httpdCfg = None


        self._cardFileManager = None
        self._cmdFileManager = None
        self._cardUpdate = True

    def readConfigFile(self):
        _cfg = ConfigObj(self._configfile)

        self._brokerCfg = _cfg.get('BROKER')
        self._logCfg = _cfg.get('LOGGING')
        self._httpdCfg = _cfg.get('HTTPD')
        self._owntracksCfg = _cfg.get('OWNTRACKS')
        return True

    def readClientConfig(self):
        self._cardFileManager = filemanager()
        self._cardFileManager.setPath(self._owntracksCfg.get('CARDS','./cards'))
        self._cardFileManager.setExtendsion('*.json')

        self._cmdFileManager = filemanager()
        self._cmdFileManager.setPath(self._owntracksCfg.get('CMD','./cmd'))
        self._cmdFileManager.setExtendsion('*.json')
        return True

    def startLogging(self):
        print('Logging',self._logCfg)
        self._log = Logger('OWNTRACKSGW')
        self._log.handle(self._logCfg.get('LOGMODE'),self._logCfg)
        self._log.level(self._logCfg.get('LOGLEVEL','DEBUG'))
        return True

    def startHttpd(self):
        _httpdCfg = {}
        _httpdCfg['server.socket_host'] = str(self._httpdCfg.get('SOCKET','0.0.0.0'))
        _httpdCfg['server.socket_port'] = int(self._httpdCfg.get('PORT', 9888))

        cherrypy.config.update(_httpdCfg)

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

        _gw = gateway(self.msgBroker)
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

        self._mqttc.register_callback('owntracks/+/+',self.mqttCallback)
      #  self._mqttc.register_callback('owntracks/+/+/card', self._updateCard)
       # self._mqttc.register_callback('owntracks/#', self._updatePossition)
    #    self._mqttc.callback(self.msgBroker)
        self._mqttc.connect()
        self._mqttc.run()

        self._mqttc.subscribe('+/+')
        return True

    def _readFileContent(self,file,content):
        _base = os.path.basename(file)
        _filename = os.path.splitext(_base)[0]
        try:
            with open(file)as fh:
                data = json.load(fh)
                print('test', data)
                part = _filename.split('-')
                self._storage[part[0] + '/' + part[1]][content]['DATA'] = data
                self._storage[part[0] + '/' + part[1]][content]['DATE'] = 0.0
                fh.close()

        except IOError:
            print('not found',_filename)
            part = _filename.split('-')
            del self._storage[part[0] + '/' + part[1]][content]
            data = None

        return True

    def updateConfig(self):
        _filelist = self._cardFileManager.modified()
        for _file in _filelist:
            print('Update CARD')
            self._readFileContent(_file,'CARD')

        _filelist = self._cmdFileManager.modified()
        for _file in _filelist:
            print('Update CMD')
            self._readFileContent(_file,'CMD')

       # for item, key in self._storage.items():
#            print(item,key)

        #print('Storage',self._storage)

    def mqttCallback(self,_topic,_msg):
        print(_topic,msg)

    def msgBroker(self,_user,_device,_msg):
        msg = json.loads(_msg)
        connectType = ''
       # print('Type',type(_msg))
       # _cardUpdateFlag = False
        _msgList = []
        #_tempStorage = {}
        #_strTopic = 'owntracks/'+_user+'/'+_device
        _strTopic = _user + '/' + _device


        if 'location' in msg['_type']:
            print('location message',_user,_device,msg)

   #       self._mqttc.publish(_strTopic, _msg,0,True)
          #  print('Storage',self._storage)

        #for item, key in self._storage.items():
         #   x = self._storage[item]['CARD']['DATE']
          #  print('xxx',x)

       # if _strTopic not in self._storage:
      #      _cardUpdateFlag = True

            self._storage[_strTopic]['LOCATION']['DATA'] = msg
            self._storage[_strTopic]['LOCATION']['DATE'] = msg['tst']

            connectType=msg['conn']

        print('Storage',self._storage)
        for key, item in self._storage.items():
            print('key', key)
            print('item', item)

            if not _strTopic in key:
               # print('TEST0',item['CARD']['DATA'])
                #print('TEST1',item['CARD']['DATE'])
                msg = item['LOCATION']['DATA']
                print('INFO',msg)
               # _msgList.append(json.loads(item['LOCATION']['DATA']))
                _msgList.append(json.loads(str({})))
               # print('xxx',_msgList)

            if 'w' in connectType:
                _msgList.append(item['CARD']['DATA'])
              #  if self._cardUpdate:
                            #   print(item['CARD']['DATA'])
               #     if
                #    _msgList.append(item['CARD']['DATA'])
                  #  _msgList.append(json.loads(str(item['CARD']['DATA'])))
                #print('xxx',_msgList)
         #   if _cardUpdateFlag:
          #      for name, card in self._storageCard.items():
           #         _msgList.append(json.loads(card))

        print('Message',_msgList)
        return _msgList

    def createMsg(self):
        _msgList = []






    def run(self):
        self.readConfigFile()
     #   self.startLogging()
        self.readClientConfig()
        self.updateConfig()
        self.mqttclient()
        self.startHttpd()
     #   self.msgBroker('x','x','yy')
      #  self.readCard()
        while(True):
            self.updateConfig()
            time.sleep(30)

        #self.mqttclient()
        #self.httpd()
        #self.publishCards()



if __name__ == '__main__':

    owntracks = owntrackGw('owntracksGW.cfg')
    owntracks.run()