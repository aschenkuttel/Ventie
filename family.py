import datetime


class Queue:
    def __init__(self):
        self._ventie = []
        self._venter = []

    def __contains__(self, item):
        cache = [u.id for u in self._ventie + self._venter]
        return item in cache

    def add_user(self, user, ventie):
        queue = self._ventie if ventie else self._venter
        queue.append(user)

    def remove_user(self, user):
        for anon in self._ventie:
            if anon.id == user.id:
                self._ventie.remove(anon)
        else:
            for anon in self._venter:
                if anon.id == user.id:
                    self._venter.remove(anon)

    def get_pair(self):
        try:
            ventie = self._ventie[0]
            venter = self._venter[0]
            self._ventie.remove(ventie)
            self._venter.remove(venter)
            return ventie, venter
        except IndexError:
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

    @classmethod
    def from_record(cls, pool, record):

        self = cls.__new__(cls)
        self.id = record['id']
        self._pool = pool
        self.ventie = record['ventie']
        self.ventie_al = record['ventie_alias']
        self.venter = record['venter']
        self.venter_al = record['venter_alias']
        self.date = record['date']
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

    async def create_id(self, conn):
        query = "SELECT id FROM session UNION SELECT id FROM infinite ORDER BY id DESC"
        data = await conn.fetch(query)
        self.id = data[0]['id'] + 1 if data else 1

    async def insert(self, conn, table):
        query = "INSERT INTO {}(id, ventie, ventie_alias, venter, venter_alias, date) " \
                "VALUES ($1, $2, $3, $4, $5, $6)"
        await conn.execute(query.format(table), *self.args)

    async def setup(self):
        conn = await self._pool.acquire()
        await self.create_id(conn)
        await self.insert(conn, 'session')
        await self._pool.release(conn)

    async def finish(self):
        conn = await self._pool.acquire()
        await self.insert(conn, 'infinite')
        query = "DELETE FROM session WHERE id = $1"
        await conn.execute(query, self.id)
        await self._pool.release(conn)

    @property
    def args(self):
        base = [self.id, self.ventie, self.venter_al]
        base.extend([self.venter, self.venter_al, self.date])
        return base
