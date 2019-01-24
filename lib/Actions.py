from .Commands import *
from .Config import *

# Menu Context is used to find out the context of the sidebar and if this menu item should be displayed

class Actions:

	thisSelf = None
	thisView = None

	# 
	# sdf_exec_deploy
	# sdf_exec_import_bundle
	# sdf_exec_import_configuration
	# sdf_exec_import_file
	# sdf_exec_import_object
	# sdf_exec_issue_token
	# sdf_exec_list_bundle
	# sdf_exec_list_files
	# sdf_exec_list_missing_dependencies
	# sdf_exec_list_objects
	# sdf_exec_preview
	# sdf_exec_revoke_token
	# sdf_exec_update
	# sdf_exec_update_custom_record_with_instances
	# sdf_exec_validate_project
	# sdf_exec_clear_password

	# 
	# deploy
	# importbundle
	# importconfiguration
	# importfiles
	# importobjects
	# issuetoken
	# listbundles
	# listfiles
	# listmissingdependencies
	# listobjects
	# preview
	# revoketoken
	# update
	# updatecustomrecordwithinstances
	# validate

	def run( this, view, action, path ):

		Actions.thisSelf = this
		Actions.thisView = view

		Settings.get_sdf_file( False, path )
		getattr(Actions, action)()


	def isSdfProject( path ):
		return False

	def downloadFile( path ):

		if ( "FileCabinet" in path and (".attributes" in path) == False and os.path.isfile( path ) ) :
			return True

		return False

	def downloadObject( path ):

		if ( "Objects" in path and ".xml" in path and os.path.isfile( path ) ) :
			return True

		return False		

	def sdf_exec_create_project( path ):

		working_dir = path

		sdfFile = working_dir + "/.sdf"
		deployFile = working_dir + "/deploy.xml"
		manifestFile = working_dir + "/manifest.xml"

		if ( os.path.isfile( sdfFile ) or os.path.isfile( deployFile ) or os.path.isfile( manifestFile ) ) :
			return False

		return True

	def sdf_exec_update_manifest():
		Commands.run( Actions.thisSelf, Actions.thisView, 'adddependencies' )

	def sdf_exec_add_dependencies_to_manifest():
		Commands.run( Actions.thisSelf, Actions.thisView, 'adddependencies' )

		