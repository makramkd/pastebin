import asyncio
import logging
import os
import time

import uvloop
from redis import Redis

from pastebin.connect import connect_redis, connect_db


async def tx(psql_client, query: str):
    async with psql_client.transaction():
        return await psql_client.execute(query)


class Subscriber:
    def __init__(self, psql_client, redis_client: Redis, loop: asyncio.AbstractEventLoop):
        self.psql_client = psql_client
        self.redis_client = redis_client
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe('__keyevent@0__:expired')
        self.logger = logging.getLogger(name='redis_subscriber')
        self.loop = loop

    def run(self):
        self.logger.info('Listening for messages on channel: __keyevent@0__:expired')
        try:
            while True:
                msg = self.pubsub.get_message()
                if msg:
                    self.logger.info(f'Got message: {msg}')
                    if msg and msg['type'] == 'message' and msg['channel'].decode() == '__keyevent@0__:expired':
                        shortlink = msg['data'].decode()

                        query = """
                        UPDATE pastes SET expired = true WHERE shortlink = '{shortlink}';
                        """.format(shortlink=shortlink)
                        self.loop.run_until_complete(tx(self.psql_client, query))
                        self.logger.info(f'Updated shortlink {shortlink} to expired')
                else:
                    time.sleep(0.1)
        except KeyboardInterrupt:
            self.logger.info('Received exit signal. Shutting down')
            self.pubsub.close()
            self.redis_client.close()


def subscriber_main():
    PSQL_DSN = os.getenv('PSQL_DSN', 'postgres://pastebin_rw:devsecret@localhost:5432/pastebin?sslmode=disable')
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger()

    uvloop.install()
    loop = asyncio.get_event_loop()

    logger.info('Connecting to Redis')
    redis_client = connect_redis(
        REDIS_HOST,
        REDIS_PORT,
        REDIS_DB,
        logger,
    )

    logger.info('Connecting to postgres')
    psql_conn = loop.run_until_complete(connect_db(
        PSQL_DSN,
        logger,
    ))

    logger.info('Creating subscriber')
    subscriber = Subscriber(
        psql_client=psql_conn,
        redis_client=redis_client,
        loop=loop,
    )

    logger.info('Running subscriber loop')
    subscriber.run()
