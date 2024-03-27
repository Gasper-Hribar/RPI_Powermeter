# raspberry_pi_powermeter
Raspberry Pi, python GUI power meter

Powermeter app written in Python for Raspberry Pi. GUI made using tkinter.

Powermeter app allows up to four photodiodes connected and displays read values in adaptive GUI according to a number of connected diodes. For each active photodiode user can select wavelength of measured light, use of filters and (optionally) amplification factor. 

GUI includes a Settings page, where the user can toggle autodetection functionality, logging values to a removable USB drive and sets refresh rate of the GUI between 1 and 10 Hz. USB drive detection performed automatically when logging values is enabled and error is raised if no drive is connected. Reset to default settings is possible inside Settings page.

Calibration file contains correction factors for each photodiode at different wavelengths of light (635 nm, 976 nm, 1030 nm and 1050 nm) and multiple filters (from OD 0,3 up to OD 4). Last set refresh rate is saved in last_settings file and is used whenever the powermeter is turned ON.

# Development ideas, not yet implemented

1. Service mode:
  - Gives the user an option to choose between normal and service mode. Service mode displays calculated power as well as read voltages from the ADC directly without the conversion. Auto range is disabled by default.

2. Statistics:
  - Exploring the possibility to draw a graph of the measurements to the GUI for better representation of the measured data.
  - Averaging measurement and adding a setting to choose how many consecutive measurements to include in one reading. Then displaying the average of the measurements.

3. Additional connectivity:
  - Adding a connectivity option between the Raspberry Pi and a PC. One possibility could be via MQTT, but it would require some sort of "global" MQTT broker. 

## TO-DO

- Fix the bug of auto range, when the thing jumps uncontrolably and does not settle. This is especially troubling on the boot of the Raspberry.
- Fix the thresholds. On the borders the range should be full in one way.
- Find a new way to search for the optimal range.
