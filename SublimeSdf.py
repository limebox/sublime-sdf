import sys, time, sublime, sublime_plugin, re
from subprocess import Popen, PIPE, STDOUT
from threading import Thread

class SdfExecRun(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    self.args = args

    if SdfExec.get_setting('debug', self.args):
      print("\n\n>>>>>>>>>>>>>>>>>> Start Shell Exec Debug:")

    if not args.get("command"):
      args["command"] = ""

    SdfExec.run_shell_command(self.args, self.view, args.get("command"))

class SdfExecOpen(sublime_plugin.TextCommand):
  def run(self, edit, **args):
    self.args = args

    if SdfExec.get_setting('debug', self.args):
      print("\n\n>>>>>>>>>>>>>>>>>> Start Shell Exec Debug:")

    cli_commands = [
      [
        "Add Dependencies to Manifest",
        "Adds missing dependencies to the manifest file.",
        "adddependencies"
      ],
      [
        "Deploy to Account",
        "Deploys the folder or zip file that contains the SuiteCloud project.",
        "deploy"
      ],
      [
        "Import Bundle",
        "Imports a customization bundle from your NetSuite account and converts it to an account customization project.",
        "importbundle"
      ],
      [
        "Import Files",
        "Imports files from your NetSuite account to the account customization project.",
        "importfiles"
      ],
      [
        "Import Objects",
        "Imports custom objects from your NetSuite account to the SuiteCloud project.",
        "importobjects"
      ],
      [
        "List Bundles",
        "Lists the customization bundles that were created in your NetSuite account.",
        "listbundles"
      ],
      [
        "List Files",
        "Lists the files in the File Cabinet of your NetSuite account.",
        "listfiles"
      ],
      [
        "List Missing Dependencies",
        "Lists the missing dependencies in the SuiteCloud project.",
        "listmissingdependencies"
      ],
      [
        "List Objects",
        "Lists the custom objects in your NetSuite account.",
        "listobjects"
      ],
      [
        "Preview",
        "Previews the deployment steps of a folder or zip file that contains the SuiteCloud project.",
        "preview"
      ],
      [
        "Project",
        "Sets the default project folder or zip file for CLI.",
        "project"
      ],
      [
        "Update",
        "Updates existing custom objects in the SuiteCloud project folder with the custom objects in your NetSuite account.",
        "update"
      ],
      [
        "Update Custom Record With Instances",
        "Updates the custom record object and its instances in the SuiteCloud project.",
        "updatecustomrecordwithinstances"
      ],
      [
        "Validate Project",
        "Validates the folder or zip file that contains the SuiteCloud project.",
        "validate"
      ]
    ]

    def runSdfExec(user_command):
      print(cli_commands[user_command][2])
#      SdfExec.run_shell_command(self.args, self.view, cli_commands[user_command])

    sublime.active_window().show_quick_panel(cli_commands, runSdfExec)

#    if args.get("command"):
#      command = SdfExec.command_variables(args, self.view, args["command"], False)

#    def checkSdfCommand(currentCommand):
#      SdfExec.check_sdf_command(self.args, self.view, edit, currentCommand)

#    sublime.active_window().show_input_panel(SdfExec.get_setting('title', self.args), command, runSdfExec, checkSdfCommand, None)

class SdfExecViewInsertCommand(sublime_plugin.TextCommand):
  def run(self, edit, pos, text):
    self.view.insert(edit, pos, text)

class SdfExec:
  def __init__(self):
    self.output_file = None
    self.panel_output = None

  def command_variables(args, view, command, format=True):
    if format and args.get("format"):
      command = args["format"].replace('${input}', command)

    for region in view.sel():
      (row,col) = view.rowcol(view.sel()[0].begin())

      command = command.replace('${row}', str(row+1))
      command = command.replace('${region}', view.substr(region))
      break

    # packages, platform, file, file_path, file_name, file_base_name,
    # file_extension, folder, project, project_path, project_name,
    # project_base_name, project_extension.
    command = sublime.expand_variables(command, sublime.active_window().extract_variables())

    return command

  def run_shell_command(args, view, command):
    command = SdfExec.command_variables(args, view, command)
    if 'folder' in sublime.active_window().extract_variables():
      if sublime.platform() == 'windows':
        pure_command = command.replace(sublime.active_window().extract_variables()['folder'] + '\\', '')
      else:
        pure_command = command.replace(sublime.active_window().extract_variables()['folder'] + '/', '')
    else:
      pure_command = command

    if SdfExec.get_setting('context', args) == 'project_folder':
      if 'folder' in sublime.active_window().extract_variables():
        command = "cd '" + sublime.active_window().extract_variables()['folder'] + "' && " + command
    if SdfExec.get_setting('context', args) == 'file_folder':
      if 'file_path' in sublime.active_window().extract_variables():
        command = "cd '" + sublime.active_window().extract_variables()['file_path'] + "' && " + command

    if SdfExec.get_setting('debug', args):
        print('new Thread')

    t = Thread(target=SdfExec.execute_shell_command, args=(command, pure_command, args))
    t.start()

  def check_sdf_command( args, view, edit, currentCommand ):
    allcontent = sublime.Region(0, view.size())
    view.replace(edit, allcontent, "adddependencies")

  def new_output_file(args, pure_command):
    if SdfExec.get_setting('debug', args):
      print('open new empty file: ' + pure_command)
    output_file = sublime.active_window().new_file()
    output_file.set_name(pure_command[0:60])
    output_file.set_scratch(True)

    if SdfExec.get_setting('output_syntax', args):
      if SdfExec.get_setting('debug', args):
        print('set output syntax: ' + SdfExec.get_setting('output_syntax', args))

      if sublime.find_resources(SdfExec.get_setting('output_syntax', args) + '.tmLanguage'):
        output_file.set_syntax_file(sublime.find_resources(SdfExec.get_setting('output_syntax', args) + '.tmLanguage')[0])

    if SdfExec.get_setting('output_word_wrap', args):
      output_file.settings().set('word_wrap', True)
    else:
      output_file.settings().set('word_wrap', False)

    return output_file

  def increment_output(self, value, args, pure_command):
    if SdfExec.get_setting('output', args) == "file":
      if not self.output_file:
        self.output_file = SdfExec.new_output_file(args, pure_command)

      self.output_file.run_command('sdf_exec_view_insert', {'pos': self.output_file.size(), 'text': value})
    elif SdfExec.get_setting('output', args) == "none":
      self.panel_output = False
    else:
      if not self.panel_output:
        self.panel_output = True
        sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": False})
      sys.stdout.write(value)

  def execute_shell_command(command, pure_command, args, return_error=True):
    code = command

    sdf_command_do_gui_instance = SdfExec()

    if SdfExec.get_setting('debug', args):
      sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": False})
      print("run command: " + command)

    SdfExec.increment_output(sdf_command_do_gui_instance, "> " + pure_command + "\n\n", args, pure_command)

    if return_error:
      stderr = STDOUT
    else:
      stderr = None

    if SdfExec.get_setting('debug', args):
      print('create Popen: executable=' + SdfExec.get_setting('cli_executable', args))
    console_command = Popen(code, executable=SdfExec.get_setting('cli_executable', args), shell=True, stderr=stderr, stdout=PIPE)

    if SdfExec.get_setting('debug', args):
      print('waiting for stdout...')

    # TODO: This code is shameful, needs to be improved...
    initial_time = time.time()
    while True:
      diff_time = float(re.sub(r"e-*", '', str(time.time()-initial_time)))
      if diff_time > 0.01:
        char = str(console_command.stdout.read(1)) # last was slow
        initial_time = time.time()
      else:
        char = str(console_command.stdout.read(10)) # last was fast
        initial_time = time.time()

      if not char == "b''":
        if re.search(r"^b('|\")", char):
          char = re.sub(r"^b('|\")|('|\")$", '', char)

        char = bytes(char, "utf-8").decode("unicode_escape")
        SdfExec.increment_output(sdf_command_do_gui_instance, char, args, pure_command)

      if console_command.poll() != None:
        if SdfExec.get_setting('debug', args):
          print('stdout complete!')

        output = str(console_command.stdout.read())
        output = re.sub(r"^b('|\")|('|\")$", '', output)
        output = bytes(output, "utf-8").decode("unicode_escape")
        output = re.sub(r"\n$", '', output)

        if SdfExec.get_setting('debug', args):
          print('send result to output file.')
        SdfExec.increment_output(sdf_command_do_gui_instance, str(output) + "\n", args, pure_command)
        break

    if SdfExec.get_setting('debug', args):
      print(">>>>>>>>>>>>>>>>>> Shell Exec Debug Finished!")

    sublime.status_message('Shell Exec | Done! > ' + pure_command[0:60])

  def get_setting(config, args, force_default=False):
    if (not force_default) and args.get(config):
      return args[config]

    settings = sublime.load_settings('Preferences.sublime-settings')
    if settings.get('sdf_exec_' + config):
      return settings.get('sdf_exec_' + config)
    else:
      settings = sublime.load_settings('SublimeSdf.sublime-settings')
      return settings.get('sdf_exec_' + config)
