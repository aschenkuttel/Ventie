import utils
import datetime


class Queue:
    def __init__(self):
        self._ventie = []
        self._venter = []

    def add_user(self, user, ventie):
        if user in self._venter or user in self._ventie:
            raise utils.AlreadyQueued
        queue = self._ventie if ventie else self._venter
        queue.append(user)

    def remove_user(self, user):
        if user in self._ventie:
            self._ventie.remove(user)
        elif user in self._venter:
            self._venter.remove(user)
        else:
            raise utils.NotQueued

    def get_pair(self):
        try:
            ventie = self._ventie[0]
            venter = self._venter[0]
            self._ventie.remove(ventie)
            self._venter.remove(venter)
            return ventie, venter
        except IndexError:
            print("called")
            return

    @property
    def status(self):
        return f"Currently {len(self._ventie)} Venties and {len(self._venter)} Venter in queue."


class Anon:
    def __init__(self, user, alias):
        self.user = user
        self.id = user.id
        self.send = user.send
        self.alias = alias

    @property
    def args(self):
        return self.id, self.alias


class Session:

    def __init__(self, pool, ventie, venter):
        self.id = None
        self._pool = pool
        self.ventie = ventie.id
        self.ventie_al = ventie.alias
        self.venter = venter.id
        self.venter_al = venter.alias
        self.date = datetime.datetime.now()
        self.args = self.sql_arguments()

    @classmethod
    def from_record(cls, pool, record):

        self = cls.__new__(cls)
        self.id = record.id
        self._pool = pool
        self.ventie = record.ventie
        self.ventie_al = record.ventie_nick
        self.venter = record.venter
        self.venter_al = record.venter_nick
        self.date = datetime.datetime.now()
        self.args = self.sql_arguments()
        return self

    def __contains__(self, item):
        return item in [self.ventie, self.venter]

    def get_partner(self, id_):
        if id_ == self.ventie:
            user_id = self.venter
            nick = self.ventie_al
        else:
            user_id = self.ventie
            nick = self.venter_al
        return user_id, nick

    async def create_id(self):
        conn = await self._pool.acquire()
        query = "SELECT DISTINCT id FROM session, infinite ORDER BY DESC"
        data = await conn.fetch(query)
        self.id = data[0] + 1 if data else 1
        await self._pool.release(conn)

    async def insert(self, conn, table):
        query = "INSERT INTO {}(id, ventie, big, venter, small, date)" \
                "VALUES ($1, $2, $3, $4, $5, $6)"
        await conn.execute(query.format(table), *self.args)

    async def finish(self):
        conn = await self._pool.acquire()
        await self.insert(conn, 'infinite')
        query = "DELETE FROM session WHERE id = $1"
        await conn.execute(query, self.id)
        await self._pool.release(conn)

    def sql_arguments(self):
        base = [self.id, self.ventie, self.venter_al]
        base.extend([self.venter, self.venter_al, self.date])
        return base
