# wasp-os-apps

Apps I created for my PineTime running wasp-os

## Usage

- `calcurse.py`: A calendar app that displays events from [calcurse](https://calcurse.org/).
  - Swipe down to view later events
  - Swipe up to view earlier events, and to view previous days
  - Swipe left to view the next day
  - Swipe right to exit the app
- `rich_clk.py`: A clock app that displays:
  - The current time and date (24h format with seconds)
  - Battery voltage
  - Free RAM
  - Uptime
  - Number of steps recorded
  - Number of apps loaded

## Installation

1. [Install wasp-os](https://wiki.pine64.org/wiki/Switching_your_PineTime_between_InfiniTime_and_Wasp-os) on your PineTime.
2. Clone this repository and the `wasp-os` repository:

```bash
git clone https://github.com/CyrilSLi/wasp-os-apps
git clone --recurse-submodules https://github.com/wasp-os/wasp-os
```

3. Verify that `tools/wasptool` is executable:

```bash
wasp-os/tools/wasptool --help
```

4. Install `mpy-cross` version 1.13:

```bash
pip install mpy-cross==1.13
```

5. Compile and upload the apps:

```bash
cd wasp-os-apps
python -m mpy_cross -mno-unicode -O3 -march=armv7m calcurse.py
python -m mpy_cross -mno-unicode -O3 -march=armv7m rich_clk.py
/path/to/wasp-os/tools/wasptool --binary --upload calcurse.mpy
/path/to/wasp-os/tools/wasptool --binary --upload rich_clk.mpy
```

6. Convert your calcurse data to a format compatible with the app:

```bash
python process_calcurse_apts.py
```

7. Set `wasptool_path` in `chunk_upload.py` to the path of your downloaded `wasptool`
8. Upload the calcurse data:

```bash
python chunk_upload.py
```