from config import config
from Tkinter import Frame, Tk, Label, Button, W, BOTTOM, SUNKEN, X
import tkFileDialog


class PmaConvert:
    def __init__(self, root, config):
        # Status and Configuration
        self.module_status = self.get_module_status()

        # Root Definition
        root.geometry('700x250')
        root.title('PMA Convert')

        # UI
        ## Frames
        self.centerFrame = Frame(root)
        self.centerFrame.place(relx=.5, rely=.5, anchor='c')

        ## Components
        self.q1_label = Label(self.centerFrame, text='1. Choose XLSForm (.xls or .xlsx) file(s) for conversion.')
        self.q1_label.pack()
        self.q1_button = Button(self.centerFrame, text='Choose file...', fg='black', command=self.on_open)
        self.q1_button.pack()

        # self.q2_label = Label(topFrame, text='2. Choose location for output file(s).').pack()
        # self.q4_button = Button(topFrame, text='Choose location...', fg='black').pack()

        # self.q3_label = Label(topFrame, text='3. Choose conversion options.').pack()

        self.q4_label = Label(self.centerFrame, text='2. Run conversion.')
        self.q4_label.pack()
        self.log = Label(self.centerFrame, text='', bd=1, relief=SUNKEN, anchor=W)
        self.file_selection = ''
        self.is_converting= False
        self.q4_button = Button(self.centerFrame, text='Convert', fg='black', command=self.convert)
        self.q4_button.pack()
        self.log.pack(fill=X, expand=1)


        # - Note: Strangely this stopped anchoring to bottom suddenly, for some reason. So it is temporarily disabled.
        self.status_bar = Label(self.centerFrame, text='Awaiting file selection.', bd=1, relief=SUNKEN, anchor=W)
        if config['status_bar_on'] == True:
            self.status_bar.pack(side=BOTTOM, fill=X)

        # Run
        root.mainloop()

    # Functions
    def on_open(self):
        if self.is_converting == False:
            file_types = [('XLS Files', '*.xls'), ('XLSX Files', '*.xlsx'), ('All files', '*')]
            self.file_selection = tkFileDialog.askopenfilename(filetypes=file_types, title='Open one or more files.',
                                                        message='Open one or more files', multiple=1)
            if self.file_selection != '':
                self.set_status('Click on Convert to convert files.')
                log_output = 'File(s) ready for conversion: ' + str(self.file_selection)
                self.log.configure(text=log_output)
                print(log_output)

    def set_status(self, newStatus):
        self.status_bar.configure(text=newStatus)

    def get_module_status(self):
        # TODO: Get this to work correctly.
        module_status = 'submodule'
        return module_status

    def log_text(self, newText):
        self.log.configure(text=self.log['text'] + '\n' + newText)

    def convert(self):
        if self.file_selection != '' and self.is_converting == False:
            self.is_converting = True
            self.log_text('Converting...')

            f = self.file_selection
            if self.module_status == 'submodule':
                self.convert_using_subprocess(f)
            else:
                self.convert_using_singlethreading(f)

    def convert_using_singlethreading(self, files_selected):
        pass

    def convert_using_multithreading(self, files_selected):
        # Task: Create a multi-threading conversion implementation.
        pass

    def convert_using_subprocess(self, files_selected):
        versions = ['python', 'python2', 'python27']

        from subprocess import Popen, PIPE

        for version in versions:
            command_args = [version, '-m', 'qtools2.convert', '-v2']
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
# Subprocess
# TODO: May be able to try multiple versions of python by checking the return code. And only return log text if conversion was successful.

# Optional Future Development
# - Change the way PMA Convert is used as a submodule. http://stackoverflow.com/questions/4161022/git-how-to-track-untracked-content
