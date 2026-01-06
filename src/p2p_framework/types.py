from abc import ABC
from dataclasses import dataclass


@dataclass
class MsgTo(ABC): ...


type PeerId = int


@dataclass(frozen=True)
class PeerEvent(ABC): ...


@dataclass(frozen=True)
class InboundPeerConnected(PeerEvent):
    peer_id: PeerId
    address: INetAddress


@dataclass(frozen=True)
class InboundPeerDisconnected(PeerEvent):
    peer_id: PeerId
    address: INetAddress
    reason: str


@dataclass(frozen=True)
class OutboundPeerConnected(PeerEvent):
    peer_id: PeerId
    address: INetAddress


@dataclass(frozen=True)
class OutboundPeerDisconnected(PeerEvent):
    peer_id: PeerId
    address: INetAddress
    reason: str


@dataclass(frozen=True)
class INetAddress:
    host: str
    port: int


@dataclass
class HandlerAndData(ABC):
    name: str


@dataclass
class MsgFrom[T: MsgTo](ABC):
    peer_id: PeerId
    msg: T
