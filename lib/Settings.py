import sublime, os

class Settings:
	account_info = {}
	password = {}
	sdfcli_ext = ""
	project_folder = ""
	active_account = ""

	def get_setting(config, args, force_default=False):
		if (not force_default) and args.get(config):
			return args[config]

		settings = sublime.load_settings('Preferences.sublime-settings')
		if settings.get('sdf_exec_' + config):
			return settings.get('sdf_exec_' + config)
		else:
			settings = sublime.load_settings('SublimeSdf.sublime-settings')
			return settings.get('sdf_exec_' + config)

	def get_sdf_file( execute_command ):
		if sublime.active_window().active_view().file_name():
			current_file = sublime.active_window().active_view().file_name()

			if os.name == 'nt':
				path_var = "\\"
				Settings.sdfcli_ext = ".bat"
			else:
				path_var = "/"
				Settings.sdfcli_ext = ""

			parent_location = current_file.rfind( path_var )
			Settings.project_folder = current_file[:parent_location]

			depth_allow = 10
			current_depth = 0
			sdfFile = ""

			while True:
				print( Settings.project_folder )
				for file in os.listdir( Settings.project_folder ):
					print( file )
					if file.endswith(".sdf"):
						sdfFile = Settings.project_folder + "/" + file
						break

				if os.path.isfile( sdfFile ):
					if os.path.isfile( Settings.project_folder + "/manifest.xml" ):
						break
					else:
						manifest_file = open( Settings.project_folder + "/manifest.xml","w+" )
						project_name = Settings.project_folder[ Settings.project_folder.rfind( path_var ) + 1 : ]
						manifest_file.write("<manifest projecttype=\"ACCOUNTCUSTOMIZATION\">\n  <projectname>" + project_name + "</projectname>\n  <frameworkversion>1.0</frameworkversion>\n</manifest>")
						manifest_file.close()
						break

				if current_depth > depth_allow:
					view = sublime.Window.new_file( sublime.active_window() )
					output = ["Either you are not in a file that exists in an SDF project or you have not created a file named .sdf","Make sure you are executing SDF from within a NetSuite project.","The following are the required lines in your .sdf file, this should be saved in the root folder of your SDF project: ","------------------------","account=","email=","role=(ID of SDF Enabled Row, traditionally role=3)","url=","------------------------"]
					view.run_command("insert", {"characters": "\n".join(output)})
					return False

				# Set the project folder to the next level
				parent_location = Settings.project_folder.rfind( path_var )
				Settings.project_folder = current_file[:parent_location]

				current_depth = current_depth + 1

			# We need to see if the user has multiple .sdf files
			print( "Check Environment" )
			os.chdir( Settings.project_folder )

			sdf_files = []
			env_list = []
			sdf_file = ""
			env_file = ""

			# Check SDF Files, if there is only one, then we just move on
			for file in os.listdir( Settings.project_folder ):
				if file == '.sdf':
					return file
				if file.endswith(".sdf"):
					env_list.append( file.replace('.sdf', "").replace('.', '').capitalize() )
					sdf_files.append( file )

			def set_file( user_command ):
				if user_command == -1:
					return False
				else:
					print( sdf_files[ user_command ] )
					os.rename( Settings.project_folder + "/" + sdf_files[ user_command ], Settings.project_folder + "/.sdf")
					env_file = sdf_files[ user_command ]
					sdfFile = Settings.project_folder + "/.sdf"

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

				execute_command( env_file )

			sublime.active_window().show_quick_panel( env_list, set_file )

		else:
			view = sublime.Window.new_file( sublime.active_window() )
			output = ["You must have a tab open connected to your NetSuite Project"]
			view.run_command("insert", {"characters": "\n".join(output)})
			return False