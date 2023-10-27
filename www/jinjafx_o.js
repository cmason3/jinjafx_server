(function() {
  var active = null;
  var obj = null;
  var tid = 0;
  var qs = '';

  function set_status(color, title, message) {
    clearTimeout(tid);
    tid = setTimeout(function() { sobj.innerHTML = "" }, 5000);
    sobj.style.color = color;
    sobj.innerHTML = "<strong>" + window.opener.quote(title) + "</strong> " + window.opener.quote(message);
  }

  window.onload = function() {
    if (window.opener != null) {
      var dt = window.opener.dt;
      window.opener.reset_dt();

      dayjs.extend(window.dayjs_plugin_advancedFormat);

      sobj = document.getElementById("ostatus");

      document.getElementById('copy').onclick = function() {
        sobj.innerHTML = '';
        try {
          var t = document.getElementById('t_' + document.querySelector('.tab-content > .active').getAttribute('id'));

          if (t.nodeName == 'IFRAME') {
            t.contentDocument.designMode = "on";
            t.contentDocument.execCommand("selectAll", false, null);
            t.contentDocument.execCommand("copy", false, null);
            t.contentDocument.designMode = "off";
            t.contentDocument.getSelection().removeAllRanges();
          }
          else {
            var oss = t.selectionStart;
            var ose = t.selectionEnd;
            var ost = t.scrollTop;
            t.focus();
            t.setSelectionRange(0, t.value.length);
            document.execCommand("copy", false, null);
            t.setSelectionRange(oss, ose);
            t.scrollTop = ost;
          }
          set_status("green", "OK", "Copied to Clipboard");
        }
        catch (e) {
          console.log(e);
          set_status("darkred", "ERROR", e);
        }
      };

      document.getElementById('print').onclick = function() {
        sobj.innerHTML = '';
        var t = document.getElementById('t_' + document.querySelector('.tab-content > .active').getAttribute('id'));

        if (t.nodeName == 'IFRAME') {
          t.contentWindow.print();
        }
        else {
          document.getElementById('print_pre').innerHTML = window.opener.quote(t.value);
          window.print();
        }
      };

      document.getElementById('docx').onclick = function() {
        sobj.innerHTML = '';
        if (obj != null) {
          var xHR = new XMLHttpRequest();
          xHR.open("POST", 'html2docx' + qs, true);

          xHR.onload = function() {
            if (this.status === 200) {
              var link = document.createElement('a');
              link.href = window.URL.createObjectURL(xHR.response);
              link.download = xHR.getResponseHeader("X-Download-Filename");
              link.click();
            }
            else {
              var sT = (this.statusText.length == 0) ? window.opener.getStatusText(this.status) : this.statusText;
              set_status("darkred", "HTTP ERROR " + this.status, sT);
            }
          };

          xHR.timeout = 10000;
          xHR.onerror = function() {
            set_status("darkred", "ERROR", "XMLHttpRequest.onError()");
          };
          xHR.ontimeout = function() {
            set_status("darkred", "ERROR", "XMLHttpRequest.onTimeout()");
          };

          xHR.responseType = "blob";
          xHR.setRequestHeader("Content-Type", "application/json");

          var o = JSON.stringify(obj.outputs[active + ':html']);
          if (o.length > 1024) {
            xHR.setRequestHeader("Content-Encoding", "gzip");
            xHR.send(pako.gzip(o));
          }
          else {
            xHR.send(o);
          }
        }
        var t = document.getElementById('t_' + document.querySelector('.tab-content > .active').getAttribute('id'));
        t.focus();
      };

      document.getElementById('download').onclick = function() {
        sobj.innerHTML = '';
        if (obj != null) {
          var zip = new JSZip();
          Object.keys(obj.outputs).forEach(function(o) {
            var ofile = o;
            var oformat = 'text';

            if (ofile.includes(':')) {
              [ofile, oformat] = ofile.split(':', 2);
            }

            ofile = ofile.replace(/[^A-Z0-9_. -/]/gi, '_').replace(/_+/g, '_');

            if (!ofile.includes('.')) {
              ofile += '.' + oformat.replace('text', 'txt');
            }

            zip.file(ofile, window.opener.d(obj.outputs[o]));
          });

          zip.generateAsync({ type: 'blob' }).then(function(content) {
            var link = document.createElement('a');
            link.href = window.URL.createObjectURL(content);
            link.download = 'Outputs.' + dayjs().format('YYYYMMDD') + '-' + dayjs().format('HHmmss') + '.zip';
            link.click();
          });
        }
        var t = document.getElementById('t_' + document.querySelector('.tab-content > .active').getAttribute('id'));
        t.focus();
      };

      if (Object.keys(dt).length !== 0) {
        var _qs = [];
        var dataset = null;

        if (dt.id != '') {
          _qs.push('dt=' + dt.id);
        }
        if (dt.dataset != '') {
          _qs.push('ds=' + dt.dataset);
          dataset = dt.dataset;
        }
        qs = (_qs.length > 0) ? '?' + _qs.join('&') : '';

        delete dt.id;
        delete dt.dataset;

        var xHR = new XMLHttpRequest();
        xHR.open("POST", '/jinjafx' + qs, true);

        xHR.onload = function() {
          if (this.status === 200) {
            try {
              obj = JSON.parse(xHR.responseText);
              if (obj.status === "ok") {
                var stderr = null;

                if (obj.outputs.hasOwnProperty('_stderr_')) {
                  stderr = window.opener.d(obj.outputs['_stderr_']);
                  delete (obj.outputs['_stderr_']);
                }

                var oc = Object.keys(obj.outputs).length;
                var oid = 1;

                var links = '';
                var tabs = '';

                Object.keys(obj.outputs).sort(function(a, b) {
                  if (a.indexOf(':') > -1) {
                    a = a.split(':').slice(0, -1).join(':')
                  }
                  if (b.indexOf(':') > -1) {
                    b = b.split(':').slice(0, -1).join(':')
                  }

                  if (a == 'Output') {
                    return -1;
                  }

                  return a > b ? 1 : b > a ? -1 : 0;
                }).forEach(function(output) {
                  var oname = output;
                  var oformat = 'text';

                  if (output.includes(':')) {
                    oname = output.substring(0, output.lastIndexOf(':'));
                    oformat = output.substring(output.lastIndexOf(':') + 1);
                  }

                  var g = window.opener.quote(oname)

                  tabs += '<div id="o' + oid + '" class="h-100 tab-pane fade' + ((oid == 1) ? ' show active' : '') + '">';
                  tabs += '<h4 class="fw-bold">' + g + '</h4>';

                  var tc = window.opener.d(obj.outputs[output]);
                  if (oformat == 'html') {
                    tabs += '<iframe id="t_o' + oid + '" class="output" srcdoc="' + tc.replace(/&/g, '&amp;').replace(/"/g, "&quot;") + '"></iframe>';
                  }
                  else {
                    tabs += '<textarea id="t_o' + oid + '" class="output" readonly>' + window.opener.quote(tc) + '</textarea>';
                  }

                  tabs += '</div>';

                  links += '<li class="nav-item">';
                  links += '<a class="nav-link' + ((oid == 1) ? ' active"' : '"') + ' data-bs-toggle="tab" href="#o' + oid + '">' + g + '</a>';
                  links += '</li>';

                  oid += 1;
                });

                document.body.style.display = 'none';
                document.getElementById('status').style.display = 'none';
                document.getElementById('summary').innerHTML = 'Generated at ' + dayjs().format('HH:mm') + ' on ' + dayjs().format('Do MMMM YYYY') + '<br />in ' + Math.ceil(obj.elapsed).toLocaleString() + ' milliseconds';
                document.getElementById('tabs').innerHTML = tabs;
                document.getElementById('nav-links').innerHTML = links;
                document.getElementById('wrap').classList.remove('d-none');
                document.getElementById('footer').classList.remove('d-none');

                document.title = 'Outputs' + ((dataset != 'Default') ? ' (' + dataset + ')' : '');

                if (oc > 1) {
                  document.getElementById('pills').classList.remove('d-none');
                }

                window.onresize = function() {
                  document.getElementById("row").style.height = (window.innerHeight - 200) + "px";
                };

                window.onresize();
                document.body.style.display = 'block';

                function toggle_docx() {
                  var e = document.getElementsByClassName('nav-link active');
                  for (var i = 0; i < e.length; i++) {
                    active = e.item(i).text;
                    if (active + ':html' in obj.outputs) {
                      document.getElementById('docx').classList.remove('d-none');
                    }
                    else {
                      document.getElementById('docx').classList.add('d-none');
                    }
                  }
                }

                var e = document.getElementsByClassName('nav-link');
                for (var i = 0; i < e.length; i++) {
                  e.item(i).onclick = toggle_docx;
                }

                toggle_docx();

                if (stderr != null) {
                  var html = '<ul class="mb-0">'
                  stderr.trim().split(/\n+/).forEach(function(w) {
                    if (html.match(/<li>/)) {
                      html += '<br />';
                    }
                    html += '<li>' + window.opener.quote(w) + '</li>';
                  });
                  html += '</ul>'

                  document.getElementById('warnings').innerHTML = html;
                  new bootstrap.Modal(document.getElementById('warning_modal'), {
                    keyboard: true
                  }).show();
                }
              }
              else {
                document.title = "Error";
                document.body.innerHTML = "<div id=\"status\" class=\"alert alert-danger\"><strong><h4>JinjaFx Error</h4></strong><pre>"+ obj.error + "</pre></div>";
              }
            }
            catch (e) {
              console.log(e);
              document.title = "Error";
              document.body.innerHTML = "<div id=\"status\" class=\"alert alert-danger\"><strong><h4>Internal Error</h4></strong>" + e + "</div>";
            }
          }
          else {
            document.title = "Error";
            var sT = (this.statusText.length == 0) ? window.opener.getStatusText(this.status) : this.statusText;
            document.body.innerHTML = "<div id=\"status\" class=\"alert alert-danger\"><strong><h4>HTTP ERROR " + this.status + "</h4></strong>"+ sT + "</div>";
          }
        };
        xHR.timeout = 0;
        xHR.onerror = function() {
          document.title = "Error";
          document.body.innerHTML = "<div id=\"status\" class=\"alert alert-danger\"><strong><h4>JinjaFx Error</h4></strong>XMLHttpRequest.onError()</div>";
        };
        xHR.setRequestHeader("Content-Type", "application/json");

        var rd = JSON.stringify(dt);
        if (rd.length > 1024) {
          xHR.setRequestHeader("Content-Encoding", "gzip");
          xHR.send(pako.gzip(rd));
        }
        else {
          xHR.send(rd);
        }
      }
      else {
        document.title = "Error";
        document.body.innerHTML = "<div id=\"status\" class=\"alert alert-danger\"><strong><h4>JinjaFx Error</h4></strong>DataTemplate Expired</div>";
      }
    }
    else {
      document.title = "Error";
      document.body.innerHTML = "<div id=\"status\" class=\"alert alert-danger\"><strong><h4>JinjaFx Error</h4></strong>DataTemplate Expired</div>";
    }
  };
})();
