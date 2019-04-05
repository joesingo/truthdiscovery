/*
 * Object to represent a truth-discovery matrix.
 * Hold entries as a 2D array, and a 2D boolean array of the same size to
 * record whether each cell is currently being edited
 */
function Matrix(entries) {
    this.entries = entries;
}

Matrix.prototype.addSource = function() {
    var new_claims = [];
    for (var i=0; i<this.entries[0].length; i++) {
        new_claims.push(null);
    }
    this.entries.push(new_claims);
};

Matrix.prototype.addVariable = function() {
    for (var i=0; i<this.entries.length; i++) {
        this.entries[i].push(null);
    }
};

/*
 * Delete the i-th source (0-indexed)
 */
Matrix.prototype.deleteSource = function(i) {
    this.entries.splice(i, 1);
}

/*
 * Delete the j-th variable (0-indexed)
 */
Matrix.prototype.deleteVariable = function(j) {
    for (var i=0; i<this.entries.length; i++) {
        this.entries[i].splice(j, 1);
    }
}

/*
 * Clear all entries
 */
Matrix.prototype.clear = function(j) {
    for (var i=0; i<this.entries.length; i++) {
        for (var j=0; j<this.entries[i].length; j++) {
            this.entries[i][j] = null;
        }
    }
}

Matrix.prototype.parseStringValue = function(val) {
    return parseFloat(val) || null;
}

/*
 * Return a Matrix object loaded from a CSV string
 */
Matrix.prototype.loadFromCSV = function(csv) {
    var entries = [];

    var lines = csv.split("\n");
    var num_cols = lines[0].split(",").length;
    for (var i=0; i<lines.length; i++) {
        var row = lines[i].split(",")
        if (row.length != num_cols) {
            throw "All rows must have the same length";
        }
        for (var j=0; j<row.length; j++) {
            row[j] = this.parseStringValue(row[j]);
        }
        entries.push(row);
    }
    return new Matrix(entries);
};

/*
 * Return the matrix as a CSV string
 */
Matrix.prototype.asCSV = function() {
    var csv = "";
    for (var i=0; i<this.entries.length; i++) {
        // Note: nulls are converted to empty strings here
        csv += this.entries[i].join(",");
        csv += "\n";
    }
    return csv;
};
