$(function () {
    function PortListerViewModel(parameters) {
        var self = this;

        self.connection = parameters[0];
        self.settingsViewModel = parameters[1];

        self.onDataUpdaterPluginMessage = function(plugin, message) {
            if (plugin == "PortLister") {
                self.connection.requestData();
            }
        }

        self.onBeforeBinding = function() {
            self.settings = self.settingsViewModel.settings;
        };
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: PortListerViewModel,
        dependencies: ["connectionViewModel", "settingsViewModel"],
        elements: ["#settings_plugin_portlister"]
    });
});
