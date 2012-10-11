import socket
from functools import partial
from itertools import izip
from tornado import iostream
from .exception import ResponseError

DEBUG = False

class Connection(object):
    def __init__(self, host, port, on_connect=None, on_disconnect=None, timeout=None, io_loop=None):
        self.host = host
        self.port = port
        self.on_connect = on_connect
        self.on_disconnect = on_disconnect
        self.timeout = timeout
        self.io_loop = io_loop

    def connect(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        if self.timeout:
            s.settimeout(self.timeout)
        s.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        self.stream = iostream.IOStream(s, io_loop=self.io_loop)
        self.stream.connect((self.host, self.port), self.on_connect)

    def disconnect(self):
        if self.stream:
            try:
                self.stream.close()
            except socket.error as e:
                pass
            self.stream = None

    def write(self, data):
        if DEBUG: print "WRITE", data
        return self.stream.write(data)

    def read_until(self, endln, callback):
        return self.stream.read_until(endln, callback)

    def read_bytes(self, endln, callback):
        return self.stream.read_bytes(endln, callback)

#
#
#
def reply_to_boolean(msg):
    return bool(msg)

def reply_to_array(msg):
    if not hasattr(msg, '__iter__'):
        return [msg]
    return msg

def reply_to_int(msg):
    return int(msg)

def reply_assert_ok(msg):
    return "OK" == msg

def reply_assert_pong(msg):
    return "PONG" == msg

def reply_to_set(msg):
    return set(msg)

def reply_to_dict(msg):
    return dict(izip(msg[::2], msg[1::2]))

def reply_to_str(msg):
    return msg or ''

class Message(object):
    def __init__(self, client, channel):
        self.client  = client
        self.channel = channel

    def message(self):
        pass

#
#
#
class Command(object):
    def __init__(self, cmd, callbacks, *args):
        self.callbacks = callbacks
        self.cmd       = cmd
        self.args      = args

    def call(self, *args):
        if DEBUG: print 'DOING CALLBACKS', args
        for cb in self.callbacks:
            try:
                if cb:
                    cb(*args)
            except Exception as e:
                print e

    def format(self, *tokens):
        cmds  = ["$%s\r\n%s\r\n" % (len(v), v) for v in [self.encode(t) for t in tokens]]
        return "*%s\r\n%s" % (len(tokens), ''.join(cmds))

    def encode(self, value):
        if isinstance(value, str):
            return value
        if isinstance(value, unicode):
            return value.encode('utf-8')
        return str(value)

    def to_bytes(self):
        return self.format(self.cmd, *self.args)

#
#
#
class Client(object):
    REPLY_MAP = {
        ### Key Commands
        'DEL'          : reply_to_boolean,
        'EXISTS'       : reply_to_boolean,
        'EXPIRE'       : reply_to_boolean,
        'EXPIREAT'     : reply_to_boolean,
        'KEYS'         : reply_to_array,
        'MOVE'         : reply_to_boolean,
        'PERSIST'      : reply_to_boolean,
        'RANDOMKEY'    : reply_to_str,
        'RENAME'       : reply_assert_ok,
        'RENAMENX'     : reply_to_int,
        #   'SORT' ...
        'TTL'          : reply_to_int,
        'TYPE'         : reply_to_str,
        #   'EVAL' ...

        ### Hashes
        'HDEL'         : reply_to_boolean,
        'HEXISTS'      : reply_to_boolean,
        'HGET'         : reply_to_str,
        'HGETALL'      : reply_to_dict,
        'HINCRBY'      : reply_to_int,
        'HKEYS'        : reply_to_set,
        'HLEN'         : reply_to_int,
        'HMGET'        : reply_to_array,
        'HMSET'        : reply_assert_ok,
        'HSET'         : reply_to_boolean,
        'HSETNX'       : reply_to_boolean,
        'HVALS'        : reply_to_array,

        ###  Strings
        'APPEND'       : reply_to_int,
        'DECR'         : reply_to_int,
        'DECRBY'       : reply_to_int,
        'GET'          : reply_to_str,
        'GETBIT'       : reply_to_boolean,
        'GETRANGE'     : reply_to_str,
        'GETSET'       : reply_to_str,
        'INCR'         : reply_to_int,
        'INCRBY'       : reply_to_int,
        'MGET'         : reply_to_array,
        'MSET'         : reply_assert_ok,
        'MSETNX'       : reply_to_boolean,
        'SET'          : reply_assert_ok,
        'SETEX'        : reply_assert_ok,
        'SETNX'        : reply_to_boolean,
        'SETRANGE'     : reply_assert_ok,
        'STRLEN'       : reply_to_int,

        ###  Lists - no blocking commands implemented!
        'RPOP'         : reply_to_str,
        'LINDEX'       : reply_to_str,
        'LINSERT'      : reply_to_int,
        'LLEN'         : reply_to_int,
        'LPOP'         : reply_to_str,
        'LPUSH'        : reply_to_int,
        'LPUSHX'       : reply_to_int,
        'LRANGE'       : reply_to_array,
        'LREM'         : reply_to_int,
        'LSET'         : reply_assert_ok,
        'LTRIM'        : reply_assert_ok,
        'RPOP'         : reply_to_str,
        'RPOPLPUSH'    : reply_to_str,
        'RPUSH'        : reply_to_int,
        'RPUSHX'       : reply_to_int,

        ###  Sets
        'SADD'         : reply_to_int,
        'SCARD'        : reply_to_int,
        'SDIFF'        : reply_to_set,
        'SDIFFSTORE'   : reply_to_int,
        'SINTER'       : reply_to_set,
        'SINTERSTORE'  : reply_to_int,
        'SISMEMBER'    : reply_to_boolean,
        'SMEMBERS'     : reply_to_set,
        'SMOVE'        : reply_to_boolean,
        'SPOP'         : reply_to_str,
        'SRANDMEMBER'  : reply_to_str,
        'SREM'         : reply_to_int,
        'SUNION'       : reply_to_set,
        'SUNIONSTORE'  : reply_to_int,

        ###  Sorted Sets
        'ZADD'         : reply_to_int,
        'ZCARD'        : reply_to_int,
        'ZCOUNT'       : reply_to_int,
        'ZINCRBY'      : reply_to_int,
        'ZINTERSTORE'  : reply_to_int,
        'ZRANGE'       : reply_to_array,
        'ZRANGEBYSCORE': reply_to_array,
        'ZRANK'        : reply_to_int,
        'ZREM'         : reply_to_int,
        'ZREMRANGEBYRANK': reply_to_int,
        'ZREMRANGEBYSCORE': reply_to_int,
        'ZREVRANGE'    : reply_to_array,
        'ZREVRANGEBYSCORE': reply_to_array,
        'ZREVRANK'     : reply_to_int,
        'ZSCORE'       : reply_to_int,
        'ZUNIONSTORE'  : reply_to_int,

        ###  Connection
        'AUTH'         : reply_to_boolean,
        'ECHO'         : reply_to_str,
        'PING'         : reply_assert_pong,
        # SELECT is not implemented, client/connection thing

        ### Server
        'BGREWRITEAOF' : reply_to_boolean,
        'BGSAVE'       : reply_to_boolean,
        'FLUSHALL'     : reply_assert_ok,
        'FLUSHDB'      : reply_assert_ok,
        'DBSIZE'       : reply_to_int,
        'INFO'         : reply_to_dict,
        'LASTSAVE'     : reply_to_int,
        'SAVE'         : reply_to_boolean,
    }

    SUBSCRIBE_CMDS = {
        'SUBSCRIBE', 'UNSUBSCRIBE',
        'PSUBSCRIBE', 'PUNSUBSCRIBE',
    }

    def __init__(self, host='localhost', port=6379, password=None, io_loop=None):
        self.password = password
        self.io_loop  = io_loop
        self.port     = port
        self.host     = host
        self.connection = None

        self.queue    = []
        self.subscriptions = {}

        #
        #
        #
        for cmd in self.REPLY_MAP.keys():
            # Rename aware from 'del' operator
            name = cmd.lower() if cmd != 'DEL' else 'delete'
            if not hasattr(self, name):
                setattr(self, name, partial(self._default_cmd, cmd))


    def connect(self, callback=None):
        if not self.connection:
            def cb(*args):
                self.on_connect(callback)

            self.connection = Connection(host=self.host, port=self.port, on_connect=cb, io_loop=self.io_loop)

            self.connection.connect()

    #
    #
    #
    def send_command(self, cmd, callbacks, *args):
        if callbacks is None:
            callbacks = []
        elif not hasattr(callbacks, '__iter__'):
            callbacks = [callbacks]

        if self.subscriptions and cmd not in self.SUBSCRIBE_CMDS:
            # TODO - Raise
            return

        qcmd = Command(cmd, callbacks, *args)
        self.queue.append(qcmd)

        if len(self.queue) == 1:
            self.connection.write(qcmd.to_bytes())
            self.connection.read_until("\r\n", self.recv_response)

    def recv_response(self, orig_data):
        data = orig_data[:-2]        # remove CRLF

        if len(data) == 0:
            # TODO - disconnect
            raise IOError('Disconnected')

        if DEBUG: print "RECV", data

        if data == '$-1':
            response = None
        elif data == '*0' or data == '*-1':
            response = []
        else:
            ch = data[0]

            if ch == '*':
                self.handle_multibulk(int(data[1:]), self.finish_cmd)
                return
            elif ch == '$':
                # Add 2 to include the CRLF at the end
                self.connection.read_bytes(int(data[1:]) + 2, self.recv_bytes)
                return
            elif ch == '+':
                response = data[1:]
            elif ch == ':':
                response = int(data[1:])
            elif ch == '-':
                if data.startswith('-ERR:'):
                    response = ResponseError(data[5:])
                else:
                    response = ResponseError(data[1:])
            else:
                raise ResponseError("Unknown response type %s" % data)
        
        self.finish_cmd(response)

    def handle_multibulk(self, count, callback):
        params = []

        def got_bytes(orig_data):
            data = orig_data[:-2]

            if DEBUG: print "RECV(multibulk)", data

            params.append(data)

            if len(params) != count:
                return self.connection.read_until('\r\n', got_data)

            callback(params)

        def got_data(orig_data):
            data = orig_data[:-2]
            
            if DEBUG: print "RECV(multibulk)", data

            if data == '$-1':
                params.append(data)
            elif data[0] == '$':
                return self.connection.read_bytes(int(data[1:]) + 2, got_bytes)
            elif data[0] == ':':
                params.append(int(data[1:]))

            if len(params) != count:
                return self.connection.read_until('\r\n', got_data)
            callback(params)
            
        self.connection.read_until('\r\n', callback=got_data)

    def recv_bytes(self, orig_data):
        """Called by a Bulk reply"""
        self.finish_cmd(orig_data[:-2])

    def finish_cmd(self, response):
        done_cmd = self.queue.pop(0)

        if self.queue:
            qcmd = self.queue[0]
            self.connection.write(qcmd.to_bytes())
            self.connection.read_until('\r\n', self.recv_response)

        done_cmd.call(self, self.REPLY_MAP[done_cmd.cmd](response) if (
                            done_cmd.cmd in self.REPLY_MAP and 
                            not isinstance(response, ResponseError)
                        ) else response)

    def remove_subscription(self, r, channel):
        if r:
            del self.subscriptions[channel]

        self.subscription_listener()

    def add_subscription(self, r, channel, cb):
        # print "IN ADD", channel
        if r:
            self.subscriptions[channel] = cb

        self.subscription_listener()

    def subscription_listener(self):
        if not self.subscriptions:
            return

        def handle_data(data):
            self.handle_multibulk(int(data[1:]), self.handle_sub_notification)

        self.connection.read_until('\r\n', handle_data)

    def handle_sub_notification(self, data):
        # TODO - ASSERT data[0] == 'message'

        cmd, channel, msg = data
        
        self.subscriptions[channel](self, msg)

        if not self.queue:
            self.subscription_listener()


    #
    #
    #
    def on_connect(self, callback):
        def cb(*args):
            if callback:
                callback(self)

        if self.password:
            self.auth(self.password, cb)
        else:
            cb()

    def on_disconnect(self):
        pass

    #
    #  Default command handler, if you want special handling then just define the method and it 
    #   will be used instead
    #
    def _default_cmd(self, cmd, *args, **kwargs):
        if 'callback' in kwargs:
            callback = kwargs.pop('callback')
        elif args and hasattr(args[-1], '__call__'):
            callback = args.pop(-1)
        else:
            callback = None
        self.send_command(cmd, callback, *args)

    #
    #
    #

    def subscribe(self, channel, callback=None):
        self.send_command('SUBSCRIBE', lambda c,r:self.add_subscription(r, channel, callback), channel)

    def psubscribe(self, channel, callback=None):
        self.send_command('PSUBSCRIBE', lambda c,r:self.add_subscription(r, channel, callback), channel)

    def unsubscribe(self, channel, callback=None):
        self.send_command('SUBSCRIBE', [lambda c,r:self.remove_subscription(r, channel), callback], channel)

    def punsubscribe(self, channel, callback=None):
        self.send_command('PSUBSCRIBE', [lambda c,r:self.remove_subscription(r, channel), callback], channel)
