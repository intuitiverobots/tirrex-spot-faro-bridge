from bosdyn.client.data_acquisition_plugin_service import Capability


CREDS_FILE = "data_acquisition_start_scan_creds.txt"
DIRECTORY_NAME = 'data-acquisition-start-scan'
AUTHORITY = 'data-acquisition-start-scan'
CAPABILITY = Capability(name='start-scan', description='Start a scan', channel_name='start-scan')

AUTHENTICATE_LOOP_TIME = 5
UPDATE_SCAN_LOOP_TIME = 0.2
