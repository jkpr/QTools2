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

Created: 11 May 2016
Last edited: 10 November 2016
E-mail: jflack@jhu.edu
"""

import sys
import traceback
import StringIO
from Tkinter import Frame, Tk, Label, Button, W, BOTTOM, SUNKEN, X, Text, \
    DISABLED, WORD, END, NORMAL, Menu, Checkbutton, BooleanVar
import tkFileDialog

from errors import ConvertError
from qgui_config import config
from convert import xlsform_convert
from constants import SUFFIX, PREEXISTING, PMA, CHECK_VERSIONING, \
    STRICT_LINKING, VALIDATE, EXTRAS, DEBUG


class PmaConvert:
    def __init__(self, config):
        root = Tk()

        # Root Definition
        root.geometry('1100x700')
        root.title('PMA Convert')

        # Configuration and Variables
        self.file_selection = ''
        self.is_converting = False
        self.options = config['option_definitions']
        gui_config = config['gui_config']

        # UI
        ## Frames
        self.main_frame = Frame(root)
        self.position_main_frame(gui_config['screen_orientation'])

        ## Components
        self.log = Text(self.main_frame, bd=1, relief=SUNKEN, width=140,
                        height=23, state=DISABLED, spacing3=1, wrap=WORD)

        choose_text = ('1. Choose XLSForm (.xls or .xlsx) file(s) for '
                       'conversion.')
        self.choose_files_label = Label(self.main_frame, text=choose_text)
        # TODO: Get spacing to work.
        # self.choose_files_label.grid(row=3, column=3, padx=(50, 50))
        # self.choose_files_label.grid(row=3, column=3, pady=(50, 50))
        self.choose_files_label.pack()
        self.choose_files_button = Button(self.main_frame,
                                          text='Choose file...', fg='black',
                                          command=self.on_open)
        self.choose_files_button.pack()

        out_text = 'Choose location for output file(s).'
        self.output_location_label = Label(self.main_frame, text=out_text)
        self.output_location_button = Button(self.main_frame,
                                             text='Choose location...',
                                             fg='black')
        if gui_config['output_location_on'] is True:
            self.output_location_label.pack()
            self.output_location_button.pack()

        self.choose_options_label = Label(self.main_frame,
                                          text='2. Choose conversion options.')
        self.choose_options_label.pack()

        ### Create Options Checkboxes
        # Task: Dynamically generate: http://stackoverflow.com/questions/...
        # ...553784/can-you-use-a-string-to-instantiate-a-class-in-python
        self.preexisting = BooleanVar()
        pre_text = self.options['preexisting']['label']
        self.preexisting_opt = Checkbutton(self.main_frame, text=pre_text,
                                           variable=self.preexisting)
        self.preexisting_opt.pack()
        self.regular = BooleanVar()
        reg_text = self.options['regular']['label']
        self.regular_opt = Checkbutton(self.main_frame, text=reg_text,
                                       variable=self.regular)
        self.regular_opt.pack()
        self.novalidate = BooleanVar()
        noval_text = self.options['novalidate']['label']
        self.novalidate_opt = Checkbutton(self.main_frame, text=noval_text,
                                          variable=self.novalidate)
        self.novalidate_opt.pack()
        self.ignore_version = BooleanVar()
        ig_text = self.options['ignore_version']['label']
        self.ignore_version_opt = Checkbutton(self.main_frame, text=ig_text,
                                              variable=self.ignore_version)
        self.ignore_version_opt.pack()
        self.linking_warn = BooleanVar()
        link_text = self.options['linking_warn']['label']
        self.linking_warn_option = Checkbutton(self.main_frame, text=link_text,
                                               variable=self.linking_warn)
        self.linking_warn_option.pack()
        self.debug = BooleanVar()
        debug_text = self.options['debug']['label']
        self.debug_option = Checkbutton(self.main_frame, text=debug_text,
                                        variable=self.debug)
        self.debug_option.pack()
        self.extras = BooleanVar()
        extras_text = self.options['extras']['label']
        self.extras_option = Checkbutton(self.main_frame, text=extras_text,
                                         variable=self.extras)
        self.extras_option.pack()

        self.convert_label = Label(self.main_frame, text='3. Run conversion.')
        self.convert_label.pack()

        # Task: Add xscrollcommand and yscrollcommand.
        self.convert_button = Button(self.main_frame, text='Convert',
                                     fg='black', command=self.convert)
        self.convert_button.pack()
        self.log.pack(fill=X, expand=1)
        self.log_text('PMA Convert allows you to convert .xls or .xlsx form '
                      'definition files to files which are compatible with ODK '
                      'Collect.\n\nIf you need to copy and paste from this '
                      'log, highlight the text and press CTRL+C to copy. Then '
                      'press CTRL+V to paste.\n\n'
                      '====================================================\n\n'
                      'Awaiting file selection.')

        # Task: Fix menus. They're not working.
        self.context_menu = Menu(self.main_frame, tearoff=0)
        self.context_menu.add_command(label="Convert", command=self.convert)
        self.main_frame.bind("<Button-3>", self.popup)

        # - Note: Strangely this stopped anchoring to bottom suddenly, for some
        # reason. So it is temporarily disabled.
        self.status_bar = Label(self.main_frame,
                                text='Awaiting file selection.',
                                bd=1, relief=SUNKEN, anchor=W)
        if gui_config['status_bar_on'] is True:
            self.status_bar.pack(side=BOTTOM, fill=X)

        # Run
        root.mainloop()

    # Functions
    def popup(self, event):
        # Note: Currently doesn't work.
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
        file_types = [
            ('XLS Files', '*.xls'),
            ('XLSX Files', '*.xlsx'),
            ('All files', '*')
        ]
        self.file_selection = tkFileDialog.askopenfilename(
            filetypes=file_types, title='Open one or more files.',
            message='Open one or more files', multiple=1
        )
        if self.file_selection != '':
            self.set_status('Click on Convert to convert files.')
            log_output = 'Ready for conversion: \n'
            for file in self.file_selection:
                log_output += '* ' + str(file) + '\n'
            log_output = log_output[:-1] # Removes the last '\n'.
            self.log.configure(self.log_text(log_output))

    def set_status(self, new_status):
        self.status_bar.configure(text=new_status)

    def log_text(self, new_text):
        self.log.configure(state=NORMAL)
        self.log.insert(END, str(new_text) + '\n\n')
        self.log.configure(state=DISABLED)
        self.log.bind("<1>", lambda event: self.log.focus_set())

    def convert(self):
        if self.file_selection != '':
            f = self.file_selection

            kwargs = {
                SUFFIX: u'',
                PREEXISTING: self.preexisting.get(),
                PMA: not self.regular.get(),
                CHECK_VERSIONING: not self.ignore_version.get(),
                STRICT_LINKING: not self.linking_warn.get(),
                VALIDATE: not self.novalidate.get(),
                EXTRAS: self.extras.get(),
                DEBUG: self.debug.get()
            }

            buffer = StringIO.StringIO()
            if not kwargs[DEBUG]:
                sys.stdout = buffer
                sys.stderr = buffer
            else:
                self.log_text('--> DEBUG MODE: check console output')

            try:
                xlsform_convert(f, **kwargs)
            except ConvertError as e:
                print unicode(e)
            except OSError as e:
                # Should catch WindowsError, impossible to test on Mac
                traceback.print_exc()
                print e

            if not kwargs[DEBUG]:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

            self.log_text(buffer.getvalue())


def run_conversion():
    PmaConvert(config)


if __name__ == '__main__':
    run_conversion()


# Tasks
# UI
# TODO: Fix positioning issues (fill, anchor, expand, etc), or use grid instead.
# Window
# TODO: Need to reset window as well after log gives its feedback.
# - Medium Priority
# Misc
# TODO: Position window in middle of screen on load.
# TODO: Have in focus in front on load.
# TODO: Add a cancel button that dynamically appears if conversion is in-process.
# TODO: Add an error alert / message when buttons are clicked, but have been disabled.
# TODO: Fix graphical issue with a minus ('-') showing for a moment when clicking a checkbox.
# - Low Prioirity
# Dependency Management for Standalone
# TODO: Alert on load if dependencies do not exist (try/except, perhaps)
# TODO: Make installers.
# TODO: Make standalone .app and .exe files.
# Subprocess
# TODO: May be able to try multiple versions of python by checking the return code. And only return log text if conversion was successful.

# Optional Future Development
# - Change the way PMA Convert is used as a submodule. http://stackoverflow.com/questions/4161022/git-how-to-track-untracked-content
