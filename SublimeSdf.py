import sys, sublime_plugin, sublime, os, json #, re, , 
from imp import reload

reload_mods = [mod for mod in sys.modules if mod[0:17] == "NetSuite SDF.lib." and sys.modules[mod] is not None]

for mod in reload_mods:
	reload( sys.modules[ mod ] )

from .lib.Commands import *
from .lib.Settings import *
from .lib.MenuContext import *
from .lib.Actions import *

class SdfExecOpen(sublime_plugin.TextCommand):

	temp_password = ""

	def is_visible( self, paths = [] ):
		path = paths[ 0 ]
		return MenuContext.isSdfProject( path )

	def run(self, edit, **args):

		def execute_command():
			Commands.run()

		Settings.get_sdf_file( execute_command )

class SdfExecViewInsertCommand(sublime_plugin.TextCommand):
	def run(self, edit, pos, text):
		self.view.insert(edit, pos, text)

class SdfExecMenu(sublime_plugin.WindowCommand):

	def is_visible( self, paths = [] ):
		path = paths[ 0 ]
		return MenuContext.isSdfProject( path )

class SdfExecNotSdfProject(sublime_plugin.WindowCommand):
	def is_visible( self, paths = [], submenu = "False" ):
		path = paths[ 0 ]
		if MenuContext.isVisible( 'Test', path ):
			return False
		else:
			if len(os.listdir( path ) ) == 0 and submenu == "False":
				return False
			else:
				return True

	def is_enabled( self, paths = [] ):
		return False

class SdfExecIsSdfProject(sublime_plugin.WindowCommand):
	def is_visible( self, paths = [] ):
		path = paths[ 0 ]
		return MenuContext.isVisible( 'Test', path )


class SdfExecActions(sublime_plugin.WindowCommand):

	def is_visible( self, action, paths = [] ):
		path = paths[ 0 ]
		return MenuContext.isVisible( action, path )

	def run( self, action, paths = [], **args ):
		path = paths[ 0 ]
		Actions.run( action, path )
		return True