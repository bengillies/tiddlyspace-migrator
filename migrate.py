"""
migrate a set of named spaces from one tiddlyspace to the local one
"""
from httplib2 import Http
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.serializer import Serializer
from sys import argv
from tiddlyweb.config import config
from tiddlywebconfig import config as twconfig
from tiddlyweb.util import merge_config
from tiddlywebplugins.utils import get_store
from tiddlywebplugins.tiddlyspace.spaces import _make_space
import simplejson

def main(server, user, spaces):
    merge_config(config, twconfig)
    store = get_store(config)
    for space in spaces:
        make_space(space, user, store)
        import_tiddlers(server, store, space)

def make_space(space, user, store):
    environ = {
        'tiddlyweb.store': store,
        'tiddlyweb.usersign': {
            'name': user
        }
    }
    _make_space(environ, space)

def import_tiddlers(server, store, space):
    http = Http()
    url = 'http://%s.%s/bags/%s_public/tiddlers?fat=1' % (space, server, space)
    response, content = http.request(url, headers={
            'Accept': 'application/json'
        })
    if response['status'] != '200':
        raise Exception(space + ' failed')

    tiddlers = simplejson.loads(content)
    for tiddler in tiddlers:
        save_tiddler(store, tiddler)

def save_tiddler(store, tiddler):
    title = tiddler['title']
    bag = tiddler['bag']
    tiddler_json = simplejson.dumps(tiddler)
    tid = Tiddler(title)
    s = Serializer('json')
    s.object = tid
    s.from_string(tiddler_json)
    tid.bag = bag
    store.put(tid)

if __name__ == '__main__':
    server = argv[1]
    user = argv[2]
    spaces = argv[3:]
    main(server, user, spaces)
