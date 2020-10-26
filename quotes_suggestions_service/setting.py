from os import environ


DEFAULT_CACHE_TTL = int(environ.get('DEFAULT_CACHE_TTL', 60))  # in seconds
REDIS_HOST = environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(environ.get('REDIS_PORT', 6379))
