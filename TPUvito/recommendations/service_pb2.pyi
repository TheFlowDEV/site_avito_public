from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Recommendations_list(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, id: _Optional[_Iterable[int]] = ...) -> None: ...

class rec4msg(_message.Message):
    __slots__ = ("adv_id",)
    ADV_ID_FIELD_NUMBER: _ClassVar[int]
    adv_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, adv_id: _Optional[_Iterable[int]] = ...) -> None: ...

class rec4msg_category(_message.Message):
    __slots__ = ("adv_id", "category")
    ADV_ID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_FIELD_NUMBER: _ClassVar[int]
    adv_id: _containers.RepeatedScalarFieldContainer[int]
    category: str
    def __init__(self, adv_id: _Optional[_Iterable[int]] = ..., category: _Optional[str] = ...) -> None: ...

class void(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
