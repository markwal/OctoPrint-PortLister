$(function () {
    function PortListerViewModel(parameters) {
        var self = this;

        self.connection = parameters[0];

        self.onDataUpdaterPluginMessage = function(plugin, message) {
            if (plugin == "PortLister") {
                self.connection.requestData();
            }
        }
    }

    OCTOPRINT_VIEWMODELS.push([
        PortListerViewModel,
        ["connectionViewModel"],
        []
    ]);
});
