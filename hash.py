#!/usr/bin/python

import hashlib


class ConsistentHash:
    def __init__(self, nodes, replicas=3):
        self.replicas = replicas
        self.nodes = nodes
        self.ring = {}

        for node in nodes:
            for i in range(replicas):
                replica_key = self.generate_key(f"{node}-{i}")
                self.ring[replica_key] = node

    def generate_key(self, data):
        return int(hashlib.md5(data.encode()).hexdigest(), 16)

    def get_node(self, key):
        if not self.ring:
            return None

        hashed_key = self.generate_key(key)
        keys = sorted(self.ring.keys())
        for ring_key in keys:
            if hashed_key <= ring_key:
                return self.ring[ring_key]

        # If the hashed_key is greater than all keys in the ring,
        # return the first node (wrap around).
        return self.ring[keys[0]]