# OctoPrint-PortLister

Have you noticed that if you load up the OctoPrint web page when your printer is
off, the printer's port isn't in the list?  Then when you turn on the printer
you have to refresh the page to make it show up?  This plugin fixes that.

It watches for the device to appear (when you turn it on) and then notifies all
the web clients to refresh the list of ports.

It also (if you have autoconnect turned on), will automatically connect to the
printer (if the new port is the same as the one you've selected in connection
settings) after a reasonable (long) delay to wait for the printer to actually
come on.  The default delay is 20 secs.  It's settable in config.yaml, if
anybody uses this plugin besides me, I could be talked into a settings page.

## Setup

Install via the bundled [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager)
or manually using this URL:

    https://github.com/markwal/OctoPrint-PortLister/archive/master.zip

## Configuration

In ~/.octoprint/config.yaml, the autoconnect_delay can be configured to
something other than the default 20 seconds it takes my printer to boot up.

plugins:
  PortLister:
    autoconnect_delay: 20
