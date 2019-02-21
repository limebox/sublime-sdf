import urllib
from .Settings import *

class Greet():

	def display_changelog():

		current_version = Settings.get_setting("plugin_version", {})
		if current_version != Settings.plugin_version:

			changelog_url = "https://raw.githubusercontent.com/limebox/sublime-sdf/master/CHANGELOG.md"
			response = urllib.request.urlopen( changelog_url )
			changelog_info = response.read().decode("utf-8")

			view = sublime.Window.new_file( sublime.active_window() )
			view.run_command("insert", {"characters": changelog_info})
			Settings.set_setting("plugin_version", Settings.plugin_version)