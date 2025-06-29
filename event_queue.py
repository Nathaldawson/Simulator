# Sim/event_queue.py

from collections import deque

class EventQueue:
    def __init__(self):
        self._queue = deque()

    def put(self, event):
        self._queue.append(event)

    def get(self):
        return self._queue.popleft()

    def empty(self):
        return len(self._queue) == 0
