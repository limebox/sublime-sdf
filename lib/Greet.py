import urllib
from .Settings import *

class Greet():

	def display_changelog():

		current_version = Settings.get_setting("plugin_version", {})
		if current_version != plugin_version:
			changelog_url = "https://raw.githubusercontent.com/limebox/sublime-sdf/master/CHANGELOG.md"
			response = urllib.request.urlopen( download_url )
			#response = urllib.urlopen( download_url )
			changelog_info = response.read()

			view = sublime.Window.new_file( sublime.active_window() )
			view.run_command("insert", {"characters": changelog_info})