

// Fills a page with a grid of DIV elements and provides an API
// to manipulate them.

var cellSize = 150;
var cellSpacing = 4;

var minColumns = 3;
var minRows = 3;

var currentColumns = 0;
var currentRows = 0;
var currentMaxX = 0;

var cells = {};

// We put all of the cells into a centered container element so that
// we don't need to shift everything when the browser resizes.
var containerElem = null;

// Since our cells stick out the edge of the window, this
// makes the size of document.body grow outside the canvas.
// So we can determine the visible size, we also place
// a fixed position element over the entire canvas that
// we can use to measure it instead of document.body.
var sizerElem = null;

function Cell(x, y) {
    if (cells[y] && cells[y][x]) {
        throw "Cell " + x + "," + y + " already exists (" + arguments.callee.caller.toString() + ")";
    }

    this.x = x;
    this.y = y;
    this.elem = makeElementForCell(x, y);
    this.colspan = 1;
    this.rowspan = 1;
    this.obscuredBy = null;

    $(document).trigger('createcell', [this]);
}
var cellMethods = {};
Cell.prototype = cellMethods;
cellMethods.setColspan = function (colspan) {
    if (this.obscuredBy) {
        var obscuredBy = this.obscuredBy;
        obscuredBy.destroy();
        obscuredBy.undestroy();
    }

    var oldColspan = this.colspan;
    var exposedColumns = oldColspan - colspan;
    if (exposedColumns > 0) {
        // We're shrinking, so we need to re-create
        // all of the cells in the space we're creating.

        var startColumn = this.x + (oldColspan - exposedColumns);
        for (var y = this.y; y < (this.y + this.rowspan); y++) {
            for (var x = startColumn; x < (this.x + oldColspan); x++) {
                cells[y][x].undestroy();
                cells[y][x].obscuredBy = null;
            }
        }
    }
    else if (exposedColumns < 0) {
        // We're growing, so we need to destroy
        // the cells that we're covering up.

        var startColumn = this.x + oldColspan;
        for (var y = this.y; y < (this.y + this.rowspan); y++) {
            for (var x = startColumn; x < (this.x + colspan); x++) {
                cells[y][x].destroy();
                cells[y][x].obscuredBy = this;
            }
        }

    }

    this.colspan = colspan;
    this.elem.width(spanSize(colspan));
};
cellMethods.setRowspan = function (rowspan) {
    if (this.obscuredBy) {
        var obscuredBy = this.obscuredBy;
        obscuredBy.destroy();
        obscuredBy.undestroy();
    }

    var oldRowspan = this.rowspan;
    var exposedRows = oldRowspan - rowspan;
    if (exposedRows > 0) {
        // We're shrinking, so we need to re-create
        // all of the cells in the space we're creating.

        var startRow = this.y + (oldRowspan - exposedRows);
        for (var y = startRow; y < (this.y + oldRowspan); y++) {
            for (var x = this.x; x < (this.x + this.colspan); x++) {
                cells[y][x].undestroy();
                cells[y][x].obscuredBy = null;
            }
        }
    }
    else if (exposedRows < 0) {
        // We're growing, so we need to destroy
        // the cells that we're covering up.

        var startRow = this.y + oldRowspan;
        for (var y = startRow; y < (this.y + rowspan); y++) {
            for (var x = this.x; x < (this.x + this.colspan); x++) {
                cells[y][x].destroy();
                cells[y][x].obscuredBy = this;
            }
        }

    }

    this.rowspan = rowspan;
    this.elem.height(spanSize(rowspan));
};
cellMethods.setBothspan = function (span) {
    this.setRowspan(span);
    this.setColspan(span);
};
cellMethods.destroy = function () {
    $(document).trigger('destroycell', [this]);

    // If we're being obscured by something, force that thing
    // to be recreated as a 1x1 cell so we don't end up
    // with large cells hanging out of the grid.
    if (this.obscuredBy) {
        var obscuredBy = this.obscuredBy;
        obscuredBy.destroy();
        obscuredBy.undestroy();
    }

    // Set the span to be 1 so that we recreate any other
    // cells that we were obscuring if we were larger.
    this.setRowspan(1);
    this.setColspan(1);
    var elem = this.elem;
    if (elem) {
        elem.remove();
        this.elem = null;
    }
};
cellMethods.undestroy = function () {
    if (! this.elem) {
        this.elem = makeElementForCell(this.x, this.y);
    }
    $(document).trigger('createcell', [this]);
};

function initializeGrid() {
    bodyElem = $(document.body);
    sizerElem = $('#gridsizer');

    containerElem = $('#gridcontainer');
    containerElem.width(cellSize);
    containerElem.height(cellSize);

    // The initial setup is actually implemented just be resizing
    // the grid from 0 by 0 to whatever the window actually requires.
    handleResize();

    $(window).resize(handleResize);

    $(document).trigger('initializedgrid');
}

function handleResize() {

    var pageWidth = sizerElem.width();
    var pageHeight = sizerElem.height();

    var columns = Math.ceil((pageWidth - cellSpacing) / (cellSize + cellSpacing));
    var rows = Math.ceil((pageHeight - cellSpacing) / (cellSize + cellSpacing));

    // We must always have an odd number of columns because our x=0 is in the center...
    if (columns % 2 == 0) columns = columns + 1;

    if (columns < minColumns) columns = minColumns;
    if (rows < minRows) rows = minRows;

    var maxX = Math.ceil(columns / 2);

    var newRows = rows - currentRows;
    var newColumns = columns - currentColumns;

    window.console.log('YAY resizing to add ' + newRows + ' rows and ' + newColumns + ' columns');

    if (newColumns < 0) {
        // We're shrinking, so we need to destroy some columns.

        for (var y = 0; y < currentRows; y++) {
            for (var x = maxX; x < currentMaxX; x++) {
                cells[y][x].destroy();
                delete cells[y][x];
                if (x > 0) {
                    cells[y][-x].destroy();
                    delete cells[y][-x];
                }
            }
        }

        currentColumns = columns;
        currentMaxX = maxX;
    }

    if (newRows > 0) {
        // We're growing, so we need to add some new rows.
        for (var y = currentRows; y < rows; y++) {
            cells[y] = {};
            for (var x = 0; x < currentMaxX; x++) {
                cells[y][x] = new Cell(x, y);
                if (x > 0) {
                    cells[y][-x] = new Cell(-x, y);
                }
            }
        }

        currentRows = rows;
    }
    else if (newRows < 0) {
        // We're shrinking, so we need to destroy some rows.

        for (var y = rows; y < currentRows; y++) {
            for (var x = 0; x < currentMaxX; x++) {
                cells[y][x].destroy();
                if (x > 0) {
                    cells[y][-x].destroy();
                }
            }
            delete cells[y];
        }

        currentRows = rows;
    }

    if (newColumns > 0) {

        // We're growing, so we need to add some new columns.
        for (var y = 0; y < currentRows; y++) {
            for (var x = currentMaxX; x < maxX; x++) {
                cells[y][x] = new Cell(x, y);
                if (x > 0) {
                    cells[y][-x] = new Cell(-x, y);
                }
            }
        }

        currentColumns = columns;
        currentMaxX = maxX;
    }

}

function makeElementForCell(cellX, cellY) {
    var elem = $("<div></div>");
    elem.addClass('gridcell');

    elem.width(cellSize);
    elem.height(cellSize);

    var realX = (cellX * (cellSize + cellSpacing)) + cellSpacing;
    var realY = (cellY * (cellSize + cellSpacing)) + cellSpacing;

    elem.css("left", realX+"px");
    elem.css("top", realY+"px");

    containerElem.append(elem);

    return elem;
}

function spanSize(span) {
    return (span * cellSize) + ((span - 1) * cellSpacing);
}
