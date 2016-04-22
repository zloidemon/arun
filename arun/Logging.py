import sys
import logging


class CounterFilter(logging.Filter):
    def __init__(self, stats):
        self.stats = stats

    def filter(self, record):
        try:
            code = record.code
            self.stats['codes'][code] += 1
        except:
            pass

        if record.levelname in ['ERROR', 'CRITICAL', 'WARNING']:
            self.stats['log'][record.levelname] += 1

        return True


def LOGGING_CONF(self):
    F_SYSLOG = '%(name)s[%(process)d] %(levelname)s %(thread)d %(message)s'
    F_VERBOSE = '%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s'
    conf = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': F_VERBOSE
            },
            'syslog': {
                'format': F_SYSLOG
            },
        },
        'handlers': {
            'stdout': {
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
                'formatter': 'verbose',
            },
            'syslog': {
                'class': 'logging.handlers.SysLogHandler',
                'address': '/dev/log',
                'facility': 'daemon',
                'formatter': 'syslog',
            },
        },
        'loggers': {
            'root': {
                'handlers': ['stdout'],
                'level': 'DEBUG',
                'propagate': True,
            },
            self.name: {
                'handlers': ['stdout', 'syslog'],
                'level': 'DEBUG',
                'propagate': True,
            },
        }
    }
    return conf
