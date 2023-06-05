from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class ActionRequest(_message.Message):
    __slots__ = ["action_name", "name", "text", "type", "vote_name"]
    ACTION_NAME_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VOTE_NAME_FIELD_NUMBER: _ClassVar[int]
    action_name: str
    name: str
    text: str
    type: str
    vote_name: str
    def __init__(self, name: _Optional[str] = ..., text: _Optional[str] = ..., type: _Optional[str] = ..., vote_name: _Optional[str] = ..., action_name: _Optional[str] = ...) -> None: ...

class ActionResponse(_message.Message):
    __slots__ = ["mafias", "name", "text", "type"]
    MAFIAS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    mafias: str
    name: str
    text: str
    type: str
    def __init__(self, text: _Optional[str] = ..., type: _Optional[str] = ..., name: _Optional[str] = ..., mafias: _Optional[str] = ...) -> None: ...

class GetPlayersRequest(_message.Message):
    __slots__ = ["name", "text"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    text: str
    def __init__(self, name: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class GetPlayersResponse(_message.Message):
    __slots__ = ["count", "names", "text"]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    NAMES_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    count: int
    names: str
    text: str
    def __init__(self, count: _Optional[int] = ..., names: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class InfoRequest(_message.Message):
    __slots__ = ["name", "text"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    text: str
    def __init__(self, name: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class InfoResponse(_message.Message):
    __slots__ = ["text"]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    text: str
    def __init__(self, text: _Optional[str] = ...) -> None: ...

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

class StartRequest(_message.Message):
    __slots__ = ["name", "text"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    name: str
    text: str
    def __init__(self, name: _Optional[str] = ..., text: _Optional[str] = ...) -> None: ...

class StartResponse(_message.Message):
    __slots__ = ["mafias", "role", "started", "text"]
    MAFIAS_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    mafias: str
    role: str
    started: bool
    text: str
    def __init__(self, started: bool = ..., role: _Optional[str] = ..., text: _Optional[str] = ..., mafias: _Optional[str] = ...) -> None: ...
