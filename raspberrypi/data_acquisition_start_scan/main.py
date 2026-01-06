import logging
from time import sleep

import bosdyn.client.util
from bosdyn.client.util import setup_logging
from bosdyn.client.data_acquisition_plugin_service import DataAcquisitionPluginService
from bosdyn.client.directory_registration import (DirectoryRegistrationClient, DirectoryRegistrationKeepAlive)
from bosdyn.client.server_util import GrpcServiceRunner
from bosdyn.api import data_acquisition_plugin_service_pb2_grpc

from data_acquisition_start_scan import StartScan
from NETWORK import ROBOT_IP
from CONST import CREDS_FILE, AUTHENTICATE_LOOP_TIME, CAPABILITY, DIRECTORY_NAME, AUTHORITY


def main():
    logger = logging.getLogger('data-acquisition-start-scan')
    setup_logging(False)

    # get the IP address of the computer running this service
    host_ip = bosdyn.client.common.get_self_ip(ROBOT_IP)

    # create and authenticate a bosdyn robot object
    sdk = bosdyn.client.create_standard_sdk('DataAcquisitionStartScan')
    robot = sdk.create_robot(ROBOT_IP)
    is_authenticated = False
    while not is_authenticated:
        try:
            print("trying to authenticate...")
            robot.authenticate_from_payload_credentials(*bosdyn.client.util.read_payload_credentials(CREDS_FILE))
            is_authenticated = True
            break
        except Exception as e:
            print(f"error: unable to authenticate: {e}")
            print(f"trying again in {AUTHENTICATE_LOOP_TIME} seconds")
            sleep(AUTHENTICATE_LOOP_TIME)


    # create a service runner to start and maintain the service on background thread
    data_acquisition_plugin = StartScan()
    servicer = DataAcquisitionPluginService(robot, [CAPABILITY], data_acquisition_plugin.start_scan, logger=logger)
    add_servicer_to_server_fn = data_acquisition_plugin_service_pb2_grpc.add_DataAcquisitionPluginServiceServicer_to_server
    service_runner = GrpcServiceRunner(servicer, add_servicer_to_server_fn, 0, logger=logger)

    # use a keep alive to register the service with the robot directory
    dir_reg_client = robot.ensure_client(DirectoryRegistrationClient.default_service_name)
    keep_alive = DirectoryRegistrationKeepAlive(dir_reg_client, logger=logger)
    keep_alive.start(DIRECTORY_NAME, DataAcquisitionPluginService.service_type, AUTHORITY, host_ip, service_runner.port)

    # attach the keep alive to the service runner and run until a SIGINT is received
    with keep_alive:
        service_runner.run_until_interrupt()


if __name__ == '__main__':
    main()
