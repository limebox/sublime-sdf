import subprocess, math, time

from .Settings import *
from .Loader import *
from .Debug import *
from .Output import *

from subprocess import STDOUT
from threading import Thread

class Create:

	def project( path ):

		sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": False})

		working_dir = path

		if sublime.platform() == 'windows':
			project_folder = path.rfind('\\')
		else:
			project_folder = path.rfind('/')

		name = path[project_folder + 1:]
		path = path[0:project_folder]

		console_stdout = ""

		code = "sdfcli createproject -o -pd " + path + " -pn " + name + " -t ACCOUNTCUSTOMIZATION"

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

		while True:
			console_command.stdin.flush()
			proc_read = console_command.stdout.readline()

			if (proc_read.find(b"BUILD SUCCESS") >= 0):
				console_command.kill()
				break

			if proc_read:
				print( proc_read.decode("utf-8").strip() )
				console_command.stdout.flush()
				console_stdout += proc_read.decode("utf-8")

		sdf_file = open( working_dir + "/.sdf","w+" )

		sdf_file.write("account=\nemail=\nrole=\nurl=\n");
		sdf_file.close()

		sublime.active_window().open_file( working_dir + "/.sdf" )