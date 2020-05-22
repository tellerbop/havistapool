import json
import time
from datetime import timedelta, datetime
import logging
import asyncio
from typing import List

from asyncio import TimeoutError
from aiohttp import ClientResponseError

import voluptuous as vol
from abc import ABC, abstractmethod

_LOGGER = logging.getLogger(__name__)

MAX_RESPONSE_ATTEMPTS = 10
REQUEST_STATUS_SLEEP = 5

from .vistapool_services import VistaPoolService
from .vistapool_api import VistaPoolAPI
from .util import log_exception, get_attr, parse_int, parse_float

class VistaPoolConnectAccount:
    """Representation of an Vista Pool Connect Account."""

    def __init__(
        self, session, username: str, password: str
    ) -> None:

        self._api = VistaPoolAPI(session)
        self._vistapool_service = VistaPoolService(self._api)

        self._username = username
        self._password = password
        self._loggedin = False

        self._connect_retries = 3
        self._connect_delay = 10

        self._vista_pools = []
        self._pools = []
     
    async def login(self):
        for i in range(self._connect_retries):
            self._loggedin = await self.try_login(i == self._connect_retries - 1)
            if self._loggedin is True:
                break

            if i < self._connect_retries - 1:
                _LOGGER.error(
                    "Login to Vista Pool service failed, trying again in {} seconds".format(
                        self._connect_delay
                    )
                )
                await asyncio.sleep(self._connect_delay)

    async def try_login(self, logError):
        try:
            await self._vistapool_service.login(self._username, self._password, False)
            return True
        except Exception as exception:
            if logError is True:
                _LOGGER.error("Login to Vista Pool service failed: " + str(exception))

            return False

    async def update(self):
        if not self._loggedin:
            await self.login()

        if not self._loggedin:
            return False

        """Update the state of all pools."""
        try:
            if len(self._vista_pools) > 0:
                for pool in self._vista_pools:
                    await self.add_or_update_pool(pool)

            else:
                pools_response = await self._vistapool_service.get_pool_information()
                self._vista_pools = pools_response.pools
                self.pools = []
                for pool in self._vista_pools:
                    await self.add_or_update_pool(pool)

            self._loggedin = False

            return True

        except IOError as exception:
            _LOGGER.exception(exception)
            return False

    async def add_or_update_pool(self, pool):
        vupd = [x for x in self._pools if x.pid == pool.pid.lower()]
        if len(vupd) > 0:
            await vupd[0].update()
        else:
            try:
                poolItem = VistaPool(self._vistapool_service, pool)
                await poolItem.update()
                self._pools.append(poolItem)
            except Exception:
                pass

    async def login_and_get_pool(self, pid: str):
        pool = [v for v in self._pools if v.pid.lower() == pid.lower()]
        if pool and len(pool) > 0:
            return pool[0]

        if not self._loggedin:
            await self.login()

        if not self._loggedin:
            return None

        return None
  

class VistaPool:
    def __init__(self, vistapool_service: VistaPoolService, pool) -> None:
        self._vistapool_service = vistapool_service
        self._pool = pool
        self._pool.state = {}
        self._pool.fields = {}
        self._logged_errors = set()
        self.support_status_report = True         

    async def call_update(self, func, ntries: int):
        try:
            await func()
        except TimeoutError:
            if ntries > 1:
                await asyncio.sleep(2)
                await self.call_update(func, ntries - 1)
            else:
                raise

    async def update(self):
        try:
            await self.call_update(self.update_pool_statusreport, 3)            
        except Exception as exception:
            log_exception(
                exception,
                "Unable to update pool data of {}".format(self._pool.pid),
            )

    def log_exception_once(self, exception, message):
        err = message + ": " + str(exception).rstrip("\n")
        if not err in self._logged_errors:
            self._logged_errors.add(err)
            _LOGGER.error(err)

    async def update_pool_statusreport(self):
        try:
            status = await self._vistapool_service.get_stored_pool_data(self._pool.pid)
            self._pool.fields = {
                status.data_fields[i].name: status.data_fields[i].value
                for i in range(0, len(status.data_fields))
            }
            self._pool.state["last_update_time"] = datetime.now()

        except TimeoutError:
            raise
        except ClientResponseError as resp_exception:
            if resp_exception.status == 403 or resp_exception.status == 502:
                self.support_status_report = False
            else:
                self.log_exception_once(
                    resp_exception,
                    "Unable to obtain the pool status report of {}".format(
                        self._pool.pid
                    ),
                )
        except Exception as exception:
            self.log_exception_once(
                exception,
                "Unable to obtain the pool status report of {}".format(
                    self._pool.pid
                ),
            )

    @property
    def last_update_time(self):        
        if self.last_update_time_supported:
            return self._pool.state.get("last_update_time")

    @property
    def last_update_time_supported(self):
        check = self._pool.state.get("last_update_time")
        if check:
            return True

    @property
    def pid(self):    
        return self._pool.pid

    @property
    def ref(self):    
        return self._pool.ref

    @property
    def connected(self):    
        return self._pool.connected

    @property
    def name(self):    
        return self._pool.name

    @property
    def pid_supported(self):    
        return True

    @property
    def ref_supported(self):    
        return True

    @property
    def connected_supported(self):    
        return True

    @property
    def name_supported(self):    
        return True

    @property
    def temperature(self):        
        if self.temperature_supported:
            check = self._pool.fields.get("temperature")
            return parse_float(check)

    @property
    def temperature_supported(self):      
        check = self._pool.fields.get("temperature")
        if check and parse_float(check):
            return True  
           
    @property
    def ph(self):        
        if self.ph_supported:
            check = self._pool.fields.get("ph")
            return parse_float(check)
    
    @property
    def ph_supported(self):      
        check = self._pool.fields.get("ph")
        if check and parse_float(check):
            return True  

    @property
    def ph_target(self):        
        if self.ph_target_supported:
            check = self._pool.fields.get("ph_target")
            return parse_float(check)
    
    @property
    def ph_target_supported(self):      
        check = self._pool.fields.get("ph_target")
        if check and parse_float(check):
            return True  

    @property
    def rx(self):        
        if self.rx_supported:
            check = self._pool.fields.get("rx")
            return parse_int(check)
    
    @property
    def rx_supported(self):      
        check = self._pool.fields.get("rx")
        if check and parse_int(check):
            return True  

    @property
    def rx_target(self):        
        if self.rx_target_supported:
            check = self._pool.fields.get("rx_target")
            return parse_int(check)
    
    @property
    def rx_target_supported(self):      
        check = self._pool.fields.get("rx_target")
        if check and parse_int(check):
            return True  
   
    @property
    def rx_relay_state(self):        
        check = self._pool.fields.get("rx_relay_state")
        return check

    @property
    def rx_relay_state_supported(self):        
        check = self._pool.fields.get("rx_relay_state")
        if check:
            return True  

    @property
    def ph_relay_state(self):
        if self.ph_relay_state_supported:        
            check = self._pool.fields.get("ph_relay_state")
            return parse_int(check)
   
    @property
    def ph_relay_state_supported(self):        
        check = self._pool.fields.get("ph_relay_state")        
        result = parse_int(check)

        if result == None: return False
        else: return True 

            