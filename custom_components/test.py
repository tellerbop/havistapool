import sys
import asyncio
import getopt
import time
import logging

# from vistapool.services import (
#     LockUnlockService,
#     RemoteTripStatisticsService,
#     RequestStatus,
# )

from vistapool.vistapool_connect_account import VistaPoolConnectAccount
from vistapool.dashboard import Dashboard

from aiohttp import ClientSession

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(__debug__)

def printHelp():
    print("test.py --user <username> --password <password>")


async def main(argv):
  
    try:
        opts, _ = getopt.getopt(argv, "hu:p:", ["user=", "password="])
    except getopt.GetoptError:
        printHelp()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            printHelp()
            sys.exit()
        elif opt in ("-u", "--user"):
            user = arg
        elif opt in ("-p", "--password"):
            password = arg

    if user == "" or password == "":
        printHelp()
        sys.exit()

    async with ClientSession() as session:
        account = VistaPoolConnectAccount(session, user, password)

        await account.update()

        for pool in account._pools:

            dashboard = Dashboard(account, pool, miles=True)
            for instrument in dashboard.instruments:
                print(str(instrument), instrument.str_state)


if __name__ == "__main__":
    task = main(sys.argv[1:])
    res = asyncio.get_event_loop().run_until_complete(task)
