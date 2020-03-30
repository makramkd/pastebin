from datetime import datetime
from logging import Logger
from io import BytesIO

from redis import Redis
from minio import Minio
import dateutil.parser
from sanic.response import json as sanic_json
from sanic.exceptions import ServerError

from pastebin.helpers import (
    generate_shortlink,
    parse_paste_path,
    format_paste_path,
)

class Pastebin:
    def __init__(self,
                 psql_client,
                 redis_client: Redis,
                 minio_client: Minio,
                 bucket_name: str,
                 logger: Logger):
        self.psql_client = psql_client
        self.redis_client = redis_client
        self.minio_client = minio_client
        self.bucket_name = bucket_name
        self.logger = logger

    async def create_paste(self, request):
        # Request validation
        if not request.json:
            raise ServerError("Request content type must be JSON", status_code=400)
        if 'paste_content' not in request.json:
            raise ServerError("Key 'paste_content' not in provided JSON body", status_code=400)

        paste_data_len = len(request.json['paste_content'])
        paste_data = BytesIO(request.json['paste_content'].encode('utf-8'))

        # TODO: figure out a better way to handle a nullable expiration date
        expiration_date = 'null'
        if 'expiration' in request.json:
            try:
                expiration_date = dateutil.parser.parse(request.json['expiration'])
                expiration_date = f"'{expiration_date}'::TIMESTAMPTZ"
            except dateutil.parser.ParserError:
                raise ServerError(f"Unable to parse given date: {request.json['expiration']}", status_code=400)

        created_at = updated_at = datetime.now()

        # Generate the shortlink to insert into the DB and object store
        shortlink = generate_shortlink()
        async with self.psql_client.transaction():
            self.minio_client.put_object(
                bucket_name=self.bucket_name,
                object_name=shortlink,
                data=paste_data,
                length=paste_data_len,
                content_type='text/plain',
            )
            await self.psql_client.execute(
                """
                INSERT INTO pastes VALUES (
                    '{shortlink}',
                    '{paste_content_link}',
                    {expired},
                    {expiration_date},
                    '{created_at}'::TIMESTAMPTZ,
                    '{updated_at}'::TIMESTAMPTZ
                );
                """.format(
                    shortlink=shortlink,
                    paste_content_link=format_paste_path(shortlink, self.bucket_name),
                    expired='false',
                    expiration_date=expiration_date,
                    created_at=created_at,
                    updated_at=updated_at,
                )
            )
            return sanic_json({'created': 'true', 'shortlink': shortlink})

    async def get_paste(self, request, shortlink):
        query = """
SELECT * FROM pastes WHERE shortlink = '{shortlink}' and expired = false
        """.format(shortlink=shortlink)
        row = await self.psql_client.fetchrow(query)
        if not row:
            raise ServerError('Given shortlink not found or expired', status_code=404)

        shortlink, bucket_name = parse_paste_path(row['paste_content_link'])
        paste_content = self.minio_client.get_object(
            bucket_name=bucket_name,
            object_name=shortlink,
        ).read(decode_content=True)

        return sanic_json({
            'paste_content': paste_content,
        })
