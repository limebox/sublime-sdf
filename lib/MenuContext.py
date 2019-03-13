import sublime, os

from .Settings import *
from .Project import *

# Menu Context is used to find out the context of the sidebar and if this menu item should be displayed

class MenuContext:

	def isVisible( action, path ):

		if MenuContext.isSdfProject( path ):
			return getattr(MenuContext, action)( path )
		else:
			if action == "sdf_exec_create_project":
				return MenuContext.sdf_exec_create_project( path )
			else:
				return False

	def isSdfProject( path ):
		return Settings.get_sdf_file( False, path )

	def Test( path ):
		return True

	def sdf_exec_reset_deploy( path ):
		relative_path = path.replace( Settings.project_folder, "" )
		if relative_path == Settings.path_var + 'deploy.xml':
			return True
		else:
			return False

	def sdf_exec_install_framework( path ):
		relative_path = path.replace( Settings.project_folder, "" )
		if relative_path.startswith( Settings.path_var + 'FileCabinet' + Settings.path_var + 'SuiteScripts' ):
			return True

		return False

	def sdf_exec_remove_from_deploy( path ):
		# I don't know, let's just OR the heck out of this
		relative_path = path.replace( Settings.project_folder, "" )
		if ( Project.inDeployFile( relative_path ) ):
			return True

		return False

	def sdf_exec_add_to_deploy( path ):
		# I don't know, let's just OR the heck out of this
		relative_path = path.replace( Settings.project_folder, "" )
		if ( Project.inDeployFile( relative_path ) == False and Project.isDeployable( relative_path ) ):
			return True

		return False

	def sdf_exec_download_file( path ):

		if ( "FileCabinet/SuiteScripts" in path and (".attributes" in path) == False and os.path.isfile( path ) ) :
			return True

		return False

	def sdf_exec_download_object( path ):

		if ( "Objects" in path and ".xml" in path and os.path.isfile( path ) ) :
			return True

		return False		

	def sdf_exec_create_project( path ):

		try:
			if ( os.path.isfile( path ) or len(os.listdir( path ) ) > 0 ) :
				return False
		except:
			return False

		return True

	def sdf_exec_update_manifest( path ):

		if path.endswith('manifest.xml'):
			return True
		else:
			return False

	def sdf_exec_add_dependencies_to_manifest( path ):
		# Always show in an SDF Project
		return True

	def sdf_exec_deploy( path ):
		# Always show in an SDF Prj
		return True

	def sdf_exec_import_bundle( path ):
		return True

	def sdf_exec_import_configuration( path ):
		return True

	def sdf_exec_import_file( path ):
		return True

	def sdf_exec_import_object( path ):
		return True

	def sdf_exec_list_bundle( path ):
		return True

	def sdf_exec_list_files( path ):
		return True

	def sdf_exec_list_missing_dependencies( path ):
		return True

	def sdf_exec_list_objects( path ):
		return True

	def sdf_exec_preview( path ):
		return True

	def sdf_exec_update( path ):
		return True

	def sdf_exec_update_custom_record_with_instances( path ):
		return True

	def sdf_exec_validate_project( path ):
		return True

	def sdf_exec_issue_token( path ):
		if path.endswith('.sdf'):
			temp_account_info = {}
			for line in open( path ):
				data = line.split("=")
				temp_account_info[ data[0] ] = data[1].rstrip('\n')

			account_settings = Settings.get_setting('account_data', {})

			if temp_account_info[ "account" ] in account_settings:
				return False
			else:
				return True
		else:
			return False

	def sdf_exec_save_token( path ):

		cli_version = Settings.set_setting("cli_version")

		if cli_version == "2018.2.0":
			return False

		if path.endswith('.sdf'):
			temp_account_info = {}
			for line in open( path ):
				data = line.split("=")
				temp_account_info[ data[0] ] = data[1].rstrip('\n')

			account_settings = Settings.get_setting('account_data', {})

			if temp_account_info[ "account" ] in account_settings:
				return False
			else:
				return True
		else:
			return False

	def sdf_exec_revoke_token( path ):
		if path.endswith('.sdf'):
			temp_account_info = {}
			for line in open( path ):
				data = line.split("=")
				temp_account_info[ data[0] ] = data[1].rstrip('\n')

			account_settings = Settings.get_setting('account_data', {})

			if temp_account_info[ "account" ] in account_settings:
				return True
			else:
				return False
		else:
			return False

	def sdf_exec_set_password( path ):
		if path.endswith('.sdf'):
			temp_account_info = {}
			for line in open( path ):
				data = line.split("=")
				temp_account_info[ data[0] ] = data[1].rstrip('\n')

			account_settings = Settings.get_setting('account_data', {})

			if temp_account_info[ "account" ] in account_settings:
				return False
			elif temp_account_info[ "account" ] in Settings.password:
				return False
			else:
				return True
		else:
			return False

	def sdf_exec_clear_password( path ):
		if path.endswith('.sdf'):
			temp_account_info = {}
			for line in open( path ):
				data = line.split("=")
				temp_account_info[ data[0] ] = data[1].rstrip('\n')

			account_settings = Settings.get_setting('account_data', {})

			if temp_account_info[ "account" ] in account_settings:
				return False
			elif temp_account_info[ "account" ] in Settings.password:
				return True
			else:
				return False
		else:
			return False