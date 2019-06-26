import utils
import asyncio


class Queue:
    def __init__(self):
        self._ventie = []
        self._venter = []

    def add_user(self, user, ventie=True):
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
            ventie = self._ventie.pop(0)
            venter = self._venter.pop(0)
            return ventie, venter
        except IndexError:
            return

    @property
    def status(self):
        return f"Currently {len(self._ventie)} Venties and {len(self._venter)} Venter in queue."
