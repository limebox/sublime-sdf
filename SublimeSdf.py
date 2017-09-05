import sys, time, sublime, sublime_plugin, re, os, subprocess, time, signal, json, time
from subprocess import STDOUT
from threading import Thread

# For anyone examining my code, please forgive how unforgivably bad this is.
# I've never written in Python before, so this was also a crash course in Python
# If anyone wants to help contribute to make it better, be my guest

class SdfExecOpen(sublime_plugin.TextCommand):

	temp_password = ""

	def run(self, edit, **args):
		self.args = args

		def run_programm( user_password ):
			SdfExec.password = SdfExecOpen.temp_password
			SdfExecRun.run(self, edit, **args)

		def get_password( user_password ):
			if( len(user_password) != len(SdfExecOpen.temp_password) ):
				chg = user_password.replace("*", "")
				if  len(user_password) < len(SdfExecOpen.temp_password):
					SdfExecOpen.temp_password = SdfExecOpen.temp_password[:len(user_password)]
				else:
					SdfExecOpen.temp_password = SdfExecOpen.temp_password + chg
				stars = "*" * len(user_password)
				sublime.active_window().show_input_panel("NetSuite Password", stars, run_programm, get_password, None)

		if SdfExec.password == "":
			#sublime.active_window().show_input_panel("NetSuite Password", "", get_password, None, None)
			sublime.active_window().show_input_panel("NetSuite Password", "", None, get_password, None)
		else:
			SdfExecRun.run(self, edit, **args)


class SdfExecRun(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		if SdfExec.get_setting('debug', self.args):
			print("\n\n>>>>>>>>>>>>>>>>>> Start Shell Exec Debug:")

		settings_file = os.path.abspath(os.path.dirname(__file__)) + "/settings.json"

		with open( settings_file ) as json_data:
			d = json.load(json_data)

			import_object = d["import_object"]
			cli_arguments = d["cli_arguments"]
			custom_objects = d["custom_objects"]
			cli_commands = d["cli_commands"]

		def runSdfExec(user_command):
			selected_id = user_command
			object_type = 0
			files = []

			if os.name == 'nt':
				path_var = "\\"
			else:
				path_var = "/"

			def selectObject(user_command):
				if user_command == -1:
					return
				cli_arguments["listobjects"] = '-type "' + custom_objects[user_command][1] + '"'
				SdfExec.run_shell_command(self.args, self.view, cli_commands[selected_id], cli_arguments, custom_objects[user_command])

			def selectObjectToImport(user_command):
				if user_command == -1:
					return
				runSdfExec.object_type=user_command
				cli_arguments["listobjects"] = '-type "' + custom_objects[runSdfExec.object_type][1] + '"'
				cli_arguments["importobjects"] = '-destinationfolder "' + custom_objects[runSdfExec.object_type][2] + '" [SCRIPTID] -type "' + custom_objects[runSdfExec.object_type][1] + '"'
				SdfExec.run_shell_command(self.args, self.view, cli_commands[selected_id], cli_arguments, custom_objects[runSdfExec.object_type])

			def selectObjectToUpdate( user_command ):
				if user_command == -1:
					return
				file_start = files[ user_command ].rfind(path_var) + 1
				update_object = files[ user_command ][file_start:-4]

				cli_arguments["update"] = '-scriptid "' + update_object + '"'
				SdfExec.run_shell_command(self.args, self.view, cli_commands[selected_id], cli_arguments, None)

			if cli_commands[selected_id][0] == "Clear Password":
				SdfExec.password = ""
			elif cli_commands[selected_id][2] == "listobjects":
				# In this instance, we need to ask the user another question about what type of object
				sublime.active_window().show_quick_panel(custom_objects, selectObject)
			elif cli_commands[selected_id][2] == "importobjects":
				# If someone wants to import an object, they need to pick an object type first
				sublime.active_window().show_quick_panel(custom_objects, selectObjectToImport)
			elif cli_commands[selected_id][2] == "update":

				current_file = sublime.active_window().active_view().file_name()
				parent_folder = current_file.rfind( path_var )
				current_file = current_file[0:parent_folder]
				objects_folder = ""
				while True:
					if os.path.isdir( current_file + path_var + "Objects" ):
						objects_folder=current_file + "/Objects"
						break
					else:
						parent_folder = current_file.rfind( path_var )
						current_file = current_file[0:parent_folder]

				for (root, dirnames, filenames) in os.walk(objects_folder):
					for name in filenames:
						if name.find(".xml") >= 0:
							files.append( path_var + "Objects" + root.replace( objects_folder, "" ) + path_var + name )

				sublime.active_window().show_quick_panel(files, selectObjectToUpdate)
			else:
				SdfExec.run_shell_command(self.args, self.view, cli_commands[selected_id], cli_arguments, None)

		sublime.active_window().show_quick_panel(cli_commands, runSdfExec)

class SdfExecViewInsertCommand(sublime_plugin.TextCommand):
	def run(self, edit, pos, text):
		self.view.insert(edit, pos, text)

class SdfExec:
	password = ""
	project_folder = ""
	loading_message = ""
	show_loader = False
	kill_loader = False

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

	def run_shell_command(args, view, command_options, cli_arguments, custom_object):

		command =	SdfExec.get_setting('cli_executable', args) + " " + SdfExec.command_variables(args, view, command_options[2])
		project_command = SdfExec.get_setting('cli_executable', args) + " project -p "
		if 'folder' in sublime.active_window().extract_variables():
			if sublime.platform() == 'windows':
				pure_command = SdfExec.command_variables(args, view, command_options[2]).replace(sublime.active_window().extract_variables()['folder'] + '\\', '')
			else:
				pure_command = SdfExec.command_variables(args, view, command_options[2]).replace(sublime.active_window().extract_variables()['folder'] + '/', '')
		else:
			pure_command = SdfExec.command_variables(args, view, command_options[2])

		if SdfExec.get_setting('context', args) == 'project_folder':
			if 'folder' in sublime.active_window().extract_variables():
				SdfExec.project_folder = sublime.active_window().extract_variables()['folder']
		else:
			if sublime.active_window().active_view().file_name():
				current_file = sublime.active_window().active_view().file_name()
				parent_location = current_file.find( SdfExec.get_setting('context', args) ) + len( SdfExec.get_setting('context', args) )
				SdfExec.project_folder = current_file[:parent_location]

		project_command = project_command + '"' + SdfExec.project_folder + '"'

		account_info = {}
		commands = {}

		if sublime.platform() == 'windows':
			command = command.replace('/', '\\')

		options=""
		sub_options=""
		if pure_command == "importfiles":
			options = cli_arguments[ "listfiles" ]
			sub_options = cli_arguments[ pure_command ]
		elif pure_command == "importobjects" and cli_arguments[ "listobjects" ] != "":
			# We're only looking here if the user did not supply a script id
			options = cli_arguments[ "listobjects" ]
			sub_options = cli_arguments[ pure_command ]
		else:
			options = cli_arguments[ pure_command ]

		sdfFile = SdfExec.project_folder + "/.sdf"
		if os.path.isfile( sdfFile ):
			for line in open( sdfFile ):
				data = line.split("=")
				account_info[ data[0] ] = data[1].rstrip('\n')

				if data[0] != "password":
					options = options + " -" + data[0] + ' "' + account_info[ data[0] ] + '"'
					sub_options = sub_options + " -" + data[0] + ' "' + account_info[ data[0] ] + '"'
		else:
			view = sublime.Window.new_file( sublime.active_window() )
			output = ["Either you are not in a file that exists in an SDF project or you have not created a file named .sdf","Make sure you are executing SDF from within a NetSuite project.","The following are the required lines in your .sdf file, this should be saved in the root folder of your SDF project: ","------------------------","account=","email=","role=(ID of SDF Enabled Row, traditionally role=3)","url=","------------------------"]
			view.run_command("insert", {"characters": "\n".join(output)})
			return

		second_command = ""
		second_pure_command = "empty"
		if pure_command == "importfiles":
			second_command = command
			command = command.replace( pure_command, "listfiles" )
			second_pure_command = pure_command
			pure_command = "listfiles"

		if pure_command == "importobjects" and cli_arguments[ "listobjects" ] != "":
			second_command = command
			command = command.replace( pure_command, "listobjects" )
			second_pure_command = pure_command
			pure_command = "listobjects"

		commands[ "adddependencies" ] = ["YES", ""]
		commands[ "deploy" ] = ["YES", ""]
		commands[ "importbundle" ] = ["YES", ""]
		commands[ "importfiles" ] = [account_info["password"],"YES"]
		commands[ "importobjects" ] = ["YES", ""]
		commands[ "listbundles" ] = ["YES", ""]
		commands[ "listfiles" ] = [account_info["password"], ""]
		commands[ "listmissingdependencies" ] = ["YES", ""]
		commands[ "listobjects" ] = ["YES", ""]
		commands[ "preview" ] = ["YES", ""]
		commands[ "update" ] = ["YES", ""]
		commands[ "updatecustomrecordwithinstances" ] = ["YES", ""]
		commands[ "validate" ] = ["YES", ""]
		commands[ "empty" ] = []

		newline = "\n"
		window_echo = " && echo "
		working_dir = SdfExec.project_folder

		if os.name == 'nt':
			command = command + ' ' + options
			second_command = second_command + ' ' + sub_options
		else:
			command = command + ' ' + options
			second_command = second_command + ' ' + sub_options

		if SdfExec.get_setting('debug', args):
			print( "SELECTED COMMAND: " + pure_command )
			print('new Thread')

		if second_pure_command == "empty":
			second_pure_command = ""

		if SdfExec.loader_thread.ident == None:
			SdfExec.loader_thread.start()

		t = Thread(target=SdfExec.execute_shell_command, args=(command, pure_command, working_dir, second_command, second_pure_command, cli_arguments, account_info, custom_object, args, command_options))
		t.start()

	def check_sdf_command( args, view, edit, currentCommand ):
		allcontent = sublime.Region(0, view.size())
		view.replace(edit, allcontent, "adddependencies")

	def display_loader():
		loading_position=0
		loading_display=( "[= ]", "[ =]" )
		starttime = time.time()
		delay_seconds = 0.5
		while True:
			if SdfExec.show_loader:
				print( SdfExec.loading_message + " " + loading_display[ loading_position ] )
				sublime.status_message( SdfExec.loading_message + " " + loading_display[ loading_position ] )
				loading_position = 1 if loading_position == 0 else 0
			if SdfExec.kill_loader:
				break

			time.sleep(delay_seconds - ((time.time() - starttime) % delay_seconds))

	loader_thread = Thread(target=display_loader)

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

	def execute_shell_command(command, pure_command, working_dir, second_command, second_pure_command, cli_arguments, account_info, custom_object, args, command_options, second_command_response = "", return_error=True, stdin=None):

		code = command

		if second_command_response != "":
			code = code.replace("importfiles", 'importfiles -paths "' + second_command_response + '"')
			code = code.replace("[SCRIPTID]", '-scriptid "' + second_command_response + '"')

		if pure_command == "importobjects":
			directory = working_dir + custom_object[2]
			if not os.path.exists(directory):
				os.makedirs(directory)

		sdf_command_do_gui_instance = SdfExec()

		if SdfExec.get_setting('debug', args):
			sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": False})
			print("run command: " + code)
			SdfExec.increment_output(sdf_command_do_gui_instance, "> " + pure_command + "\n\n", args, pure_command)

		if return_error:
			stderr = STDOUT
		else:
			stderr = None

		sublime.status_message( command_options[1] )

		console_stdout = ""
		startupinfo = None
		if os.name == 'nt':
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

		console_command = subprocess.Popen(code,
											stdin=subprocess.PIPE,
											stdout=subprocess.PIPE,
											stderr=subprocess.STDOUT,
											shell=True,
											cwd=working_dir,
											startupinfo=startupinfo)

		SdfExec.loading_message = "Connecting to NetSuite"
		SdfExec.show_loader = True

		while True:
			console_command.stdin.flush()
			proc_read = console_command.stdout.readline()
			if ( pure_command != "adddependencies" ) and (proc_read.find(b"SuiteCloud Development Framework CLI") >= 0 ):
				password_line = account_info["password"] + '\n'
				console_command.stdin.write( str.encode( password_line ) )

			if (proc_read.find(b"Type YES to continue") >= 0) or ( proc_read.find(b"Type YES to update the manifest file") >= 0 ):
				console_command.stdin.write(b'YES\n')

			if (proc_read.find(b"BUILD SUCCESS") >= 0):
				console_command.kill()
				break

			if (proc_read.find(b"must be specified") >= 0):
				console_command.kill()
				sublime.status_message( "There was an error with the call, please see the error log." )
				return
				break

			if proc_read:
				if SdfExec.get_setting('debug', args):
					print( proc_read.decode("utf-8").strip() )
				console_command.stdout.flush()
				console_stdout += proc_read.decode("utf-8")

		SdfExec.show_loader = False

		second_command_data = []
		if second_pure_command != "":
			second_command_data = SdfExec.parse_output(args, pure_command, console_stdout, custom_object, True)
		else:
			SdfExec.parse_output(args, pure_command, console_stdout, custom_object)

		if second_pure_command == "":
			if SdfExec.get_setting('debug', args):
				print(">>>>>>>>>>>>>>>>>> Shell Exec Debug Finished!")

			SdfExec.kill_loader = True
			sublime.status_message( "sdfcli command complete" )
		else:
			def runSecondCall(user_command):
				if user_command == -1:
					return
				if SdfExec.get_setting('debug', args):
					print( second_command_data[user_command] )
				ttwo = Thread(target=SdfExec.execute_shell_command, args=(second_command, second_pure_command, working_dir, "", "", cli_arguments, account_info, custom_object, args, command_options, second_command_data[user_command].strip()))
				ttwo.start()

			sublime.active_window().show_quick_panel(second_command_data, runSecondCall)


	def get_setting(config, args, force_default=False):
		if (not force_default) and args.get(config):
			return args[config]

		settings = sublime.load_settings('Preferences.sublime-settings')
		if settings.get('sdf_exec_' + config):
			return settings.get('sdf_exec_' + config)
		else:
			settings = sublime.load_settings('SublimeSdf.sublime-settings')
			return settings.get('sdf_exec_' + config)

	def parse_output(args, command, console_stdout, custom_object, return_result=False):

		sdf_command_do_gui_instance = sublime.active_window()
		if return_result == True:
			output = []
		else:
			output = ""

		if command == "listfiles":
			for line in console_stdout.splitlines():
				if line.find('/SuiteScripts') >= 0:
					if return_result == True:
						output.append( line.replace("Enter password:", "") + "\n" )
					else:
						output += line.replace("Enter password:", "") + "\n" # Since "Enter password:" doesn't create a new line, remove it
		elif command == "listbundles":
			for line in console_stdout.splitlines():
				if line[:2].isdigit() or line.find("Enter password:") >= 0:
					if return_result == True:
						output.append( line.replace("Enter password:", "") + "\n" )
					else:
						output += line.replace("Enter password:", "") + "\n" # Since "Enter password:" doesn't create a new line, remove it
		elif command == "listmissingdependencies":
			print_line = False
			for line in console_stdout.splitlines():
				if line.find("[INFO]") >= 0:
					print_line = False
				if print_line:
					output += line + "\n"
				if line.find("Unresolved dependencies:") >= 0:
					print_line = True
		elif command == "listobjects":
			for line in console_stdout.splitlines():
				if line.find("Enter password:") >= 0:
					if return_result == True:
						output.append( line.replace("Enter password:", "").replace(custom_object[1] + ":", "") + "\n" )
					else:
						output += line.replace("Enter password:", "").replace(custom_object[1] + ":", "") + "\n" # Since "Enter password:" doesn't create a new line, remove it
				elif line.find(custom_object[1]) >= 0:
					if return_result == True:
						output.append( line.replace("Enter password:", "").replace(custom_object[1] + ":", "") + "\n" )
					else:
						output += line.replace("Enter password:", "").replace(custom_object[1] + ":", "") + "\n" # Since "Enter password:" doesn't create a new line, remove it
		elif command == "preview":
			print_line = False
			for line in console_stdout.splitlines():
				if line.find("[INFO]") >= 0:
					print_line = False
				if print_line:
					output += line + "\n"
				if line.find("Enter password:") >= 0:
					output += line.replace("Enter password:", "") + "\n"
					print_line = True

		if return_result == True:
			return output
		elif command == "listfiles" or command == "listbundles" or command == "listmissingdependencies" or command == "listobjects" or command == "preview":
			view = sublime.Window.new_file( sdf_command_do_gui_instance )
			view.run_command("insert", {"characters": output})