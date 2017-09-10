import random
import string
import json

import cherrypy
from cherrypy.lib import auth_basic



class sample(object):
    def callback(self,msg):
        print('sample',msg)


@cherrypy.expose
class gateway(object):

    def __init__(self):
        self._callback = None
        self._authenticate = False

    def register_callback(self,_callback):
        self._callback = _callback

    @cherrypy.tools.accept(media='application/json')
    def GET(self):
        return cherrypy.session['mystring']

    def POST(self, length=8):
       # print ('hier',cherrypy.request.headers['Authorization'])
        if cherrypy.request.headers['Authorization'] == 'Basic dGdkc2NtNDE6dGVzdA==':
            user = cherrypy.request.headers['X-Limit-U']
            passwd = cherrypy.request.headers['X-Limit-D']


           #print('Header',cherrypy.request.headers)
            length = cherrypy.request.headers['Content-Length']
            user = cherrypy.request.headers['X-Limit-U']
            passwd = cherrypy.request.headers['X-Limit-D']
            authorize = cherrypy.request.headers['Authorization']
           # print(user,passwd,authorize)

            rawbody = cherrypy.request.body.read(int(length))



            print('Receive: ',rawbody)
           # input_json = json.loads(rawbody)
          #  print(input_json)
            _r = self._callback(user,passwd,rawbody)
            cherrypy.response.status = 200
            cherrypy.response.headers['Content-Type']='application/json'
            response = json.dumps(_r)
            print('Responced:', response)
    #    some_string = ''.join(random.sample(string.hexdigits, int(length)))
     #   cherrypy.session['mystring'] = some_string
      #  return some_string
     #   return json.dumps(input_json)
      #  return json.dumps({"_type":"location","tid":"12","acc":20,"batt":63,"conn":"w","lat":46.9748776,"lon":7.4716709,"t":"u","tst":1504273932,"_cp":True})
        return response.encode('utf8')

    def PUT(self, another_string):
        cherrypy.session['mystring'] = another_string

    def DELETE(self):
        cherrypy.session.pop('mystring', None)




def start():

#if __name__ == '__main__':
    USERS={"admin":"2Sec4You", "test":"test", "test":"mobil"}

    conf = {
        '/protected/area': {
            'tools.auth_basic.on': True,
            'tools.auth_basic.realm': 'localhost',
            'tools.auth_basic.checkpassword': validate_password
        }
    }

  #  cherrypy.quickstart(gateway(sample), '/', conf)

    print('START')
    cherrypy.config.update('server.conf')
    _s = sample()
    print('TEST')
    gw = gateway(_s)
    print('config',cherrypy.config)
    cherrypy.tree.mount(gw,'/','app.conf')
    cherrypy.engine.start()


  #  cherrypy.quickstart(gw,'/',config=conf)
    #cherrypy.quickstart(gw, '/', 'server.conf')
