from fastapi import FastAPI, WebSocket
from contextlib import asynccontextmanager
import socket
import uvicorn
from time import sleep

from converter_api import ConverterApi

from NETWORK import CONVERTER_API_IP, CONVERTER_API_PORT
from CONST import SERVER_CONNECTION_LOOP_TIME


### SERVER ###

# create the API
converter_api = ConverterApi()

# lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    converter_api.startup()
    yield
    converter_api.shutdown()

# FastAPI
fapi = FastAPI(lifespan=lifespan)


### WEBSOCKET ###

# receive a scan in '.fls' format, then convert it, then send it back in '.las' format
@fapi.websocket("/convert/{scan_name}/{scanner_api_port}")
async def ws_convert(websocket: WebSocket, scan_name: str, scanner_api_port: str):
    await converter_api.ws_convert(websocket, scan_name, scanner_api_port)


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
        print(f"port {port} unreachable, trying again with port {port + 1}...")
        port += 1
    print(f"server starting on address {ip}:{port}")
    uvicorn.run(fapi, host=ip, port=port)

if __name__ == "__main__":
    main(CONVERTER_API_IP, CONVERTER_API_PORT)
