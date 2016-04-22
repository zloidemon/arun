import argparse
import asyncio
import logging
import logging.config
import traceback
import configparser
import sys
import socket
import signal
from aiohttp import web
from aiohttp_jrpc import jrpc_errorhandler_middleware
from setproctitle import setproctitle
from datetime import datetime
from .Manage import ManageInterface
from .Logging import LOGGING_CONF, CounterFilter


class ARun(object):
    def __init__(self, name=None, version='', description=None, manage=None,
                 args=None, errordb={}):
        self.version = version
        self.argparse = argparse.ArgumentParser(prog=name,
                                                description=description)
        self.loop = asyncio.get_event_loop()
        self.config = None
        self.manage = ManageInterface
        self.name = name
        self.time_run = datetime.now()
        self.init_args = args
        self.stats = {
            'log': {
                'ERROR': 0,
                'CRITICAL': 0,
                'WARNING': 0,
            },
            'codes': {e: 0 for e in errordb},
        }

        if manage:
            self.manage = manage

        if self.name:
            setproctitle(self.name)
            self.log = logging.getLogger(self.name)
        else:
            self.log = logging.getLogger('root')

        self.log.addFilter(CounterFilter(self.stats))

    def free_port(self, ipv4):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ipv4, 0))
        port = sock.getsockname()[1]
        sock.close()
        return port

    def __setupargs(self):
        self.argparse.add_argument('-v', '--version',
                                   action='version',
                                   version='%(prog)s {version}'.format(
                                            version=self.version))
        self.argparse.add_argument('--verbose',
                                   action='store_true',
                                   help='increase output verbosity')
        self.argparse.add_argument('--manage',
                                   action='store_true',
                                   help='enable web based manage interface')
        self.argparse.add_argument('--config', type=str, required=True,
                                   help='set up config file')
        self.argparse.add_argument('--logconfig', type=str,
                                   help='set up logging configuration')

        if self.init_args:
            for a in self.init_args:
                self.argparse.add_argument(a, **self.init_args[a])

        self.args = self.argparse.parse_args()

    def __sighup_handler(self, signal, frame):
        self.log.warn('catched SIGHUP signal')
        self.setupconf('got SIGHUP')

    def __setupsig(self, scriptsig={}):
        handlers = {
            'SIGHUP': self.__sighup_handler
        }
        handlers.update(scriptsig)
        for s in handlers:
            sig_name = getattr(signal, s)
            signal.signal(sig_name, handlers[s])

    def __setuplogger(self):
        if self.args.logconfig:
            logging.config.fileConfig(self.args.logconfig)
        else:
            logging.config.dictConfig(LOGGING_CONF(self))

    @asyncio.coroutine
    def __init_manage(self):
        try:
            try:
                manage_ip = self.config.get('manage', 'ip')
            except:
                manage_ip = '127.0.0.1'
                self.log.warning(
                    'init default IPv4 %s address for mange interface',
                    manage_ip)

            try:
                manage_port = self.config.getint('manage', 'port')
            except:
                manage_port = self.free_port(manage_ip)
                self.log.warning(
                    'got free port %s for mange interface',
                    manage_port)

            try:
                manage_location = self.config.get('manage', 'location')
            except:
                manage_location = '/manage'
                self.log.warning(
                    'init default value %s for mange interface',
                    manage_location)

            manage = web.Application(loop=self.loop,
                                     middlewares=[
                                        jrpc_errorhandler_middleware,
                                     ])
            manage.router.add_route('POST', manage_location, self.manage)
            manage.service = self

            self.log.info('starting manage interface on http://%s:%s%s',
                          manage_ip, manage_port, manage_location)

            yield from self.loop.create_server(manage.make_handler(),
                                               manage_ip, manage_port)
        except Exception:
            self.log.critical('can not init manage interface\n%s',
                              traceback.format_exc())

    @asyncio.coroutine
    def __init(self, application):
        if self.args.manage:
            yield from self.__init_manage()

        yield from application.run()

    def setupconf(self, reason='no reason'):
        self.log.info('reload configuration: %s', reason)
        if not self.config:
            self.config = configparser.ConfigParser()

        self.config.read(self.args.config)

    def start(self, script):
        try:
            self.__setupargs()
            self.__setuplogger()
            self.setupconf()
        except Exception:
            self.log.critical('can not setup settings\n%s',
                              traceback.format_exc())
            sys.exit('Error: can not setup settings')

        self.log.info('setup configuration signal handling')

        application = script(loop=self.loop, logger=self.log,
                             config=self.config, stats=self.stats,
                             reconfig=self.setupconf, args=self.args)

        try:
            self.__setupsig(application.signals)
        except Exception:
            self.log.critical('can not init signals\n%s',
                              traceback.format_exc())
            sys.exit('Error: can not init signals')

        try:
            self.log.info('prepare to run your application')
            self.loop.run_until_complete(self.__init(application))
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.log.info('have gotten signal from keyboard')
        except Exception:
            self.log.critical('exception\n%s', traceback.format_exc())
        finally:
            self.log.info('server shutdown')
            self.loop.close()
