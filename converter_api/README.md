This application uses the *FARO sdk* which only works under **Windows OS**.


# Installation

## Python

- ensure you have python 3.10+ installed `python3 --version`
- ensure you have pip installed `python3 -m pip --version`
- create a virtual environment `python3 -m venv converter_api_env`
- activate the virtual environment `converter_api_env/Scripts/activate`
- install the dependencies `python3 -m pip install requests "fastapi[standard]"`

## ConverterFlsToLas

- follow the instructions in the `README.md` file of the `converterflstolas` directory to compile/retrieve the `ConverterFlsToLas.exe` application


# Setting up

Modify `NETWORK.py` to enable communication between the different servers:
- in the `CONVERTER_IP` and `CONVERTER_PORT` variables (line 4-5).
- in the `SCANNER_API_IP` and `SCANNER_API_PORT` variables (line 9-10).

Modify `CONST.py` to assign the path to the `ConverterFlsToLas.exe` executable file in the `CONVERTER_FLS_TO_LAS_PATH` variable (line 2).


# Start the application

*Don't forget to activate your virtual environment `converter_api_env/Scripts/activate`*
- start the application `python3 main.py`
