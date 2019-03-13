import sys, sublime_plugin, sublime, os, json #, re, , 
from imp import reload

reload_mods = [mod for mod in sys.modules if mod[0:17] == "NetSuite SDF.lib." and sys.modules[mod] is not None]

for mod in reload_mods:
	reload( sys.modules[ mod ] )

from .lib.Commands import *
from .lib.Settings import *
from .lib.MenuContext import *
from .lib.Actions import *
from .lib.Greet import *

def plugin_loaded():
	Greet.display_changelog()
	Settings.show_sdf()
	Settings.check_version()

class SdfExecOpen(sublime_plugin.TextCommand):

	temp_password = ""

	def is_visible( self, paths = [] ):
		if len( paths ) > 0:
			path = paths[ 0 ]
			return MenuContext.isSdfProject( path )
		else:
			return False

	def run(self, edit, **args):

		def execute_command():
			Commands.run()

		Settings.get_sdf_file( execute_command )

class SdfExecViewInsertCommand(sublime_plugin.TextCommand):
	def run(self, edit, pos, text):
		self.view.insert(edit, pos, text)

class SdfExecMenu(sublime_plugin.WindowCommand):

	def is_visible( self, paths = [] ):
		if len( paths ) > 0:
			path = paths[ 0 ]
			return MenuContext.isSdfProject( path )
		else:
			return False

class SdfExecNotSdfProject(sublime_plugin.WindowCommand):
	def is_visible( self, paths = [], submenu = "False" ):
		if len( paths ) > 0:
			path = paths[ 0 ]
		else:
			return False

		if MenuContext.isVisible( 'Test', path ):
			return False
		else:
			if os.path.isdir( path ) and len(os.listdir( path ) ) == 0 and submenu == "False":
				return False
			else:
				return True

	def is_enabled( self, paths = [] ):
		return False

class SdfExecIsSdfProject(sublime_plugin.WindowCommand):
	def is_visible( self, paths = [] ):
		if len( paths ) > 0:
			path = paths[ 0 ]
			return MenuContext.isVisible( 'Test', path )
		else:
			return False


class SdfExecActions(sublime_plugin.WindowCommand):

	def is_visible( self, action, paths = [] ):
		if len( paths ) > 0:
			path = paths[ 0 ]
			return MenuContext.isVisible( action, path )
		else:
			return False

	def run( self, action, paths = [], **args ):
		if len( paths ) > 0:
			path = paths[ 0 ]
			Actions.run( action, path )
			return True
		else:
			return False