import sublime

class Output:

	def parse_output(args, command, console_stdout, custom_object, has_error, return_result=False):
		sdf_command_do_gui_instance = sublime.active_window()
		if return_result == True:
			output = []
		else:
			output = ""

		if has_error:
			for line in console_stdout.splitlines():
				if line.find("[INFO]") < 0:
					output += line + "\n"
		elif command == "listfiles":
			if return_result == True:
				output.append( "All" + "\n" )

			for line in console_stdout.splitlines():
				if line.find('/SuiteScripts') >= 0:
					if return_result == True:
						output.append( line.replace("Enter password:", "") + "\n" )
					else:
						output += line.replace("Enter password:", "") + "\n" # Since "Enter password:" doesn't create a new line, remove it
		elif command == "listbundles":
			for line in console_stdout.splitlines():
				if line[:2].isdigit() or line.find("Enter password:") >= 0:
					if return_result == True:
						output.append( line.replace("Enter password:", "") + "\n" )
					else:
						output += line.replace("Enter password:", "") + "\n" # Since "Enter password:" doesn't create a new line, remove it
		elif command == "listmissingdependencies":
			print_line = False
			for line in console_stdout.splitlines():
				if line.find("[INFO]") >= 0:
					print_line = False
				if print_line:
					output += line + "\n"
				if line.find("Unresolved dependencies:") >= 0:
					print_line = True

			if output.replace("\n", "") == "":
				output = "No unresolved dependencies"
		elif command == "listobjects":
			if return_result == True:
				output.append( "All" + "\n" )

			for line in console_stdout.splitlines():
				if line.find("Enter password:") >= 0:
					if return_result == True:
						output.append( line.replace("Enter password:", "").replace(custom_object[1] + ":", "") + "\n" )
					else:
						output += line.replace("Enter password:", "").replace(custom_object[1] + ":", "") + "\n" # Since "Enter password:" doesn't create a new line, remove it
				elif line.find(custom_object[1]) >= 0:
					if return_result == True:
						output.append( line.replace("Enter password:", "").replace(custom_object[1] + ":", "") + "\n" )
					else:
						output += line.replace("Enter password:", "").replace(custom_object[1] + ":", "") + "\n" # Since "Enter password:" doesn't create a new line, remove it
		elif command == "preview" or command == "validate":
			print_line = False
			for line in console_stdout.splitlines():
				if line.find("[INFO]") < 0:
					output += line.replace("Enter password:", "") + "\n"

		if return_result == True:
			return output
		elif has_error or command == "listfiles" or command == "listbundles" or command == "listmissingdependencies" or command == "listobjects" or command == "preview" or command == "validate":
			view = sublime.Window.new_file( sdf_command_do_gui_instance )
			view.run_command("insert", {"characters": output})