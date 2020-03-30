import time
from logging import Logger

import asyncpg
from asyncpg.exceptions import CannotConnectNowError
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)
from redis import Redis

async def connect_db(psql_dsn: str, logger: Logger):
    conn = None
    for i in range(3):
        try:
            conn = await asyncpg.connect(dsn=psql_dsn)
            logger.info('Successfully connected to db')
            break
        except CannotConnectNowError as e:
            logger.warning('DB still starting up, will re-try connecting')
            time.sleep(3)

    if not conn:
        raise RuntimeError('Cannot connect to Postgres')

    return conn


def connect_minio(minio_addr: str,
                minio_port: str,
                minio_access_key: str,
                minio_secret_key: str,
                minio_bucket_name: str,
                logger: Logger):
    minio_client = Minio(
        f'{minio_addr}:{minio_port}',
        access_key=minio_access_key,
        secret_key=minio_secret_key,
        secure=False,
    )
    try:
       minio_client.make_bucket(minio_bucket_name)
    except (BucketAlreadyOwnedByYou, BucketAlreadyExists) as err:
        pass
    except ResponseError as err:
        raise

    logger.info('Successfully connected to minio')
    return minio_client


def connect_redis(redis_host: str,
                  redis_port: str,
                  db: int,
                  logger: Logger):
    redis_client = Redis(
        host=redis_host,
        port=redis_port,
        db=db,
    )
    logger.info('Successfully connected to Redis')
    return redis_client
