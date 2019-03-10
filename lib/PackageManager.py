import subprocess, math, time, os

from .Loader import *
from .Settings import *
from subprocess import STDOUT
from threading import Thread

class PackageManager:

	threads = []
	current_thread = -1
	Settings = None

	def __init__(self):
		self.output_file = None
		self.panel_output = None

	def isVisible( action ):

		sdk_options = Settings.get_setting('sdk_options', {});

		if sdk_options == '':
			# If these weren't set, then you are on a non-Windows / non-Mac machine
			return False


		if Loader.loader_thread.ident == None:
			Loader.loader_thread.start()

		#t = Thread(target=PackageManager.execute_cli, args=(  ))
		#t.start()

	def checkSDKVersions():


	def setOptions():
		sdk_options = Settings.get_setting('sdk_options', {});

		if os.name == 'nt':
			sdk_options.manager = "choco"
			sdk_options.help = "-?"
			sdk_options.ver
		elif os.name == 'posix':
			sdk_options.manager = "brew"
		else:
			# This won't work on non-Windows / non-Mac machines
			return False

		t = Thread(target=PackageManager.execute_cli, args=( sdk_options.manager,  ))
		t.start()

	def execute_cli( command ):

		console_stdout = ""
		startupinfo = None

		if os.name == 'nt':
			startupinfo = subprocess.STARTUPINFO()
			startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

		console_command = subprocess.Popen(command,
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