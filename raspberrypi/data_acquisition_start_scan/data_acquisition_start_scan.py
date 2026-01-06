import requests
from time import sleep
import sys

from bosdyn.client.data_acquisition_plugin_service import (DataAcquisitionStoreHelper, RequestCancelledError)
from bosdyn.api import data_acquisition_pb2

sys.path.append("..")
from scanner_api.NETWORK import SCANNER_API_ADDRESS
from CONST import UPDATE_SCAN_LOOP_TIME, CAPABILITY


class StartScan:
    """data acquisition plugin which start a new scan when receiving the action for"""
    
    def start_scan(self, request, store_helper: DataAcquisitionStoreHelper):
        """send a request to the API to start a new scan and wait until it finishes"""

        # send 'start-scan' request to the scanner api
        print("sending 'start-scan' request")
        url = f"{SCANNER_API_ADDRESS}/start-scan"
        try:
            start_scan_response = requests.post(url)
            start_scan_response_json = start_scan_response.json()
        except Exception as ex:
            print(f"error: couldn't connect to scanner api: {ex}")
            self.acquisition_completed(request, store_helper)
            return
        
        # check if request has succeed
        if not start_scan_response_json["status"]:
            message = start_scan_response_json["message"]
            print(f"error: 'start-scan' request has failed: {message}")
            self.acquisition_completed(request, store_helper)
            return
        
        # wait until the scan finishes
        while True:

            # waiting
            print("scan in progress...")
            sleep(UPDATE_SCAN_LOOP_TIME)

            # check if the action has been cancelled
            try:
                store_helper.cancel_check()
            except RequestCancelledError as request_cancelled_exception:
                # send 'abort-scan' request to the scanner api
                try:
                    abort_scan_response = requests.post(f"{SCANNER_API_ADDRESS}/abort-scan")
                    abort_scan_response_json = abort_scan_response.json()
                except Exception as ex:
                    print(f"error: couldn't connect to scanner api: {ex}")
                    raise request_cancelled_exception
                
                # check if request has succeed
                message = abort_scan_response_json["message"]
                if abort_scan_response_json["status"]:
                    print(f"success: scan has been cancelled: {message}")
                else:
                    print(f"error: scan couldn't be cancelled: {message}")
                raise request_cancelled_exception

            # send 'is-scanning' request to the scanner api
            try:
                is_scanning_response = requests.get(f"{SCANNER_API_ADDRESS}/is-scanning")
                is_scanning_response_json = is_scanning_response.json()
            except Exception as ex:
                print(f"error: couldn't connect to scanner api: {ex}")
                self.acquisition_completed(request, store_helper)
                return

            # break if the scanner has stopped scanning
            if not is_scanning_response_json["message"]:
                print("scanner has stopped scanning")
                break

        # scan completed
        print("success: scan completed")
        self.acquisition_completed(request, store_helper)


    def acquisition_completed(self, request, store_helper: DataAcquisitionStoreHelper):
        store_helper.state.set_status(data_acquisition_pb2.GetStatusResponse.STATUS_SAVING)
        message = data_acquisition_pb2.AssociatedMetadata()
        message.reference_id.action_id.CopyFrom(request.action_id)
        message.metadata.data.update({})
        data_id = data_acquisition_pb2.DataIdentifier(action_id=request.action_id, channel=CAPABILITY.channel_name)
        store_helper.store_metadata(message, data_id)
