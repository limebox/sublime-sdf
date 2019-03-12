import sublime, subprocess, math, time, os

from .Settings import *
from .Loader import *
from .Debug import *
from .Output import *

from subprocess import STDOUT
from threading import Thread

class Create:

	def folderExists( path ):
		project_data = sublime.active_window().project_data()
		project_path = sublime.active_window().extract_variables()['project_path']

		i = 0

		if project_data:
			for project_folder in project_data['folders']:
				if project_folder['path']:
					try:
						if os.path.samefile( path, project_folder['path'] ):
							return i
					except:
						if os.path.samefile( path, project_path + Settings.path_var + project_folder['path'] ):
							return i
				i = i + 1;

		return False

	def removeFolder( path, index ):
		project_data = sublime.active_window().project_data()

		folder_path = project_data['folders'][ index ]['path']

		del ( project_data['folders'][ index ])
		sublime.active_window().set_project_data( project_data )
		return folder_path

	def addFolder( path, oldIndex ):
		project_data = sublime.active_window().project_data()

		# if no project present
		if not project_data:
			project_data = {'folders': [{'path': path}] }
			sublime.active_window().set_project_data( project_data )
			return True

		project_data['folders'].insert( oldIndex, {'path': path} )
		sublime.active_window().set_project_data( project_data )

	def project( fullPath ):

		sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": False})

		folder_index = Create.folderExists( fullPath )

		if folder_index != False:
			project_path = sublime.active_window().extract_variables()['project_path']
			folder_path = Create.removeFolder( fullPath, folder_index )

			os.rename( fullPath, fullPath + "TEMPSUBLIMEFOLDER" )

		if sublime.platform() == 'windows':
			project_folder = fullPath.rfind('\\')
		else:
			project_folder = fullPath.rfind('/')

		name = fullPath[project_folder + 1:]
		path = fullPath[0:project_folder]

		console_stdout = ""

		code = 'sdfcli createproject -pd "' + path + '" -pn ' + name + " -t ACCOUNTCUSTOMIZATION"

		startupinfo = None
		if os.name == 'nt':
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

		console_command = subprocess.Popen(code,
											stdin=subprocess.PIPE,
											stdout=subprocess.PIPE,
											stderr=subprocess.STDOUT,
											shell=True,
											cwd=path,
											startupinfo=startupinfo)

		while True:
			console_command.stdin.flush()
			proc_read = console_command.stdout.readline()

			if (proc_read.find(b"could not be created") >= 0):
				console_command.kill()
				break

			if (proc_read.find(b"has been created") >= 0):
				console_command.kill()
				break

			if proc_read:
				print( proc_read.decode("utf-8").strip() )
				console_command.stdout.flush()
				console_stdout += proc_read.decode("utf-8")

		#os.rename( path + Settings.path_var + "TEMPSUBLIMEFOLDER" + name, path + Settings.path_var + name)
		os.rmdir( fullPath + "TEMPSUBLIMEFOLDER" )

		Create.addFolder( path + Settings.path_var + name, folder_index )

		sdf_file = open( path + Settings.path_var + name + Settings.path_var + ".sdf","w+" )

		sdf_file.write("account=\nemail=\nrole=\nurl=\n");
		sdf_file.close()

		sublime.active_window().open_file( path + Settings.path_var + name + Settings.path_var + ".sdf" )