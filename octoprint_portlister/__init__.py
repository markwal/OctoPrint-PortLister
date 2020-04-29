# coding=utf-8
from __future__ import absolute_import

import os
from threading import Timer
import watchdog
from watchdog.observers import Observer

import octoprint.plugin
from octoprint.printer import get_connection_options
from octoprint.util import get_exception_string

class PortListEventHandler(watchdog.events.FileSystemEventHandler):
	def __init__(self, parent):
		self._parent = parent

	def on_created(self, event):
		if not event.is_directory:
			self._parent.on_port_created(event.src_path)

class PortListerPlugin(octoprint.plugin.StartupPlugin, octoprint.plugin.AssetPlugin, octoprint.plugin.SettingsPlugin):
	def on_after_startup(self, *args, **kwargs):
		self._logger.info("Port Lister %s %s" % (repr(args), repr(kwargs)))
		event_handler = PortListEventHandler(self)
		self._observer = Observer()
		self._observer.schedule(event_handler, "/dev", recursive=False)
		self._observer.start()

	def on_port_created(self, port, *args, **kwargs):
		# if we're already connected ignore it
		if self._printer.is_closed_or_error():
			connection_options = get_connection_options()
			self._logger.info("on_port_created connection_options %s" % (repr(connection_options)))

			# is the new device in the port list? yes, tell the view model
			self._logger.info("Checking if %s is in %s" % (port, repr(connection_options["ports"])))
			if port in connection_options["ports"]:
				self._plugin_manager.send_plugin_message(self._plugin_name, port)

				# if autoconnect and the new port matches, try to connect
				if self._settings.global_get_boolean(["serial", "autoconnect"]):
					self._logger.info("autoconnect_delay %d", self._settings.get(["autoconnect_delay"]))
					Timer(self._settings.get(["autoconnect_delay"]), self.do_auto_connect, [port]).start()
				else:
					self._logger.info("Not autoconnecting because autoconnect is turned off.")
			else:
				self._logger.warning("Won't autoconnect because %s isn't in %s" % (port, repr(connection_options["ports"])))
		else:
			self._logger.warning("Not auto connecting because printer is not closed nor in error state.")

	def on_shutdown(self, *args, **kwargs):
		self._logger.info("Shutting down file system observer")
		self._observer.stop();
		self._observer.join()

	def do_auto_connect(self, port, *args, **kwargs):
		try:
			self._logger.info("do_auto_connect")
			(autoport, baudrate) = self._settings.global_get(["serial", "port"]), self._settings.global_get_int(["serial", "baudrate"])
			if not autoport:
				autoport = "AUTO"
			if not port:
				port = "AUTO"
			if autoport == "AUTO" or os.path.realpath(autoport) == os.path.realpath(port):
				self._logger.info("realpath match")
				printer_profile = self._printer_profile_manager.get_default()
				profile = printer_profile["id"] if "id" in printer_profile else "_default"
				if not self._printer.is_closed_or_error():
					self._logger.info("Not autoconnecting; printer already connected")
					return
				self._logger.info("Attempting to connect to %s at %d with profile %s" % (autoport, baudrate, repr(profile)))
				self._printer.connect(port=autoport, baudrate=baudrate, profile=profile)
			else:
				self._logger.info("realpath no match")
				self._logger.info("Skipping auto connect on %s because it isn't %s" % (os.path.realpath(port), os.path.realpath(autoport)))
		except:
			self._logger.error("Exception in do_auto_connect %s", get_exception_string())

	def get_settings_defaults(self, *args, **kwargs):
		return dict(autoconnect_delay=20)

	def get_assets(self, *args, **kwargs):
		return dict(js=["js/portlister.js"])

	def get_update_information(self, *args, **kwargs):
		return dict(
			portlister=dict(
				displayName="PortLister",
				displayVersion=self._plugin_version,

				# use github release method of version check
				type="github_release",
				user="markwal",
				repo="OctoPrint-PortLister",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/markwal/OctoPrint-PortLister/archive/{target_version}.zip"
			)
		)

__plugin_name__ = "PortLister"
__plugin_pythoncompat__ = ">=2.7,<4"

def __plugin_load__():
	global __plugin_implementation__
	plugin = PortListerPlugin()
	__plugin_implementation__ = plugin

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": plugin.get_update_information,
	}

