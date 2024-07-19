# coding: utf-8
class Cache:
    def __init__(self):
        self.storage={}

    def get(self, key):
        return self.storage.get(key,None)

    def set(self, key, value):
        self.storage[key] = value

    def delete(self, key):
        if key in self.storage:
            del self.storage[key]
            return '1'
        return '0'

    def __str__(self):
        return str(self.storage)