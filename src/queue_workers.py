from collections import deque


class JobQueue:

    def __init__(self):
        self._elements = deque()

    def enqueue(self, element):
        self._elements.append(element)

    def dequeue(self):
        return self._elements.popleft()

    def empty(self):
        return not self._elements

    def __len__(self):
        return len(self._elements)
