# coding=utf-8
from __future__ import absolute_import

from threading import Timer
import watchdog
from watchdog.observers import Observer

import octoprint.plugin
from octoprint.printer import get_connection_options

class PortListEventHandler(watchdog.events.FileSystemEventHandler):
	def __init__(self, parent):
		self._parent = parent

	def on_created(self, event):
		if not event.is_directory:
			self._parent.on_port_created(event.src_path)

class PortListerPlugin(octoprint.plugin.StartupPlugin, octoprint.plugin.AssetPlugin, octoprint.plugin.SettingsPlugin):
	def on_after_startup(self, *args, **kwargs):
		self._logger.info("Port Lister %s %s", repr(args), repr(kwargs))
		event_handler = PortListEventHandler(self)
		self._observer = Observer()
		self._observer.schedule(event_handler, "/dev", recursive=False)
		self._observer.start()

	def on_port_created(self, port, *args, **kwargs):
		# if we're already connected ignore it
		if self._printer.is_closed_or_error():
			connection_options = get_connection_options()
			self._logger.info("on_port_created connection_options %s", repr(connection_options))

			# is the new device in the port list? yes, tell the view model
			if port in connection_options["ports"]:
				self._plugin_manager.send_plugin_message(self._plugin_name, port)

				# if autoconnect and the new port matches, try to connect
				if self._settings.global_get_boolean(["serial", "autoconnect"]):
					self._logger.info("autoconnect_delay %d", self._settings.get(["autoconnect_delay"]))
					Timer(self._settings.get(["autoconnect_delay"]), self.do_auto_connect, [port]).start()

	def on_shutdown(self, *args, **kwargs):
		self._logger.info("Shutting down file system observer")
		self._observer.stop();
		self._observer.join()

	def do_auto_connect(self, port, *args, **kwargs):
		(autoport, baudrate) = self._settings.global_get(["serial", "port"]), self._settings.global_get_int(["serial", "baudrate"])
		if autoport == port or autoport == "AUTO":
			printer_profile = self._printer_profile_manager.get_default()
			profile = printer_profile["id"] if "id" in printer_profile else "_default"
			self._logger.info("Attempting to connect to %s at %d with profile %s", autoport, baudrate, repr(profile))
			self._printer.connect(port=autoport, baudrate=baudrate, profile=profile)

	def get_settings_defaults(self, *args, **kwargs):
		return dict(autoconnect_delay=20)

	def get_assets(self, *args, **kwargs):
		return dict(js=["js/portlister.js"])

__plugin_name__ = "PortLister"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = PortListerPlugin()

	# global __plugin_hooks__
	# __plugin_hooks__ = {
	#    "some.octoprint.hook": __plugin_implementation__.some_hook_handler
	# }

