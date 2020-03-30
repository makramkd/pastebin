import asyncio
import os

from sanic import Sanic
from sanic.log import logger

import uvloop

from pastebin.helpers import (
    generate_shortlink,
    format_paste_path,
    parse_paste_path
)
from pastebin.connect import (
    connect_db,
    connect_minio,
    connect_redis,
)
from pastebin.api import Pastebin

def main():
    APP_HOST = os.getenv('PASTEBIN_APP_HOST', '0.0.0.0')
    APP_PORT = int(os.getenv('PASTEBIN_APP_PORT', 8000))
    MINIO_ADDR = os.getenv('MINIO_ADDR', 'pastebin_minio')
    MINIO_PORT = int(os.getenv('MINIO_PORT', 9000))
    MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', 'dev_access_key')
    MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', 'dev_secret_key')
    MINIO_BUCKET_NAME = os.getenv('MINIO_BUCKET_NAME', 'pastes')
    PSQL_DSN = os.getenv('PSQL_DSN', 'postgres://pastebin_rw:devsecret@pastebin_pg:5432/pastebin?sslmode=disable')
    REDIS_HOST = os.getenv('REDIS_HOST', 'pastebin_redis')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    # Set up uvloop
    uvloop.install()
    loop = asyncio.get_event_loop()

    # Connect to services

    # S3-like object store
    minio_client = connect_minio(
        minio_addr=MINIO_ADDR,
        minio_port=MINIO_PORT,
        minio_access_key=MINIO_ACCESS_KEY,
        minio_secret_key=MINIO_SECRET_KEY,
        minio_bucket_name=MINIO_BUCKET_NAME,
        logger=logger,
    )

    # Redis cache
    redis_client = connect_redis(
        REDIS_HOST,
        REDIS_PORT,
        REDIS_DB,
        logger,
    )

    # PostgreSQL
    psql_conn = loop.run_until_complete(connect_db(PSQL_DSN, logger))

    pastebin = Pastebin(
        psql_client=psql_conn,
        redis_client=redis_client,
        minio_client=minio_client,
        bucket_name=MINIO_BUCKET_NAME,
        logger=logger,
    )

    # Set up sanic application on the same loop as asyncpg
    app = Sanic(
        name='pastebin',
    )
    app.add_route(pastebin.create_paste, '/api/v1/pastes', methods=['POST'], name='create_paste')
    app.add_route(pastebin.get_paste, '/api/v1/pastes/<shortlink:string>', methods=['GET'], name='get_paste')
    server = app.create_server(
        host=APP_HOST,
        port=APP_PORT,
        return_asyncio_server=True,
    )

    serv_task = asyncio.ensure_future(server, loop=loop)
    server = loop.run_until_complete(serv_task)
    server.after_start()

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.stop()
    finally:
        server.before_stop()

        # Wait for server to close
        close_task = server.close()
        loop.run_until_complete(close_task)

        # Complete all tasks on the loop
        for connection in server.connections:
            connection.close_if_idle()
        server.after_stop()
