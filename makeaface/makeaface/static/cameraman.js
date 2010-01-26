/*
 *  Cameraman
 */


var cameraman = null;

function CameraMan(opts) {
    var _self = this;
    this.options = opts;
    this.cameras = {};

    this.createCamera = function (opts) {

        var container = document.getElementById(opts.id);
        // TODO: what if id is invalid?

        // make the embed
        var embedattr = {
            name: opts.id,
            id: opts.id,
            src: _self.url + 'cameraman.swf',
            width: opts.width,
            height: opts.height,
            quality: 'high',
            allowScriptAccess: 'always',
            bgcolor: opts.bgColor,
            pluginspage: 'http://www.macromedia.com/go/getflashplayer',
            type: 'application/x-shockwave-flash',
            wmode: opts.wmode,
            allowfullscreen: (opts.allowFullScreen?'true':'false'),
            flashvars: 'cameraid=' + opts.id
        };

        if (opts.sendto) {
            embedattr.flashvars += '&sendto=' + opts.sendto;
        }

        if (!opts.bgColor) {
            embedattr.bgColor = '#000000';
        }

        if (!opts.wmode) {
            delete embedattr.wmode; // don't write empty attribute
        }

        if (navigator.userAgent.match(/MSIE/i)) {
            var movie = document.createElement('div');
            // TODO: include flashvars
            var movieHTML = '<object id="'+embedattr.id+'" data="'+embedattr.src+'" type="application/x-shockwave-flash" width="'+embedattr.width+'" height="'+embedattr.height+'"><param name="movie" value="'+embedattr.src+'" /><param name="AllowScriptAccess" value="always" /><param name="quality" value="high" />'+(embedattr.wmode?'<param name="wmode" value="'+embedattr.wmode+'" /> ':'')+'<param name="bgcolor" value="'+embedattr.bgColor+'" /><param name="allowFullScreen" value="'+(embedattr.allowFullScreen?'true':'false')+'" /><!-- --></object>';
            movie.innerHTML = movieHTML;
            container.appendChild(movie);
        }
        else {
            var movie = document.createElement('embed');
            for (attr in embedattr) {
                if (embedattr.hasOwnProperty(attr)) {
                    movie.setAttribute(attr, embedattr[attr]);
                }
            }
            container.appendChild(movie);
        }

        // make the camera object
        var newcam = new CameraCamera(opts);
        _self.cameras[newcam.id] = newcam;
        return newcam;
    };

}

function CameraCamera(opts) {
    var _self = this;
    this.options = opts;
    this.id = opts.id;

    this.getApp = function () {
        var name = _self.id;
        return (navigator.appName.indexOf ("Microsoft") != -1 ? window : document)[name];
    };

    this.takePhoto = function () {
        _self.getApp().takePhoto();
    };
    this.dropPhoto = function () {
        _self.getApp().dropPhoto();
    };
    this.sendPhoto = function () {
        _self.getApp().sendPhoto();
    };

    this._cameraReady = function () {
        if (_self.options.cameraReady) {
            _self.options.cameraReady.apply(null, [_self]);
        }
    }
    this._cameraNotReady = function () {
        if (_self.options.cameraNotReady) {
            _self.options.cameraNotReady.apply(null, [_self]);
        }
    }
    this._tookPhoto = function () {
        if (_self.options.tookPhoto) {
            _self.options.tookPhoto.apply(null, [_self]);
        }
    };
    this._droppedPhoto = function () {
        if (_self.options.droppedPhoto) {
            _self.options.droppedPhoto.apply(null, [_self]);
        }
    };
    this._sentPhoto = function (url) {
        if (_self.options.sentPhoto) {
            _self.options.sentPhoto.apply(null, [_self, url]);
        }
    };
    this._errorSending = function (errormsg) {
        if (_self.options.errorSending) {
            _self.options.errorSending.apply(null, [_self, errormsg]);
        }
    }
}

cameraman = new CameraMan({});
