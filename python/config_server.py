import gevent
import bottle
import redis
import json
import os
from collections import defaultdict

from gevent import monkey
monkey.patch_all()

APPCONFIG = "appconfig:env:%s"
APPINDEX = "appconfig:index"

"""
    .env and .ini dynamic configurator
    .env is suitable to foreman, .ini is the goodole ini file

    section.test, 1
    section.elmo, 2

    conf/ini file:
    [section]
    test = 1
    elmo = 2

    env file
    section.test=1
    section.elmo=2

"""

p = redis.ConnectionPool(host='localhost', port=6379, db=0)
conn = redis.Redis(connection_pool=p)


@bottle.get('/ini/<appname>')
def send_ini(appname):
    s = conn.sismember(APPINDEX, appname)
    if s is False:
        bottle.abort(404, "Application not found")

    h = conn.hgetall(APPCONFIG % appname)

    if h is None:
        bottle.abort(401, "Application has no configuration")

    options = defaultdict(lambda: [])

    for k in h.keys():
        l = k.split('.')
        if len(l) == 2:
            options[l[0]].append((l[1], h[k]))
        else:
            options['_'].append((l[0], h[k]))
    buffer = ""
    for option in options.keys():
        if option is not '_':
            buffer = buffer + "[%s]\n" % option
        t = options[option]
        for a in t:
            buffer = buffer + "%s=%s\n" % (a[0], a[1])

    return buffer


@bottle.get('/env/<appname>')
def send_env(appname):
    s = conn.sismember(APPINDEX, appname)
    if s is False:
        bottle.abort(404, "Application not found")
    h = conn.hgetall(APPCONFIG % appname)
    if h is None:
        bottle.abort(401, "Application has no configuration")
    buffer = ""
    for a in h.keys():
        buffer = buffer + "%s=%s\n" % (a, h[a])

    return buffer


@bottle.post('/env/<appname>')
def post_env(appname):
    try:
        key = bottle.request.POST['key']
        val = bottle.request.POST['val']
        s = conn.sismember(APPINDEX, appname)
        if s is False:
            bottle.abort(404, "Application not found")
        conn.hset(APPCONFIG % appname, key, val)
    except Exception, e:
        print e


@bottle.post('/app/new')
def create_app():
    appname = bottle.request.POST['appname']
    s = conn.sismember(APPINDEX, appname)
    if s is True:
        bottle.abort(401, "Application already exists")
    conn.sadd(APPINDEX, appname)


@bottle.post('/app/delete')
def delete_app():
    appname = bottle.request.POST['appname']
    s = conn.sismember(APPINDEX, appname)
    if s is False:
        bottle.abort(401, "Application not found")
    conn.srem(APPINDEX, appname)
    conn.delete(APPCONFIG % appname)

bottle.debug=True
bottle.run(server='gevent', port=os.environ.get('PORT', 5000), host="0.0.0.0")
