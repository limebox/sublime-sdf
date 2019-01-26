from .Commands import *
from .Config import *
from .Settings import *

# Menu Context is used to find out the context of the sidebar and if this menu item should be displayed

class Actions:

	path = ''

	def run( action, path ):
		Actions.path = path
		execute_command = getattr(Actions, action)
		Settings.get_sdf_file( execute_command, path )

	def sdf_exec_download_file():
		Commands.run( 'importfiles', Actions.path.replace( Settings.project_folder + "/FileCabinet", "" ) )

	def sdf_exec_download_object():

		Commands.run( 'update', Actions.path )	

	def sdf_exec_create_project():

		working_dir = path

		sdfFile = Actions.path + "/.sdf"
		deployFile = Actions.path + "/deploy.xml"
		manifestFile = Actions.path + "/manifest.xml"

		if ( os.path.isfile( sdfFile ) or os.path.isfile( deployFile ) or os.path.isfile( manifestFile ) ) :
			return False

		return True

	def sdf_exec_add_dependencies_to_manifest():
		Commands.run( 'adddependencies' )

	def sdf_exec_set_password():
		Commands.run( 'setpassword' )

	def sdf_exec_deploy():
		Commands.run( 'deploy' )

	def sdf_exec_import_bundle():
		Commands.run( 'importbundle' )

	def sdf_exec_import_configuration():
		Commands.run( 'importconfiguration' )

	def sdf_exec_import_file():
		Commands.run( 'importfiles' )

	def sdf_exec_import_object():
		Commands.run( 'importobjects' )

	def sdf_exec_issue_token():
		Commands.run( 'issuetoken' )

	def sdf_exec_list_bundle():
		Commands.run( 'listbundles' )

	def sdf_exec_list_files():
		Commands.run( 'listfiles' )

	def sdf_exec_list_missing_dependencies():
		Commands.run( 'listmissingdependencies' )

	def sdf_exec_list_objects():
		Commands.run( 'listobjects' )

	def sdf_exec_preview():
		Commands.run( 'preview' )

	def sdf_exec_revoke_token():
		Commands.run( 'revoketoken' )

	def sdf_exec_update():
		Commands.run( 'update' )

	def sdf_exec_update_custom_record_with_instances():
		Commands.run( 'updatecustomrecordwithinstances' )

	def sdf_exec_validate_project():
		Commands.run( 'validate' )

	def sdf_exec_clear_password():
		Commands.run( 'clearpassword' )

	def sdf_exec_set_password():
		Commands.run( 'setpassword' )