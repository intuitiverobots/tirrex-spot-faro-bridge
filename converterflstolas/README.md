# ConverterFlsToLas

Convert a scan from *.fls* format to *.las* format using the *FARO sdk*.


# Installation

You can compile the application using Visual Studio following this [guide](https://developer.faro.com/scene_api/index.html) as a [standalone application](https://developer.faro.com/scene_api/md_pages_guides_standalone_app.html) (or find the pre-compiled application in \_Utils/converter_fls_to_las).
To follow along, you will need to ask FARO about:
- the developer package (\_Utils/Developper)
- a FARO SCENE API key (\_Utils/FARO SCENE API key)

# FARO SCENE API Key Setup

This application requires a valid FARO SCENE API key to function properly. The API key has been externalized from the source code for security reasons.

## Setup Instructions

1. Ensure you have a valid FARO SCENE API key file named `SDK-SC-0603251312.txt` in the following location:
   ```
   converterflstolas/_Utils/FARO SCENE API key/SDK-SC-0603251312.txt
   ```

2. The API key file should contain the complete key in the following format:
   ```
   -----BEGIN SCENE API KEY-----
   [Your API key content here]
   -----END SCENE API KEY-----
   ```

3. The `_Utils/FARO SCENE API key/` directory is automatically ignored by git, so your API key will not be committed to version control.


# Usage

Then use `ConverterFlsToLas.exe <scan_path> <scan_converted_dir>` with:
- `scan_path` the path to the scan under *.fls* format
- `scan_converted_dir` the path to the directory in which the scan converted will be saved under *.las* format
