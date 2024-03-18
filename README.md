# raspberry_pi_powermeter
Raspberry Pi, python GUI power meter

Powermeter app written in Python for Raspberry Pi. GUI made using tkinter.

Powermeter app allows up to four photodiodes connected and displays read values in adaptive GUI according to a number of connected diodes. For each active photodiode user can select wavelength of measured light, use of filters and (optionally)
amplification factor. 

GUI includes a Settings page, where the user can toggle autodetection functionality, logging values to a removable USB drive and sets refresh rate of the GUI between 1 and 10 Hz. USB drive detection performed automatically when logging values is enabled
and error is raised if no drive is connected. Reset to default settings is possible inside Settings page.

Calibration file contains correction factors for each photodiode at different wavelengths of light (650 nm, 976 nm, 1030 nm and 1050 nm) and multiple filters (from OD 0,3 up to OD 4). Last set refresh rate is saved in last_settings file and is used
whenever the powermeter is turned ON.
