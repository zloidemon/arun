from arun import ARun, ARunService
import asyncio
import logging


log = logging.getLogger('application')


class NewApp(ARunService):
    def __init__(self, loop=None, **kwargs):
        self.loop = loop
        self.config = kwargs['config']
        self.stats = kwargs['stats']
        self.reconfig = kwargs['reconfig']
        self.args = kwargs['args']

    @property
    def signals(self):
        sigs = {
            'SIGTERM': lambda signal, frame: self.reconfig('custom sig'),
        }
        return sigs

    @asyncio.coroutine
    def display_date(self):
        self.stats['xxx'] = 0
        while True:
            log.error('%s',
                      self.config.get('main', 'test'),
                      extra={'code': '33010'})
            self.stats['xxx'] += 1
            yield from asyncio.sleep(1)

    @asyncio.coroutine
    def run(self):
        yield from self.display_date()

args = {
    '--example': {'help': 'Example argument'}
}

errors = {
    '33010': 'Example error'
}
ARun(name='application',
     description='Example application',
     args=args,
     errordb=errors).start(NewApp)
