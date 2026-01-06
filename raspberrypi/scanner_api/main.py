from fastapi import FastAPI, WebSocket, Request
from contextlib import asynccontextmanager
import socket
import uvicorn
from time import sleep

from scanner_api import ScannerApi

from NETWORK import SCANNER_API_IP, SCANNER_API_PORT
from CONST import SERVER_CONNECTION_LOOP_TIME


### SERVER ###

# create the API
scanner_api = ScannerApi(SCANNER_API_PORT)

# server lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    scanner_api.startup()
    yield
    scanner_api.shutdown()

# FastAPI
fapi = FastAPI(lifespan=lifespan)


### API ###

# start a new scan
@fapi.post("/start-scan")
def start_scan():
    return scanner_api.start_scan()

# return 'true' if the scanner is scanning
@fapi.get("/is-scanning")
def is_scanning():
    return scanner_api.is_scanning()

# abort the current scan
@fapi.post("/abort-scan")
def abort_scan():
    return scanner_api.abort_scan()

# set the converter
@fapi.post("/set-converter/{converter_api_port}")
def set_converter(request: Request, converter_api_port: str):
    ws_url = f"ws://{request.client.host}:{converter_api_port}"
    return scanner_api.set_converter(ws_url)

# add a visualiser
@fapi.post("/add-visualiser/{visualiser_port}")
def add_visualiser(request: Request, visualiser_port: str):
    ws_url = f"ws://{request.client.host}:{visualiser_port}"
    return scanner_api.add_visualiser(ws_url)

# remove a visualiser
@fapi.post("/remove-visualiser/{visualiser_port}")
def remove_visualiser(request: Request, visualiser_port: str):
    ws_url = f"ws://{request.client.host}:{visualiser_port}"
    return scanner_api.remove_visualiser(ws_url)


### WEBSOCKET ###

# receive a scan once converted and send it to the registered visualisers
@fapi.websocket("/converted/{scan_name_converted}/{point_count}")
async def ws_converted(websocket: WebSocket, scan_name_converted: str, point_count: int):
    await scanner_api.ws_converted(websocket, scan_name_converted, point_count)


### UVICORN ###

def is_ip_reachable(ip: str) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((ip, 0))
        return True
    except OSError:
        return False

def is_port_free(ip: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((ip, port)) != 0

def main(ip: str, port: int) -> None:
    while not is_ip_reachable(ip):
        print(f"ip {ip} unreachable, trying again in {SERVER_CONNECTION_LOOP_TIME} sec...")
        sleep(SERVER_CONNECTION_LOOP_TIME)
    while not is_port_free(ip, port):
        print(f"port {port} unreachable, trying again in {SERVER_CONNECTION_LOOP_TIME} sec...")
        sleep(SERVER_CONNECTION_LOOP_TIME)
    print(f"server starting on address {ip}:{port}")
    uvicorn.run(fapi, host=ip, port=port)

if __name__ == "__main__":
    main(SCANNER_API_IP, SCANNER_API_PORT)
