var DATA = (JSON.parse(document.getElementById("data-json").innerHTML
                .replace(/&#34;/g, '"')));

angular.module("tdApp", []);

// Service to make HTTP requests and get results
angular.
    module("tdApp").
    service("tdService", ["$http", function($http) {
        this.url = "/run/";
        this.method = "GET";
        this.gotFirstResults = false;

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
                self.results = response.data;
                self.gotFirstResults = true;
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
                // Disable all form elements while we wait for response
                self.disabled = true;
                promise.then(function() {
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
