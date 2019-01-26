# The project module handles non-SDF interactions with the project.

import os
from .Settings import *

class Project:

	def addToDeploy( file ):

		deploy_file_path = Settings.project_folder + Settings.path_var + "deploy.xml"

		deploy_file = open( deploy_file_path , "r")
		contents = deploy_file.readlines()
		deploy_file.close()

		relative_path = file.replace( Settings.project_folder, "" )
		file_line = "        <path>~" + relative_path + "</path>\n"

		tofind = [ "<files>", "</files>" ]
		if relative_path.startswith('/Objects/'):
			tofind = [ "<objects>", "</objects>" ]
		elif relative_path.startswith('/AccountConfiguration/'):
			tofind = [ "<configuration>", "</configuration>" ]

		insert_line = 0
		line_number = 0
		already_exists = False
		for line in contents:
			if tofind[ 1 ] in line:
				insert_line = line_number
			elif relative_path in line:
				already_exists = True
			else:
				line_number = line_number + 1

		if already_exists == False:
			# Well, if this already exists in the deploy file, we don't want to do anything
			if line_number == len( contents ):
				# This deploy file does not have the object we are looking for
				file_line = "    " + tofind[ 0 ] + "\n" + file_line + "    " + tofind[ 1 ] + "\n"
				insert_line = line_number - 1

			contents.insert(insert_line, file_line)

			deploy_file = open( deploy_file_path, "w")
			contents = "".join(contents)
			deploy_file.write(contents)
			deploy_file.close()

	def resetDeploy():

		are_you_sure = []
		are_you_sure.append( ["Yes, I really want to reset my deploy.xml", "I understand this will erase deploy.xml back to the Sublime default", "I accept this responsibility"] )
		are_you_sure.append( ["No, I do not want to reset my deploy.xml", "I don't know what I was thinking", "I should probably make sure my project is backed up"] )

		def accept_consequence( user_command ):

			if user_command == 0:

				account_cconfiguration_temp_file = Settings.project_folder + Settings.path_var + 'AccountConfiguration' + Settings.path_var + "Temp"
				objects_temp_file = Settings.project_folder + Settings.path_var + 'Objects' + Settings.path_var + "Temp"
				scripts_temp_file = Settings.project_folder + Settings.path_var + 'FileCabinet' + Settings.path_var + "SuiteScripts" + Settings.path_var + "sdf_ignore"
				deploy_file_path = Settings.project_folder + Settings.path_var + "deploy.xml"

				access_rights = 0o755

				contents = []
				contents.append( "<deploy>\n" )
				contents.append( "    <configuration>\n" )
				contents.append( "        <!-- This is using a Temp folder for the wildcard, Instead of a wildcard, add a new line for each Customization outside of the Temp folder. -->\n")
				contents.append( "        <path>~/AccountConfiguration/Temp/*</path>\n" )
				contents.append( "    </configuration>\n" )
				contents.append( "    <files>\n" )
				contents.append( "        <!-- This is a dummy script file. Instead of a wildcard, add a new line for each File. A better explanation is in this file -->\n")
				contents.append( "        <path>~/FileCabinet/sdf_ignore</path>\n" )
				contents.append( "    </files>\n" )
				contents.append( "    <objects>\n" )
				contents.append( "        <!-- This is using a Temp folder for the wildcard, Instead of a wildcard, add a new line for each Object outside of the Temp folder. -->\n")
				contents.append( "        <path>~/Objects/Temp/*</path>\n" )
				contents.append( "    </objects>\n" )
				contents.append( "</deploy>" )

				deploy_file = open( deploy_file_path, "w")
				contents = "".join(contents)
				deploy_file.write(contents)
				deploy_file.close()

				try:
					if os.path.isdir( account_cconfiguration_temp_file ) == False:
						os.mkdir( account_cconfiguration_temp_file, access_rights )
				except OSError:
					print( "Could not create directory %, Sublime may not have permission.", account_cconfiguration_temp_file )

				try:
					if os.path.isdir( objects_temp_file ) == False:
						os.mkdir( objects_temp_file, access_rights )
				except OSError:
					print( "Could not create directory %, Sublime may not have permission.", objects_temp_file )

				script_ignore_file = open( scripts_temp_file, "w")
				contents = "What is this file? I'm glad you asked.\n\nNetSuite SDF uses the deploy.xml file to tell your project which files and objects you want to promote.\nWhile SDF does a decent job determining what files changed, you rarely want to use a wildcard ( this -> *) to tell SDF what to check.\nBut if we ommit an object block in the deploy.xml (i.e. <objects>), the deploy validation complains that we are missing something.\nThe solution here is to point each object block to a real empty folder or file that you don't touch, like this one.\nThen, as you update files and objects, only add the those specifically to the deploy.xml file.\nThis can be done manually by adding the files between <path></path> tags and preceded by ~/SuiteScripts, ~/Objects, or ~/AccountConfiguration.\nIf you use the Sublime NetSuite SDF plugin, you can right click on the file or object you want to add to the deploy.xml file and select \"Add To deploy.xml\"\n\nIn any case, we hope this makes your development experience easier!\n\n\n\nHappy coding!\n\nLimebox Team\nhttp://limebox.com"
				script_ignore_file.write(contents)
				script_ignore_file.close()

		sublime.active_window().show_quick_panel(are_you_sure, accept_consequence)