import sublime, sublime_plugin, os, json
from .Settings import *
from .Config import *
from .Sdf import *


class Commands():

	actionParameter = None # In case this is called from a file / object, we want to be able to download the file / object directly

	account_settings = Settings.get_setting('account_data', {})
	temp_password = ""

	custom_objects = Config.get("custom_objects")
	cli_commands = Config.get("cli_commands")
	cli_arguments = Config.get("cli_arguments")

	reset_cli_arguments = {}

	adjusted_commands = []

	current_file = None
	files = []

	def adddependencies( sdfCallback ):
		sdfCallback( 'adddependencies', Commands.reset_cli_arguments )
		return True

	def deploy( sdfCallback ):
		sdfCallback( 'deploy', Commands.reset_cli_arguments )
		return True

	def importbundle( sdfCallback ):
		Commands.reset_cli_arguments["importbundle"] = Commands.reset_cli_arguments["importbundle"] + ' [BUNDLEID]'
		sdfCallback( 'importbundle', Commands.reset_cli_arguments )
		return True

	def importconfiguration( sdfCallback ):
		Commands.reset_cli_arguments["importconfiguration"] = Commands.reset_cli_arguments["importconfiguration"] + ' [CONFIGURATIONID]'
		sdfCallback( 'importconfiguration', Commands.reset_cli_arguments )
		return True

	def importfiles( sdfCallback ):
		sdfCallback( 'importfiles', Commands.reset_cli_arguments, None, Commands.actionParameter )
		return True

	def importobjects( sdfCallback ):

		def selectObjectToImport(user_command):
			if user_command == -1:
				return

			Commands.reset_cli_arguments["listobjects"] = '-type "' + Commands.custom_objects[ user_command ][1] + '"'
			Commands.reset_cli_arguments["importobjects"] = Commands.reset_cli_arguments["importobjects"] +  ' -destinationfolder "' + Commands.custom_objects[ user_command ][2] + '" [SCRIPTID] -type "' + Commands.custom_objects[ user_command ][1] + '"'
			sdfCallback( 'importobjects', Commands.reset_cli_arguments, Commands.custom_objects[ user_command ], Commands.actionParameter)

		sublime.active_window().show_quick_panel(Commands.custom_objects, selectObjectToImport)
		return True

	def listbundles( sdfCallback ):
		sdfCallback( 'listbundles', Commands.reset_cli_arguments )
		return True

	def listconfiguration( sdfCallback ):
		sdfCallback( 'listconfiguration', Commands.reset_cli_arguments )
		return True

	def listfiles( sdfCallback ):
		sdfCallback( 'listfiles', Commands.reset_cli_arguments )
		return True

	def listmissingdependencies( sdfCallback ):
		sdfCallback( 'listmissingdependencies', Commands.reset_cli_arguments )
		return True

	def listobjects( sdfCallback ):
		def selectObject( userCommand ):
			if userCommand == -1:
				return
			Commands.reset_cli_arguments["listobjects"] = '-type "' + custom_objects[userCommand][1] + '"'

			sdfCallback( 'listobjects', Commands.reset_cli_arguments, custom_objects[user_command])

		sublime.active_window().show_quick_panel(Commands.custom_objects, selectObject)
		return True

	def preview( sdfCallback ):
		sdfCallback( 'preview', Commands.reset_cli_arguments )
		return True
	def update( sdfCallback, action = 'update' ):

		def selectObjectToUpdate( user_command ):
			if user_command == -1:
				return
			elif isinstance(user_command, int):
				# This is true when selected from the standard SDF Menu
				file_start = Commands.files[ user_command ].rfind(Settings.path_var) + 1
				update_object = Commands.files[ user_command ][file_start:-4]
			else:
				update_object = user_command

			if action == "updatecustomrecordwithinstances":
				Commands.reset_cli_arguments["updatecustomrecordwithinstances"] += ' -scriptid "' + update_object + '"'
			else:
				Commands.reset_cli_arguments["update"] += ' -scriptid "' + update_object + '"'

			sdfCallback( action, Commands.reset_cli_arguments )

		if Settings.selected_file != '' and Settings.context == 'menu':
			file_to_update = Settings.selected_file.replace('.xml', '')
			selectObjectToUpdate( file_to_update )
		else:
			objects_folder = ""
			test_dir = Settings.project_folder
			while True:

				if action == "updatecustomrecordwithinstances":
					testDir = test_dir + Settings.path_var + "Objects" + Settings.path_var + "Records"
				else:
					testDir = test_dir + Settings.path_var + "Objects"

				if os.path.isdir( testDir ):
					objects_folder=testDir
					break
				else:
					parent_folder = test_dir.rfind( Settings.path_var )
					test_dir = test_dir[0:parent_folder]

			for (root, dirnames, filenames) in os.walk(objects_folder):
				for name in filenames:
					if name.find(".xml") >= 0:
						Commands.files.append( Settings.path_var + "Objects" + root.replace( objects_folder, "" ) + Settings.path_var + name )

			sublime.active_window().show_quick_panel(Commands.files, selectObjectToUpdate)

	def updatecustomrecordwithinstances( sdfCallback ):
		Commands.update( sdfCallback, 'updatecustomrecordwithinstances')
		return True

	def validate( sdfCallback ):
		sdfCallback( 'validate', Commands.reset_cli_arguments )
		return True

	def revoketoken( sdfCallback ):
		sdfCallback( 'revoketoken', Commands.reset_cli_arguments )
		return True

	def issuetoken( sdfCallback ):
		sdfCallback( 'issuetoken', Commands.reset_cli_arguments )
		return True

	def setpassword( sdfCallback ):

		def set_password( user_password ):
			Settings.password[ Settings.active_account ] = Commands.temp_password

		def get_password( user_password ):
			if( len(user_password) != len(Commands.temp_password) ):
				if  len(user_password) < len(Commands.temp_password):
					Commands.temp_password = Commands.temp_password[:len(user_password)]
				else:
					chg = user_password[len( Commands.temp_password ):]
					Commands.temp_password = Commands.temp_password + chg
				stars = "*" * len(user_password)
				sublime.active_window().show_input_panel("NetSuite Password", stars, set_password, get_password, None)

		sublime.active_window().show_input_panel("NetSuite Password", "", None, get_password, None)

	def clearpassword( sdfCallback ):
		del Settings.password[ Settings.active_account ]

	def run( action = False, actionParameter = None ):

		for argument in Commands.cli_arguments:
			Commands.reset_cli_arguments[ argument ] = Commands.cli_arguments[ argument ]

		def runSdfExec(user_command):

			if user_command == -1:
				return False

			sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": False})
			print("\n\n>>>>>>>>>>>>>>>>>> Initiate NetSuite SDF:")

			selected_id = None

			if isinstance(user_command, int):
				# This is true when selected from the standard SDF Menu
				selected_id = user_command
			else:
				# This is the case when this is being executed from the Context Menu
				i = 0
				command_length = len( Commands.cli_commands )
				while i < command_length:
					if user_command == Commands.cli_commands[ i ][2]:
						selected_id = i
						break;
					else:
						i += 1

			object_type = 0
			files = []
			getattr(Commands, Commands.adjusted_commands[selected_id][2])( Sdf.prepare_command )

			# End runSdfExec

		Commands.adjusted_commands = [] # Reset the adjusted_commands array

		if action == False:
			Settings.context = "tab"
			for command in Commands.cli_commands:

				if ((command[2] == 'issuetoken' and Settings.active_account in Commands.account_settings)
					or (command[2] == 'revoketoken' and (Settings.active_account in Commands.account_settings) == False)
					or (command[2] == 'setpassword' and Settings.active_account in Settings.password)
					or (command[2] == 'clearpassword' and (Settings.active_account in Settings.password) == False)):
					continue
				else:
					Commands.adjusted_commands.append( command )

			sublime.active_window().show_quick_panel(Commands.adjusted_commands, runSdfExec)
		else:
			Settings.context = "menu"
			for command in Commands.cli_commands:
				Commands.adjusted_commands.append( command )

			Commands.actionParameter = actionParameter

			runSdfExec( action )