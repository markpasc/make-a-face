
var createdCamera = false;

var defaultPictures = [];
(function() {
    for (var i = 1; i <= 20; i++) {
        defaultPictures.push("http://static.typepad.com/.shared/images/default-avatars/avatar-"+i+"-250x250.gif");
    }
})();

function onCellCreate(cell) {

    if (cell.x == -2) {
        if (cell.y < faces.length) {
            var url = faces[cell.y];
            cell.elem.css("background-image", "url("+url+")");
        }
    }

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
    }

}
addCreateListener(onCellCreate);

$(document).ready(
    function () {
        initializeGrid();
        cells[1][-1].setBothspan(3);
    }
);
