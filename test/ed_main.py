from asyncio import sleep
from dataclasses import dataclass
from datetime import timedelta
from random import randint
from typing import Optional
from p2p_framework import (
    Service,
    ProcessGroup,
    Networker,
    EventQueue,
    INetAddress,
    MsgTo,
    MsgFrom,
    InboundPeerConnected,
    marshaller,
    request_handler,
    event_handler,
    periodic,
)
from p2p_framework.decorators import worker


# ============
# Define DataTypes
# ============
@dataclass
class Frog(MsgTo):
    name: str
    say: str


@dataclass
class FrogMsg(MsgTo):
    heller: str


@dataclass
class FrogResponse(MsgTo):
    goodbyer: str


@dataclass
class SolutionFound(MsgTo):
    solution: int


# ============
# Register Data Types
# ============
marshaller.register("frog", Frog)
marshaller.register("frog_msg", FrogMsg)
marshaller.register("frog_response", FrogResponse)
marshaller.register("solution_found", SolutionFound)


# ============
# Create handlers
# ============
@periodic("frog_periodic", timedelta(seconds=1))
async def frog_periodic(event_queue: EventQueue, networker: Networker) -> None:
    frog = Frog("froggie", "ribbit")
    print("Sending Frog")
    event_queue.put(frog)


@event_handler("frog_handler", Frog)
async def frog_handler(frog: Frog, event_queue: EventQueue, networker: Networker):
    print(f"Frog '{frog.name}' says {frog.say}")
    networker.broadcast(FrogMsg("Networking is working!"))


@request_handler("frog_msg_handler", FrogMsg)
async def frog_msg_handler(
    frog: MsgFrom[FrogMsg],
    event_queue: EventQueue,
    networker: Networker,
):
    print(frog.msg.heller)
    networker.send(frog.peer_id, FrogResponse("Goodbyer"))


@request_handler("frog_response_handler", FrogResponse)
async def frog_response_handler(
    frog: MsgFrom[FrogResponse],
    event_queue: EventQueue,
    networker: Networker,
):
    print(frog.msg.goodbyer)
    if randint(0, 1):
        sol = randint(0, 10)
        print(f"Broadcasting Solution: {sol}")
        event_queue.put(SolutionFound(sol))


@event_handler("peer_connected_handler", InboundPeerConnected)
async def peer_connected_handler(
    peer_connected: InboundPeerConnected, event_queue: EventQueue, networker: Networker
):
    print(
        f"Connected to peer {peer_connected.address} with id {peer_connected.peer_id}"
    )


@worker("solution_found_handler", listen_for=SolutionFound, ignore_stale=True)
async def solution_found_handler(
    maybe_solution_found: Optional[SolutionFound],
    event_queue: EventQueue,
    networker: Networker,
    data: dict,
):
    if not "solution" in data:
        data["solution"] = None
    print("Solution: ", data["solution"])
    if maybe_solution_found:
        print(f"Solution recieved: {maybe_solution_found.solution}")
        data["solution"] = maybe_solution_found.solution
    for _ in range(10):
        await sleep(0.1)


# ============
# Use the handlers
# ============
def main() -> None:
    s1 = Service(
        config={
            "hello_world": ProcessGroup(
                frog_periodic,
                frog_handler,
                peer_connected_handler,
                frog_response_handler,
                solution_found_handler,
            )
        },
        debug=True,
        known_addresses=[INetAddress("127.0.0.1", 8081)],
    )
    s2 = Service(
        config={
            "hello_world": ProcessGroup(
                frog_msg_handler,
                peer_connected_handler,
            )
        },
        debug=True,
        addr=INetAddress("127.0.0.1", 8081),
    )
    s1.run()
    s2.run()
    s1.join()
    s2.join()


if __name__ == "__main__":
    main()
