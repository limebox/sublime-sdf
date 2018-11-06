import subprocess, math, time

from .Settings import *
from .Loader import *
from .Debug import *
from .Output import *

from subprocess import STDOUT
from threading import Thread

class Sdf:

	threads = []
	current_thread = -1

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

	def prepare_command(args, view, command_options, cli_arguments, custom_object):

		# Reset threads
		Sdf.threads = []
		Sdf.current_thread = -1

		command = Settings.get_setting('cli_executable', args) + Settings.sdfcli_ext + " " + Sdf.command_variables(args, view, command_options[2])
		project_command = Settings.get_setting('cli_executable', args) + " project -p "
		if 'folder' in sublime.active_window().extract_variables():
			if sublime.platform() == 'windows':
				pure_command = Sdf.command_variables(args, view, command_options[2]).replace(sublime.active_window().extract_variables()['folder'] + '\\', '')
			else:
				pure_command = Sdf.command_variables(args, view, command_options[2]).replace(sublime.active_window().extract_variables()['folder'] + '/', '')
		else:
			pure_command = Sdf.command_variables(args, view, command_options[2])

		project_command = project_command + '"' + Settings.project_folder + '"'

		if sublime.platform() == 'windows':
			command = command.replace('/', '\\')

		for cli_argument in cli_arguments:
			# Replace commands for the project folder
			cli_arguments[ cli_argument ] = cli_arguments[ cli_argument ].replace("[PROJECT_FOLDER]", Settings.project_folder)

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

		for item in Settings.account_info[ Settings.active_account ]:
			if item != "password":
				options = options + " -" + item + ' "' + Settings.account_info[ Settings.active_account ][ item ] + '"'
				sub_options = sub_options + " -" + item + ' "' + Settings.account_info[ Settings.active_account ][ item ] + '"'

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

		newline = "\n"
		window_echo = " && echo "
		working_dir = Settings.project_folder

		if os.name == 'nt':
			command = command + ' ' + options
			second_command = second_command + ' ' + sub_options
		else:
			command = command + ' ' + options
			second_command = second_command + ' ' + sub_options

		if Settings.get_setting('debug', args):
			print( "SELECTED COMMAND: " + pure_command )
			print('new Thread')

		if second_pure_command == "empty":
			second_pure_command = ""

		if Loader.loader_thread.ident == None:
			Loader.loader_thread.start()

		t = Thread(target=Sdf.execute_sdf_command, args=(command, pure_command, working_dir, second_command, second_pure_command, cli_arguments, custom_object, args, command_options))
		t.start()

	def check_sdf_command( args, view, edit, currentCommand ):
		allcontent = sublime.Region(0, view.size())
		view.replace(edit, allcontent, "adddependencies")

	def execute_sdf_command(command, pure_command, working_dir, second_command, second_pure_command, cli_arguments, custom_object, args, command_options, second_command_response = "", return_error=True, stdin=None):
		code = command
		has_error = False

		if second_command_response != "":
			code = code.replace("importfiles", 'importfiles -paths ' + second_command_response)
			code = code.replace("[SCRIPTID]", '-scriptid ' + second_command_response )

		if pure_command == "importobjects":
			directory = working_dir + custom_object[2]
			if not os.path.exists(directory):
				os.makedirs(directory)
		elif pure_command == "adddependencies":
			# Since the manifest might have old information, let's reset it
			if os.name == 'nt':
				path_var = "\\"
			else:
				path_var = "/"

			manifest_file = open( Settings.project_folder + "/manifest.xml","w+" )
			project_name = Settings.project_folder[ Settings.project_folder.rfind( path_var ) + 1 : ]
			manifest_file.write("<manifest projecttype=\"ACCOUNTCUSTOMIZATION\">\n  <projectname>" + project_name + "</projectname>\n  <frameworkversion>1.0</frameworkversion>\n</manifest>")
			manifest_file.close()

		if Settings.get_setting('debug', args):
			sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": False})
			print("run command: " + code)
			Debug.increment_output(Sdf(), "> " + pure_command + "\n\n", args, pure_command)

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

		Loader.loading_message = "Connecting to NetSuite"
		Loader.show_loader = True


		line_continue=0

		# Looping through the lines. This will also look at each line and determine if we need to output the error.
		while True:
			console_command.stdin.flush()
			proc_read = console_command.stdout.readline()
			if ( proc_read.find(b"Using user credentials.") >= 0 ):
				password_line = Settings.password[ Settings.active_account ] + '\n'
				console_command.stdin.write( str.encode( password_line ) )

			if (
				(proc_read.find(b"Type YES to continue") >= 0)
				or (proc_read.find(b"enter YES to continue") >= 0)
				or ( proc_read.find(b"Type YES to update the manifest file") >= 0)
				or ( proc_read.find(b"Proceed with deploy?") >= 0)
				):
				console_command.stdin.write(b'YES\n')

			if (proc_read.find(b"BUILD SUCCESS") >= 0):
				console_command.kill()
				break

			if (
				(proc_read.find(b"must be specified") >= 0)
				or (proc_read.find(b"Installation FAILED") >= 0)
				or (proc_read.find(b"Unknown host.") >= 0)
				or ( proc_read.find(b"The remote server returned an error") >= 0 )
				or (proc_read.find(b"Partial Content") >= 0) ):
				console_command.kill()
				sublime.status_message( "There was an error with the call, please see the error log." )
				has_error=True
				line_continue=2

			if (proc_read.find(b"Invalid account specified") >= 0 ):
				has_error=True
				console_stdout += proc_read.decode("utf-8")
				console_stdout = "************** INVALID ACCOUNT SPECIFIED **************\n Please update your .sdf file and use the proper account #\n" + console_stdout
				console_command.kill()
				break

			if (proc_read.find(b"not enabled in this account") >= 0 ):
				has_error=True
				console_stdout += proc_read.decode("utf-8")
				console_stdout = "************** Token Based Authentication Feature Not Enabled **************\n Please enable Token Based Authentication in 'Enable Features' #\n" + console_stdout
				console_command.kill()
				break

			if (
				( proc_read.find(b"were not imported") >= 0 )
				or ( proc_read.find(b"A file upload error occurred") >= 0 )
				or ( proc_read.find(b"Unable to connect to server") >= 0 )):
				sublime.status_message( "There was an error with the call, please see the error log." )
				has_error=True
				line_continue=-1

			if (proc_read.find(b"invalid email address or password") >= 0):
				sublime.status_message( "You have entered an invalid email address or password. Please check your .sdf file and try again" )
				has_error=True
				Settings.password[ Settings.active_account ] = "" # Reset the password since it might be invalid
				console_stdout += proc_read.decode("utf-8")
				console_stdout = "************** INVALID EMAIL OR PASSWORD **************\n IF YOU TRY TOO MANY TIMES YOU WILL BE LOCKED OUT\n" + console_stdout
				console_command.kill()
				break

			if proc_read:
				if Settings.get_setting('debug', args):
					print( proc_read.decode("utf-8").strip() )
				console_command.stdout.flush()
				console_stdout += proc_read.decode("utf-8")

			if has_error and line_continue == 0:
				break
			elif has_error:
				line_continue = line_continue - 1

		Loader.show_loader = False

		second_command_data = []

		if has_error:
			Output.parse_output(args, pure_command, console_stdout, custom_object, has_error, False, Settings.get_setting('debug', self.args))
		elif second_pure_command != "":
			second_command_data = Output.parse_output(args, pure_command, console_stdout, custom_object, has_error, True)
		else:
			Output.parse_output(args, pure_command, console_stdout, custom_object, has_error)

		if len(Sdf.threads) > 1 and len(Sdf.threads) > Sdf.current_thread + 1:
			Sdf.current_thread = Sdf.current_thread + 1
			Sdf.threads[ Sdf.current_thread ].start()

		if second_pure_command == "":
			if Settings.get_setting('debug', args):
				print(">>>>>>>>>>>>>>>>>> Shell Exec Debug Finished!")

			sublime.status_message( "sdfcli command complete" )
		else:
			def runSecondCall(user_command):
				if user_command == -1:
					return
				if Settings.get_setting('debug', args):
					print( second_command_data[user_command] )

				data_to_get = second_command_data[user_command].strip()
				bad_characters = ["?","(",")", " ","&", ".xml"]

				if data_to_get == "All":
					second_command_data.pop(0)
					failed_files = []
					acceptable_files = []

					# SDF doesn't like spaces in filenames
					for file in second_command_data:
						if any(bad_character in file for bad_character in bad_characters):
							failed_files.append( file )
						elif file != "":
							acceptable_files.append( '"' + file.strip() + '"' )
					sub_array_length = 100
					total_objects = len( acceptable_files )
					array_length = int( math.ceil( float(total_objects) / float(sub_array_length)) )

					for i in range(0, array_length):
						start = i * sub_array_length
						end = i * sub_array_length + sub_array_length
						data_array = acceptable_files[ start : end ]
						data_to_get = " ".join( data_array ).strip().replace("\n", "")
						Sdf.threads.append( Thread(target=Sdf.execute_sdf_command, args=(second_command, second_pure_command, working_dir, "", "", cli_arguments, custom_object, args, command_options, data_to_get)) )

					if len( failed_files ) > 0:
						Output.parse_output(args, second_command, "These files:\n" + ",".join(failed_files) + "Have characters not permitted by SDF.\nCharacters cannot be: (" + ",".join( bad_characters ) + ")", custom_object, True)

					Sdf.current_thread = Sdf.current_thread + 1
					Sdf.threads[ Sdf.current_thread ].start()

				else:
					if any(bad_character in data_to_get for bad_character in bad_characters):
						Output.parse_output(args, second_command, "The requested file: " + data_to_get + "\nHas characters not permitted by SDF. Characters cannot be: (" + ",".join( bad_characters ) + ")", custom_object, True)
					else:
						Sdf.threads.append( Thread(target=Sdf.execute_sdf_command, args=(second_command, second_pure_command, working_dir, "", "", cli_arguments, custom_object, args, command_options, data_to_get)) )
						Sdf.current_thread = Sdf.current_thread + 1
						Sdf.threads[ Sdf.current_thread ].start()

			sublime.active_window().show_quick_panel(second_command_data, runSecondCall)