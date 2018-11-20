import sys, sublime, glob, os

class Environment:
	def set_environment( projectFolder ):
		print( "Check Environment" )
		os.chdir( projectFolder )

		sdf_files = []
		env_list = []
		sdf_file = ""

		# os.path.isfile( sdf_file )
		# Check SDF Files, if there is only one, then we just move on
		for file in os.listdir( projectFolder ):
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
					os.rename( projectFolder + "/" + sdf_files[ user_command ], projectFolder + "/.sdf")
					return sdf_files[ user_command ]

		sublime.active_window().show_quick_panel( env_list, set_file )