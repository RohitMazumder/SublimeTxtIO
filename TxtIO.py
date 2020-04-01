import os
import subprocess
import threading

import sublime
import sublime_plugin


class TxtIoCommand(sublime_plugin.TextCommand):

    encoding = 'utf-8'
    killed = False
    proc = None
    panel = None
    panel_lock = threading.Lock()

    def run(self, edit):

        self.window = self.view.window()
        vars = self.window.extract_variables()

        assert vars['platform'] == 'Windows', sublime.error_message(
            vars['platform'] + ' not supported')

        try:
            file_extension = vars['file_extension']
            file_name = vars['file_base_name']
            file = vars['file']
            working_dir = vars['file_path']
        except KeyError:
            sublime.error_message('Please save your file before continuing ')
            raise

        classpath = working_dir
        input_file = open(working_dir + '\\input.txt', 'r')
        output_file = open(working_dir + '\\output.txt', 'w')

        try:
            settings = sublime.load_settings("TxtIO.sublime-build")
            command = settings.get(file_extension)['cmd']
        except TypeError:
            sublime.error_message(
                file_extension + ' is not currently supported')
            raise

        cmd = command.replace('${file}', file)\
            .replace('${classpath}', classpath)\
            .replace('${file_name}', file_name)

        # A lock is used to ensure only one thread is
        # touching the output panel at a time
        with self.panel_lock:
            # Creating the panel implicitly clears any previous contents
            self.panel = self.window.create_output_panel('exec')

            # Enable result navigation. The result_file_regex does
            # the primary matching, but result_line_regex is used
            # when build output includes some entries that only
            # contain line/column info beneath a previous line
            # listing the file info. The result_base_dir sets the
            # path to resolve relative file names against.
            settings = self.panel.settings()
            settings.set(
                'result_file_regex',
                r'^File "([^"]+)" line (\d+) col (\d+)'
            )
            settings.set(
                'result_line_regex',
                r'^\s+line (\d+) col (\d+)'
            )
            settings.set('result_base_dir', working_dir)

            self.window.run_command('show_panel', {'panel': 'output.exec'})

        if self.proc is not None:
            self.proc.terminate()
            self.proc = None

        self.proc = subprocess.Popen(cmd, stdin=input_file, stdout=output_file,
                                     stderr=subprocess.PIPE, shell=True)

        threading.Thread(
            target=self.read_handle,
            args=(self.proc.stderr,)
        ).start()

    def read_handle(self, handle):

        chunk_size = 2 ** 13
        out = b''
        while True:
            try:
                data = os.read(handle.fileno(), chunk_size)
                # If exactly the requested number of bytes was
                # read, there may be more data, and the current
                # data may contain part of a multibyte char
                out += data
                if len(data) == chunk_size:
                    continue
                if data == b'' and out == b'':
                    raise IOError('EOF')
                # We pass out to a function to ensure the
                # timeout gets the value of out right now,
                # rather than a future (mutated) version
                self.queue_write(out.decode(self.encoding))
                if data == b'':
                    raise IOError('EOF')
                out = b''
            except (UnicodeDecodeError) as e:
                msg = 'Error decoding output using %s - %s'
                self.queue_write(msg % (self.encoding, str(e)))
                break
            except (IOError):
                if self.killed:
                    msg = 'Cancelled'
                else:
                    msg = 'Finished'
                self.queue_write('\n[%s]' % msg)
                break

    def queue_write(self, text):
        sublime.set_timeout(lambda: self.do_write(text), 1)

    def do_write(self, text):
        with self.panel_lock:
            self.panel.run_command('append', {'characters': text})
