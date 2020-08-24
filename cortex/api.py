import asyncio
import json
import logging
from typing import List

import websockets

logger = logging.getLogger(__name__)


class CortexException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class CortexError(CortexException):
    def __init__(self, error_code, msg):
        self.error_code = error_code
        self.msg = msg

    def __str__(self):
        return f"{self.error_code}: {self.msg}"


class ID:
    class AUTH:
        GET_USER_LOGIN = 0x10
        REQUEST_ACCESS = 0x11
        HAS_ACCESS_RIGHT = 0x12
        AUTHORIZE = 0x13
        GENERATE_NEW_TOKEN = 0x14
        GET_USER_INFORMATION = 0x15
        GET_LICENSE_INFO = 0x16

    class HEADSET:
        QUERY_HEADSETS = 0x20
        CONTROL_DEVICE = 0x21
        UPDATE_HEADSET = 0x22
        UPDATE_HEADSET_CUSTOM_INFO = 0x23

    class SESSION:
        CREATE_SESSION = 0x30
        UPDATE_SESSION = 0x31
        QUERY_SESSIONS = 0x32

    class SUBSCRIPTION:
        SUBSCRIBE = 0x40
        UNSUBSCRIBE = 0x41

    class RECORD:
        CREATE_RECORD = 0x50
        STOP_RECORD = 0x51
        UPDATE_RECORD = 0x52
        DELETE_RECORD = 0x53
        QUERY_RECORDS = 0x54
        GET_RECORD_INFO = 0x55
        CONFIG_OPT_OUT = 0x56

    class MARKER:
        INJECT_MARKER = 0x60
        UPDATE_MARKER = 0x61

    class SUBJECT:
        CREATE_SUBJECT = 0x70
        UPDATE_SUBJECT = 0x71
        DELETE_SUBJECTS = 0x72
        QUERY_SUBJECTS = 0x73
        GET_DEMOGRAPHIC_ATTRIBUTES = 0x74

    class BCI:
        QUERY_PROFILE = 0x80
        GET_CURRENT_PROFILE = 0x81
        SETUP_PROFILE = 0x82
        LOAD_GUEST_PROFILE = 0x83
        GET_DETECTION_INFO = 0x84
        TRAINING = 0x85


class Wrapper:
    ws = None
    __result_dict = dict()
    __running = True
    main = None
    client_id: str
    client_secret: str
    listeners = list()

    def __init__(self, client_id, client_secret, main):
        self.url = "wss://localhost:6868"
        self.loop = asyncio.get_event_loop()
        self.client_id = client_id
        self.client_secret = client_secret
        self.main = main

    def register_listener(self, listener):
        self.listeners.append(listener)

    def __handle_listener(self, name, data, is_success: bool):
        for listener in self.listeners:
            listener.handle(name, data, is_success)

    def run(self):
        loop = self.loop

        async def runner():
            try:
                await self.start()
            finally:
                await self.close()

        def stop_loop_on_completion(f):
            loop.stop()

        future = asyncio.ensure_future(runner(), loop=loop)
        future.add_done_callback(stop_loop_on_completion)
        try:
            loop.run_until_complete(future)
        finally:
            future.remove_done_callback(stop_loop_on_completion)

        if not future.cancelled():
            return future.result()

    async def start(self):
        self.ws = await websockets.connect(self.url)
        asyncio.create_task(self.main())
        self.__handle_listener("start", None, True)
        await self.__recv_task()

    async def close(self):
        await self.ws.close()
        self.__handle_listener("close", None, True)
        self.__running = False

    def exit(self):
        self.__running = False

    async def __recv_task(self):
        while self.__running:
            try:
                recv = await asyncio.wait_for(self.ws.recv(), 5)
                result_dict = json.loads(recv)
                if "id" in result_dict:
                    self.__result_dict[result_dict["id"]] = result_dict
                    if "result" in result_dict:
                        self.__handle_listener(result_dict["id"], result_dict["result"], True)
                    elif "error" in result_dict:
                        self.__handle_listener(result_dict["id"], result_dict["error"], False)

                elif "warning" in result_dict:
                    logger.warning(result_dict["warning"])
                else:
                    self.__handle_listener(list(result_dict)[0], result_dict, True)
            except Exception as e:
                pass

    async def __get_response(self, _id):
        while _id not in self.__result_dict:
            await asyncio.sleep(0.1)
        return self.__result_dict.pop(_id)

    async def __request_api(self, data: dict):
        _id = data["id"]
        await self.ws.send(json.dumps(data))
        result_dict = await self.__get_response(_id)
        logger.debug(data["method"] + " result \r\n" + json.dumps(result_dict, indent=4))
        if "result" in result_dict:
            return result_dict["result"]
        else:
            raise CortexError(result_dict["error"]["code"], result_dict["error"]["message"])

    """
    Authentication
    """

    async def get_user_login(self):
        payload = {
            "id": ID.AUTH.GET_USER_LOGIN,
            "jsonrpc": "2.0",
            "method": "getUserLogin"
        }
        return await self.__request_api(payload)

    async def request_access(self, client_id: str = None, client_secret: str = None):
        payload = {
            "id": ID.AUTH.REQUEST_ACCESS,
            "jsonrpc": "2.0",
            "method": "requestAccess",
            "params": {
                "clientId": client_id if client_id else self.client_id,
                "clientSecret": client_secret if client_secret else self.client_secret
            }
        }
        return await self.__request_api(payload)

    async def has_access_right(self, client_id: str = None, client_secret: str = None):
        payload = {
            "id": ID.AUTH.HAS_ACCESS_RIGHT,
            "jsonrpc": "2.0",
            "method": "hasAccessRight",
            "params": {
                "clientId": client_id if client_id else self.client_id,
                "clientSecret": client_secret if client_secret else self.client_secret
            }
        }
        return await self.__request_api(payload)

    async def authorize(self, client_id: str = None, client_secret: str = None, _license: str = None,
                        debit: int = None):
        payload = {
            "id": ID.AUTH.AUTHORIZE,
            "jsonrpc": "2.0",
            "method": "authorize",
            "params": {
                "clientId": client_id if client_id else self.client_id,
                "clientSecret": client_secret if client_secret else self.client_secret
            }
        }

        if _license:
            payload["params"]["license"] = _license
        if debit:
            payload["params"]["debit"] = debit

        return await self.__request_api(payload)

    async def generate_new_token(self, cortex_token, client_id: str = None, client_secret: str = None):
        payload = {
            "id": ID.AUTH.GENERATE_NEW_TOKEN,
            "jsonrpc": "2.0",
            "method": "generateNewToken",
            "params": {
                "cortexToken": cortex_token,
                "clientId": client_id if client_id else self.client_id,
                "clientSecret": client_secret if client_secret else self.client_secret
            }
        }
        return await self.__request_api(payload)

    async def get_user_information(self, cortex_token):
        payload = {
            "id": ID.AUTH.GET_USER_INFORMATION,
            "jsonrpc": "2.0",
            "method": "getUserInformation",
            "params": {
                "cortexToken": cortex_token
            }
        }
        return await self.__request_api(payload)

    async def get_license_info(self, cortex_token):
        payload = {
            "id": ID.AUTH.GET_LICENSE_INFO,
            "jsonrpc": "2.0",
            "method": "getLicenseInfo",
            "params": {
                "cortexToken": cortex_token
            }
        }
        return await self.__request_api(payload)

    """
    Headsets
    """

    async def query_headsets(self, _id: str = None):
        payload = {
            "jsonrpc": "2.0",
            "id": ID.HEADSET.QUERY_HEADSETS,
            "method": "queryHeadsets"
        }

        if _id:
            payload["params"] = {"id": _id}

        return await self.__request_api(payload)

    async def control_device(self, command: str, headset: str = None, mappings: dict = None,
                             connection_type: str = None):
        payload = {
            "id": ID.HEADSET.CONTROL_DEVICE,
            "jsonrpc": "2.0",
            "method": "controlDevice",
            "params": {
                "command": command,
            }
        }

        if headset:
            payload["params"]["headset"] = headset

        if mappings:
            payload["params"]["mappings"] = mappings

        if connection_type:
            payload["params"]["connectionType"] = connection_type

        return await self.__request_api(payload)

    async def update_headset(self, cortex_token: str, headset: str, setting: dict):
        payload = {
            "id": ID.HEADSET.UPDATE_HEADSET,
            "jsonrpc": "2.0",
            "method": "updateHeadset",
            "params": {
                "cortexToken": cortex_token,
                "headsetId": headset,
                "setting": setting
            }
        }

        return await self.__request_api(payload)

    async def update_headset_custom_info(self, cortex_token: str, headset: str, headband_position: str):
        payload = {
            "id": ID.HEADSET.UPDATE_HEADSET_CUSTOM_INFO,
            "jsonrpc": "2.0",
            "method": "updateHeadsetCustomInfo",
            "params": {
                "cortexToken": cortex_token,
                "headbandPosition": headband_position,
                "headsetId": headset
            }
        }
        return await self.__request_api(payload)

    """
    Sessions
    """

    async def create_session(self, cortex_token: str, status: str, headset_id: str = None):
        payload = {
            "id": ID.SESSION.CREATE_SESSION,
            "jsonrpc": "2.0",
            "method": "createSession",
            "params": {
                "cortexToken": cortex_token,
                "status": status
            }
        }
        if headset_id:
            payload["params"]["headset"] = headset_id

        return await self.__request_api(payload)

    async def update_session(self, cortex_token: str, session: str, status: str):
        payload = {
            "id": ID.SESSION.UPDATE_SESSION,
            "jsonrpc": "2.0",
            "method": "updateSession",
            "params": {
                "cortexToken": cortex_token,
                "session": session,
                "status": status
            }
        }
        return await self.__request_api(payload)

    async def query_sessions(self, cortex_token: str):
        payload = {
            "id": ID.SESSION.QUERY_SESSIONS,
            "jsonrpc": "2.0",
            "method": "querySessions",
            "params": {
                "cortexToken": cortex_token
            }
        }
        return await self.__request_api(payload)

    """
    Data Subscription
    """

    async def subscribe(self, cortex_token: str, session: str, streams: List[str]):
        payload = {
            "id": ID.SUBSCRIPTION.SUBSCRIBE,
            "jsonrpc": "2.0",
            "method": "subscribe",
            "params": {
                "cortexToken": cortex_token,
                "session": session,
                "streams": streams
            }
        }

        return await self.__request_api(payload)

    async def unsubscribe(self, cortex_token: str, session: str, streams: List[str]):
        payload = {
            "id": ID.SUBSCRIPTION.UNSUBSCRIBE,
            "jsonrpc": "2.0",
            "method": "unsubscribe",
            "params": {
                "cortexToken": cortex_token,
                "session": session,
                "streams": streams
            }
        }

        return await self.__request_api(payload)

    """
    Records
    """

    async def create_record(self, cortex_token: str, session: str, title: str, description: str = None,
                            subject_name: str = None, tags: List[str] = None, experiment_id: List[int] = None):
        payload = {
            "id": ID.RECORD.CREATE_RECORD,
            "jsonrpc": "2.0",
            "method": "createRecord",
            "params": {
                "cortexToken": cortex_token,
                "session": session,
                "title": title
            }
        }

        if description:
            payload["params"]["description"] = description

        if subject_name:
            payload["params"]["subjectName"] = subject_name

        if tags:
            payload["params"]["tags"] = tags

        if experiment_id:
            payload["params"]["experimentId"] = experiment_id

        return await self.__request_api(payload)

    async def stop_record(self, cortex_token: str, session: str):
        payload = {
            "id": ID.RECORD.STOP_RECORD,
            "jsonrpc": "2.0",
            "method": "stopRecord",
            "params": {
                "cortexToken": cortex_token,
                "session": session
            }
        }

        return await self.__request_api(payload)

    async def update_record(self, cortex_token: str, session: str, title: str, description: str = None,
                            subject_name: str = None, tags: List[str] = None):
        payload = {
            "id": ID.RECORD.UPDATE_RECORD,
            "jsonrpc": "2.0",
            "method": "updateRecord",
            "params": {
                "cortexToken": cortex_token,
                "session": session,
                "title": title
            }
        }

        if description:
            payload["params"]["description"] = description

        if subject_name:
            payload["params"]["subjectName"] = subject_name

        if tags:
            payload["params"]["tags"] = tags

        return await self.__request_api(payload)

    # async def export_record(self):
    #     return await self.__request_api(payload)
    #
    # async def query_records(self):
    #     return await self.__request_api(payload)
    #
    # async def get_record_info(self):
    #     return await self.__request_api(payload)
    #
    # async def config_opt_out(self):
    #     return await self.__request_api(payload)

    """
    Markers
    """

    # async def inject_marker(self):
    #     return await self.__request_api(payload)
    #
    # async def update_marker(self):
    #     return await self.__request_api(payload)

    """
    Subjects
    """

    # async def create_subject(self):
    #     return await self.__request_api(payload)
    #
    # async def update_subject(self):
    #     return await self.__request_api(payload)
    #
    # async def delete_subjects(self):
    #     return await self.__request_api(payload)
    #
    # async def query_subjects(self):
    #     return await self.__request_api(payload)
    #
    # async def get_demographic_attributes(self):
    #     return await self.__request_api(payload)

    """
    BCI
    """

    async def query_profile(self, cortex_token: str):
        payload = {
            "id": ID.BCI.QUERY_PROFILE,
            "jsonrpc": "2.0",
            "method": "queryProfile",
            "params": {
                "cortexToken": cortex_token
            }
        }
        return await self.__request_api(payload)

    async def get_current_profile(self, cortex_token: str, headset: str):
        payload = {
            "id": ID.BCI.GET_CURRENT_PROFILE,
            "jsonrpc": "2.0",
            "method": "getCurrentProfile",
            "params": {
                "cortexToken": cortex_token,
                "headset": headset
            }
        }
        return await self.__request_api(payload)

    async def setup_profile(self, cortex_token: str, status: str, profile: str, headset: str = None,
                            new_profile_name: str = None):
        payload = {
            "id": ID.BCI.SETUP_PROFILE,
            "jsonrpc": "2.0",
            "method": "setupProfile",
            "params": {
                "cortexToken": cortex_token,
                "profile": profile,
                "status": status
            }
        }

        if headset:
            payload["params"]["headset"] = headset
        if new_profile_name:
            payload["params"]["newProfileName"] = new_profile_name

        return await self.__request_api(payload)

    async def load_guest_profile(self, cortex_token: str, headset: str):
        payload = {
            "id": ID.BCI.LOAD_GUEST_PROFILE,
            "jsonrpc": "2.0",
            "method": "loadGuestProfile",
            "params": {
                "cortexToken": cortex_token,
                "headset": headset
            }
        }
        return await self.__request_api(payload)

    async def get_detection_info(self, detection: str):
        payload = {
            "id": ID.BCI.GET_DETECTION_INFO,
            "jsonrpc": "2.0",
            "method": "getDetectionInfo",
            "params": {
                "detection": detection
            }
        }
        return await self.__request_api(payload)

    async def training(self, cortex_token: str, session: str, detection: str, status: str, action: str):
        payload = {
            "id": ID.BCI.TRAINING,
            "jsonrpc": "2.0",
            "method": "training",
            "params": {
                "action": action,
                "cortexToken": cortex_token,
                "detection": detection,
                "session": session,
                "status": status
            }
        }
        return await self.__request_api(payload)

    """
    Utils
    """

    async def connect_headset(self, headset_id: str):
        return await self.control_device("connect", headset=headset_id)

    async def disconnect_headset(self, headset_id: str):
        return await self.control_device("disconnect", headset=headset_id)

    async def refresh_headsets(self):
        return await self.control_device("refresh")

    async def load_profile(self, cortex_token, headset, profile):
        return await self.setup_profile(cortex_token, "load", profile, headset=headset)

    async def get_current_profile_id(self, cortex_token: str, headset: str):
        _id = (await self.get_current_profile(cortex_token, headset))["name"]
        return _id if _id != "null" else None

    async def get_headset(self, headset: str = None):
        res = await self.query_headsets(headset)
        if len(res) < 1:
            raise CortexException("기기를 찾을 수 없습니다.")
        return res[0]["id"]

    async def prepare(self, client_id: str = None, client_secret: str = None, headset: str = None, debit: int = 10):
        client_id = client_id if client_id else self.client_id
        client_secret = client_secret if client_secret else self.client_secret

        headset = await self.get_headset(headset)
        await self.connect_headset(headset)
        await self.request_access(client_id, client_secret)
        res = await self.authorize(client_id, client_secret, debit=debit)
        token = res["cortexToken"]
        res = await self.create_session(token, "active", headset)
        session = res["id"]
        return token, session


class Listener:
    def __new__(cls, *args, **kwargs):
        s_handlers = {}
        f_handlers = {}
        for elem, value in cls.__dict__.items():
            if hasattr(value, "__is_listener__"):
                if getattr(value, "__is_success__"):
                    s_handlers[getattr(value, "__listener_name__")] = value
                else:
                    f_handlers[getattr(value, "__listener_name__")] = value

        cls = object.__new__(cls)
        cls.s_handlers = s_handlers
        cls.f_handlers = f_handlers
        return cls

    def handle(self, name, value, is_success: bool):
        if is_success:
            if name in self.s_handlers:
                self.s_handlers[name](self, value)
        else:
            if name in self.f_handlers:
                self.f_handlers[name](self, value)

    @classmethod
    def handler(cls, name, is_success: bool = True):
        def wrapper(func):
            actual = func
            if isinstance(actual, staticmethod):
                actual = actual.__func__

            actual.__is_listener__ = True
            actual.__is_success__ = is_success
            actual.__listener_name__ = name

            return func

        return wrapper
