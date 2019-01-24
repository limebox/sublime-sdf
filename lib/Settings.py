import sublime, os

class Settings:
	account_info = {}
	password = {}
	sdfcli_ext = ""
	project_folder = ""
	active_account = ""

	if os.name == 'nt':
		path_var = "\\"
		sdfcli_ext = ".bat"
	else:
		path_var = "/"
		sdfcli_ext = ""

	def get_setting(config, args, force_default=False):
		if (not force_default) and args.get(config):
			return args[config]

		settings = sublime.load_settings('Preferences.sublime-settings')
		if settings.get('sdf_exec_' + config):
			return settings.get('sdf_exec_' + config)
		else:
			settings = sublime.load_settings('SublimeSdf.sublime-settings')
			return settings.get('sdf_exec_' + config)

	def set_setting( setting, value ):
		settings = sublime.load_settings('SublimeSdf.sublime-settings')
		setattr(settings, 'sdf_exec_' + setting, value)
		sublime.save_settings('SublimeSdf.sublime-settings')

	def get_sdf_file( executeCallback, path = "" ):

		root_folder = sublime.active_window().extract_variables()[ 'project_path' ] + Settings.path_var

		if path != "":
			# This is a request from the context menu and we want to see if an SDF file even exists
			if os.path.isdir( path ):
				# If this is a directory, we want to turn it into a fake file 
				path = path + Settings.path_var + 'not_a_file.txt'

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
					current_file = sdf_projects[ user_command ][1] + Settings.path_var + '.sdf' # This may or may not be a file, but that's ok, next step is to look for the sdf file
					if current_file.find( Settings.path_var ) != 0:
						current_file = root_folder + current_file

					Settings.get_environment( current_file, executeCallback )

			if len( sdf_projects ) == 0:
				# There are no active SDF Projects, now the warning
				sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": False})
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
		Settings.project_folder = currentFile[:parent_location]

		depth_allow = 10
		current_depth = 0
		sdf_file = ""

		while True:
			if Settings.project_folder != "":
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

			if ( current_depth > depth_allow or Settings.project_folder == ""):
				if justVerify == False and executeCallback != False:
					view = sublime.Window.new_file( sublime.active_window() )
					output = ["Either you are not in a file that exists in an SDF project or you have not created an .sdf file","Make sure you are executing SDF from within a NetSuite project.","The following are the required lines in your .sdf file, this should be saved in the root folder of your SDF project: ","------------------------","account=","email=","role=(ID of an SDF Enabled Role)","url=","------------------------"]
					view.run_command("insert", {"characters": "\n".join(output)})
				return False

			# Set the project folder to the next level
			parent_location = Settings.project_folder.rfind( Settings.path_var )
			Settings.project_folder = currentFile[:parent_location]

			current_depth = current_depth + 1

		if justVerify and executeCallback != False:
			return True

		# We need to see if the user has multiple .sdf files
		os.chdir( Settings.project_folder )

		sdf_files = []
		env_list = []

		# Check SDF Files, if there is only one, then we just move on
		for file in os.listdir( Settings.project_folder ):
			if file == '.sdf':
				sdf_file = file
				break
			if file.endswith(".sdf"):
				environment = file.replace('.sdf', "").replace('.', '').capitalize()
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

			if "password" in temp_account_info:
				Settings.password[ current_account ] = temp_account_info["password"]

			if executeCallback != False:
				executeCallback()

		def set_env_info( user_command ):
			if user_command == -1:
				return False
			else:
				sdf_file = Settings.project_folder + "/" + sdf_files[ user_command ]

				set_account_info( sdf_file )

		if sdf_file == '.sdf':
			sdf_file = Settings.project_folder + "/" + sdf_file
			set_account_info( sdf_file )
		else:
			sublime.active_window().show_quick_panel( env_list, set_env_info )