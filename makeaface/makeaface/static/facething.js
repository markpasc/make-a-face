
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

    if (cell.x == -1 && cell.y == 1) {
        if (! createdCamera) {
            cell.elem.attr("id", "camera");
            cameraman.url = '{% url static path="makeaface/" %}';
            window.setTimeout(function () {
                    var mycam = cameraman.createCamera({
                            'id': 'camera',
                            'width': spanSize(3),
                            'height': spanSize(3),
                            'sendto': '{% absoluteurl %}{% url upload_photo %}{% endabsoluteurl %}',
                            'errorSending': function(cam, err) { alert('OOPS: ' + err) },
                            'tookPhoto': function(cam) { tookPhoto(cam) },
                            //'droppedPhoto': function(cam) { droppedPhoto(cam) },
                            'sentPhoto': function(cam, url) { sentPhoto(cam, url) }
                        });
                }, 2000);
            createdCamera = true;
        }

        return;
    }

    cell.elem.mouseover(embiggenCell);
    cell.elem.mouseout(ensmallenCell);

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
    cells[1][-1].setBothspan(3);
});
