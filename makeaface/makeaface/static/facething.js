
var createdCamera = false;

var defaultPictures = $.map([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], function (x) {
    return "http://static.typepad.com/.shared/images/default-avatars/avatar-"
        + (x < 10 ? "0" : "") + x + "-250x250.gif";
});

var didInitialRandomness = false;
var shuffledCells = [];
var nextCell = 0;
var nextFace = 0;

function embiggenCell(event) {
    var newsize = 1.1 * cellSize;
    $(this).width(newsize)
        .height(newsize)
        .css({
            "z-index": "9",
            "margin-top": "-" + (0.05 * cellSize) + "px",
            "margin-left": "-" + (0.05 * cellSize) + "px",
        });
}

function ensmallenCell(event) {
    $(this).width(cellSize)
        .height(cellSize)
        .css({
            "z-index": "1",
            "margin-top": "0",
            "margin-left": "0"
        });
}

function onCellCreate(event, cell) {
    //cell.elem.mouseover(embiggenCell);
    //cell.elem.mouseout(ensmallenCell);

    var url;
    if (cell.x == -2 && cell.y < faces.length) {
        url = faces[cell.y];
    } else {
        var num = (Math.abs(cell.x) + Math.abs(cell.y)) % defaultPictures.length;
        url = defaultPictures[num];
    }

    var img = $('<img/>');
    img.attr('src', url);
    cell.elem.append(img);
}

function getNextCell() {
    var cellCoords = shuffledCells[nextCell];
    var ret = cells[cellCoords[1]][cellCoords[0]];
    nextCell++;
    if (nextCell >= shuffledCells.length) {
        nextCell = 0;
    }
    return ret;
}

function getNextFace() {
    var faceUrl = faces[nextFace];
    nextFace++;
    if (nextFace >= faces.length) {
        nextFace = 0;
    }
    return faceUrl;
}

function onGridComplete(event) {
    cells[0][-1].setBothspan(3);
    cells[2][-3].setBothspan(2);
    cells[2][2].setBothspan(2);
}

function onGridResize(event) {
    shuffledCells = [];

    for (var y = 0; y < currentRows; y++) {
        for (x = -currentMaxX + 1; x < currentMaxX; x++) {
            if (! cells[y][x].obscuredBy) {
                shuffledCells.push([x, y]);
            }
        }
    }

    shuffle(shuffledCells);

    for (var i = 0; i < shuffledCells.length; i++) {
        var cell = getNextCell();
        if (cell.populated) continue;
        var faceUrl = getNextFace();
        var cellElem = cell.elem;
        var imgElem = cellElem.find('img');
        imgElem.attr('src',  faceUrl);
        cell.populated = true;
    }
}

$(document).ready(function () {
    $(document).bind('createcell', onCellCreate);
    $(document).bind('initializedgrid', onGridComplete);
    $(document).bind('gridresized', onGridResize);

    initializeGrid();
});

function shuffle(list) {
    for (var j, x, i = list.length; i; j = parseInt(Math.random() * i), x = list[--i], list[i] = list[j], list[j] = x);
};

