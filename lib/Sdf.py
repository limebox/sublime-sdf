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

	def prepare_command( command, cli_arguments, custom_object = None, fileOrObject = None ):

		command_prefix = Settings.get_setting('cli_executable', {}) + Settings.sdfcli_ext

		command_one = ''
		command_two = ''

		command_one_options = ''
		command_two_options = ''

		execute_command_one = ''
		execute_command_two = ''

		# There are a few commands that require a previous command, we handle that here.
		# We also set command options
		if command == "importfiles" and fileOrObject == None:

			# When importing files, we need a list of files to import
			command_one_options = cli_arguments[ "listfiles" ]
			command_two_options = cli_arguments[ command ]

			command_one = "listfiles"
			command_two = command

		elif command == "importobjects" and cli_arguments[ "listobjects" ] != "" and fileOrObject == None:

			# When importing objects, we first need to get the list of objects.
			command_one_options = cli_arguments[ "listobjects" ]
			command_two_options = cli_arguments[ command ]

			command_one = "listobjects"
			command_two = command

		else:
			command_one = command
			command_one_options = cli_arguments[ command ]


		for item in Settings.account_info[ Settings.active_account ]:
			command_one_options = command_one_options + " -" + item + ' "' + Settings.account_info[ Settings.active_account ][ item ] + '"'
			command_two_options = command_two_options + " -" + item + ' "' + Settings.account_info[ Settings.active_account ][ item ] + '"'

		execute_command_one = command_prefix + " " + command_one + " " + command_one_options.replace('[PROJECT_FOLDER]', Settings.project_folder)
		if command_two != '':
			execute_command_two = command_prefix + " " + command_two + " " + command_two_options.replace('[PROJECT_FOLDER]', Settings.project_folder)
		
		if Loader.loader_thread.ident == None:
			Loader.loader_thread.start()

		t = Thread(target=Sdf.execute_sdf_command, args=( command_one, execute_command_one, command_two, execute_command_two, cli_arguments, custom_object, fileOrObject ))
		t.start()

		return True

	def execute_sdf_command( command_one, execute_command_one, command_two, execute_command_two, cli_arguments, custom_object, second_command_response = "", return_error=True, stdin=None):

		has_error = False

		# If this is a two command request, then the second round will have a response
		if second_command_response != "" and second_command_response != None:
			execute_command_one = execute_command_one.replace("importfiles", 'importfiles -paths ' + second_command_response)
			execute_command_one = execute_command_one.replace("[SCRIPTID]", '-scriptid ' + second_command_response )

		if command_one == "importobjects":
			directory = Settings.working_dir + custom_object[2]
			if not os.path.exists(directory):
				os.makedirs(directory)
		elif command_one == "adddependencies":
			# Since the manifest might have old information, let's reset it

			manifest_file = open( Settings.project_folder + "/manifest.xml","w+" )
			project_name = Settings.project_folder[ Settings.project_folder.rfind( Settings.path_var ) + 1 : ]
			manifest_file.write("<manifest projecttype=\"ACCOUNTCUSTOMIZATION\">\n  <projectname>" + project_name + "</projectname>\n  <frameworkversion>1.0</frameworkversion>\n</manifest>")
			manifest_file.close()

		print("Execute sdfcli Command: " + execute_command_one)

		if return_error:
			stderr = STDOUT
		else:
			stderr = None

		console_stdout = ""
		startupinfo = None

		if os.name == 'nt':
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

		console_command = subprocess.Popen(execute_command_one,
											stdin=subprocess.PIPE,
											stdout=subprocess.PIPE,
											stderr=subprocess.STDOUT,
											shell=True,
											cwd=Settings.project_folder,
											startupinfo=startupinfo)

		Loader.loading_message = "Connecting to NetSuite"
		Loader.show_loader = True

		line_continue=0
		last_line = ""

		# Looping through the lines. This will also look at each line and determine if we need to output the error.
		while True:
			console_command.stdin.flush()
			proc_read = console_command.stdout.readline()
			if ( proc_read.find(b"Using user credentials.") >= 0 ):
				# If a token has not been set, we will see this message
				password_line = Settings.password[ Settings.active_account ] + '\n'
				console_command.stdin.write( str.encode( password_line ) )

			if (
				(proc_read.find(b"Type YES to continue") >= 0)
				or (proc_read.find(b"enter YES to continue") >= 0)
				or ( proc_read.find(b"Type YES to update the manifest file") >= 0)
				or ( proc_read.find(b"Proceed with deploy?") >= 0)
				):
				console_command.stdin.write(b'YES\n')

			if (proc_read.find(b"Token has been issued.") >= 0):
				account_settings = Settings.get_setting('account_data', {})
				account_settings[ Settings.active_account ] = {'token': True}
				Settings.set_setting( 'account_data', account_settings )

			if (proc_read.find(b"Token has been revoked.") >= 0):
				account_settings = Settings.get_setting('account_data', {})
				del account_settings[ Settings.active_account ]
				Settings.set_setting( 'account_data', account_settings )

			if (proc_read.find(b"BUILD SUCCESS") >= 0):
				console_command.kill()
				break

			if proc_read:
				print( proc_read.decode("utf-8").strip() )
				console_command.stdout.flush()
				console_stdout += proc_read.decode("utf-8")

			if last_line == proc_read:
				console_command.kill()
				break
			else:
				last_line = proc_read

		Loader.show_loader = False

		second_command_data = []

		if execute_command_two != "":
			second_command_data = Output.parse_output( command_one, console_stdout, custom_object, True)
		else:
			Output.parse_output( command_one, console_stdout, custom_object)

		if len(Sdf.threads) > 1 and len(Sdf.threads) > Sdf.current_thread + 1:
			Sdf.current_thread = Sdf.current_thread + 1
			Sdf.threads[ Sdf.current_thread ].start()

		if execute_command_two == "":

			# This is executed on the second command of a two command request or the only command of a single command request
			print(">>>>>>>>>>>>>>>>>> NetSuite SDF Complete.")
			sublime.status_message( "sdfcli command complete" )

		else:

			# This request requires a second command that is based off of the data from the first
			def runSecondCall( user_command ):

				if user_command == -1:
					return

				print( "Selection Made: " + second_command_data[user_command] )

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

					# Given that you asked for all files or objects, SDF crashes if you ask for too much.
					# Because of this, we are going to ask for 100 files / objects at a time
					sub_array_length = 100
					total_objects = len( acceptable_files )
					array_length = int( math.ceil( float(total_objects) / float(sub_array_length)) )

					for i in range(0, array_length):
						start = i * sub_array_length
						end = i * sub_array_length + sub_array_length
						data_array = acceptable_files[ start : end ]
						data_to_get = " ".join( data_array ).strip().replace("\n", "")

						Sdf.threads.append( Thread(target=Sdf.execute_sdf_command, args=( command_two, execute_command_two, "", "", cli_arguments, custom_object, data_to_get )) )

					if len( failed_files ) > 0:
						Output.parse_output(args, command_one, "These files:\n" + ",".join(failed_files) + "Have characters not permitted by SDF.\nCharacters cannot be: (" + ",".join( bad_characters ) + ")", custom_object, True)

					Sdf.current_thread = Sdf.current_thread + 1
					Sdf.threads[ Sdf.current_thread ].start()

				else:
					if any(bad_character in data_to_get for bad_character in bad_characters):
						Output.parse_output(args, command_one, "The requested file: " + data_to_get + "\nHas characters not permitted by SDF. Characters cannot be: (" + ",".join( bad_characters ) + ")", custom_object, True)
					else:
						Sdf.threads.append( Thread(target=Sdf.execute_sdf_command, args=( command_two, execute_command_two, "", "", cli_arguments, custom_object, data_to_get )) )
						Sdf.current_thread = Sdf.current_thread + 1
						Sdf.threads[ Sdf.current_thread ].start()

			sublime.active_window().show_quick_panel(second_command_data, runSecondCall)




