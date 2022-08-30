#!/usr/local/lib/  python3

from pigpio import *
from Diode import Diode
import tkinter as tk
import tkinter.messagebox as messagebox
import datetime
import os
import yaml
from threading import Timer

if os.environ.get('DISPLAY','') == '':
    os.environ.__setitem__('DISPLAY', ':0.0')  # sets display environment variable to 0.0

# START
# definition of fonts
normal = "Lato 18"
titles = "Lato 20"
outputfont = "Lato 36 bold"
outputminifont = "Lato 16 bold"
normalminifont = "Lato 16"
menufont = "Lato 16 bold"
settingsfont = "Lato 14"
ampfont = "Lato 12"
# END

ptomm = 0.19375  # pixel size in [mm]

# START
# definition of colors
teal = '#538083'
red = '#E3170A' 
light_gray = '#CDD6D0'
dark_gray = '#89909f'
black = '#13070c'
orange = '#E16036'
space_blue = '#0d0f16'
dark_blue = '#767b91'
light_blue = '#c7ccdb'
white_ish = '#e1e5ee'
# END

# START
# main GUI functionality
class powermeter_app(tk.Tk):  # powermeter_app inherits from tk.Tk class
    """
    Powermeter app GUI for Raspberry Pi. 
    """

    def close_app(self):
        """Closes possible open files, then quits."""
        try:
            self.file_log.close()
        except:
            print('No open files.')
        self.quit()

    def refresh(self):
        """Calls a function that checks which photodiodes are connected. Calls a function to reorganize the display if neccessary."""
        prev_diodes = self.diodecount
        self.check_diodes()
        if not prev_diodes == self.diodecount:
            self.rewrite_frames()            
        self.source = self.chosen_source
        return

    def get_time(self):
        """Returns current time as string. Format: YYYY-MM-DD_HH-MM-SS."""
        ct = datetime.datetime.now()
        time_string = f'{ct}'[0:10] + '_' + f'{ct}'[11:13] + '-' + f'{ct}'[14:16] + '-' + f'{ct}'[17:19]
        # print(time_string)
        return time_string

    def get_usb_path(self):
        """Returns a path to USB where it logs measured values."""
        path_to_usb = '/media/pi/'
        dirs = os.listdir(path_to_usb)
        if not dirs == []:
            return f'{path_to_usb}'+f'{dirs[0]}/'
        else:
            messagebox.showerror(title='No USB connected', message='There is no USB device connected to port.')
            return ''

    def write_to_file(self, string_tw):
        """Writes a string it gets to file."""
        try:
            self.file_log.write(string_tw)
            self.file_log.close()
        except:
            print('Error')
        return

    def reset_values(self):
        """Resets vaules used for logging values."""
        self.diode0_log = ' ,'
        self.diode1_log = ' ,'
        self.diode2_log = ' ,'
        self.diode3_log = ' '
        
        return

######
######
######
###### CHECKING NUMBER OF ACTIVE DIODES

    def check_diodes(self):
        """Performs a check on active diodes. Overwrites arrays that include active diodes used later in app. Updates diode count."""        
        self.active_diodes = []
        self.list_of_act_diodes = []
        if self.d0.is_active():
                self.active_diodes.append(0)
                self.list_of_act_diodes.append(self.d0)
        if self.d1.is_active():
                self.active_diodes.append(1)
                self.list_of_act_diodes.append(self.d1)
        if self.d2.is_active():
              self.active_diodes.append(2)
              self.list_of_act_diodes.append(self.d2)
        if self.d3.is_active():
              self.active_diodes.append(3)
              self.list_of_act_diodes.append(self.d3)
        self.diodecount = len(self.active_diodes)
        return

######
######
######
###### CLEARING DISPLAY AND REWRITING IT

    def all_children (self) :
        _list = self.winfo_children()
        print(_list)

        for item in _list :
            if item.winfo_children() :
                _list.extend(item.winfo_children())

        return _list

    def rewrite_frames(self):
        widget_list = self.all_children()
        for item in widget_list:
            item.destroy()
        self.create_widgets()

######
######
######
###### SETTING DEFAULT VALUES FOR GUI VARIABLES

    def set_default_values(self):
        
        with open('config.yaml', 'r') as file:
            self.data = yaml.load(file, Loader=yaml.FullLoader)

        self.delay_time = 1 / self.data['defaults']['refresh rate']  # sets refresha rate on update timer

        # adc and i/o expander addresses 
        self.adc0 = self.data['diode ports']['diodeport 1']['i2c address']['adc']
        self.adc1 = self.data['diode ports']['diodeport 2']['i2c address']['adc']
        self.adc2 = self.data['diode ports']['diodeport 3']['i2c address']['adc']
        self.adc3 = self.data['diode ports']['diodeport 4']['i2c address']['adc']
        self.tca0 = self.data['diode ports']['diodeport 1']['i2c address']['tca']
        self.tca1 = self.data['diode ports']['diodeport 2']['i2c address']['tca']
        self.tca2 = self.data['diode ports']['diodeport 3']['i2c address']['tca']
        self.tca3 = self.data['diode ports']['diodeport 4']['i2c address']['tca']

        # empty usb path -> default = no usb drive connected
        self.usb_path = ''
        
        # declaration of Diodes and setting I2C communication 
        self.d0 = Diode(self.adc0, self.tca0)
        self.d1 = Diode(self.adc1, self.tca1)
        self.d2 = Diode(self.adc2, self.tca2)
        self.d3 = Diode(self.adc3, self.tca3)
        self.all_diodes = [self.d0, self.d1, self.d2, self.d3]

        print(hex(self.d0.get_adc_address()), hex(self.d0.get_io_address()))
        print(hex(self.d1.get_adc_address()), hex(self.d1.get_io_address()))

        print(self.d3.get_adc_address(), self.d3.get_io_address())
        print(self.data['diode ports']['diodeport 4']['i2c address']['adc'], self.data['diode ports']['diodeport 4']['i2c address']['tca'])

        self.d0.set_i2c()
        self.d1.set_i2c()
        self.d2.set_i2c()
        self.d3.set_i2c()

        # getting active diodes - defines number of frames on display
        # self.active_diodes = [0, 1, 2, 3]
        # self.list_of_act_diodes = [self.d0, self.d1]
        # self.diodecount = len(self.active_diodes)

        self.check_diodes()

        self.source = True  # source -> photodiode voltage address: True, power on photodiode: False
        
        # setting tk.Tk() attribute variables used in GUI
        # setting frame dimensions based od screen resolution, pixel to mm transformation
        
        # global dimensions for GUI
        (self.width, self.height) = (self.winfo_width(), self.winfo_height())  # get self.width and self.height of screen in pixels
        (self.labelx, self.labely) = (1.2, 35)
        (self.vol_tx, self.vol_ty) = (1, 120)

        self.frame_height = int((self.height) * ptomm)
        self.h_banner = int(self.height/35  * ptomm)
        self.wid_width = int((self.width/8)  * ptomm)
        self.label_width = 12
        self.text_width = 20
        self.autodetect = False
        self.reading_pow = False
        self.chosen_source = False 

        # log boolean variable, default = False
        self.log_sys = False
        self.file_not_set = True

        # deafult strings to log
        self.diode0_log = ' ,'
        self.diode1_log = ' ,'
        self.diode2_log = ' ,'
        self.diode3_log = ' '

        self.voltage0_factor = 1  # measurement multiplication factors for each diode frame in GUI
        self.voltage1_factor = 1
        self.voltage2_factor = 1
        self.voltage3_factor = 1
        self.volt_factors = [self.voltage0_factor, self.voltage1_factor, self.voltage2_factor, self.voltage3_factor]

        self.multi_text0 = tk.StringVar(self)  # string variable displayed on multiply button
        self.multi_text1 = tk.StringVar(self)
        self.multi_text2 = tk.StringVar(self)
        self.multi_text3 = tk.StringVar(self)
        self.multi_texts = [self.multi_text0, self.multi_text1, self.multi_text2, self.multi_text3]

        self.multi_text0.set('multiply')
        self.multi_text1.set('multiply')
        self.multi_text2.set('multiply')
        self.multi_text3.set('multiply')

        # definition of amplification levels as text on display
        self.amp_level0 = tk.StringVar(self)  # amplification level -> value on DG408 mux pins
        self.amp_level1 = tk.StringVar(self)
        self.amp_level2 = tk.StringVar(self)
        self.amp_level3 = tk.StringVar(self)
        self.amp_levels = [self.amp_level0, self.amp_level1, self.amp_level2, self.amp_level3]

        self.amp_level0.set('amp level auto')
        self.amp_level1.set('amp level auto')
        self.amp_level2.set('amp level auto')
        self.amp_level3.set('amp level auto')
        self.amp_levels = [self.amp_level0, self.amp_level1, self.amp_level2, self.amp_level3]

        # definition of wavelengths as text on display
        self.wavelength_text0 = tk.StringVar(self)
        self.wavelength_text1 = tk.StringVar(self)
        self.wavelength_text2 = tk.StringVar(self)
        self.wavelength_text3 = tk.StringVar(self)
        self.wavelength_texts = [self.wavelength_text0, self.wavelength_text1, self.wavelength_text2, self.wavelength_text3]

        self.wavelength_text0.set('1030 nm')  # wavelength value
        self.wavelength_text1.set('1030 nm')
        self.wavelength_text2.set('1030 nm')
        self.wavelength_text3.set('1030 nm')

        return

######
######
######
###### MULTIPLY VALUE PAGE

    def multiply_value_page(self, num):
        self.mult_value = 0
        self.decimal_count = 0

        def set_value(value, text, num):
            self.list_of_act_diodes[num].set_multiply_factor(value)
            self.list_of_act_diodes[num].set_multiply_factor_string(text)
            mult_page.destroy()

        def custom_value(num):  # custom value window
            self.mult_value = 0
            new_mult = tk.Toplevel(
                bg=white_ish,
                relief='flat')

            new_mult.title('Multiply')
            new_mult.geometry(f'225x210+290+140')

            multiplication = tk.Label(new_mult,
                font=normalminifont,
                fg=space_blue,
                bg=light_gray, 
                justify='center',
                height=2,
                width=20,
                text='multiply value by')

            btn_0 = tk.Button(new_mult, 
                bg=space_blue,
                fg=white_ish,
                font=ampfont,
                justify='center',
                text='0',
                width=2,
                height=2,
                command=lambda: add_to_value(0))

            btn_1 = tk.Button(new_mult, 
                bg=space_blue,
                fg=white_ish,
                font=ampfont,
                justify='center',
                text='1',
                width=2,
                height=2,
                command=lambda: add_to_value(1))

            btn_2 = tk.Button(new_mult, 
                bg=space_blue,
                fg=white_ish,
                font=ampfont,
                justify='center',
                text='2',
                width=2,
                height=2,
                command=lambda: add_to_value(2))

            btn_3 = tk.Button(new_mult, 
                bg=space_blue,
                fg=white_ish,
                font=ampfont,
                justify='center',
                text='3',
                width=2,
                height=2,
                command=lambda: add_to_value(3))

            btn_4 = tk.Button(new_mult, 
                bg=space_blue,
                fg=white_ish,
                font=ampfont,
                justify='center',
                text='4',
                width=2,
                height=2,
                command=lambda: add_to_value(4))

            btn_5 = tk.Button(new_mult, 
                bg=space_blue,
                fg=white_ish,
                font=ampfont,
                justify='center',
                text='5',
                width=2,
                height=2,
                command=lambda: add_to_value(5))

            btn_6 = tk.Button(new_mult, 
                bg=space_blue,
                fg=white_ish,
                font=ampfont,
                justify='center',
                text='6',
                width=2,
                height=2,
                command=lambda: add_to_value(6))

            btn_7 = tk.Button(new_mult, 
                bg=space_blue,
                fg=white_ish,
                font=ampfont,
                justify='center',
                text='7',
                width=2,
                height=2,
                command=lambda: add_to_value(7))

            btn_8 = tk.Button(new_mult, 
                bg=space_blue,
                fg=white_ish,
                font=ampfont,
                justify='center',
                text='8',
                width=2,
                height=2,
                command=lambda: add_to_value(8))

            btn_9 = tk.Button(new_mult, 
                bg=space_blue,
                fg=white_ish,
                font=ampfont,
                justify='center',
                text='9',
                width=2,
                height=2,
                command=lambda: add_to_value(9))

            btn_dot = tk.Button(new_mult, 
                bg=space_blue,
                fg=white_ish,
                font=ampfont,
                justify='center',
                text='.',
                width=2,
                height=2,
                command=lambda: dec_count())

            btn_OK = tk.Button(new_mult, 
                bg=space_blue,
                fg=red,
                font=ampfont,
                justify='center',
                text='ok',
                width=18,
                height=2,
                command=lambda: confirm_value(num))

            multiplication.place(relx=0.5, rely=0.1, anchor='center')
            btn_0.place(relx=0, rely=0.22)
            btn_1.place(relx=0.2, rely=0.22)
            btn_2.place(relx=0.4, rely=0.22)
            btn_3.place(relx=0.6, rely=0.22)
            btn_4.place(relx=0.8, rely=0.22)
            btn_5.place(relx=0, rely=0.48)
            btn_6.place(relx=0.2, rely=0.48)
            btn_7.place(relx=0.4, rely=0.48)
            btn_8.place(relx=0.6, rely=0.48)
            btn_9.place(relx=0.8, rely=0.48)
            btn_dot.place(relx=0, rely=0.74)
            btn_OK.place(relx=0.2, rely=0.74)

            def confirm_value(num):
                new_mult.destroy()
                set_value(self.mult_value, f'{self.mult_value}', num)

            def dec_count():
                self.decimal_count += 1

            def add_to_value(val):
                if self.decimal_count == 0:
                    self.mult_value = (10 * self.mult_value) + val
                else:
                    self.mult_value = self.mult_value + (val / 10**self.decimal_count)
                    self.decimal_count += 1
                multiplication['text'] = self.mult_value

        mult_page = tk.Toplevel(self,
            bg=white_ish,
            relief='flat')

        mult_page.title('.')
        mult_page.geometry('100x400+350+10')

        btn_ND03 = tk.Button(mult_page, 
            bg=space_blue,
            fg=white_ish,
            font=ampfont,
            justify='center',
            text='ND0,3',
            width=7,
            height=2,
            command=lambda: set_value(2, 'ND0,3', num))

        btn_ND06 = tk.Button(mult_page, 
            bg=space_blue,
            fg=white_ish,
            font=ampfont,
            justify='center',
            text='ND0,6',
            width=7,
            height=2,
            command=lambda: set_value(4, 'ND0,6', num))

        btn_ND1 = tk.Button(mult_page, 
            bg=space_blue,
            fg=white_ish,
            font=ampfont,
            justify='center',
            text='ND1',
            width=7,
            height=2,
            command=lambda: set_value(10, 'ND1', num))

        btn_ND2 = tk.Button(mult_page, 
            bg=space_blue,
            fg=white_ish,
            font=ampfont,
            justify='center',
            text='ND2',
            width=7,
            height=2,
            command=lambda: set_value(100, 'ND2', num))

        btn_ND3 = tk.Button(mult_page, 
            bg=space_blue,
            fg=white_ish,
            font=ampfont,
            justify='center',
            text='ND3',
            width=7,
            height=2,
            command=lambda: set_value(1000, 'ND3', num))

        btn_ND4 = tk.Button(mult_page, 
            bg=space_blue,
            fg=white_ish,
            font=ampfont,
            justify='center',
            text='ND4',
            width=7,
            height=2,
            command=lambda: set_value(10000, 'ND4', num))

        btn_reset = tk.Button(mult_page, 
            bg=teal,
            fg=white_ish,
            font=ampfont,
            justify='center',
            text='reset',
            width=7,
            height=2,
            command=lambda: set_value(1, 'mulitply', num))

        btn_custom = tk.Button(mult_page, 
            bg=dark_blue,
            fg=white_ish,
            font=ampfont,
            justify='center',
            text='custom',
            width=7,
            height=2,
            command=lambda: custom_value(num))

        btn_ND03.place(relx=0.5, rely=0.08, anchor='center')
        btn_ND06.place(relx=0.5, rely=0.20, anchor='center')
        btn_ND1.place(relx=0.5, rely=0.32, anchor='center')
        btn_ND2.place(relx=0.5, rely=0.44, anchor='center')
        btn_ND3.place(relx=0.5, rely=0.56, anchor='center')
        btn_ND4.place(relx=0.5, rely=0.68, anchor='center')
        btn_custom.place(relx=0.5, rely=0.80, anchor='center')
        btn_reset.place(relx=0.5, rely=0.92, anchor='center')


        return

###### 
######
######
###### SETTINGS PAGE

    def settings_page(self):
        """Opens a new Toplevel window on top of root window. 
        
        Contains settings for powermeter.
        """

        setts_page = tk.Toplevel(  # new Toplevel window
            bg=light_gray,
            name='settings',
            relief='flat')

        setts_page.title('Settings')
        setts_page.geometry('500x300+150+10')

        """SOURCE SELECTION"""

        # msg = tk.Message(setts_page,  # introductory message
        #     text="Welcome to Settings", 
        #     width=200,
        #     bg=light_gray,
        #     font=settingsfont,
        #     fg=dark_blue,
        #     justify='center')
        # msg.place(relx=0.5, rely=0.05, anchor='center')

        # set_source_msg = tk.Message(setts_page,  # source selection message
        #     text="Select source:", 
        #     width=100,
        #     bg=light_gray,
        #     justify='center')
        # set_source_msg.place(relx=0.25, rely=0.2, anchor='center')

        # volt_source_btn = tk.Button(setts_page,  # select voltage button
        #     bg=teal,
        #     fg=white_ish,
        #     font=settingsfont,
        #     justify='center',
        #     text='voltage',
        #     width=8,
        #     height=1,
        #     command=lambda: choose_volt())
        # volt_source_btn.place(relx=0.49, rely=0.20, anchor='center')

        # pow_source_btn = tk.Button(setts_page,  # select power button
        #     bg=teal,
        #     fg=white_ish,
        #     font=settingsfont,
        #     justify='center',
        #     text='power',
        #     width=8,
        #     height=1,
        #     command=lambda: choose_pow())
        # pow_source_btn.place(relx=0.70, rely=0.20, anchor='center')

        """AUTO DETECTION"""

        en_autodetect_msg = tk.Message(setts_page,  # toggle auto detection message
            text="Auto-detection: ", 
            width=120,
            bg=light_gray,
            fg=black,
            justify='center')
        en_autodetect_msg.place(relx=0.2, rely=0.12, anchor='center')

        if self.autodetect:  # setting button colours according to auto detection 
        # if True:
            enb_color = teal
            disb_color = light_gray
            disb_fg = black
            enb_fg = white_ish
        else:
            enb_color = light_gray
            disb_color = red
            disb_fg = white_ish
            enb_fg = black

        enable_btn = tk.Button(setts_page,  # enable auto detection button
            bg=enb_color,
            fg=enb_fg,
            font=settingsfont,
            justify='center',
            text='enable',
            width=8,
            height=1,
            command=lambda: enable_auto())
        enable_btn.place(relx=0.5, rely=0.12, anchor='center')

        disable_btn = tk.Button(setts_page,  # disable auto detection button
            bg=disb_color,
            fg=disb_fg,
            font=settingsfont,
            justify='center',
            text='disable',
            width=8,
            height=1,
            command=lambda: disable_auto())
        disable_btn.place(relx=0.75, rely=0.12, anchor='center')

        """LOGGING VALUES SETTINGS"""

        if self.log_sys:  # setting button colours when logging is happening 
            logb_color = teal
            dislogb_color = light_gray
            dislogb_fg = black
            logb_fg = white_ish
        else:
            logb_color = light_gray
            dislogb_color = red
            dislogb_fg = white_ish
            logb_fg = black

        start_log_msg = tk.Message(setts_page,  # start logging message
            text="Logging values:", 
            width=120,
            bg=light_gray,
            fg=black,
            justify='center')
        start_log_msg.place(relx=0.2, rely=0.3, anchor='center')

        log_diode_btn = tk.Button(setts_page,  # start logging values from diodes frame button
            bg=logb_color,
            fg=logb_fg,
            font=settingsfont,
            justify='center',
            text='start log',
            width=8,
            height=1,
            command=lambda: start_log())
        log_diode_btn.place(relx=0.5, rely=0.3, anchor='center')

        stoplog_diode_btn = tk.Button(setts_page,  # stop logging values from diodes frame button
            bg=dislogb_color,
            fg=dislogb_fg,
            font=settingsfont,
            justify='center',
            text='stop log',
            width=8,
            height=1,
            command=lambda: stop_log())
        stoplog_diode_btn.place(relx=0.75, rely=0.3, anchor='center')

        """MISCELLANEOUS BUTTONS"""

        eject_btn = tk.Button(setts_page, 
            bg=teal,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='eject usb',
            width=6,
            height=1,
            command=lambda: eject_usb())
        eject_btn.place(relx=0.5, rely=0.9, anchor='center')

        back_btn = tk.Button(setts_page, 
            bg=red,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='back',
            width=3,
            height=1,
            command=lambda:setts_page.destroy())
        back_btn.place(relx=0.9, rely=0.9, anchor='center')

        reset_btn = tk.Button(setts_page, 
            bg=teal,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='reset',
            width=3,
            height=1,
            command=lambda: reset())
        reset_btn.place(relx=0.1, rely=0.9, anchor='center')

        """BUTTONS RELATED FUNCTIONS"""

        def eject_usb():
            cmd = "sudo umount /dev/sda1"
            os.system(cmd)
            stop_log()

        def start_log():
            if self.log_sys == False:
                self.usb_path = self.get_usb_path()
                self.log_sys = True
            setts_page.destroy()

        def stop_log():
            self.log_sys = False
            self.usb_path = ''
            self.file_log.close()
            setts_page.destroy()

        # def choose_volt():
        #     self.source = True
        #     self.chosen_source = True
        #     self.reading_pow = False
        #     setts_page.destroy()

        # def choose_pow():
        #     self.source = False
        #     self.chosen_source = False
        #     self.reading_pow = True
        #     setts_page.destroy()

        def enable_auto():
            self.autodetect = True
            setts_page.destroy()

        def disable_auto():
            self.autodetect = False
            setts_page.destroy()

        def reset():  # resets all settings to their default values
            self.source = False
            self.reading_pow = True
            self.autodetect = False
            if self.diodecount > 0:
                self.voltage0_factor = 1
                self.wavelength_text0.set('1030 nm')
                self.list_of_act_diodes[0].set_wavelength(1030)
                self.list_of_act_diodes[0].toggle_true_auto_range()
                self.amp_level0.set('amp level auto')
                self.multi_text0.set('multiply')
            if self.diodecount >= 2:
                self.voltage1_factor = 1
                self.wavelength_text1.set('1030 nm')
                self.list_of_act_diodes[1].set_wavelength(1030)
                self.list_of_act_diodes[1].toggle_true_auto_range()
                self.amp_level1.set('amp level auto')
                self.multi_text1.set('multiply')
            if self.diodecount >= 3:
                self.voltage2_factor = 1
                self.wavelength_text2.set('1030 nm')
                # self.list_of_act_diodes[2].set_wavelength(1030)
                # self.list_of_act_diodes[2].toggle_true_auto_range()
                self.amp_level2.set('amp level auto')
                self.multi_text2.set('multiply')
            if self.diodecount == 4:
                self.voltage3_factor = 1
                self.wavelength_text3.set('1030 nm')
                # self.list_of_act_diodes[3].set_wavelength(1030)
                # self.list_of_act_diodes[3].toggle_true_auto_range()
                self.amp_level3.set('amp level auto')
                self.multi_text3.set('multiply')
            setts_page.destroy()
            self.update_widgets()
            return

###### 
######
######
###### WAVELENGTH SETTINGS POP-UP WINDOW

    def set_wavelength(self, num):
        "Displays a new Toplevel window in which user sets a new wavelength for a photodiode."

        self.wave_value = 0

        new_wave = tk.Toplevel(
            bg=white_ish,
            relief='flat')

        new_wave.title('.')
        new_wave.geometry(f'225x225+290+130')

        wavelength = tk.Label(new_wave,
            font=outputminifont,
            fg=space_blue,
            bg=light_gray, 
            justify='center',
            height=2,
            width=20,
            text='')

        btn_0 = tk.Button(new_wave, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='0',
            width=2,
            height=2,
            command=lambda: add_to_value(0))

        btn_1 = tk.Button(new_wave, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='1',
            width=2,
            height=2,
            command=lambda: add_to_value(1))

        btn_2 = tk.Button(new_wave, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='2',
            width=2,
            height=2,
            command=lambda: add_to_value(2))

        btn_3 = tk.Button(new_wave, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='3',
            width=2,
            height=2,
            command=lambda: add_to_value(3))

        btn_4 = tk.Button(new_wave, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='4',
            width=2,
            height=2,
            command=lambda: add_to_value(4))

        btn_5 = tk.Button(new_wave, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='5',
            width=2,
            height=2,
            command=lambda: add_to_value(5))

        btn_6 = tk.Button(new_wave, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='6',
            width=2,
            height=2,
            command=lambda: add_to_value(6))

        btn_7 = tk.Button(new_wave, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='7',
            width=2,
            height=2,
            command=lambda: add_to_value(7))

        btn_8 = tk.Button(new_wave, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='8',
            width=2,
            height=2,
            command=lambda: add_to_value(8))

        btn_9 = tk.Button(new_wave, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='9',
            width=2,
            height=2,
            command=lambda: add_to_value(9))

        btn_OK = tk.Button(new_wave, 
            bg=space_blue,
            fg=red,
            font=settingsfont,
            justify='center',
            text='ok',
            width=18,
            height=2,
            command=lambda: confirm_value(num))

        wavelength.place(relx=0.5, rely=0.1, anchor='center')
        btn_0.place(relx=0, rely=0.22)
        btn_1.place(relx=0.2, rely=0.22)
        btn_2.place(relx=0.4, rely=0.22)
        btn_3.place(relx=0.6, rely=0.22)
        btn_4.place(relx=0.8, rely=0.22)
        btn_5.place(relx=0, rely=0.48)
        btn_6.place(relx=0.2, rely=0.48)
        btn_7.place(relx=0.4, rely=0.48)
        btn_8.place(relx=0.6, rely=0.48)
        btn_9.place(relx=0.8, rely=0.48)
        btn_OK.place(relx=0, rely=0.75)

        def confirm_value(num):
            if self.wave_value > 400 and self.wave_value <= 1100:
                self.wavelength_texts[num].set(f'{self.wave_value} nm')
                self.list_of_act_diodes[num].set_wavelength(self.wave_value)
                # if num == 0:
                #     self.wavelength_text0.set(f'{self.wave_value} nm')
                #     self.list_of_act_diodes[0].set_wavelength(self.wave_value)
                # elif num == 1:
                #     self.wavelength_text1.set(f'{self.wave_value} nm')
                #     self.list_of_act_diodes[1].set_wavelength(self.wave_value)
                # elif num == 2:
                #     self.wavelength_text2.set(f'{self.wave_value} nm')
                #     self.list_of_act_diodes[2].set_wavelength(self.wave_value)
                # elif num == 3:
                #     self.wavelength_text3.set(f'{self.wave_value} nm')
                #     self.list_of_act_diodes[3].set_wavelength(self.wave_value)
            else:
                messagebox.showwarning(title='Unsupported wavelength',
                    message='Inserted wavelength is outside of measurable interval.')

        #     print(self.wave_value)
            self.wave_value = 0
            new_wave.destroy()

        def add_to_value(val):
            self.wave_value = (10 * self.wave_value) + val
            wavelength['text'] = self.wave_value

###### 
######
######
###### RANGE SETTINGS POP-UP WINDOW

    def set_range_to(self, num):
        """Displays a new Toplevel window in which user manually sets a new range for Diode"""

        new_range = tk.Toplevel(
            bg=white_ish,
            relief='flat')

        new_range.title('.')
        new_range.geometry(f'190x172+305+155')

        btn_0 = tk.Button(new_range, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='0',
            width=2,
            height=2,
            command=lambda: man_change_range(0, num))

        btn_1 = tk.Button(new_range, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='1',
            width=2,
            height=2,
            command=lambda: man_change_range(1, num))

        btn_2 = tk.Button(new_range, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='2',
            width=2,
            height=2,
            command=lambda: man_change_range(2, num))

        btn_3 = tk.Button(new_range, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='3',
            width=2,
            height=2,
            command=lambda: man_change_range(3, num))

        btn_4 = tk.Button(new_range, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='4',
            width=2,
            height=2,
            command=lambda: man_change_range(4, num))

        btn_5 = tk.Button(new_range, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='5',
            width=2,
            height=2,
            command=lambda: man_change_range(5, num))

        btn_6 = tk.Button(new_range, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='6',
            width=2,
            height=2,
            command=lambda: man_change_range(6, num))

        btn_7 = tk.Button(new_range, 
            bg=space_blue,
            fg=white_ish,
            font=settingsfont,
            justify='center',
            text='7',
            width=2,
            height=2,
            command=lambda: man_change_range(7, num))

        btn_auto = tk.Button(new_range, 
            bg=space_blue,
            fg=red,
            font=settingsfont,
            justify='center',
            text='auto',
            width=15,
            height=2,
            command=lambda: set_auto_amp(num))

        btn_0.place(relx=0, rely=0)
        btn_1.place(relx=0.25, rely=0)
        btn_2.place(relx=0.5, rely=0)
        btn_3.place(relx=0.75, rely=0)
        btn_4.place(relx=0, rely=0.35)
        btn_5.place(relx=0.25, rely=0.35)
        btn_6.place(relx=0.5, rely=0.35)
        btn_7.place(relx=0.75, rely=0.35)
        btn_auto.place(relx=0, rely=0.68)
        
        def man_change_range(rang, num):
            if not self.autodetect:
                self.list_of_act_diodes[num].set_amplification(rang)
                self.amp_levels[num].set(f'amp level {rang}')
                # if num == 0:
                #     self.list_of_act_diodes[num].set_amplification(rang)
                #     self.amp_levels[num].set(f'amp level {rang}')
                # elif num == 1:
                #     self.d1.set_amplification(rang)
                #     self.amp_level1.set(f'amp level {rang}')
                # elif num == 2:
                #     self.d2.set_amplification(rang)
                #     self.amp_level2.set(f'amp level {rang}')
                # elif num == 3:
                #     self.d3.set_amplification(rang)
                #     self.amp_level3.set(f'amp level {rang}')
                # self.amp_levels = [self.amp_level0, self.amp_level1, self.amp_level2, self.amp_level3]
                new_range.destroy()

            else:
                messagebox.showwarning(title='Auto-detection enabled', 
                    message='Auto-detection of photodiodes is enabled. In order to choose your own amplification range, disable it in the settings.')

        def set_auto_amp(num):
            self.list_of_act_diodes[num].toggle_true_auto_range()
            self.amp_levels[num].set('amp level auto')
            # if num == 0:
            #     self.d0.toggle_true_auto_range()
            #     self.amp_level0.set('amp level auto')
            # elif num==1:
            #     self.d1.toggle_true_auto_range()
            #     self.amp_level1.set('amp level auto')
            # elif num==2:
            #     self.d2.toggle_true_auto_range()
            #     self.amp_level2.set('amp level auto')
            # elif num==3:
            #     self.d3.toggle_true_auto_range()
            #     self.amp_level3.set('amp level auto')

            new_range.destroy()

###### 
######
######
###### UPDATE WIDGETS FUNCTION

    def update_widgets(self):
        """Updates voltages and rewrites them on screen."""

        if self.autodetect:            
            self.refresh()

        self.diodecount = len(self.list_of_act_diodes)
        # self.list_of_act_diodes[0].choose_source(self.source)
        # while True:
        #     self.check_diodes()

        if self.source:
            self.reading_pow = False
        else:
            self.reading_pow = True
            for i in self.list_of_act_diodes:
                i.read_data_adc()  # reads voltages on active photodiodes

        if self.reading_pow:

            string_tw = ''
            value_arr = []

            for i in range(self.diodecount):  # updates all variables on displayed frames
                value = f'{(round(self.list_of_act_diodes[i].get_power(), 5)):.3f}'[:7]
                value_arr.append(value)
                self.unit_labels[i]['text'] = f'{self.list_of_act_diodes[i].get_power_unit()}'
                self.output_labels[i]['text'] = value
                self.wavelength_buttons[i]['text'] = self.wavelength_texts[i].get()
                self.amp_nums[i]['text'] = f'{hex(self.list_of_act_diodes[i].get_amplification())}'
                self.amp_labels[i]['text'] = f'{self.list_of_act_diodes[i].get_exposure()}'
                self.amp_buttons[i]['text'] = self.amp_levels[i].get()               
                self.factor_buttons[i]['text'] = self.list_of_act_diodes[i].get_multiply_factor_string()

            if self.log_sys:

                for i in range(self.diodecount):  # saves read values to specified variables in order to keep the right diode orde of values
                    if self.list_of_act_diodes[i].get_adc_address() == self.adc0:
                        self.diode0_log = value_arr[i] + ','
                    if self.list_of_act_diodes[i].get_adc_address() == self.adc1:
                        self.diode1_log = value_arr[i] + ','
                    if self.list_of_act_diodes[i].get_adc_address() == self.adc2:
                        self.diode2_log = value_arr[i] + ','
                    if self.list_of_act_diodes[i].get_adc_address() == self.adc3:
                        self.diode3_log = value_arr[i]
                
                if not self.file_not_set:  # opens a SET file to APPEND to it
                    self.file_log = open(self.file_p, 'a')

                if self.file_not_set:  # opens a NOT SET file to WRITE to it
                    self.file_not_set = False
                    time_frame = self.get_time()
                    filename = 'powermeter_' + time_frame + '.csv'
                    self.file_p = self.usb_path + filename  # define a name for file
                    if not self.usb_path == '':
                        self.file_log = open(self.file_p, 'w')
                        self.file_log.write(f'PowerMeter: FOLAS -> log @ {time_frame}.\n')  # header of a file
                        self.file_log.write('diode 0, diode 1, diode 2, diode 4\n')
                
                string_tw = self.diode0_log + self.diode1_log + self.diode2_log + self.diode3_log + '\n'
                self.write_to_file(string_tw)
                self.reset_values()
            
        return
###### 
######
######
###### CREATE WIDGETS FUNCTION

    def create_widgets(self):
        """Creates frames according to the number of photodiodes attached.
        
        Adds labels and text widgets to frames.
        """

        self.source = False
        self.diodecount = len(self.list_of_act_diodes)

        if self.source:
            self.voltagetext = 'Voltage [V]'
        else:
            self.voltagetext = 'Power [W]'

        self.menu = tk.Menu(self, 
            bg=light_gray, 
            fg=space_blue, 
            activebackground=teal, 
            font=menufont)

        self.config(menu=self.menu)

        if self.diodecount > 0:
            frame_width = 0.96 / self.diodecount
            frame_dist = 0.04 / (self.diodecount + 1)

        settsMenu = tk.Menu(self.menu)
        exitMenu = tk.Menu(self.menu)
        settsMenu.add_command(label='Settings', command=self.settings_page, font=menufont)
        # settsMenu.add_command(label='Refresh', command=self.refresh, font=menufont)        
        self.menu.add_cascade(label='Settings', menu=settsMenu)
        exitMenu.add_command(label='Exit', command=self.close_app, background=red, font=menufont, activebackground=red)
        self.menu.add_cascade(label='Exit', menu=exitMenu)
        
        if self.diodecount == 0:
            messagebox.showerror(title='No diodes connected', message='There are no photodiodes connected to the powermeter.')

        self.diode_banners = []
        self.title_labels = []
        self.unit_labels = []
        self.output_labels = []
        self.wavelength_buttons = []
        self.amp_nums = []
        self.amp_labels = []
        self.amp_buttons = []
        self.factor_buttons = []

        if self.diodecount > 0:
            self.diode_banner = tk.Frame(self, 
                width=f'{self.wid_width}m', 
                height=f'{self.frame_height}m', 
                relief='flat',
                bg=light_gray)
            self.diode_banners.append(self.diode_banner)

            self.l = tk.Label(self.diode_banner, 
                text=f"P{self.active_diodes[0]}: {self.list_of_act_diodes[0].get_name()}", 
                font=titles,
                fg=space_blue,
                bg=light_gray, 
                justify='center',
                height=self.h_banner,
                width=self.label_width)
            self.title_labels.append(self.l)

            self.unit0 = tk.Label(self.diode_banner, 
                width=self.label_width, 
                height=self.h_banner,
                fg=space_blue,
                bg=light_gray, 
                font=normal,
                text=self.voltagetext)
            self.unit_labels.append(self.unit0)

            self.output0 = tk.Label(self.diode_banner, 
                width=self.text_width-2, 
                height=1, 
                bg=white_ish, 
                fg=red, 
                font=outputfont,
                relief='flat',
                justify='center',
                text='0.0')
            self.output_labels.append(self.output0)

            self.wave_text = tk.Button(self.diode_banner, 
                width=self.label_width+6, 
                height=1,
                fg=teal,
                bg=light_gray, 
                font=outputminifont,
                text=self.wavelength_text0,
                relief='flat',
                command=lambda: self.set_wavelength(0))
            self.wavelength_buttons.append(self.wave_text)

            self.amp_num = tk.Label(self.diode_banner, 
                width=self.label_width, 
                height=self.h_banner,
                fg=space_blue,
                bg=light_gray, 
                font=ampfont,
                text='0x00')
            self.amp_nums.append(self.amp_num)

            self.amp_msg = tk.Label(self.diode_banner,
                width=self.label_width+10, 
                height=self.h_banner,
                bg=light_gray,
                font=ampfont,
                fg=orange,
                justify='center',
                text='')
            self.amp_labels.append(self.amp_msg)

            self.ampl = tk.Button(self.diode_banner,
                width=self.text_width-2, 
                height=1, 
                bg=light_gray, 
                fg=teal, 
                font=outputminifont,
                relief='flat',
                border=0,
                text=self.amp_level0.get(),
                command=lambda: self.set_range_to(self.active_diodes[0]))
            self.amp_buttons.append(self.ampl)

            self.factor_button = tk.Button(self.diode_banner, 
                width=self.label_width+6, 
                height=1,
                fg=teal,
                bg=light_gray, 
                font=outputminifont,
                text=self.multi_text0.get(),
                relief='flat',
                command=lambda: self.multiply_value_page(0))
            self.factor_buttons.append(self.factor_button)

            self.l.place(relx=0.5, y=self.labely, anchor='center')
            self.unit0.place(relx=0.5, rely=0.23, anchor='center')
            self.output0.place(relx=0.5, rely=0.38, anchor='center')
            self.amp_msg.place(relx=0.5, rely=0.51, anchor='center')
            self.factor_button.place(relx=0.5, rely=0.6, anchor='center')
            self.wave_text.place(relx=0.5, rely=0.7, anchor='center')
            self.ampl.place(relx=0.5, rely=0.8, anchor='center')
            self.amp_num.place(relx=0.5, rely=0.90, anchor='center')
            self.diode_banner.place(relx=frame_dist, 
                y=10, 
                relwidth=frame_width, 
                relheight=0.95)  # relative positioning of frames to master window


        if self.diodecount >= 2:
            self.diode_banner_1 = tk.Frame(self, 
                width=f'{self.wid_width}m', 
                height=f'{self.frame_height}m', 
                relief='flat',
                bg=light_gray)
            self.diode_banners.append(self.diode_banner_1)

            self.l1 = tk.Label(self.diode_banner_1, 
                text=f"P{self.active_diodes[1]}: {self.list_of_act_diodes[1].get_name()}", 
                font=titles, 
                justify='center',
                fg=space_blue,
                bg=light_gray,
                height=self.h_banner,
                width=self.label_width)
            self.title_labels.append(self.l1)

            self.unit1 = tk.Label(self.diode_banner_1, 
                width=self.label_width, 
                height=self.h_banner,
                fg=space_blue,
                bg=light_gray, 
                font=normal,
                text=self.voltagetext)
            self.unit_labels.append(self.unit1)

            self.output1 = tk.Label(self.diode_banner_1, 
                width=self.text_width-2, 
                height=1, 
                bg=white_ish, 
                fg=red, 
                font=outputfont,
                relief='flat',
                justify='center',
                text='0.0')
            self.output_labels.append(self.output1)

            self.wave_text1 = tk.Button(self.diode_banner_1, 
                width=self.label_width+6, 
                height=1,
                fg=teal,
                bg=light_gray, 
                font=outputminifont,
                text=self.wavelength_text1,
                relief='flat',
                command=lambda: self.set_wavelength(1))
            self.wavelength_buttons.append(self.wave_text1)

            self.amp_num1 = tk.Label(self.diode_banner_1, 
                width=self.label_width, 
                height=self.h_banner,
                fg=space_blue,
                bg=light_gray, 
                font=ampfont,
                text='0x00')
            self.amp_nums.append(self.amp_num1)

            self.amp_msg1 = tk.Label(self.diode_banner_1,
                width=self.label_width+10, 
                height=self.h_banner,
                bg=light_gray,
                font=ampfont,
                fg=orange,
                justify='center',
                text='')
            self.amp_labels.append(self.amp_msg1)

            self.ampl1 = tk.Button(self.diode_banner_1,
                width=self.text_width-2, 
                height=1, 
                bg=light_gray, 
                fg=teal, 
                font=outputminifont,
                relief='flat',
                border=0,
                text=self.amp_level1.get(),
                command=lambda: self.set_range_to(self.active_diodes[1]))
            self.amp_buttons.append(self.ampl1)

            self.factor_button1 = tk.Button(self.diode_banner_1, 
                width=self.label_width+6, 
                height=1,
                fg=teal,
                bg=light_gray, 
                font=outputminifont,
                text=self.multi_text1.get(),
                relief='flat',
                command=lambda: self.multiply_value_page(1))
            self.factor_buttons.append(self.factor_button1)

            self.l1.place(relx=0.5, y=self.labely, anchor='center')
            self.unit1.place(relx=0.5, rely=0.23, anchor='center')
            self.output1.place(relx=0.5, rely=0.38, anchor='center')
            self.amp_msg1.place(relx=0.5, rely=0.51, anchor='center')
            self.factor_button1.place(relx=0.5, rely=0.6, anchor='center')
            self.wave_text1.place(relx=0.5, rely=0.7, anchor='center')
            self.ampl1.place(relx=0.5, rely=0.8, anchor='center')
            self.amp_num1.place(relx=0.5, rely=0.90, anchor='center')
            self.diode_banner_1.place(relx=2*frame_dist + frame_width, 
                y=10, 
                relwidth=frame_width, 
                relheight=0.95)


        if self.diodecount >= 3:
            self.diode_banner_2 = tk.Frame(self, 
                width=f'{self.wid_width}m', 
                height=f'{self.frame_height}m', 
                relief='flat',
                bg=light_gray)
            self.diode_banners.append(self.diode_banner_2)

            self.l2 = tk.Label(self.diode_banner_2, 
                text=f"P{self.active_diodes[2]}: {self.list_of_act_diodes[2].get_name()}", 
                font=titles,
                fg=space_blue,
                bg=light_gray, 
                justify='center',
                height=self.h_banner,
                width=self.label_width)
            self.title_labels.append(self.l2)

            self.unit2 = tk.Label(self.diode_banner_2, 
                width=self.label_width, 
                height=self.h_banner,
                fg=space_blue,
                bg=light_gray, 
                font=normal,
                text=self.voltagetext)
            self.unit_labels.append(self.unit2)

            self.output2 = tk.Label(self.diode_banner_2, 
                width=self.text_width-2, 
                height=1, 
                bg=white_ish, 
                fg=red, 
                font=outputfont,
                relief='flat',
                justify='center',
                text='0.0')
            self.output_labels.append(self.output2)

            self.wave_text2 = tk.Button(self.diode_banner_2, 
                width=self.label_width+6, 
                height=1,
                fg=teal,
                bg=light_gray, 
                font=outputminifont,
                text=self.wavelength_text2,
                relief='flat',
                command=lambda: self.set_wavelength(2))
            self.wavelength_buttons.append(self.wave_text2)

            self.amp_num2 = tk.Label(self.diode_banner_2, 
                width=self.label_width, 
                height=self.h_banner,
                fg=space_blue,
                bg=light_gray, 
                font=ampfont,
                text='0x00')
            self.amp_nums.append(self.amp_num2)

            self.amp_msg2 = tk.Label(self.diode_banner_2,
                width=self.label_width+10, 
                height=self.h_banner,
                bg=light_gray,
                font=ampfont,
                fg=orange,
                justify='center',
                text='')
            self.amp_labels.append(self.amp_msg2)

            self.ampl2 = tk.Button(self.diode_banner_2,
                width=self.text_width-2, 
                height=1, 
                bg=light_gray, 
                fg=teal, 
                font=outputminifont,
                relief='flat',
                border=0,
                text=self.amp_level2.get(),
                command=lambda: self.set_range_to(self.active_diodes[0]))
            self.amp_buttons.append(self.ampl2)
            
            self.factor_button2 = tk.Button(self.diode_banner_2, 
                width=self.label_width+6, 
                height=1,
                fg=teal,
                bg=light_gray, 
                font=outputminifont,
                text=self.multi_text2.get(),
                relief='flat',
                command=lambda: self.multiply_value_page(2))
            self.factor_buttons.append(self.factor_button2)
            
            self.l2.place(relx=0.5, y=self.labely, anchor='center')
            self.unit2.place(relx=0.5, rely=0.23, anchor='center')
            self.output2.place(relx=0.5, rely=0.38, anchor='center')
            self.amp_msg2.place(relx=0.5, rely=0.51, anchor='center')
            self.factor_button2.place(relx=0.5, rely=0.6, anchor='center')
            self.wave_text2.place(relx=0.5, rely=0.7, anchor='center')
            self.ampl2.place(relx=0.5, rely=0.8, anchor='center')
            self.amp_num2.place(relx=0.5, rely=0.90, anchor='center')
            self.diode_banner_2.place(relx=3*frame_dist + 2*frame_width, 
                y=10, 
                relwidth=frame_width, 
                relheight=0.95)

        if self.diodecount == 4:

            self.diode_banner_3 = tk.Frame(self, 
                width=f'{self.wid_width}m', 
                height=f'{self.frame_height}m', 
                relief='flat',
                bg=light_gray)
            self.diode_banners.append(self.diode_banner_3)

            self.l3 = tk.Label(self.diode_banner_3, 
                text=f"P{self.active_diodes[3]}: {self.list_of_act_diodes[3].get_name()}", 
                font=titles, 
                justify='center',
                fg=space_blue,
                bg=light_gray,
                height=self.h_banner,
                width=self.label_width)
            self.title_labels.append(self.l3)

            self.unit3 = tk.Label(self.diode_banner_3, 
                width=self.label_width, 
                height=self.h_banner,
                fg=space_blue,
                bg=light_gray, 
                font=normal,
                text=self.voltagetext)
            self.unit_labels.append(self.unit3)

            self.output3 = tk.Label(self.diode_banner_3, 
                width=self.text_width-2, 
                height=1, 
                bg=white_ish, 
                fg=red, 
                font=outputfont,
                relief='flat',
                justify='center',
                text='0.0')
            self.output_labels.append(self.output3)
            
            self.wave_text3 = tk.Button(self.diode_banner_3, 
                width=self.label_width+6, 
                height=1,
                fg=teal,
                bg=light_gray, 
                font=outputminifont,
                text=self.wavelength_text3,
                relief='flat',
                command=lambda: self.set_wavelength(3))
            self.wavelength_buttons.append(self.wave_text3)

            self.amp_num3 = tk.Label(self.diode_banner_3, 
                width=self.label_width, 
                height=self.h_banner,
                fg=space_blue,
                bg=light_gray, 
                font=ampfont,
                text='0x00')
            self.amp_nums.append(self.amp_num3)

            self.amp_msg3 = tk.Label(self.diode_banner_3,
                width=self.label_width+10, 
                height=self.h_banner,
                bg=light_gray,
                font=ampfont,
                fg=orange,
                justify='center',
                text='')
            self.amp_labels.append(self.amp_msg3)

            self.ampl3 = tk.Button(self.diode_banner_3,
                width=self.text_width-2, 
                height=1, 
                bg=light_gray, 
                fg=teal, 
                font=outputminifont,
                relief='flat',
                border=0,
                text=self.amp_level3.get(),
                command=lambda: self.set_range_to(self.active_diodes[0]))
            self.amp_buttons.append(self.ampl3)

            self.factor_button3 = tk.Button(self.diode_banner_3, 
                width=self.label_width+6, 
                height=1,
                fg=teal,
                bg=light_gray, 
                font=outputminifont,
                text=self.multi_text3.get(),
                relief='flat',
                command=lambda: self.multiply_value_page(3))
            self.factor_buttons.append(self.factor_button3)
            
            self.l3.place(relx=0.5, y=self.labely, anchor='center')
            self.unit3.place(relx=0.5, rely=0.23, anchor='center')
            self.output3.place(relx=0.5, rely=0.38, anchor='center')
            self.amp_msg3.place(relx=0.5, rely=0.51, anchor='center')
            self.factor_button3.place(relx=0.5, rely=0.6, anchor='center')
            self.wave_text3.place(relx=0.5, rely=0.7, anchor='center')
            self.ampl3.place(relx=0.5, rely=0.8, anchor='center')
            self.amp_num3.place(relx=0.5, rely=0.90, anchor='center')
            self.diode_banner_3.place(relx=4*frame_dist + 3*frame_width, 
                y=10, 
                relwidth=frame_width,
                relheight=0.95)  

###### 
######
######
###### MAIN WINDOW INITIALIZATION

    def __init__(self):
        tk.Tk.__init__(self)  # self = root window

        self.set_default_values()

        #GUI
        self.title('PowerMeter')
        self.attributes("-fullscreen", True)  # app window starts in borderless fullscreen mode
        self.bind("<F11>", lambda event: self.attributes("-fullscreen", not self.attributes("-fullscreen")))
        self.bind("<Escape>", lambda event: self.attributes("-fullscreen", False))  # keyboard key bindings for exiting fullscreen mode
        self.update_idletasks() 
        self.configure(bg=space_blue)
        self.config(cursor="none")

        self.d0.choose_source(self.source)
        self.create_widgets()  # creates frames with all widgets in them

        self.T = updateTimer(self.delay_time, self.update_widgets)  # calls a timer to update values on the GUI
        self.T.start()

###### 
######
######
###### TIMER FOR RECURRING EVENTS

class updateTimer():
    """Creates a new Thread for timing operation. 

    t = time in [s] - defines refresh rate
    hFunction = function it calls repeatedly every t [s]

    start() -> starts new thread and timer
    cancel() -> stops a running thread and timer
    """

    def __init__(self, t, hFunction):
        self.t=t
        self.hFunction = hFunction
        self.thread = Timer(self.t, self.handle_function)

    def handle_function(self):
        self.hFunction()
        self.thread = Timer(self.t, self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()

###### 
######
######
###### START OF THE APPLICATION

if __name__ == '__main__':
    app = powermeter_app()
    app.mainloop()
# END
