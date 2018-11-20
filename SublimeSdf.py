import sys, sublime_plugin, sublime, os, json #, re, , 
from imp import reload

reload_mods = [mod for mod in sys.modules if mod[0:17] == "NetSuite SDF.lib." and sys.modules[mod] is not None]

for mod in reload_mods:
	reload( sys.modules[ mod ] )

from .lib.Commands import *
from .lib.Settings import *
from .lib.Create import *


# For anyone examining my code, please forgive how unforgivably bad this is.
# I've never written in Python before, so this was also a crash course in Python
# If anyone wants to help contribute to make it better, be my guest

class SdfExecOpen(sublime_plugin.TextCommand):

	temp_password = ""

	def run(self, edit, **args):
		self.args = args

		def run_programm( user_password ):
			Settings.password[ Settings.active_account ] = SdfExecOpen.temp_password
			Commands.run(self, edit, **args)

		def get_password( user_password ):
			if( len(user_password) != len(SdfExecOpen.temp_password) ):
				if  len(user_password) < len(SdfExecOpen.temp_password):
					SdfExecOpen.temp_password = SdfExecOpen.temp_password[:len(user_password)]
				else:
					chg = user_password[len( SdfExecOpen.temp_password ):]
					SdfExecOpen.temp_password = SdfExecOpen.temp_password + chg
				stars = "*" * len(user_password)
				sublime.active_window().show_input_panel("NetSuite Password", stars, run_programm, get_password, None)

		def execute_command():
			if Settings.active_account not in Settings.password and ("password" not in Settings.account_info[ Settings.active_account ] or Settings.account_info[ Settings.active_account ][ "password" ] != ""):
				sublime.active_window().show_input_panel("NetSuite Password", "", None, get_password, None)
			else:
				Commands.run(self, edit, **args)

		Settings.get_sdf_file( execute_command )

class SdfExecViewInsertCommand(sublime_plugin.TextCommand):
	def run(self, edit, pos, text):
		self.view.insert(edit, pos, text)

class SdfExecCreateProject(sublime_plugin.WindowCommand):

	def run(self, paths = []):
		path = paths[ 0 ]

		Create.project( path )