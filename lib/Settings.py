import sublime, sublime_plugin, os

class Settings( sublime_plugin.TextCommand ):

	context = "tab"
	account_info = {}
	password = {}
	sdfcli_ext = ""
	project_folder = ""
	selected_file = ""
	selected_file_path = ""
	active_account = ""
	path_var = "/"
	sdfcli_ext = ""
	temp_password = ""

	if os.name == 'nt':
		path_var = "\\"
		sdfcli_ext = ".bat"

	def get_setting(config, args, force_default=False):
		if (not force_default) and args.get(config):
			return args[config]

		settings = sublime.load_settings('Preferences.sublime-settings')
		if settings.get('sdf_exec_' + config):
			return settings.get('sdf_exec_' + config)
		else:
			settings = sublime.load_settings('SublimeSdf.sublime-settings')
			if settings.get('sdf_exec_' + config):
				return settings.get('sdf_exec_' + config)
			else:
				return args

	def set_setting( setting, value ):
		plugin_settings = sublime.load_settings('SublimeSdf.sublime-settings')
		#old_setting = plugin_settings.get( 'sdf_exec_' + setting )
		plugin_settings.set( 'sdf_exec_' + setting, value )
		sublime.save_settings('SublimeSdf.sublime-settings')

	def setpassword( executeCallback ):
		def set_password( user_password ):
			Settings.password[ Settings.active_account ] = Settings.temp_password
			executeCallback()

		def get_password( user_password ):
			if( len(user_password) != len(Settings.temp_password) ):
				if  len(user_password) < len(Settings.temp_password):
					Settings.temp_password = Settings.temp_password[:len(user_password)]
				else:
					chg = user_password[len( Settings.temp_password ):]
					Settings.temp_password = Settings.temp_password + chg
				stars = "*" * len(user_password)
				sublime.active_window().show_input_panel("NetSuite Password", stars, set_password, get_password, None)

		sublime.active_window().show_input_panel("NetSuite Password", "", None, get_password, None)

	def get_sdf_file( executeCallback, path = "" ):
		active_vars = sublime.active_window().extract_variables()
		if 'project_path' in active_vars:
			root_folder = active_vars[ 'project_path' ] + Settings.path_var
		elif 'file_path' in active_vars:
			root_folder = active_vars[ 'file_path' ] + Settings.path_var
		else:
			root_folder = ""

		if path != "":
			# This is a request from the context menu and we want to see if an SDF file even exists
			if os.path.isdir( path ):
				# If this is a directory, we want to turn it into a fake file 
				path = path + Settings.path_var + 'not_a_file.not_a_file'

			return Settings.get_environment( path, executeCallback, True )
		elif sublime.active_window().active_view().file_name() is None:
			# Instead of showing an error, let's loop through the project folders and see if any are SDF Projects before complaining
			sdf_projects = []
			sdf_project_data = {}
			project_data = sublime.active_window().project_data()

			if project_data is None:
				sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": False})
				view = sublime.Window.new_file( sublime.active_window() )
				output = ["You must be in a NetSuite SDF Project.", "You can do this by having a file open from an existing project or having one or more SDF Projects in your folder list on the right."]
				view.run_command("insert", {"characters": "\n".join(output)})
				return False
			else:
				for folder in project_data['folders']:

					folder_path = folder['path']

					if folder['path'].find( Settings.path_var ) != 0:
						folder_path = root_folder + folder['path']

					for file in os.listdir( folder_path ):
						if file.endswith(".sdf") or file == '.sdf':
							project_folder_key = folder['path'].rfind('/') + 1
							project_name = folder['path'][ project_folder_key:]

							if (project_name in sdf_project_data) == False:
								sdf_projects.append( [ project_name, folder['path'] ] );
								sdf_project_data[ project_name ] = True
							break
				

			def select_project( user_command ):
				if user_command == -1:
					return False
				else:
					current_file = sdf_projects[ user_command ][1] + Settings.path_var + 'not_a_file.not_a_file' # This may or may not be a file, but that's ok, next step is to look for the sdf file
					if current_file.find( Settings.path_var ) != 0:
						current_file = root_folder + current_file

					Settings.get_environment( current_file, executeCallback )

			if len( sdf_projects ) == 0:
				# There are no active SDF Projects, now the warning
				view = sublime.Window.new_file( sublime.active_window() )
				output = ["You must be in a NetSuite SDF Project.", "You can do this by having a file open from an existing project or having one or more SDF Projects in your folder list on the right."]
				view.run_command("insert", {"characters": "\n".join(output)})
				return False
			elif len( sdf_projects ) == 1:
				# There is one active SDF Projects, we can safely assume we'll use this one
				current_file = sdf_projects[0][1] + Settings.path_var + '.sdf' # This may or may not be a file, but that's ok, next step is to look for the sdf file
				if current_file.index('/') > 0:
					# We are checking to see if this is a relative or absolute path. If relative, make absolute
					current_file = root_folder + current_file

				Settings.get_environment( current_file, executeCallback )
			else:
				# There are several active SDF Projects, the user needs to pick one
				sublime.active_window().show_quick_panel( sdf_projects, select_project )

		else:
			current_file = sublime.active_window().active_view().file_name()
			Settings.get_environment( current_file, executeCallback )

	def get_environment( currentFile, executeCallback, justVerify = False ):

		parent_location = currentFile.rfind( Settings.path_var )

		if os.path.isfile( currentFile ):
			Settings.selected_file_path = currentFile[:parent_location]
			Settings.selected_file = currentFile[parent_location + 1:]

		Settings.project_folder = currentFile[:parent_location]

		depth_allow = 10
		current_depth = 0
		sdf_file = ""
		sdf_files = []
		env_list = []
		while True:
			if Settings.project_folder != "":
				if currentFile.endswith('.sdf'):
					sdf_file = currentFile
				else:
					for file in os.listdir( Settings.project_folder ):
						if file.endswith(".sdf"):
							sdf_file = Settings.project_folder + "/" + file
							break

			if os.path.isfile( sdf_file ):
				if os.path.isfile( Settings.project_folder + "/manifest.xml" ):
					break
				else:
					manifest_file = open( Settings.project_folder + "/manifest.xml","w+" )
					project_name = Settings.project_folder[ Settings.project_folder.rfind( Settings.path_var ) + 1 : ]
					manifest_file.write("<manifest projecttype=\"ACCOUNTCUSTOMIZATION\">\n  <projectname>" + project_name + "</projectname>\n  <frameworkversion>1.0</frameworkversion>\n</manifest>")
					manifest_file.close()
					break

			if ( current_depth > depth_allow or Settings.project_folder == "" or len(Settings.project_folder) == 2 ):
				if justVerify == False and executeCallback != False:
					view = sublime.Window.new_file( sublime.active_window() )
					output = ["Either you are not in a file that exists in an SDF project or you have not created an .sdf file","Make sure you are executing SDF from within a NetSuite project.","The following are the required lines in your .sdf file, this should be saved in the root folder of your SDF project: ","------------------------","account=","email=","role=(ID of an SDF Enabled Role)","url=","------------------------"]
					view.run_command("insert", {"characters": "\n".join(output)})

				return False

			# Set the project folder to the next level
			parent_location = Settings.project_folder.rfind( Settings.path_var )
			Settings.project_folder = currentFile[:parent_location]

			current_depth = current_depth + 1

		if justVerify and executeCallback == False:
			return True


		# Check SDF Files, if there is only one, then we just move on (unless we are calling from an .sdf file)
		if currentFile.endswith('.sdf') == False:
			for file in os.listdir( Settings.project_folder ):
				if file.endswith(".sdf"):
					environment = file.replace('.sdf', "").replace('.', '').capitalize()
					if environment == "":
						environment = "Default"
					project_start = Settings.project_folder.rfind( Settings.path_var )
					project = Settings.project_folder[project_start + 1:]
					project_location = Settings.project_folder.replace(project, "")

					env_list.append( [ environment, "Environment File: " + file, "Project: " + project, "Project Location: " + project_location ] )
					sdf_files.append( file )

		def set_account_info( sdfFile ):
			temp_account_info = {}
			current_account = ""

			for line in open( sdfFile ):
				data = line.split("=")
				temp_account_info[ data[0] ] = data[1].rstrip('\n')

				if data[0] == "account":
					current_account = data[1].rstrip('\n')

			Settings.active_account = current_account
			Settings.account_info[ current_account ] = temp_account_info
			account_settings = Settings.get_setting('account_data', {})

			if ( ( current_account in account_settings ) == False ) and ( ( current_account in Settings.password ) == False ):
				Settings.setpassword( executeCallback )
			elif executeCallback != False:
				executeCallback()

		def set_env_info( user_command ):
			if user_command == -1:
				return False
			else:
				sdf_file = Settings.project_folder + "/" + sdf_files[ user_command ]
				set_account_info( sdf_file )
				return True

		if ( len( env_list ) == 1 and sdf_file.endswith( '.sdf' ) ) or len( env_list ) == 0:
			if sdf_file.rfind( Settings.path_var ) < 0:
				# If we've just found the file name and not the file path
				sdf_file = Settings.project_folder + Settings.path_var + sdf_file

			set_account_info( sdf_file )
		else:
			sublime.active_window().show_quick_panel( env_list, set_env_info )