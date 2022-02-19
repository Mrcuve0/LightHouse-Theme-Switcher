import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
        'console': {
            'format': "[%(asctime)s][%(levelname)s: %(funcName)s] - [Line %(lineno)d] > %(message)s"
        }
    },
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'console'
        }
    },
    'loggers': {
        'LightHouse': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    }
}