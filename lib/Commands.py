import sublime, sublime_plugin, os, json
from .Settings import *
from .Config import *
from .Sdf import *


class Commands(sublime_plugin.TextCommand):
	def run(self, edit, **args, envFile):
		if Settings.get_setting('debug', self.args):
			print("\n\n>>>>>>>>>>>>>>>>>> Start Shell Exec Debug:")

		custom_objects = Config.get("custom_objects")
		cli_commands = Config.get("cli_commands")
		cli_arguments = Config.get("cli_arguments")

		def runSdfExec(user_command):
			selected_id = user_command
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
				Sdf.prepare_command(self.args, self.view, cli_commands[selected_id], reset_cli_arguments, custom_objects[user_command])

			def selectObjectToImport(user_command):
				if user_command == -1:
					return
				runSdfExec.object_type=user_command
				reset_cli_arguments["listobjects"] = '-type "' + custom_objects[runSdfExec.object_type][1] + '"'
				reset_cli_arguments["importobjects"] = reset_cli_arguments["importobjects"] +  ' -destinationfolder "' + custom_objects[runSdfExec.object_type][2] + '" [SCRIPTID] -type "' + custom_objects[runSdfExec.object_type][1] + '"'
				Sdf.prepare_command(self.args, self.view, cli_commands[selected_id], reset_cli_arguments, custom_objects[runSdfExec.object_type])

			def selectObjectToUpdate( user_command ):
				if user_command == -1:
					return
				file_start = files[ user_command ].rfind(path_var) + 1
				update_object = files[ user_command ][file_start:-4]

				if cli_commands[selected_id][2] == "updatecustomrecordwithinstances":
					reset_cli_arguments["updatecustomrecordwithinstances"] += ' -scriptid "' + update_object + '"'
				else:
					reset_cli_arguments["update"] += ' -scriptid "' + update_object + '"'
				Sdf.prepare_command(self.args, self.view, cli_commands[selected_id], reset_cli_arguments, None)

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
				Sdf.prepare_command(self.args, self.view, cli_commands[selected_id], reset_cli_arguments, None)

		sublime.active_window().show_quick_panel(cli_commands, runSdfExec)