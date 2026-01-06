# Setting up

Modify `NETWORK.py` to enable communication with the robot in the `ROBOT_IP` variable (line 2).


# Data acquisition plugin

Read this [documentation](https://dev.bostondynamics.com/docs/concepts/data_acquisition_overview) to fully understand **data acquisition plugin**.

Don't forget to [register](https://dev.bostondynamics.com/docs/python/daq_tutorial/daq1#register-a-payload-for-development) your payload. And authorise it from the admin console panel.

This plugin was created mostly based on the [example](https://dev.bostondynamics.com/docs/python/daq_tutorial/daq3#data-acquisition-plugin-service) given on their website.


# Tickets

## Request Cancelled Error

The function `store_helper.cancel_check()` raises an `RequestCancelledError` exception when the request has been cancelled by the client. However, I've never encountered this exception...even by using the Boston Dynamics application on the tablet. Still, the plugin theoretically handles it.

> If you have a long-running capture, you should periodically check that the capture has not been cancelled by the client. Store_helper provides the cancel_check() helper which will raise a RequestCancelledError if the request has already been cancelled. If you need to do any cleanup upon cancellation, you should catch the exception, perform your cleanup, and re-raise it. Note that most store_helper functions can raise this exception as well. [*Boston Dynamics documentation*](https://dev.bostondynamics.com/docs/python/daq_tutorial/daq3#data-acquisition-plugin-service)
