const MATRIX_INPUT_FOCUS_DELAY = 50;
const DATA = (JSON.parse(document.getElementById("data-json").innerHTML
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
            this.matrix = {
                "entries": [
                    [1, 2, null],
                    [null, 3, 5],
                    [2, 2, 4],
                    [1, null, 3]
                ],
                "being_edited": []
            };
            for (var i=0; i<this.matrix.entries.length; i++) {
                this.matrix.being_edited.push([]);
                for (var j=0; j<this.matrix.entries[i].length; j++) {
                    this.matrix.being_edited[i].push(false);
                }
            }

            this.algorithm_labels = DATA.algorithm_labels;

            var self = this;

            /*
             * Return the matrix as a CSV string
             */
            this.getMatrixCSV = function() {
                var csv = "";
                for (var i=0; i<self.matrix.entries.length; i++) {
                    // Note: nulls are converted to empty strings here
                    csv += self.matrix.entries[i].join(",");
                    csv += "\n";
                }
                return csv;
            };

            /*
             * Mark a cell in the matrix as being edited, and focus the input
             * box
             */
            this.startEditingCell = function(row, col, event) {
                self.matrix.being_edited[row][col] = true;
                // Get text input and focus manually.
                // Seems that we cannot focus input immediately here since it
                // is not visible until after angular model change...
                var input = $(event.target).parent().find("input");
                window.setTimeout(function() {
                    input.focus();
                }, MATRIX_INPUT_FOCUS_DELAY);
                // TODO: find a better way of doing this...
            };

            /*
             * Validate a matrix entry and mark the cell as not being edited
             */
            this.stopEditingCell = function(row, col) {
                var val = parseFloat(self.matrix.entries[row][col]);
                self.matrix.entries[row][col] = val;
                if (isNaN(val)) {
                    self.matrix.entries[row][col] = null;
                }
                self.matrix.being_edited[row][col] = false;
            };

            this.run = function() {
                var promise = tdService.getResults(
                    self.algorithm, self.getMatrixCSV()
                );
                // Disable all form elements and cancel errors while we wait
                // for response
                self.disabled = true;
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
