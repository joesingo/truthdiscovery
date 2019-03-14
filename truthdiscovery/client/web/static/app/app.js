var DATA = (JSON.parse(document.getElementById("data-json").innerHTML
                .replace(/&#34;/g, '"')));

angular.module("tdApp", []);

// Service to make HTTP requests and get results
angular.
    module("tdApp").
    service("tdService", ["$http", function($http) {
        this.url = "/run/";
        this.method = "GET";
        this.hasResults = false;

        /*
         * Make the HTTP request to get results of an algorithm
         */
        this.getResults = function(algorithm, matrix) {
            var self = this;
            var promise = $http({
                "url": self.url,
                "method": self.method,
                "params": {
                    "algorithm": algorithm,
                    "matrix": matrix
                }
            });
            promise.then(function(response) {
                // Our server's response is in response.data, and is an object
                // with keys 'ok' and 'data' (in the success case)
                self.results = response.data.data;
                self.hasResults = true;
            }, function(error) {
                self.hasResults = false;
            });
            return promise;
        }
    }]);

// Form component
angular.
    module("tdApp").
    component("mainForm", {
        "templateUrl": "/static/app/templates/form.html",
        "controller": function MainformController(tdService) {
            this.disabled = false;
            this.error = null;  // error message to show underneath form
            this.algorithm = "sums";
            // Default example matrix
            this.matrix = "1,2,_\n" +
                           "_,3,5\n" +
                           "2,2,4\n" +
                           "1,_,3";
            this.algorithm_labels = DATA.algorithm_labels;
            var self = this;
            this.run = function() {
                var promise = tdService.getResults(self.algorithm, self.matrix);
                // Disable all form elements and cancel errors while we wait
                // for response
                self.disabled = true;
                self.error = null;

                promise.catch(function(response) {
                    // Set error message on failure
                    self.error = response.data.error;
                    self.error = self.error[0].toUpperCase() + self.error.slice(1);
                }).finally(function() {
                    self.disabled = false;
                });
            };
        }
    });

// Results component
angular.
    module("tdApp").
    component("results", {
        "templateUrl": "/static/app/templates/results.html",
        "controller": function ResultsController(tdService) {
            this.service = tdService;
        }
    });
