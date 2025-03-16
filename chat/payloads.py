from typing import TypeVar, TypedDict


class FrontendPayload:
    pass

FrontendPayloadType = TypeVar('FrontendPayloadType', bound=FrontendPayload)

class FrontendEvent[FrontendPayloadType]:
    type: str
    payload: FrontendPayloadType

class FrontendChatSwitchPayload(FrontendPayload):
    chat_id: int

class FrontendMessagePayload(FrontendPayload):
    chat_id: int
    content: str

class FrontendAddMemberPayload(FrontendPayload):
    chat_id: int
    user_id: int



class GroupPayload(TypedDict):
    pass

GroupPayloadType = TypeVar('GroupPayloadType', bound=GroupPayload)
class GroupEvent[GroupPayloadType](TypedDict):
    type: str
    payload: GroupPayloadType

class GroupChatAddPayload(GroupPayload):
    chat_id: int

class GroupChatSendPayload(GroupPayload):
    chat_id: int
    content: str


class BackendPayload(TypedDict):
    pass

BackendPayloadType = TypeVar('BackendPayloadType', bound=BackendPayload)

class BackendEvent[BackendPayloadType](TypedDict):
    type: str
    payload: BackendPayloadType

class BackendChatSendPayload(BackendPayload):
    chat_id: int
    content: str

class BackendChatAddPayload(BackendPayload):
    chat_id: int


class BackendMultiPayload(BackendPayload):
    events: list[BackendEvent]
