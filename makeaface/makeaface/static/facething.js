
var createdCamera = false;

var defaultPictures = $.map([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], function (x) {
    return "http://static.typepad.com/.shared/images/default-avatars/avatar-"
        + (x < 10 ? "0" : "") + x + "-250x250.gif";
});

function embiggenCell(event) {
    var newsize = 1.1 * cellSize;
    $(this).width(newsize)
        .height(newsize)
        .css({
            "z-index": "9",
            "margin-top": "-" + (0.05 * cellSize) + "px",
            "margin-left": "-" + (0.05 * cellSize) + "px"
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

$(document).ready(function () {
    $(document).bind('createcell', onCellCreate);

    initializeGrid();
});
