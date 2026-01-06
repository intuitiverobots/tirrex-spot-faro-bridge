from time import sleep
import threading
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
import websockets
import httpx

from api_message import ApiMessage
from scanner import Scanner

from CONST import VISUALISER_ADDRESSES_FILE, UPDATE_SCANNER_LOOP_TIME, CHUNK_SIZE


class ScannerApi:
    
    def __init__(self, scanner_api_port):
        self._scanner_api_port = scanner_api_port
        self._is_active = True
        self._scanner = Scanner()
        self._converter_api_address = ""
        self._visualiser_addresses: list[str] = self._read_visualiser_ws_addresses()
        threading.Thread(target=lambda: asyncio.run(self._check_visualisers_connection()), daemon=True).start()
    
    def _read_visualiser_ws_addresses(self) -> list[str]:
        try:
            with open(VISUALISER_ADDRESSES_FILE, "r") as file:
                lines = file.readlines()
                if lines:
                    return [line.strip() for line in lines]
        except Exception as ex:
            print(f"error while reading the file '{VISUALISER_ADDRESSES_FILE}: {ex}")
        return []

    async def _check_visualisers_connection(self) -> None:
        visualiser_addresses_connected = []
        for visualiser_address in self._visualiser_addresses:
            try:
                ws_visualiser = await websockets.connect(visualiser_address)
                visualiser_addresses_connected.append(visualiser_address)
                await ws_visualiser.close()
            except Exception as ex:
                print(f"visualiser on address '{visualiser_address}' is no longer active")
        self._visualiser_addresses = visualiser_addresses_connected

    # LIFESPAN
    def startup(self) -> None:
        threading.Thread(target=self._update_scanner, daemon=True).start()

    def _update_scanner(self) -> None:
        while self._is_active:
            self._scanner.update_scanner()
            sleep(UPDATE_SCANNER_LOOP_TIME)
    
    def shutdown(self) -> None:
        self._is_active = False
        try:
            with open(VISUALISER_ADDRESSES_FILE, "w") as file:
                file.write("\n".join(self._visualiser_addresses))
        except Exception as ex:
            print(f"error while writing the file '{VISUALISER_ADDRESSES_FILE}: {ex}")

    # API
    def start_scan(self) -> ApiMessage:
        start_scan_message = self._scanner.start_scan()
        if not start_scan_message.is_error():
            if len(self._visualiser_addresses) > 0: # stream current job if at least one client is registered
                threading.Thread(target=lambda: asyncio.run(self.stream_to_converter()), daemon=True).start()
        return start_scan_message

    async def stream_to_converter(self) -> None:
        stream_url, scan_name = self._scanner.get_stream_info()
        print(f"starting streaming of scan '{scan_name}' on '{stream_url}'")
        ws_url = f"{self._converter_api_address}/convert/{scan_name}/{self._scanner_api_port}"
        try:
            async with websockets.connect(ws_url) as ws_converter:
                async with httpx.AsyncClient() as client:
                    async with client.stream("GET", stream_url, timeout=60.0) as stream:
                        async for chunk in stream.aiter_bytes(CHUNK_SIZE):
                            if chunk:
                                await ws_converter.send(chunk)
        except Exception as ex:
            print(f"couldn't connect to converter on address '{ws_url}': {ex}")
            return
        print(f"scan '{scan_name}' sent")

    def is_scanning(self) -> ApiMessage:
        return self._scanner.is_scanning()

    def abort_scan(self) -> ApiMessage:
        return self._scanner.abort_scan()
    
    def set_converter(self, converter_api_address: str) -> ApiMessage:
        self._converter_api_address = converter_api_address
        return ApiMessage.success_message_str(f"converter registered on address '{converter_api_address}'")

    def add_visualiser(self, visualiser_address: str) -> ApiMessage:
        if visualiser_address not in self._visualiser_addresses:
            self._visualiser_addresses.append(visualiser_address)
            return ApiMessage.success_message_str(f"visualiser added on address '{visualiser_address}'")
        return ApiMessage.success_message_str(f"visualiser already registered on address '{visualiser_address}'")

    def remove_visualiser(self, visualiser_address: str) -> ApiMessage:
        if visualiser_address in self._visualiser_addresses:
            self._visualiser_addresses.remove(visualiser_address)
            return ApiMessage.success_message_str(f"visualiser removed on address '{visualiser_address}'")
        return ApiMessage.success_message_str(f"no visualiser is registered on address '{visualiser_address}'")

    # WEBSOCKET
    async def ws_converted(self, ws: WebSocket, scan_name_converted: str, point_count: int) -> None:
        await ws.accept()
        ws_visualisers = []
        for visualiser_address in self._visualiser_addresses:
            try:
                ws_visualiser = await websockets.connect(visualiser_address)
                ws_visualisers.append(ws_visualiser)
            except Exception as ex:
                print(f"couldn't connect to visualiser on address '{visualiser_address}': {ex}")
                self._visualiser_addresses.remove(visualiser_address)
        if len(ws_visualisers) == 0:
            print("no visualiser is still listening")
            return
        # first message is the name of the scan with the number of points
        message = {"scan_name": scan_name_converted, "point_count": point_count}.__str__().replace("'", "\"")
        await asyncio.gather(*(self._ws_send(ws_visualiser, message, ws_visualisers) for ws_visualiser in ws_visualisers))
        if len(ws_visualisers) == 0:
            print(f"all visualisers has disconnected")
            return
        # then comes the data
        bytes_received = 0
        while True:
            try:
                chunk = await ws.receive_bytes()
                bytes_received += len(chunk)
                await asyncio.gather(*(self._ws_send(ws_visualiser, chunk, ws_visualisers) for ws_visualiser in ws_visualisers.copy()))
                if len(ws_visualisers) == 0:
                    print(f"all visualisers has disconnected")
                    await ws.close()
                    return
            except WebSocketDisconnect:
                print(f"{bytes_received} byte received (and sended)")
                break
            except Exception as ex:
                print(f"error receiving scan: {ex}")
                break
        for ws_visualiser in ws_visualisers:
            await ws_visualiser.close()
        txt = "visualiser"
        if (len(ws_visualisers) > 1):
            txt += "s"
        print(f"scan '{scan_name_converted}' received and sent to {len(ws_visualisers)} {txt}:")
        for ws_visualiser in ws_visualisers:
            print(f"{ws_visualiser.remote_address[0]}:{ws_visualiser.remote_address[1]}")

    async def _ws_send(self, ws_visualiser: websockets.ClientConnection, message: str | bytes, ws_visualisers: list[websockets.ClientConnection]):
        try:
            await ws_visualiser.send(message)
        except Exception as ex:
            print(f"visualiser on address '{ws_visualiser.remote_address[0]}:{ws_visualiser.remote_address[1]}' has disconnected: {ex}")
            if ws_visualiser in ws_visualisers:
                ws_visualisers.remove(ws_visualiser)
