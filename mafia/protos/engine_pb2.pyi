from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class CheckRequest(_message.Message):
    __slots__ = ["check_name", "name", "text"]
    CHECK_NAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    check_name: str
    name: str
    text: str
    def __init__(self, name: _Optional[str] = ..., check_name: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class CheckResponse(_message.Message):
    __slots__ = ["result", "role", "text"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    result: bool
    role: str
    text: str
    def __init__(self, result: bool = ..., role: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class EndDayRequest(_message.Message):
    __slots__ = ["name", "text"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    text: str
    def __init__(self, name: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class EndDayResponse(_message.Message):
    __slots__ = ["dead_player_name", "ended", "text"]
    DEAD_PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    ENDED_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    dead_player_name: str
    ended: bool
    text: str
    def __init__(self, ended: bool = ..., text: _Optional[str] = ..., dead_player_name: _Optional[str] = ...) -> None: ...

class EndNightRequest(_message.Message):
    __slots__ = ["name", "text"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    text: str
    def __init__(self, name: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class EndNightResponse(_message.Message):
    __slots__ = ["dead_player_name", "ended", "text"]
    DEAD_PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    ENDED_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    dead_player_name: str
    ended: bool
    text: str
    def __init__(self, ended: bool = ..., text: _Optional[str] = ..., dead_player_name: _Optional[str] = ...) -> None: ...

class GetPlayersRequest(_message.Message):
    __slots__ = ["name", "text"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    text: str
    def __init__(self, name: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class GetPlayersResponse(_message.Message):
    __slots__ = ["names", "text"]
    NAMES_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    names: str
    text: str
    def __init__(self, text: _Optional[str] = ..., names: _Optional[str] = ...) -> None: ...

class InfoRequest(_message.Message):
    __slots__ = ["name", "text"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    text: str
    def __init__(self, name: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class InfoResponse(_message.Message):
    __slots__ = ["dead_player_name", "text", "type"]
    DEAD_PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    dead_player_name: str
    text: str
    type: str
    def __init__(self, type: _Optional[str] = ..., text: _Optional[str] = ..., dead_player_name: _Optional[str] = ...) -> None: ...

class JoinRequest(_message.Message):
    __slots__ = ["name", "text"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    text: str
    def __init__(self, name: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class JoinResponse(_message.Message):
    __slots__ = ["id", "text"]
    ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    id: int
    text: str
    def __init__(self, id: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...

class KillRequest(_message.Message):
    __slots__ = ["kill_name", "name", "text"]
    KILL_NAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    kill_name: str
    name: str
    text: str
    def __init__(self, name: _Optional[str] = ..., kill_name: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class KillResponse(_message.Message):
    __slots__ = ["result", "text"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    result: bool
    text: str
    def __init__(self, result: bool = ..., text: _Optional[str] = ...) -> None: ...

class LeaveRequest(_message.Message):
    __slots__ = ["name", "text"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    text: str
    def __init__(self, name: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class LeaveResponse(_message.Message):
    __slots__ = ["text"]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

class PublishRequest(_message.Message):
    __slots__ = ["name", "text"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    text: str
    def __init__(self, name: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class PublishResponse(_message.Message):
    __slots__ = ["result", "text"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    result: bool
    text: str
    def __init__(self, result: bool = ..., text: _Optional[str] = ...) -> None: ...

class StartRequest(_message.Message):
    __slots__ = ["name", "text"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    text: str
    def __init__(self, name: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class StartResponse(_message.Message):
    __slots__ = ["mafias", "players", "role", "started", "text"]
    MAFIAS_FIELD_NUMBER: _ClassVar[int]
    PLAYERS_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    mafias: str
    players: str
    role: str
    started: bool
    text: str
    def __init__(self, started: bool = ..., role: _Optional[str] = ..., text: _Optional[str] = ..., players: _Optional[str] = ..., mafias: _Optional[str] = ...) -> None: ...

class VoteRequest(_message.Message):
    __slots__ = ["name", "text", "vote_name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    VOTE_NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    text: str
    vote_name: str
    def __init__(self, name: _Optional[str] = ..., vote_name: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class VoteResponse(_message.Message):
    __slots__ = ["result", "text"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    result: bool
    text: str
    def __init__(self, result: bool = ..., text: _Optional[str] = ...) -> None: ...
