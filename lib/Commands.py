import sublime, sublime_plugin, os, json
from .Settings import *
from .Config import *
from .Sdf import *


class Commands(sublime_plugin.TextCommand):

	def run(self, edit, action = False):

		# This will need to be moved to check for password
		# def get_password( user_password ):
		# 	if( len(user_password) != len(SdfExecOpen.temp_password) ):
		# 		if  len(user_password) < len(SdfExecOpen.temp_password):
		# 			SdfExecOpen.temp_password = SdfExecOpen.temp_password[:len(user_password)]
		# 		else:
		# 			chg = user_password[len( SdfExecOpen.temp_password ):]
		# 			SdfExecOpen.temp_password = SdfExecOpen.temp_password + chg
		# 		stars = "*" * len(user_password)
		# 		sublime.active_window().show_input_panel("NetSuite Password", stars, run_programm, get_password, None)

		# if Settings.active_account not in Settings.password and ("password" not in Settings.account_info[ Settings.active_account ] or Settings.account_info[ Settings.active_account ][ "password" ] != ""):
		# 	sublime.active_window().show_input_panel("NetSuite Password", "", None, get_password, None)

		def runSdfExec(user_command):

			print("\n\n>>>>>>>>>>>>>>>>>> Initiate NetSuite SDF:")

			custom_objects = Config.get("custom_objects")
			cli_commands = Config.get("cli_commands")
			cli_arguments = Config.get("cli_arguments")

			selected_id = None

			if isinstance(user_command, int):
				selected_id = user_command
			else:
				i = 0
				command_length = len( cli_commands )
				while i < command_length:
					if user_command == cli_commands[ i ][2]:
						selected_id = i
						break;
					else:
						i += 1

			object_type = 0
			files = []
			reset_cli_arguments = {}

			for argument in cli_arguments:
				reset_cli_arguments[ argument ] = cli_arguments[ argument ]

			if os.name == 'nt':
				path_var = "\\"
			else:
				path_var = "/"

			def selectObject(user_command):
				if user_command == -1:
					return
				reset_cli_arguments["listobjects"] = '-type "' + custom_objects[user_command][1] + '"'
				Sdf.prepare_command(self, self.view, cli_commands[selected_id], reset_cli_arguments, custom_objects[user_command])

			def selectObjectToImport(user_command):
				if user_command == -1:
					return
				runSdfExec.object_type=user_command
				reset_cli_arguments["listobjects"] = '-type "' + custom_objects[runSdfExec.object_type][1] + '"'
				reset_cli_arguments["importobjects"] = reset_cli_arguments["importobjects"] +  ' -destinationfolder "' + custom_objects[runSdfExec.object_type][2] + '" [SCRIPTID] -type "' + custom_objects[runSdfExec.object_type][1] + '"'
				Sdf.prepare_command(self, self.view, cli_commands[selected_id], reset_cli_arguments, custom_objects[runSdfExec.object_type])

			def selectObjectToUpdate( user_command ):
				if user_command == -1:
					return
				file_start = files[ user_command ].rfind(path_var) + 1
				update_object = files[ user_command ][file_start:-4]

				if cli_commands[selected_id][2] == "updatecustomrecordwithinstances":
					reset_cli_arguments["updatecustomrecordwithinstances"] += ' -scriptid "' + update_object + '"'
				else:
					reset_cli_arguments["update"] += ' -scriptid "' + update_object + '"'
				Sdf.prepare_command(self, self.view, cli_commands[selected_id], reset_cli_arguments, None)

			if cli_commands[selected_id][0] == "Clear Password":
				Settings.password = {}
			elif cli_commands[selected_id][2] == "listobjects":
				# In this instance, we need to ask the user another question about what type of object
				sublime.active_window().show_quick_panel(custom_objects, selectObject)
			elif cli_commands[selected_id][2] == "importobjects":
				# If someone wants to import an object, they need to pick an object type first
				sublime.active_window().show_quick_panel(custom_objects, selectObjectToImport)
			elif ( cli_commands[selected_id][2] == "update" or cli_commands[selected_id][2] == "updatecustomrecordwithinstances" ):

				current_file = sublime.active_window().active_view().file_name()
				parent_folder = current_file.rfind( path_var )
				current_file = current_file[0:parent_folder]
				objects_folder = ""
				while True:

					if cli_commands[selected_id][2] == "updatecustomrecordwithinstances":
						testDir = current_file + path_var + "Objects" + path_var + "Records"
					else:
						testDir = current_file + path_var + "Objects"

					if os.path.isdir( testDir ):
						objects_folder=testDir
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
				Sdf.prepare_command(self, self.view, cli_commands[selected_id], reset_cli_arguments, None)

		if action == False:
			sublime.active_window().show_quick_panel(cli_commands, runSdfExec)
		else:
			runSdfExec( action )