import sys, sublime
from .Settings import *

class Debug:
	def new_output_file(args, pure_command):

		output_file = sublime.active_window().new_file()
		output_file.set_name(pure_command[0:60])
		output_file.set_scratch(True)

		if Settings.get_setting('output_syntax', args):
			if Settings.get_setting('debug', args):
				print('set output syntax: ' + Settings.get_setting('output_syntax', args))

			if sublime.find_resources(Settings.get_setting('output_syntax', args) + '.tmLanguage'):
				output_file.set_syntax_file(sublime.find_resources(Settings.get_setting('output_syntax', args) + '.tmLanguage')[0])

		if Settings.get_setting('output_word_wrap', args):
			output_file.settings().set('word_wrap', True)
		else:
			output_file.settings().set('word_wrap', False)

		return output_file

	def increment_output(self, value, args, pure_command):
		if Settings.get_setting('output', args) == "file":
			if not self.output_file:
				self.output_file = Debug.new_output_file(args, pure_command)

			self.output_file.run_command('sdf_exec_view_insert', {'pos': self.output_file.size(), 'text': value})
		elif Settings.get_setting('output', args) == "none":
			self.panel_output = False
		else:
			if not self.panel_output:
				self.panel_output = True
				sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": False})
			sys.stdout.write(value)
