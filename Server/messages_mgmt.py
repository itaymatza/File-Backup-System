

class MessageIdHandler:
    def __init__(self):
        self.next_available_id = 0
        self.released_ids = set()

    def get_available_id(self):
        ulong_max = (2 ** (8 * 4)) - 1

        if self.released_ids:
            return self.released_ids.pop()

        available_id = self.next_available_id
        self.next_available_id += 1
        if ulong_max < self.next_available_id:
            raise MemoryError('The number of message IDs is out of the 4 bytes range.')
        return available_id

    def release_id(self, released_id):
        self.released_ids.add(released_id)
