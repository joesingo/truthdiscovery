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
                var input = $(event.target).find("input");
                window.setTimeout(function() {
                    input.focus();
                }, MATRIX_INPUT_FOCUS_DELAY);
                // TODO: find a better way of doing this...
            };

            this.addSource = function() {
                var num_variables = self.matrix.entries[0].length;
                var new_claims = [];
                var new_editing = [];
                for (var i=0; i<num_variables; i++) {
                    new_claims.push(null);
                    new_editing.push(false);
                }
                self.matrix.entries.push(new_claims);
                self.matrix.being_edited.push(new_editing);
            };

            this.addVariable = function() {
                for (var i=0; i<self.matrix.entries.length; i++) {
                    self.matrix.entries[i].push(null);
                    self.matrix.being_edited[i].push(false);
                }
            };

            /*
             * Delete the i-th source (0-indexed)
             */
            this.deleteSource = function(i) {
                self.matrix.entries.splice(i, 1);
                self.matrix.being_edited.splice(i, 1);
            }

            /*
             * Delete the j-th variable (0-indexed)
             */
            this.deleteVariable = function(j) {
                for (var i=0; i<self.matrix.entries.length; i++) {
                    self.matrix.entries[i].splice(j, 1);
                    self.matrix.being_edited[i].splice(j, 1);
                }
            }

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
