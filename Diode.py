from pigpio import *
import time
import yaml
import numpy as np
import time

class Diode:
    """Diode class.
    
    Defines a Diode for use in Power meter App for Raspberry Pi. 
    
    Diode attributes:
        - name (name)
        - ADC I2C address (adc_add)
        - I/O Expander I2C address (tca_add)
        - amplification factor byte - sets mux (amp_bit_dg408)
        - power reading from photodiode (power_read)
        - check boolean for initialization (not_set)
        - check boolean for automatic amplification setting (auto_range)
        - integer variable used in order to stop runtime error (readcount)
        - check boolean for limit cases (overexposed)
        - check boolean for limit cases (underexposed)
        - activity boolean, based on dis/connected photodiode (active)
        - wavelength parameter (wavelength)
        - multiplication factor (multiply_factor)
        - multiplication factor string (multiply_factor_string) [used because value is float and string is 'multiply'/'NDx'/float]

    Constructor takes: ADC address, I/O Expander address.

    Example: d0 = Diode.Diode(0x48, 0x38)
    """
    
    rpi = pi()

    diodeCount = 0
    not_set = True
    int_ref_adc = 2.048
    thresh_up = 1.8
    thresh_down = 0.5
    amp_res = [1000, 3000, 10000, 30000, 100000, 300000, 1000000, 3000000]
    units = ['W', 'mW', 'uW', 'nW', 'pW']
    delay = 0.050

    file = open('calibration.yaml')
    caldata = yaml.load(file, Loader=yaml.FullLoader)
    file.close()

    specific_wavelengths = caldata['calibrated wavelengths']

    # START
    # pin definitions
    scl1_pin = 3
    sda1_pin = 2

    adc_sel_pin = 17
    # END 

    # START
    # I2C protocol setup
    BUS = 1

    # register addresses
    D0_ADC_CONV_REG = 0x00
    D0_ADC_CONF_REG = 0x01 

    D0_TCA_CONF_REG = 0x03
    D0_TCA_OUT_REG = 0x01
    # END

    def __init__(self, adc_add=0x00, tca_add=0x00):
        self.name = ''
        self.adc_add = adc_add
        self.io_add = tca_add
        self.amp_bit_dg408 = 0x00
        self.power_read = 0.
        self.power_unit = 'W'
        self.not_set = True
        self.auto_range = True
        self.readcount = 0
        self.overexposed = False
        self.underexposed = False
        self.active = True
        self.wasactive = False
        self.wavelength = 1030
        self.multiply_factor = 1
        self.multiply_factor_string = 'multiply'
        self.voltage_address = 2.048
        self.calibration = []
        self.serviceMode = False
        Diode.diodeCount += 1
        
    def get_name(self):
        return self.name

    def get_power(self):
        return self.power_read

    def get_adc_address(self):
        return self.adc_add

    def get_io_address(self):
        return self.io_add

    def get_auto_range(self):
        return self.auto_range    
    
    def get_amplification(self):
        return self.amp_bit_dg408

    def get_wavelength(self):
        return self.wavelength

    def get_multiply_factor(self):
        return self.multiply_factor

    def get_multiply_factor_string(self):
        return self.multiply_factor_string

    def get_power_unit(self):
        return self.power_unit

    def display_diode_count(self):
        print('Number of diodes: ', Diode.diodeCount)
        return

    def set_multiply_factor(self, mult):
        self.multiply_factor = mult

    def set_multiply_factor_string(self, s):
        self.multiply_factor_string = s

    def set_serviceMode(self, mode):
        self.serviceMode = mode

    def set_name(self):
        file = open('config.yaml', 'r')
        data = yaml.load(file, Loader=yaml.FullLoader)
        file.close()
        if self.active:
            self.name = data['diodes'][f'd{self.voltage_address:.1f}']['name']
        else:
            self.is_active()

    def set_amplification(self, amp):
        """Manually sets amplification. Disables auto range function."""
        self.amp_bit_dg408 = amp
        self.auto_range = False
        Diode.rpi.i2c_write_byte_data(self.hiic2, Diode.D0_TCA_OUT_REG, self.amp_bit_dg408)
        time.sleep(Diode.delay)

    def set_wavelength(self, wave_val):
        """Sets wavelength."""
        self.wavelength = wave_val

    def toggle_true_auto_range(self):
        """Toggle automatic range of amplification to True."""
        self.auto_range = True

    def get_exposure(self):
        if self.overexposed:
            return 'OVEREXPOSED'
        elif self.underexposed:
            return 'UNDEREXPOSED'
        else:
            return ''

    def choose_source(self, source):
        """Writes appropriate value to the adc_sel (GPIO17) pin in order to choose between diode selection or."""
        # source = True
        
        if source:
            Diode.rpi.write(Diode.adc_sel_pin, True)
            self.read_power = False
        
        else:
            Diode.rpi.write(Diode.adc_sel_pin, False)
            self.read_power = True
        
        return

    def is_active(self):
        """Checks if a photodiode is connected. Updates name."""

        activity = False
        self.read_voltage_add()
        self.choose_source(True)

        if self.voltage_address < 2.0 and self.voltage_address >= 0.0:                  
            self.active = True

            if not self.wasactive:                
                file = open('calibration.yaml', 'r')
                self.calibration = yaml.load(file, Loader=yaml.FullLoader)
                file.close()

            try:
                self.set_name()
            except:
                pass
            self.wasactive = self.active
            activity = True
        
        else:
            self.multiply_factor = 1
            self.multiply_factor_string = 'multiply'
            self.active = False
            self.wasactive = self.active
            activity = False

        return activity

    def set_i2c(self):
        """Initializes I2C protocol for two I2C devices: ADC and I/O Expander with addresses given to constructor."""
        if self.not_set:
            Diode.rpi.set_mode(Diode.adc_sel_pin, OUTPUT)
            Diode.rpi.write(Diode.adc_sel_pin, False)

            self.hiic1 = Diode.rpi.i2c_open(Diode.BUS, self.adc_add)
            self.hiic2 = Diode.rpi.i2c_open(Diode.BUS, self.io_add)   
            if self.hiic1 >= 0:         
                Diode.rpi.i2c_write_i2c_block_data(self.hiic1, Diode.D0_ADC_CONF_REG, [0x84, 0xC3])
                Diode.rpi.i2c_write_byte_data(self.hiic2, Diode.D0_TCA_CONF_REG, 0x00)  
                Diode.rpi.i2c_write_byte(self.hiic1, Diode.D0_ADC_CONV_REG)

            self.not_set = False

    def change_amp(self, fact):
        """Writes to I/O Expander in order to change voltage amplification in circuit.
        
        Takes: fact (bool): if True = amplify, if False = 'deamplify'."""    
        if self.auto_range:
            if fact:        
                if self.amp_bit_dg408 < 0x07:
                    self.amp_bit_dg408 += 0x01
                else:
                    self.amp_bit_dg408 = 0x07
                    self.underexposed = True
                    self.readcount += 1
        
            else:        
                if self.amp_bit_dg408 > 0x00:
                    self.amp_bit_dg408 -= 0x01
                else:
                    self.amp_bit_dg408 = 0x00
                    self.overexposed = True
                    self.readcount += 1
            Diode.rpi.i2c_write_byte_data(self.hiic2, Diode.D0_TCA_OUT_REG, self.amp_bit_dg408)
            time.sleep(Diode.delay)

        else:
            self.readcount +=1

        if self.readcount == 5:  # return 1 if it cycles itself in a loop -> executes when for 5 consecutive calls of change_amp amp stays the same
            self.readcount = 0
            if fact:
                self.underexposed = True
                # self.power_read = 0.000
            elif not fact:
                self.overexposed = True
                # self.power_read = 10.00
            
            return 1
    
        return 0

    def read_voltage_add(self):
        """Reads voltage address on a photodiode."""

        while True:
            
            volt = self.voltage_address

            self.choose_source(True)
            time.sleep(0.01)
        
            (c, data) = Diode.rpi.i2c_read_device(self.hiic1, 2)        
            self.voltage_address = Diode.int_ref_adc * (int.from_bytes(data, 'big', signed=True) / ((2**15) - 1))     

            if (self.voltage_address - volt) <= (self.voltage_address*0.05):
                break

        return 

    def read_data_adc(self):
        """Reads data through I2C protocol from A/D Converter with address given to the constructor."""
        
        # This part defines in which wavelength section photodiode is measuring the power of light.
        if not self.name == '':
            sections = self.calibration['diodes'][f'{self.name}']['sections']
            sec_keys = list(sections.keys())
            true_section = ''
            for i in sec_keys:
                min_index = sections[i].find('-')
                sec_min = int(sections[i][0:min_index])
                sec_max = int(sections[i][min_index+1:])
                if self.wavelength > sec_min and self.wavelength <= sec_max:
                    true_section = i
                    break
                else:
                    true_section = ''        

            if self.is_active():
                self.choose_source(False)

                while True:

                    (c, data) = Diode.rpi.i2c_read_device(self.hiic1, 2)        
                    self.power_read = Diode.int_ref_adc * (int.from_bytes(data, 'big', signed=True) / ((2**15) - 1))
                    
                    """ AUTO RANGE """
                    if self.amp_bit_dg408 == 0x07:
                        lower_limit = 0.01
                    else:
                        lower_limit = Diode.thresh_down

                    if self.amp_bit_dg408 == 0x00:
                        upper_limit = 2.04
                    else:
                        upper_limit = Diode.thresh_up

                    if self.power_read > upper_limit:
                        ex = self.change_amp(False)
                        self.underexposed = False

                    elif self.power_read < lower_limit:
                        ex = self.change_amp(True)
                        self.overexposed = False

                    elif self.power_read <= upper_limit and self.power_read >= lower_limit:
                            # if photodiode is not under or overexposed calculate true power in W by approximating the inverse of responsitivity curve
                            # and multiply it by current -> get W.
                        
                        if self.serviceMode:
                            self.power_unit = 'V'
                            break

                        else:
                            volt = self.power_read
                            current = volt / Diode.amp_res[self.amp_bit_dg408]

                            if self.calibration['diodes'][f'{self.name}'][true_section]['type'] == 'exp':
                                self.power_read = (current * (self.calibration['diodes'][f'{self.name}'][true_section]['eq'][0]*np.exp(self.calibration['diodes'][f'{self.name}'][true_section]['eq'][1]*self.wavelength)))
                            
                            if self.calibration['diodes'][f'{self.name}'][true_section]['type'] == 'poly':
                                poly_power = len(self.calibration['diodes'][f'{self.name}'][true_section]['eq'])
                                self.power_read = 0
                                for i in range(poly_power):
                                    self.power_read += (current * (self.calibration['diodes'][f'{self.name}'][true_section]['eq'][i] * (self.wavelength**i)))
                            
                            if self.wavelength in Diode.specific_wavelengths:
                                self.power_read = self.calibration['diodes'][f'{self.name}']['specific corrections'][f'{self.wavelength}'][f'{int(self.amp_bit_dg408)}'] * self.power_read

                            self.power_read = 2 * (self.multiply_factor * self.power_read * self.calibration['diode ports'][f'{hex(self.adc_add)}'])

                            if self.multiply_factor > 0:
                                ratio_pow = 1 / self.power_read
                                self.power_unit = 'W'

                                if ratio_pow > 1:
                                    if ratio_pow <= 1000:
                                        self.power_read = 1000 * self.power_read
                                        self.power_unit = 'mW'
                                    elif ratio_pow <= 1e6:
                                        self.power_read = 1e6 * self.power_read
                                        self.power_unit = 'uW'
                                    elif ratio_pow <= 1e9:
                                        self.power_read = 1e9 * self.power_read
                                        self.power_unit = 'nW'
                                    elif ratio_pow <= 1e12:
                                        self.power_read = 1e12 * self.power_read
                                        self.power_unit = 'pW'
                            self.readcount = 0
                            self.underexposed = False
                            self.overexposed = False
                            break

                    if ex == 1:
                        return    
          
        return
