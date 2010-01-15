
var createdCamera = false;

var defaultPictures = $.map([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20], function (x) {
    return "http://static.typepad.com/.shared/images/default-avatars/avatar-"
        + (x < 10 ? "0" : "") + x + "-250x250.gif";
});

function onCellCreate(event, cell) {

    if (cell.x == -2) {
        if (cell.y < faces.length) {
            var url = faces[cell.y];
            cell.elem.css("background-image", "url("+url+")");
        }
    } else if (cell.x == -1 && cell.y == 1) {
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
    } else {
        var num = (Math.abs(cell.x) + Math.abs(cell.y)) % defaultPictures.length;
        cell.elem.css("background-image", "url(" + defaultPictures[num] + "#" + num + ")");
    }

}

$(document).ready(
    function () {
        $(document).bind('createcell', onCellCreate);
        initializeGrid();
        cells[1][-1].setBothspan(3);
    }
);
