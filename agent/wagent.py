import zmq
import zmq.ssh
import json
import logging

REMOTE_ADDR = "tcp://127.0.0.2:5555"
# send/receive timeout
TIMEOUT = 10000
logging.raiseExceptions = False

class WAgent:
    def __init__(self, hostname, login):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, TIMEOUT)
        server = "{}@{}".format(login, hostname)
        self.tunnel = zmq.ssh.tunnel_connection(self.socket, REMOTE_ADDR, server, paramiko=True, timeout=10)

    def make_request_json(self, req):
        jreq = json.dumps(req)
        jres = self.make_request(jreq)
        res = json.loads(jres)
        return res

    def make_request(self, req):
        breq = bytes(req)
        self.socket.send(breq)
        res = self.socket.recv()
        return res

    def close(self):
        self.socket.close()

class RBDAgent(WAgent):

    def snap_list(self, image):
        req = {
            'action': 'rbd',
            'subaction': 'snap_list',
            'image': image,
        }
        res = self.make_request_json(req)
        return (res['exitcode'], res['message'])

    def snap_create(self, image, snap_name):
        req = {
            'action': 'rbd',
            'subaction': 'snap_create',
            'image': image,
            'snap_name': snap_name,
        }
        res = self.make_request_json(req)
        return (res['exitcode'], res['message'])
    
    def snap_rollback(self, image, snap_name):
        req = {
            'action': 'rbd',
            'subaction': 'snap_rollback',
            'image': image,
            'snap_name': snap_name,
        }
        res = self.make_request_json(req)
        return (res['exitcode'], res['message'])

    def snap_remove(self, image, snap_name):
        req = {
            'action': 'rbd',
            'subaction': 'snap_remove',
            'image': image,
            'snap_name': snap_name,
        }
        res = self.make_request_json(req)
        return (res['exitcode'], res['message'])

    def clone(self, source, target):
        req = {
            'action': 'rbd',
            'subaction': 'clone',
            'source': source,
            'target': target,
        }
        res = self.make_request_json(req)
        return (res['exitcode'], res['message'])

