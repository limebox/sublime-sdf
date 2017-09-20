import sublime, time
from threading import Thread

class Loader:

	loading_message = ""
	show_loader = False

	def display_loader():
		loading_position=0
		loading_display=( "[= ]", "[ =]" )
		starttime = time.time()
		delay_seconds = 0.5
		while True:
			if Loader.show_loader:
				sublime.status_message( Loader.loading_message + " " + loading_display[ loading_position ] )
				loading_position = 1 if loading_position == 0 else 0
			time.sleep(delay_seconds - ((time.time() - starttime) % delay_seconds))

	loader_thread = Thread(target=display_loader)