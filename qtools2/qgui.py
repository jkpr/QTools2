#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License (MIT)
#
# Copyright (c) 2015 PMA2020
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Fire up the GUI for XLSForm conversion

Under the hood, ``convert`` does the dirty work. The code here presents the
knobs and whistles for setting options and choosing files.

Currently, the code prints to console and the only graphical part is the
file picker.

Created: 11 May 2016
Last edited: 8 November 2016
"""

from qgui_config import config
from Tkinter import Frame, Tk, Label, Button, W, BOTTOM, SUNKEN, X, Text, DISABLED, WORD, END, NORMAL, Menu,\
    Checkbutton, BooleanVar
# from Tkinter import IntVar
import tkFileDialog


class PmaConvert:
    def __init__(self, root, config):
        # Root Definition
        root.geometry('700x700')
        root.title('PMA Convert')

        # Configuration and Variables
        self.module_status = self.get_module_status()
        self.file_selection = ''
        self.is_converting= False
        self.options = config['option_definitions']
        gui_config = config['gui_config']

        # UI
        ## Frames
        self.main_frame = Frame(root)
        self.position_main_frame(gui_config['screen_orientation'])

        ## Components
        self.log = Text(self.main_frame, bd=1, relief=SUNKEN, width=80, height=30, state=DISABLED, spacing3=1,
                        wrap=WORD)

        self.choose_files_label = Label(self.main_frame, text='1. Choose XLSForm (.xls or .xlsx) file(s) for conversion.')
        # TODO: Get spacing to work.
        # self.choose_files_label.grid(row=3, column=3, padx=(50, 50))
        # self.choose_files_label.grid(row=3, column=3, pady=(50, 50))
        self.choose_files_label.pack()
        self.choose_files_button = Button(self.main_frame, text='Choose file...', fg='black', command=self.on_open)
        self.choose_files_button.pack()

        self.output_location_label = Label(self.main_frame, text='Choose location for output file(s).')
        self.output_location_button = Button(self.main_frame, text='Choose location...', fg='black')
        if gui_config['output_location_on'] == True:
            self.output_location_label.pack()
            self.output_location_button.pack()

        self.choose_options_label = Label(self.main_frame, text='Choose conversion options.')
        self.choose_options_label.pack()

        ### Create Options Checkboxes
        # Task: Dynamically generate: http://stackoverflow.com/questions/553784/can-you-use-a-string-to-instantiate-a-class-in-python
        self.preexisting_option_value = BooleanVar()
        self.preexisting_option = Checkbutton(self.main_frame, text=self.options['preexisting']['label'], variable=self.preexisting_option_value)
        self.preexisting_option.pack()
        self.regular_option_value = BooleanVar()
        self.regular_option = Checkbutton(self.main_frame, text=self.options['regular']['label'], variable=self.regular_option_value)
        self.regular_option.pack()
        self.novalidate_option_value = BooleanVar()
        self.novalidate_option = Checkbutton(self.main_frame, text=self.options['novalidate']['label'], variable=self.novalidate_option_value)
        self.novalidate_option.pack()
        self.ignore_version_option_value = BooleanVar()
        self.ignore_version_option = Checkbutton(self.main_frame, text=self.options['ignore_version']['label'], variable=self.ignore_version_option_value)
        self.ignore_version_option.pack()
        self.linking_warn_option_value = BooleanVar()
        self.linking_warn_option = Checkbutton(self.main_frame, text=self.options['linking_warn']['label'], variable=self.linking_warn_option_value)
        self.linking_warn_option.pack()
        self.debug_option_value = BooleanVar()
        self.debug_option = Checkbutton(self.main_frame, text=self.options['debug']['label'], variable=self.debug_option_value)
        self.debug_option.pack()
        self.extras_option_value = BooleanVar()
        self.extras_option = Checkbutton(self.main_frame, text=self.options['extras']['label'], variable=self.extras_option_value)
        self.extras_option.pack()

        self.convert_label = Label(self.main_frame, text='2. Run conversion.')
        self.convert_label.pack()

        # Task: Add xscrollcommand and yscrollcommand.
        self.convert_button = Button(self.main_frame, text='Convert', fg='black', command=self.convert)
        self.convert_button.pack()
        self.log.pack(fill=X, expand=1)
        self.log_text('PMA Convert allows you to convert .xls or .xlsx form definition files to files which are '
                      'compatible with ODK Collect.\n\nIf you need to copy and paste from this log, highlight the text '
                      'and press CTRL+C to copy. Then press CTRL+V to paste.\n\n'
                      '===============================================================================\n\n'
                      'Awaiting file selection.')

        # Task: Fix menus. They're not working.
        self.context_menu = Menu(self.main_frame, tearoff=0)
        self.context_menu.add_command(label="Convert", command=self.convert)
        self.main_frame.bind("<Button-3>", self.popup)

        # - Note: Strangely this stopped anchoring to bottom suddenly, for some reason. So it is temporarily disabled.
        self.status_bar = Label(self.main_frame, text='Awaiting file selection.', bd=1, relief=SUNKEN, anchor=W)
        if gui_config['status_bar_on'] == True:
            self.status_bar.pack(side=BOTTOM, fill=X)

        # Run
        root.mainloop()

    # Functions
    def popup(self, event):
        self.context_menu.post(event.x_root, event.y_root)
        # display the popup menu
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.context_menu.grab_release()

    def position_main_frame(self, orientation):
        if orientation == 'center':
            x, y, a = .5, .5, 'c'
            return self.main_frame.place(relx=x, rely=y, anchor=a)
        elif orientation == 'top':
            return self.main_frame.pack()
        else:
            return self.main_frame.pack()

    def on_open(self):
        if self.is_converting == False:
            file_types = [('XLS Files', '*.xls'), ('XLSX Files', '*.xlsx'), ('All files', '*')]
            self.file_selection = tkFileDialog.askopenfilename(filetypes=file_types, title='Open one or more files.',
                                                        message='Open one or more files', multiple=1)
            if self.file_selection != '':
                self.set_status('Click on Convert to convert files.')
                log_output = 'Ready for conversion: \n'
                for file in self.file_selection:
                    log_output += '* ' + str(file) + '\n'
                log_output = log_output[:-1] # Removes the last '\n'.
                self.log.configure(self.log_text(log_output))
                print(log_output)

    def set_status(self, newStatus):
        self.status_bar.configure(text=newStatus)

    def get_module_status(self):
        # TODO: Get this to work correctly.
        module_status = 'submodule'
        return module_status

    def log_text(self, newText):
        # self.log.configure(state=self.log['text'] + '\n' + newText)
        self.log.configure(state=NORMAL)
        self.log.insert(END, str(newText) + '\n\n')
        self.log.configure(state=DISABLED)
        self.log.bind("<1>", lambda event: self.log.focus_set())

    def convert(self):
        if self.file_selection != '' and self.is_converting == False:
            self.log_text('Converting...')
            self.is_converting = True
            self.convert()
        elif self.file_selection != '' and self.is_converting == True:
            f = self.file_selection

            checkbox_values = {
                'preexisting': self.preexisting_option_value.get(),
                'regular': self.regular_option_value.get(),
                'novalidate': self.novalidate_option_value.get(),
                'ignore_version': self.ignore_version_option_value.get(),
                'linking_warn': self.linking_warn_option_value.get(),
                'debug': self.debug_option_value.get(),
                'extras': self.extras_option_value.get()
            }
            arguments = []
            for key in checkbox_values:
                if checkbox_values[key] == True:
                    arguments.append(self.options[key]['short-flag'])
            # Testing
            # for key in checkbox_values:
            #     self.log_text(str(key) + str(checkbox_values[key]))
            # self.log_text(str(arguments))

            if self.module_status == 'submodule':
                self.convert_using_subprocess(f, arguments)
            else:
                try:
                    self.convert_using_multithreading(f, arguments)
                except:
                    self.convert_using_singlethreading(f, arguments)

    def convert_using_singlethreading(self, files_selected, arguments):
        pass

    def convert_using_multithreading(self, files_selected, arguments):
        pass

    def convert_using_subprocess(self, files_selected, arguments):
        from subprocess import Popen, PIPE

        versions = ['python', 'python2', 'python27']
        for version in versions:
            command_args = [version, '-m', 'qtools2.convert']
            for arg in arguments:
                command_args.append(arg)
            for file in files_selected:
                command_args.append(str(file))
                
            p = Popen(command_args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
            output, err = p.communicate(b"input data that is passed to subprocess' stdin")
            rc = p.returncode
            # Task: Improve logging.
            # Task: If return code is success, break the loop.
            self.log_text(str(rc))
            self.log_text(str(err))
            self.log_text(str(output))

    def run_qtools2_conversion(self, python_version, files):
        # TODO: Restore this when ready. But also need to break up this tuple first.
        # command = python_version + ' -m qtools2.convert -v2 ' + str(files)
        f = ''
        for file in files:
            f += ' ' + str(file)
        command = python_version + ' -m qtools2.convert -v2' + f
        # command = python_version + ' -m qtools2.convert -v2 ' + '/Users/joeflack4/Desktop/KER5-Female-Questionnaire-v12-jef.xls /Users/joeflack4/Desktop/KER5-Household-Questionnaire-v12-jef.xls'
        return command


def run_conversion():
    PmaConvert(Tk(), config)


if __name__ == '__main__':
    run_conversion()


# Tasks
# - High Priority
# TODO: Change API to call qtools directly. Set conditional to run subprocess if needed.
# Log
# TODO: Get feedback in log when conversion is sucessful. This may require some work with qtools2, or otherwise find a way to get info from the console.
# TODO: Log needs to have fixed width.
# UI
# TODO: Fix positioning issues (fill, anchor, expand, etc), or use grid instead.
# Window
# TODO: Need to reset window as well after log gives its feedback.
# - Medium Priority
# Options
# TODO: Might want to add some conversion options.
# Dependency Hell
# TODO: Alert on load if dependencies do not exist (try/except, perhaps)
# TODO: Make installers.
# TODO: Make standalone .app and .exe files.
# - Low Prioirity
# Misc
# TODO: Position in middle of screen on load.
# TODO: Have in focus in front on load.
# TODO: Add a cancel button that dynamically appears if conversion is in-process.
# TODO: Add an error alert / message when buttons are clicked, but have been disabled.
# TODO: Fix graphical issue with a minus ('-') showing for a moment when clicking a checkbox.
# Subprocess
# TODO: May be able to try multiple versions of python by checking the return code. And only return log text if conversion was successful.

# Optional Future Development
# - Change the way PMA Convert is used as a submodule. http://stackoverflow.com/questions/4161022/git-how-to-track-untracked-content
