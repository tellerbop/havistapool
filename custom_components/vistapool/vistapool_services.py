from abc import abstractmethod, ABCMeta
import json

from .pool import (
    CurrentPoolDataResponse,
    PoolResponse,
    PoolDataResponse,
    Pool,    
)
from .vistapool_api import VistaPoolAPI
from .util import to_byte_array, get_attr

from hashlib import sha512
import asyncio

MAX_RESPONSE_ATTEMPTS = 10
REQUEST_STATUS_SLEEP = 10

SUCCEEDED = "succeeded"
FAILED = "failed"
REQUEST_SUCCESSFUL = "request_successful"
REQUEST_FAILED = "request_failed"


class VistaPoolService:
    def __init__(self, api: VistaPoolAPI):
        self._api = api        
        self.vistaPoolToken = ""

    async def login(self, user: str, password: str, persist_token: bool = True):
        await self.login_request(user, password)

    async def get_pool_information(self):
        self._api.use_token(self.vistaPoolToken)
        data = await self._api.get(
            "http://vistapool.es/api/pool"
            # "http://vistapool.es/api/pool?select=main%20weather%20modules%20hidro"
        )
        # f = open("c:\\temp\\vistapooldata.json")
        # data = json.loads(f.read())

        response = PoolResponse()
        response.parse(data)
        return response

    async def get_stored_pool_data(self, pid: str):
        self._api.use_token(self.vistaPoolToken)

        data = await self._api.get(
            "http://vistapool.es/api/pool/{pid}?select=main%20modules%20light%20filtration".format(
                pid=pid
            )
        )
        
        # f = open("c:\\temp\\vistapooldata_spec.json")
        # data = json.loads(f.read())

        return PoolDataResponse(data)

    async def check_request_succeeded(
        self, url: str, action: str, successCode: str, failedCode: str, path: str
    ):

        for _ in range(MAX_RESPONSE_ATTEMPTS):
            await asyncio.sleep(REQUEST_STATUS_SLEEP)

            self._api.use_token(self.vwToken)
            res = await self._api.get(url)

            status = get_attr(res, path)

            if status is None or (failedCode is not None and status == failedCode):
                raise Exception(
                    "Cannot {action}, return code '{code}'".format(
                        action=action, code=status
                    )
                )

            if status == successCode:
                return

        raise Exception("Cannot {action}, operation timed out".format(action=action))

    async def login_request(self, user: str, password: str):
        # Login and get Vista Pool cookie 
        self._api.use_token(None)
        data = {            
            "username": user,
            "password": password,
            "company_id": 1
        }

        self.vistaPoolToken = await self._api.post(
            "http://vistapool.es/api/auth", data,  use_json=True
        )


