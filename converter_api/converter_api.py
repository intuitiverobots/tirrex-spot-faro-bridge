import requests
import os
import zipfile
import shutil
import struct
import websockets
from fastapi import WebSocket, WebSocketDisconnect
# sys is useful if the path to the ConverterFlsToLas.exe is higher in your hierarchy
import sys
sys.path.append("..")

from message import Message

from NETWORK import CONVERTER_API_PORT, SCANNER_API_ADDRESS
from CONST import *


class ConverterApi:
    
    def __init__(self):
        pass
    
    ### LIFESPAN ###
    def startup(self) -> None:
        os.makedirs(SCANS_TMP_DIR, exist_ok=True)
        os.makedirs(SCANS_CONVERTED_DIR, exist_ok=True)
        url = f"{SCANNER_API_ADDRESS}/set-converter/{CONVERTER_API_PORT}"
        converter_set = False
        while not converter_set:
            try:
                response = requests.post(url, data="", timeout=REQUEST_TIMEOUT)
                print(response)
                converter_set = True
            except requests.RequestException as ex:
                print(f"[Error] converter couldn't be set:\n\turl: '{url}'\n\texception: {ex}")

    def shutdown(self) -> None:
        pass

    ### WEBSOCKET ###
    async def ws_convert(self, ws: WebSocket, scan_name: str, scanner_api_port: str) -> None:
        await ws.accept()
        print(f"new client accepted : wanting to convert '{scan_name}'")

        scan_name_converted = scan_name[:scan_name.rfind(".")] + SCAN_CONVERTED_EXTENSION
        scan_converted_path = f"{SCANS_CONVERTED_DIR}\\{scan_name_converted}"
        if not os.path.exists(scan_converted_path):

            # reception
            scan_zip_tmp_path = f"{SCANS_TMP_DIR}\\{scan_name}.zip"
            if not await self.download(ws, scan_zip_tmp_path):
                if os.path.exists(scan_zip_tmp_path):
                    os.remove(scan_zip_tmp_path)
                return
            
            # unzipping
            scan_unzip_tmp_path = f"{SCANS_TMP_DIR}\\{scan_name}"
            if not await self.unzip(scan_zip_tmp_path, scan_unzip_tmp_path):
                if os.path.exists(scan_zip_tmp_path):
                    os.remove(scan_zip_tmp_path)
                return
            
            # conversion
            scan_fls_tmp_path = f"{scan_unzip_tmp_path}\\{scan_name}"
            cmd = COMMAND_CONVERTER_FLS_TO_LAS.format(scan_path=scan_fls_tmp_path, scan_converted_dir=SCANS_CONVERTED_DIR)
            os.system(cmd)
            print(f"scan '{scan_fls_tmp_path}' converted into '{scan_converted_path}'")

            # cleaning
            if os.path.exists(scan_zip_tmp_path):
                os.remove(scan_zip_tmp_path)
            if os.path.exists(scan_unzip_tmp_path):
                shutil.rmtree(scan_unzip_tmp_path)

        else: # exists
            
            # close connection
            await ws.close()

        # reading & sending
        with open(scan_converted_path, "rb") as scan_converted_file:
            las_header = self.read_las_header(scan_converted_file)
            print(f"scan '{scan_name}' has {las_header['points']} points")
            ws_url = f"ws://{ws.client.host}:{scanner_api_port}/converted/{scan_name_converted}/{las_header["points"]}"
            try:
                async with websockets.connect(ws_url) as ws_scanner_api:
                    match(las_header["id"]):
                        case 0:
                            las_point_reader = self.read_las_point_0
                        case 2:
                            las_point_reader = self.read_las_point_2
                        case _:
                            print(f"error: id {las_header['id']} is unknown")
                            return
                    vertex_buffer = bytearray(VERTEX_BUFFER_SIZE)
                    vertex_buffer[VERTEX_BUFFER_ALIGNMENT_START:VERTEX_BUFFER_ALIGNMENT_END] = struct.pack("<B", 255)
                    message = Message(ws_scanner_api)
                    for _ in range(las_header["points"]):
                        point = las_point_reader(scan_converted_file)
                        vertex_buffer[VERTEX_BUFFER_X_START:VERTEX_BUFFER_X_END] = struct.pack("<f", point["x"] * las_header["scale_x"] + las_header["offset_x"])
                        vertex_buffer[VERTEX_BUFFER_Y_START:VERTEX_BUFFER_Y_END] = struct.pack("<f", point["y"] * las_header["scale_y"] + las_header["offset_y"])
                        vertex_buffer[VERTEX_BUFFER_Z_START:VERTEX_BUFFER_Z_END] = struct.pack("<f", point["z"] * las_header["scale_z"] + las_header["offset_z"])
                        vertex_buffer[VERTEX_BUFFER_COLORS_START:VERTEX_BUFFER_COLORS_END] = point["colors"]
                        await message.add(vertex_buffer)
                    await message.flush()
            except Exception as ex:
                print(f"error while sending scan to '{ws_url}': {ex}")
        print(f"scan '{scan_converted_path}' sent successfully")

    @staticmethod
    async def download(ws: WebSocket, file_path: str) -> bool:
        try:
            with open(file_path, "wb") as scan_zip:
                while True:
                    try:
                        chunk = await ws.receive_bytes()
                        scan_zip.write(chunk)
                    except WebSocketDisconnect:
                        break
        except Exception as ex:
            print(f"error while receiving file '{file_path}': {ex}")
            return False
        print(f"file '{file_path}' received")
        return True

    @staticmethod
    async def unzip(file_zip_path: str, file_unzip_path: str) -> bool:
        try:
            with zipfile.ZipFile(file_zip_path, 'r') as zip_ref:
                zip_ref.extractall(file_unzip_path)
        except zipfile.BadZipFile as ex:
            print(f"error while extracting zip file '{file_zip_path}': {ex}")
            return False
        print(f"file '{file_zip_path}' unzipped at '{file_unzip_path}'")
        return True

    @staticmethod
    def read_las_header(las_file) -> dict:
        raw = las_file.read(LAS_HEADER_SIZE)
        header = {}
        header["id"] = struct.unpack("<B", raw[LAS_HEADER_ID_START:LAS_HEADER_ID_END])[0]
        header["points"] = struct.unpack("<L", raw[LAS_HEADER_POINTS_START:LAS_HEADER_POINTS_END])[0]
        header["scale_x"] = struct.unpack("<d", raw[LAS_HEADER_SCALE_X_START:LAS_HEADER_SCALE_X_END])[0]
        header["scale_y"] = struct.unpack("<d", raw[LAS_HEADER_SCALE_Y_START:LAS_HEADER_SCALE_Y_END])[0]
        header["scale_z"] = struct.unpack("<d", raw[LAS_HEADER_SCALE_Z_START:LAS_HEADER_SCALE_Z_END])[0]
        header["offset_x"] = struct.unpack("<d", raw[LAS_HEADER_OFFSET_X_START:LAS_HEADER_OFFSET_X_END])[0]
        header["offset_y"] = struct.unpack("<d", raw[LAS_HEADER_OFFSET_Y_START:LAS_HEADER_OFFSET_Y_END])[0]
        header["offset_z"] = struct.unpack("<d", raw[LAS_HEADER_OFFSET_Z_START:LAS_HEADER_OFFSET_Z_END])[0]
        offset_to_points = struct.unpack("<L", raw[LAS_HEADER_OFFSET_TO_POINTS_START:LAS_HEADER_OFFSET_TO_POINTS_END])[0]
        las_file.read(offset_to_points - LAS_HEADER_SIZE)
        return header

    @staticmethod
    def read_las_point_position(raw: bytes, point: dict) -> None:
        point["x"] = struct.unpack("<l", raw[LAS_POINT_POSITION_X_START:LAS_POINT_POSITION_X_END])[0]
        point["y"] = struct.unpack("<l", raw[LAS_POINT_POSITION_Y_START:LAS_POINT_POSITION_Y_END])[0]
        point["z"] = struct.unpack("<l", raw[LAS_POINT_POSITION_Z_START:LAS_POINT_POSITION_Z_END])[0]

    @staticmethod
    def read_las_point_0(las_file) -> dict:
        raw = las_file.read(LAS_POINT_0_SIZE)
        point = {}
        ConverterApi.read_las_point_position(raw, point)
        point["colors"] = raw[LAS_POINT_0_COLORS_START:LAS_POINT_0_COLORS_END] * 3
        return point
    
    @staticmethod
    def read_las_point_2(las_file) -> dict:
        raw = las_file.read(LAS_POINT_2_SIZE)
        point = {}
        ConverterApi.read_las_point_position(raw, point)
        point["colors"] = raw[LAS_POINT_2_COLOR_R_START:LAS_POINT_2_COLOR_R_END] + raw[LAS_POINT_2_COLOR_G_START:LAS_POINT_2_COLOR_G_END] + raw[LAS_POINT_2_COLOR_B_START:LAS_POINT_2_COLOR_B_END]
        return point
