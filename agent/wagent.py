import zmq
import zmq.ssh
import json
import logging

REMOTE_ADDR = "tcp://127.0.0.2:5555"
# send/receive timeout
TIMEOUT = 10000
logging.raiseExceptions = False

class WAgentManager:
    def __init__(self, agent_class):
        self.agent_class = agent_class
        self.agents = []

    def search(self, hostname, login):
        for a in self.agents:
            if a.hostname == hostname and a.login == login:
                return a
        return None

    def __connect(self, hostname, login):
        new_agent = self.agent_class(hostname, login)
        self.agents.append(new_agent)
        return new_agent

    def get(self, hostname, login):
        agent = self.search(hostname, login)
        if not agent:
            agent = self.__connect(hostname, login)
        return agent


class WAgentException(Exception):
    def __init__(self, exitcode, err):
        self.message = "Error({}): {}".format(exitcode, err)
        super(WAgentException, self).__init__(self.message)
        self.exitcode = exitcode
        self.err = err


class WAgent:
    def __init__(self, hostname, login):
        self.hostname = hostname
        self.login = login
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.setsockopt(zmq.RCVTIMEO, TIMEOUT)
        server = "{}@{}".format(login, hostname)
        self.tunnel = zmq.ssh.tunnel_connection(self.socket, REMOTE_ADDR, server, paramiko=True, timeout=10)

    def make_request_json(self, req):
        jreq = json.dumps(req)
        jres = self.make_request(jreq)
        res = json.loads(jres)
        if res['exitcode'] > 0:
            raise WAgentException(res['exitcode'], res['message'])
        return res

    def make_request(self, req):
        breq = bytes(req)
        self.socket.send(breq)
        res = self.socket.recv()
        return res

    def close(self):
        self.socket.close()
        self.tunnel.terminate()


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


#rbd_agent_manager = WAgentManager(RBDAgent)

