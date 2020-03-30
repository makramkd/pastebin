import hashlib
import uuid

def generate_shortlink():
    uid = uuid.uuid4().bytes
    hasher = hashlib.blake2b()
    hasher.update(uid)
    shortlink = hasher.hexdigest()[:8]
    return shortlink


def format_paste_path(shortlink: str, bucket_name: str):
    return f'shortlink={shortlink},bucket_name={bucket_name}'


def parse_paste_path(path: str):
    shortlink, bucket_name = path.split(',')
    return (shortlink.split('=')[1], bucket_name.split('=')[1])


async def query_pg(conn, query: str):
    return await conn.fetchrow(query)
