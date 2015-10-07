# coding=utf-8
from __future__ import absolute_import

import threading
import octoprint.plugin
import inotify.adapters

class PortListerPlugin(octoprint.plugin.StartupPlugin):
	def on_after_startup(self):
		self._logger.info("Port Lister")
		self.dev_watcher_thread = threading.Thread(target=self._watcher, name="portlisterwatcher")
		self.dev_watcher_thread.daemon = True
		self.dev_watcher_thread.start()

	def _watcher(self):
		i = inotify.adapters.Inotify(block_duration_s=30)
		i.add_watch('/dev', mask=(inotify.constants.IN_DELETE | inotify.constants.IN_CREATE))
		try:
			for event in i.event_gen():
				if event is not None:
					(header, type_names, watch_path, filename) = event
					self._logger.info("WD=(%d) MASK=(%d) COOKIE=(%d) LEN=(%d) MASK->NAMES=%s "
                             "WATCH-PATH=[%s] FILENAME=[%s]",
                             header.wd, header.mask, header.cookie, header.len, type_names,
                             watch_path, filename)
		finally:
			i.remove_watch('/dev')

__plugin_name__ = "PortLister"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = PortListerPlugin()

	# global __plugin_hooks__
	# __plugin_hooks__ = {
	#    "some.octoprint.hook": __plugin_implementation__.some_hook_handler
	# }

