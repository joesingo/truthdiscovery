const MATRIX_INPUT_FOCUS_DELAY = 200;
const DATA = (JSON.parse(document.getElementById("data-json").innerHTML
                  .replace(/&#34;/g, '"')));

angular.module("tdApp", []);

// Service to make HTTP requests and get results
angular.
    module("tdApp").
    service("tdService", ["$http", function($http) {
        this.url = "/run/";
        this.method = "GET";
        this.state = "empty";

        /*
         * Make the HTTP request to get results of an algorithm
         */
        this.getResults = function(algorithm, matrix) {
            this.state = "loading";
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
                self.state = "has_results";
            }, function(error) {
                self.state = "empty";
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
            this.service = tdService;
            this.error = null;  // error message to show underneath form
            this.algorithm = "sums";

            // Initialise matrix
            var entries = [
                [1, 2, null],
                [null, 3, 5],
                [2, 2, 4],
                [1, null, 3]
            ];
            this.matrix = new Matrix(entries);
            this.load_csv = {
                "dialog_open": false,
                "error": "",
                "textarea": ""
            }

            this.algorithm_labels = DATA.algorithm_labels;

            var self = this;

            /*
             * Mark a cell in the matrix as being edited, and focus the input
             * box
             */
            this.startEditingCell = function(row, col, event) {
                self.matrix.editCell(row, col);
                // Get text input and focus manually.
                // Seems that we cannot focus input immediately here since it
                // is not visible until after angular model change...
                var input = $(event.target).find("input");
                window.setTimeout(function() {
                    input.focus();
                }, MATRIX_INPUT_FOCUS_DELAY);
                // TODO: find a better way of doing this...
            };

            this.stopEditingCell = function(row, col) {
                self.matrix.stopEditingCell(row, col);
            };

            this.toggleCsvDialog = function() {
                self.load_csv.dialog_open ^= true;
                self.load_csv.error = "";
            };

            this.loadFromCSV = function() {
                try {
                    self.matrix = self.matrix.loadFromCSV(self.load_csv.textarea);
                    self.load_csv.dialog_open = false;
                }
                catch (err) {
                    self.load_csv.error = err;
                }
            };

            this.run = function() {
                var promise = tdService.getResults(
                    self.algorithm, self.matrix.asCSV()
                );
                // Cancel errors while we wait for response
                self.error = null;

                promise.catch(function(response) {
                    if ("error" in response.data) {
                        // Set error message on failure
                        self.error = response.data.error;
                        self.error = self.error[0].toUpperCase() + self.error.slice(1);
                    }
                    else {
                        // throw any unknown errors
                        throw response;
                    }
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
