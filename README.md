# BasestationPowerManager
python based power manager for Vive 1.0 base stations
Currently built for Windows, the script may function on Linux but the USB part is specifically Windows only for now.

## Prerequisites
1) The ID of your base station set to channel B. This can be found on the back of the base station, see this image: ![Image of a base station](https://i.imgur.com/yUDwfBD.jpg)
2) If you are running the script, you will need some additional python modules:
  `pip install bleak pywinusb`
  
  If you are running the .exe file, all necessary modules are included.
  
## Usage
Run either the .py script or the .exe executable. On first run, a configuration file will be created, and you will be asked to enter the unique ID of your B channel base station. After entering this, you will be taken to a menu that explains all options. ![Image of BasestaionPowerManager running in console](https://i.imgur.com/rMilQxD.png)

## Notes
If you edit the script and/or want to compile your own .exe file, make sure to include the BleakUWPBridge.dll file found within your python modules folder.
