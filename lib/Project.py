# The project module handles non-SDF interactions with the project.

import urllib
import zipfile
import os
from .Settings import *

class Project:

	def inDeployFile( file ):

		deploy_file_path = Settings.project_folder + Settings.path_var + "deploy.xml"

		deploy_file = open( deploy_file_path , "r")
		contents = deploy_file.readlines()
		deploy_file.close()

		relative_path = file.replace( Settings.project_folder, "" )

		already_exists = False
		for line in contents:
			if relative_path in line:
				already_exists = True

		return already_exists
		

	# Check if the requested file meets the standards for being deployable
	def isDeployable( file ):

		is_deployable_folder = False
		is_deployable_file = False
		deployable_folders = [ 'Objects', 'FileCabinet', 'AccountConfiguration']
		deployable_files = ['js','xml','html','jpeg','png','pdf','jpg','css']

		for folder in deployable_folders:
			if file.startswith( Settings.path_var + folder + Settings.path_var ):
				is_deployable_folder = True
				break

		if is_deployable_folder:
			for filetype in deployable_files:
				if file.endswith('.' + filetype):
					is_deployable_file = True

		return is_deployable_file

	def removeFromDeploy( file ):

		sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": False})

		print("Attempting to remove " + file + " from deploy.xml")

		deploy_file_path = Settings.project_folder + Settings.path_var + "deploy.xml"

		deploy_file = open( deploy_file_path , "r")
		contents = deploy_file.readlines()
		deploy_file.close()

		relative_path = file.replace( Settings.project_folder, "" )

		new_contents = []
		for line in contents:
			if ( relative_path in line ) == False:
				new_contents.append( line )

		deploy_file = open( deploy_file_path, "w")
		new_contents = "".join(new_contents)
		deploy_file.write(new_contents)
		deploy_file.close()

		print("Removed from deploy.xml")
		sublime.active_window().open_file( deploy_file_path )


	def addToDeploy( file ):

		sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": False})

		print("Attempting to add " + file + " to deploy.xml")

		deploy_file_path = Settings.project_folder + Settings.path_var + "deploy.xml"

		deploy_file = open( deploy_file_path , "r")
		contents = deploy_file.readlines()
		deploy_file.close()

		relative_path = file.replace( Settings.project_folder, "" )
		file_line = "        <path>~" + relative_path + "</path>\n"

		if relative_path.startswith( Settings.path_var + 'Objects' + Settings.path_var ):
			tofind = [ "<objects>", "</objects>" ]
		elif relative_path.startswith( Settings.path_var + 'AccountConfiguration' + Settings.path_var ):
			tofind = [ "<configuration>", "</configuration>" ]
		else:
			tofind = [ "<files>", "</files>" ]

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

			print("Added to deploy.xml")
			sublime.active_window().open_file( deploy_file_path )
		else:
			print("Object already exists in deploy.xml, ignoring")

	def resetDeploy():

		sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": False})

		print("Resetting deploy.xml on your command")

		are_you_sure = []
		are_you_sure.append( ["Yes, I really want to reset my deploy.xml", "I understand this will erase deploy.xml back to the Sublime default", "I accept this responsibility"] )
		are_you_sure.append( ["No, I do not want to reset my deploy.xml", "I don't know what I was thinking", "I should probably make sure my project is backed up"] )

		def accept_consequence( user_command ):

			if user_command == 0:

				print("")
				print("Accepting Consequence, resetting deploy.xml")

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
				contents.append( "        <path>~/FileCabinet/SuiteScripts/sdf_ignore</path>\n" )
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

				print("Complete")
				sublime.active_window().open_file( deploy_file_path )

		sublime.active_window().show_quick_panel(are_you_sure, accept_consequence)

	def importFramework():

		sublime.active_window().run_command('show_panel', {"panel": "console", "toggle": False})

		# Thank you user714415 for an easy start to a Python zip downloader and unzipper: https://stackoverflow.com/q/5710867/4439020

		# Create a temporary download folder
		download_folder = "TMP_framework_download"
		extracted_folder = "TMP_framework_exctacted"
		if not os.path.isdir( Settings.project_folder + Settings.path_var + download_folder ):
			os.makedirs( Settings.project_folder + Settings.path_var + download_folder )
		# if not os.path.isdir( Settings.project_folder + Settings.path_var + extracted_folder ):
		# 	os.makedirs( Settings.project_folder + Settings.path_var + extracted_folder )

		download_url = "https://github.com/limebox/framework/archive/master.zip"
		output_filename = Settings.project_folder + Settings.path_var + download_folder + Settings.path_var + "framework.zip"

		print("Downloading Limebox Framework from https://github.com/limebox/framework")

		response = urllib.request.urlopen( download_url )
		#response = urllib.urlopen( download_url )
		zipped_data = response.read()

		# save data to disk
		output = open(output_filename,'wb')
		output.write(zipped_data)
		output.close()

		# extract the data
		zfobj = zipfile.ZipFile(output_filename)
		for name in zfobj.namelist():
			uncompressed = zfobj.read(name)

			check_name = name.replace('framework-master', '')

			if check_name.startswith( Settings.path_var + 'FileCabinet' + Settings.path_var + 'SuiteScripts' ) and os.path.isfile( Settings.project_folder + check_name ) == False:
				save_file = Settings.project_folder + check_name

				if check_name.endswith( Settings.path_var ):
					 if os.path.isdir( save_file ) == False:
					 	os.makedirs( save_file )
				else:
					output = open(save_file,'wb')
					output.write(uncompressed)
					output.close()

		os.remove( Settings.project_folder + Settings.path_var + download_folder + Settings.path_var + "framework.zip" )
		os.rmdir( Settings.project_folder + Settings.path_var + download_folder )

		print( "Successfully installed the Limebox Framework. See the restlet in " + Settings.path_var + "FileCabinet" + Settings.path_var + "SuiteScripts" + Settings.path_var + "Restlet" + Settings.path_var + "GetCustomer.js for a general overview of how the framework works. You can also review at https://limebox.com/developers/framework." )