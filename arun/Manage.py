from aiohttp_jrpc import Service
from datetime import datetime


class ManageInterface(Service):
    def stats(self, ctx, data):
        time_run = ctx.app.service.time_run
        time_now = datetime.now()
        uptime = time_now - time_run
        stat = {
            'name': ctx.app.service.name,
            'version': ctx.app.service.version,
            'started': time_run.timestamp(),
            'uptime': uptime.total_seconds(),
            'daemon': ctx.app.service.stats,
        }
        return stat

    def reconfig(self, ctx, data):
        ctx.app.service.setupconf('Web Call')
        return {'status': 'ok'}
