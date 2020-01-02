import asyncpg
import json


class MaybeAcquire:
    def __init__(self, connection, *, pool):
        self.connection = connection
        self.pool = pool
        self._cleanup = False

    async def __aenter__(self):
        if self.connection is None:
            self._cleanup = True
            self._connection = c = await self.pool.acquire()
            return c
        return self.connection

    async def __aexit__(self, *args):
        if self._cleanup:
            await self.pool.release(self._connection)


async def create_pool(credentials):
    async def init(conn):
        await conn.set_type_codec('jsonb', schema='pg_catalog', encoder=json.dumps, decoder=json.load, format='text')

    return await asyncpg.create_pool(**credentials, init=init)