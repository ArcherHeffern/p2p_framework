from dataclasses import dataclass
from multiprocessing import Queue
from random import choice

from p2p_framework.types import MsgTo


@dataclass
class EventQueue:
    group_data: dict[type, dict[str, Queue]]

    def put(self, obj: object) -> bool:
        """
        Sends obj to a random event handler for type(obj)
        """
        t: type = type(obj)
        if qs := self.group_data.get(t):
            random_q = choice(list(qs.values()))
            random_q.put_nowait(obj)
            return True
        else:
            print(f"Not event handler for {t}. Did you forget to register it? ")
            return False

    def broadcast(self, obj: MsgTo) -> bool:
        """
        Broadcasts obj to all event handlers for type(obj)
        """
        t: type = type(obj)
        if qs := self.group_data.get(t):
            for q in qs.values():
                q.put_nowait(obj)
            return True
        else:
            raise Exception(f"Broadcasting {t} but no event handlers found")
