var dt = {};

function reset_dt() {
  dt = {};
}

function rot47(data) {
  return data.replace(/[ -}]/g, function(c) {
    var n = c.charCodeAt(0) + 47;

    if (n > 125) {
      n -= 94;
    }

    return String.fromCharCode(n);
  });
}

var _fromCC = String.fromCharCode.bind(String);

function _utob(c) {
  if (c.length < 2) {
    var cc = c.charCodeAt(0);
    return cc < 0x80 ? c : cc < 0x800 ? (_fromCC(0xc0 | (cc >>> 6)) + _fromCC(0x80 | (cc & 0x3f))) : (_fromCC(0xe0 | ((cc >>> 12) & 0x0f)) + _fromCC(0x80 | ((cc >>> 6) & 0x3f)) + _fromCC(0x80 | (cc & 0x3f)));
  }
  else {
    var cc = 0x10000 + (c.charCodeAt(0) - 0xD800) * 0x400 + (c.charCodeAt(1) - 0xDC00);
    return (_fromCC(0xf0 | ((cc >>> 18) & 0x07)) + _fromCC(0x80 | ((cc >>> 12) & 0x3f)) + _fromCC(0x80 | ((cc >>> 6) & 0x3f)) + _fromCC(0x80 | (cc & 0x3f)));
  }
}

function utob(u) {
  // Borrowed from Dan Kogai (https://github.com/dankogai/js-base64)
  return u.replace(/[\uD800-\uDBFF][\uDC00-\uDFFFF]|[^\x00-\x7F]/g, _utob);
}

function _btou(cccc) {
  switch (cccc.length) {
    case 4:
      var cp = ((0x07 & cccc.charCodeAt(0)) << 18) | ((0x3f & cccc.charCodeAt(1)) << 12) | ((0x3f & cccc.charCodeAt(2)) << 6) | (0x3f & cccc.charCodeAt(3)), offset = cp - 0x10000;
      return (_fromCC((offset >>> 10) + 0xD800) + _fromCC((offset & 0x3FF) + 0xDC00));
    case 3:
      return _fromCC(((0x0f & cccc.charCodeAt(0)) << 12) | ((0x3f & cccc.charCodeAt(1)) << 6) | (0x3f & cccc.charCodeAt(2)));
    default:
      return _fromCC(((0x1f & cccc.charCodeAt(0)) << 6) | (0x3f & cccc.charCodeAt(1)));
  }
}

function btou(b) {
  // Borrowed from Dan Kogai (https://github.com/dankogai/js-base64)
  return b.replace(/[\xC0-\xDF][\x80-\xBF]|[\xE0-\xEF][\x80-\xBF]{2}|[\xF0-\xF7][\x80-\xBF]{3}/g, _btou);
}

function e(data) {
  return window.btoa(utob(rot47(data)));
}

function d(data) {
  return rot47(btou(window.atob(data)));
}

function quote(str) {
  str = str.replace(/&/g, "&amp;");
  str = str.replace(/>/g, "&gt;");
  str = str.replace(/</g, "&lt;");
  str = str.replace(/"/g, "&quot;");
  str = str.replace(/'/g, "&apos;");
  return str;
}

function getStatusText(code) {
  var statusText = {
    400: 'Bad Request',
    403: 'Forbidden',
    404: 'Not Found',
    413: 'Request Entity Too Large',
    429: 'Too Many Requests',
    500: 'Internal Server Error',
    503: 'Service Unavailable'
  };

  if (statusText.hasOwnProperty(code)) {
    return statusText[code];
  }
  return '';
}

(function() {
  var loaded = false;
  var dirty = false;
  var tinfo = true;
  var sobj = undefined;
  var fe = undefined;
  var tid = 0;
  var dt_id = '';
  var qs = {};
  var datasets = {
    'Default': [CodeMirror.Doc('', 'data'), CodeMirror.Doc('', 'yaml')]
  };
  var current_ds = 'Default';
  var pending_dt = '';
  var dt_password = null;
  var dt_opassword = null;
  var dt_mpassword = null;
  var input_form = null;
  var r_input_form = null;
  var jinput = null;
  var protect_action = 0;
  var revision = 0;
  var protect_ok = false;
  var csv_on = false;
  var cDataPos = null;
  var xsplit = null;

  var jsyaml_schema = {
    schema: jsyaml.DEFAULT_SCHEMA.extend(['scalar', 'sequence', 'mapping'].map(function(kind) {
      return new jsyaml.Type('!', {
        kind: kind,
        multi: true
      });
    })),
    json: true
  };

  function select_dataset(e) {
    switch_dataset(e.currentTarget.ds_name, true);
  }

  function switch_dataset(ds, sflag) {
    if (sflag) {
      datasets[current_ds][0] = window.cmData.swapDoc(datasets[ds][0]);
      datasets[current_ds][1] = window.cmVars.swapDoc(datasets[ds][1]);
    }
    else {
      window.cmData.swapDoc(datasets[ds][0]);
      window.cmVars.swapDoc(datasets[ds][1]);
    }
    if (ds != current_ds) {
      window.addEventListener('beforeunload', onBeforeUnload);
      if (document.getElementById('get_link').value != 'false') {
        document.title = 'JinjaFx [unsaved]';
      }
      dirty = true;
      document.getElementById('selected_ds').innerHTML = ds;
      current_ds = ds;
      onDataBlur();
    }
    fe.focus();
  }

  function rebuild_datasets() {
    document.getElementById('datasets').innerHTML = '';

    Object.keys(datasets).forEach(function(ds) {
      var a = document.createElement('a');
      a.classList.add('dropdown-item', 'text-decoration-none');
      a.addEventListener('click', select_dataset, false);
      a.href = '#';
      a.ds_name = ds;
      a.innerHTML = ds;
      document.getElementById('datasets').appendChild(a);
    });

    if (Object.keys(datasets).length > 1) {
      if (document.getElementById('select_ds').disabled == true) {
        document.getElementById('xgvars').classList.remove('d-none');
        document.getElementById('xlvars').classList.remove('h-100');

        xsplit = Split(["#xgvars", "#xlvars"], {
          direction: "vertical",
          cursor: "row-resize",
          sizes: [50, 50],
          snapOffset: 0,
          minSize: 30,
          onDragStart: remove_info
        });
        window.cmgVars.refresh();
      }
      document.getElementById('select_ds').disabled = false;
      document.getElementById('delete_ds').disabled = false;
    }
    else {
      document.getElementById('select_ds').disabled = true;
      document.getElementById('delete_ds').disabled = true;
      document.getElementById('xgvars').classList.add('d-none');
      document.getElementById('xlvars').classList.add('h-100');

      if (xsplit != null) {
        xsplit.destroy();
        xsplit = null;

        if (window.cmgVars.getValue().match(/\S/)) {
          var ds = Object.keys(datasets)[0];
          datasets[ds][1].setValue(window.cmgVars.getValue().trimEnd() + "\n\n" + datasets[ds][1].getValue());
        }

        window.cmgVars.setValue("");
        window.cmgVars.getDoc().clearHistory();
      }
    }
    document.getElementById('selected_ds').innerHTML = current_ds;
  }

  function delete_dataset(ds) {
    delete datasets[ds];
    //window.addEventListener('beforeunload', onBeforeUnload);
    //if (document.getElementById('get_link').value != 'false') {
    //  document.title = 'JinjaFx [unsaved]';
    //}
    //dirty = true;

    rebuild_datasets();
    switch_dataset(Object.keys(datasets)[0], false);
    fe.focus();
  }

  function bufferToHex(buffer) {
    return [...new Uint8Array(buffer)].map(b => b.toString(16).padStart(2, '0')).join ('');
  }

  function ansible_vault_encrypt(plaintext, password) {
    var t = new TextEncoder();

    return window.crypto.subtle.importKey('raw', t.encode(password), 'PBKDF2', false, ['deriveBits']).then(function(key) {
      var salt = window.crypto.getRandomValues(new Uint8Array(32));

      return window.crypto.subtle.deriveBits({ name: 'PBKDF2', salt: salt, iterations: 10000, hash: 'SHA-256' }, key, 640).then(function(db) {
        return window.crypto.subtle.importKey('raw', db.slice(0, 32), 'AES-CTR', false, ['encrypt']).then(function(ekey) {
          var b_plaintext = t.encode(plaintext);
          var pkcs7_padding = 16 - (b_plaintext.byteLength % 16);
          var r = new Uint8Array(b_plaintext.byteLength + pkcs7_padding);

          r.set(b_plaintext);
          for (var i = b_plaintext.byteLength; i < r.byteLength; i++) {
            r[i] = pkcs7_padding;
          }

          return window.crypto.subtle.encrypt({ name: 'AES-CTR', counter: db.slice(64, 80), length: 64 }, ekey, r).then(function(ciphertext) {
            return window.crypto.subtle.importKey('raw', db.slice(32, 64), { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']).then(function(hkey) {
              return window.crypto.subtle.sign('HMAC', hkey, ciphertext).then(function(hmac) {
                var h = bufferToHex(t.encode(bufferToHex(salt) + '\n' + bufferToHex(hmac) + '\n' + bufferToHex(ciphertext)));
                var vtext = h.match(/.{1,80}/g).map(x => ' '.repeat(10) + x).join('\n');
                return '!vault |\n' + ' '.repeat(10) + '$ANSIBLE_VAULT;1.1;AES256\n' + vtext;
              });
            });
          });
        });
      });
    });
  }

  function jinjafx_generate() {
    var vaulted_vars = dt.vars.indexOf('$ANSIBLE_VAULT;') > -1;
    dt.vars = e(dt.vars);
    dt.template = e(window.cmTemplate.getValue().replace(/\t/g, "  "));
    dt.id = dt_id;
    dt.dataset = current_ds;

    if (JSON.stringify(dt).length > 2048 * 1024) {
      set_status("darkred", "ERROR", 'Content Too Large');
    }
    else {
      if (vaulted_vars) {
        new bootstrap.Modal(document.getElementById('vault_input'), {
          keyboard: false
        }).show();
      }
      else {
        if (dt_id != '') {
          window.open("/output.html?dt=" + dt_id, "_blank");
        }
        else {
          window.open("/output.html", "_blank");
        }
      }
    }
  }

  function jinjafx(method) {
    clear_status();
    fe.focus();

    if (method == "delete_dataset") {
      if ((window.cmData.getValue().match(/\S/) || window.cmVars.getValue().match(/\S/)) || ((Object.keys(datasets).length == 2) && window.cmgVars.getValue().match(/\S/))) {
        if (confirm("Are You Sure?") === true) {
          delete_dataset(current_ds);
        }
      }
      else {
        delete_dataset(current_ds);
      }
      return false;
    }
    else if (method == "add_dataset") {
      document.getElementById("ds_name").value = '';
      new bootstrap.Modal(document.getElementById('dataset_input'), {
        keyboard: true
      }).show();
      return false;
    }

    if (method == "protect") {
      document.getElementById('password_open2').classList.remove('is-invalid');
      document.getElementById('password_open2').classList.remove('is-valid');
      document.getElementById('password_modify2').classList.remove('is-invalid');
      document.getElementById('password_modify2').classList.remove('is-valid');
      new bootstrap.Modal(document.getElementById('protect_dt'), {
        keyboard: false
      }).show();
      return false;
    }

    if (window.cmTemplate.getValue().length === 0) {
      window.cmTemplate.focus();
      set_status("darkred", "ERROR", "No Template");
      return false;
    }

    var nonASCIIRegex = /[^\u0000-\u007f]+/;
    var cData = window.cmData.getSearchCursor(nonASCIIRegex);
    if (cData.findNext()) {
      setTimeout(function() {
        cDataPos = [cData.from(), cData.to()];
        document.getElementById("csv").dispatchEvent(new CustomEvent('click'));
      }, 50);
      set_status("darkred", "ERROR", "Non ASCII Character(s) in 'data.csv'");
      return false;
    }

    if (document.getElementById('select_ds').disabled == false) {
      var cgVars = window.cmgVars.getSearchCursor(nonASCIIRegex);
      if (cgVars.findNext()) {
        window.cmgVars.focus();
        window.cmgVars.setSelection(cgVars.from(), cgVars.to());
        set_status("darkred", "ERROR", "Non ASCII Character(s) in 'global.yml'");
        return false;
      }
    }

    var cVars = window.cmVars.getSearchCursor(nonASCIIRegex);
    if (cVars.findNext()) {
      window.cmVars.focus();
      window.cmVars.setSelection(cVars.from(), cVars.to());
      set_status("darkred", "ERROR", "Non ASCII Character(s) in 'vars.yml'");
      return false;
    }

    dt = {};

    try {
      if (method === "generate") {
        dt.data = window.cmData.getValue().split(/\r?\n/).filter(function(e) {
          return !e.match(/^[ \t]*#/) && e.match(/\S/);
        });

        if (dt.data.length == 1) {
          window.cmData.focus();
          set_status("darkred", "ERROR", "Not Enough Data Rows");
          return false;
        }

        dt.vars = '';
        dt.data = e(dt.data.join("\n"));

        var vars = window.cmVars.getValue().replace(/\t/g, "  ");

        if (document.getElementById('select_ds').disabled == false) {
          var global = window.cmgVars.getValue().replace(/\t/g, "  ");

          if (global.match(/\S/)) {
            if (global.trimStart().startsWith('$ANSIBLE_VAULT;') && vars.match(/\S/)) {
              set_status("darkred", "ERROR", "Ansible Vault not supported in 'global.yml' with 'vars.yml'");
              return false;
            }
            if (vars.trimStart().startsWith('$ANSIBLE_VAULT;')) {
              set_status("darkred", "ERROR", "Ansible Vault not supported in 'vars.yml' with 'global.yml'");
              return false;
            }

            try {
              jsyaml.load(global, jsyaml_schema);
              dt.vars += global.trimEnd() + "\n\n";
            }
            catch (e) {
              console.log(e);
              set_status("darkred", "ERROR", '[global.yml] ' + e);
              return false;
            }
          }
        }

        if (vars.match(/\S/)) {
          try {
            jsyaml.load(vars, jsyaml_schema);
            dt.vars += vars;
          }
          catch (e) {
            console.log(e);
            set_status("darkred", "ERROR", '[vars.yml] ' + e);
            return false;
          }
        }

        if (dt.vars.match(/\S/)) {
          try {
            var vars = jsyaml.load(dt.vars, jsyaml_schema);
            if (vars !== null) {
              if (vars.hasOwnProperty('jinjafx_input') && (vars['jinjafx_input'].constructor.name === "Object")) {
                document.getElementById('input_modal').className = "modal-dialog modal-dialog-centered";
                if (vars['jinjafx_input'].hasOwnProperty('size')) {
                  document.getElementById('input_modal').className += " modal-" + vars['jinjafx_input']['size'];
                }

                if (vars['jinjafx_input'].hasOwnProperty('body')) {
                  if (input_form !== vars['jinjafx_input']['body']) {
                    var xHR = new XMLHttpRequest();
                    xHR.open("POST", '/jinjafx?dt=jinjafx_input', true);

                    r_input_form = null;

                    xHR.onload = function() {
                      if (this.status === 200) {
                        try {
                          obj = JSON.parse(xHR.responseText);
                          if (obj.status === "ok") {
                            r_input_form = d(obj.outputs['Output']);
                            document.getElementById('jinjafx_input_form').innerHTML = r_input_form;
                            input_form = vars['jinjafx_input']['body'];
                            jinput = new bootstrap.Modal(document.getElementById('jinjafx_input'), {
                              keyboard: false
                            });
                            jinput.show();
                          }
                          else {
                            var e = obj.error.replace("template.j2", "jinjafx_input");
                            set_status("darkred", 'ERROR', e.substring(5));
                          }
                        }
                        catch (e) {
                          console.log(e);
                          set_status("darkred", "ERROR", e);
                        }
                      }
                      else {
                        var sT = (this.statusText.length == 0) ? getStatusText(this.status) : this.statusText;
                        set_status("darkred", "HTTP ERROR " + this.status, sT);
                      }
                      clear_wait();
                    };
                    xHR.onerror = function() {
                      set_status("darkred", "ERROR", "XMLHttpRequest.onError()");
                      clear_wait();
                    };
                    xHR.ontimeout = function() {
                      set_status("darkred", "ERROR", "XMLHttpRequest.onTimeout()");
                      clear_wait();
                    };

                    set_wait();

                    var rbody = vars['jinjafx_input']['body'];
                    rbody = rbody.replace(/<(?:output[\t ]+.+?|\/output[\t ]*)>.*?\n/gi, '');

                    xHR.timeout = 10000;
                    xHR.setRequestHeader("Content-Type", "application/json");

                    var rd = JSON.stringify({ "template": e(rbody) });
                    if (rd.length > 1024) {
                      xHR.setRequestHeader("Content-Encoding", "gzip");
                      xHR.send(pako.gzip(rd));
                    }
                    else {
                      xHR.send(rd);
                    }
                    return false;
                  }
                  else {
                    jinput = new bootstrap.Modal(document.getElementById('jinjafx_input'), {
                      keyboard: false
                    });
                    jinput.show();
                    return false;
                  }
                }
                else if (vars['jinjafx_input'].hasOwnProperty('prompt')) {
                  if (vars['jinjafx_input']['prompt'].constructor.name === "Object") {
                    var body = '';

                    Object.keys(vars['jinjafx_input']['prompt']).forEach(function(f) {
                      var v = vars['jinjafx_input']['prompt'][f];
                      body += '<div class="row"><div class="col">';

                      if (v.constructor.name === "Object") {
                        body += '<label for="' + f + '" class="col-form-label">' + v['text'] + '</label>';
                        body += '<input id="' + f + '" class="form-control" data-var="' + f + '"';

                        if (v.hasOwnProperty('type')) {
                          body += ' type="' + v['type'] + '"';
                        }

                        if (v.hasOwnProperty('pattern')) {
                          body += ' pattern="' + v['pattern'] + '"';
                        }

                        if (v.hasOwnProperty('required') && v['required']) {
                          body += ' required>';
                        }
                        else {
                          body += '>';
                        }
                      }
                      else {
                        body += '<label for="' + f + '" class="col-form-label">' + v + '</label>';
                        body += '<input id="' + f + '" class="form-control" data-var="' + f + '">';
                      }

                      body += '</div></div>';
                    });

                    if (r_input_form !== body) {
                      document.getElementById('jinjafx_input_form').innerHTML = body;
                      r_input_form = body;
                    }
                    jinput = new bootstrap.Modal(document.getElementById('jinjafx_input'), {
                      keyboard: false
                    });
                    jinput.show();
                    return false;
                  }
                }
              }
            }
          }
          catch (e) {
            console.log(e);
            set_status("darkred", "ERROR", '[all.yml] ' + e);
            return false;
          }
        }
        jinjafx_generate();
      }
      else if ((method === "export") || (method === "get_link") || (method === "update_link")) {
        if ((method === "update_link") && !dirty) {
          set_status("#e64c00", "OK", 'No Changes Detected');
          return false;
        }

        dt.dataset = current_ds;
        dt.template = e(window.cmTemplate.getValue().replace(/\t/g, "  "));

        if ((current_ds === 'Default') && (Object.keys(datasets).length === 1)) {
          dt.vars = e(window.cmVars.getValue().replace(/\t/g, "  "));
          dt.data = e(window.cmData.getValue());
        }
        else {
          dt.datasets = {};

          if (Object.keys(datasets).length > 1) {
            dt.global = e(window.cmgVars.getValue().replace(/\t/g, "  "));
          }

          switch_dataset(current_ds, true);
          Object.keys(datasets).forEach(function(ds) {
            dt.datasets[ds] = {};
            dt.datasets[ds].data = e(datasets[ds][0].getValue());
            dt.datasets[ds].vars = e(datasets[ds][1].getValue().replace(/\t/g, "  "));
          });
        }

        if (method === "export") {
          if (dt_id != '') {
            window.open("/dt.html?dt=" + dt_id, "_blank");
          }
          else {
            window.open("/dt.html", "_blank");
          }
        }
        else {
          set_wait();

          if (method == "update_link") {
            update_link(dt_id);
          }
          else {
            update_link(null);
          }
        }
      }
    }
    catch (ex) {
      console.log(ex);
      set_status("darkred", "ERROR", ex);
      clear_wait();
    }
  }

  function update_link(v_dt_id) {
    var xHR = new XMLHttpRequest();

    if (v_dt_id !== null) {
      xHR.open("POST", "/get_link?id=" + v_dt_id, true);
      if (dt_password !== null) {
        xHR.setRequestHeader("X-Dt-Password", dt_password);
      }
      if (dt_opassword != null) {
        xHR.setRequestHeader("X-Dt-Open-Password", dt_opassword);
      }
      if (dt_mpassword != null) {
        xHR.setRequestHeader("X-Dt-Modify-Password", dt_mpassword);
      }
      xHR.setRequestHeader("X-Dt-Revision", revision + 1);
    }
    else {
      xHR.open("POST", "/get_link", true);
    }

    xHR.onload = function() {
      if (this.status === 200) {
        if (v_dt_id !== null) {
          revision += 1;
          if (dt_mpassword != null) {
            dt_password = dt_mpassword;
          }
          else if (dt_opassword != null) {
            dt_password = dt_opassword;
          }
          dt_opassword = null;
          dt_mpassword = null;
          set_status("green", "OK", "Link Updated");
          window.removeEventListener('beforeunload', onBeforeUnload);
        }
        else {
          window.removeEventListener('beforeunload', onBeforeUnload);
          window.location.href = '/dt/' + this.responseText.trim();
        }
        document.title = 'JinjaFx - Jinja2 Templating Tool';
        dirty = false;
      }
      else if (this.status == 401) {
        protect_action = 2;
        new bootstrap.Modal(document.getElementById('protect_input'), {
          keyboard: false
        }).show();
        return false;
      }
      else if (this.status == 409) {
        set_status("darkred", "DENIED", "Remote DataTemplate is a Later Revision");
      }
      else {
        var sT = (this.statusText.length == 0) ? getStatusText(this.status) : this.statusText;
        set_status("darkred", "HTTP ERROR " + this.status, sT);
      }
      clear_wait();
    };

    xHR.onerror = function() {
      set_status("darkred", "ERROR", "XMLHttpRequest.onError()");
      clear_wait();
    };
    xHR.ontimeout = function() {
      set_status("darkred", "ERROR", "XMLHttpRequest.onTimeout()");
      clear_wait();
    };

    xHR.timeout = 10000;
    xHR.setRequestHeader("Content-Type", "application/json");

    var rd = JSON.stringify(dt);
    if (rd.length > 2048 * 1024) {
      set_status("darkred", "ERROR", 'Content Too Large');
    }
    else if (rd.length > 1024) {
      xHR.setRequestHeader("Content-Encoding", "gzip");
      xHR.send(pako.gzip(rd));
    }
    else {
      xHR.send(rd);
    }
  }

  function reset_location(suffix) {
    if (window.location.pathname.startsWith('/dt/')) {
      window.history.replaceState({}, document.title, window.location.href.substr(0, window.location.href.indexOf('/dt/')) + suffix);
    }
    else if (window.location.href.indexOf('/index.html?') > -1) {
      if (suffix.length == 0) {
        window.history.replaceState({}, document.title, window.location.href.substr(0, window.location.href.indexOf('?')));
      }
      else {
        window.history.replaceState({}, document.title, window.location.href.substr(0, window.location.href.indexOf('/index.html?')) + suffix);
      }
    }
    else if (window.location.href.indexOf('/?') > -1) {
      window.history.replaceState({}, document.title, window.location.href.substr(0, window.location.href.indexOf('/?')) + suffix);
    }
    else if (window.location.href.indexOf('?') > -1) {
      window.history.replaceState({}, document.title, window.location.href.substr(0, window.location.href.indexOf('?')) + suffix);
    }
  }

  function try_to_load() {
    try {
      if (qs.hasOwnProperty('dt')) {
        set_wait();
        var xHR = new XMLHttpRequest();
        xHR.open("GET", "/get_dt/" + qs.dt, true);

        xHR.onload = function() {
          if (this.status === 401) {
            protect_action = 1;
            new bootstrap.Modal(document.getElementById('protect_input'), {
              keyboard: false
            }).show();
            return false;
          }
          else if (this.status === 200) {
            try {
              var dt = jsyaml.load(d(JSON.parse(this.responseText)['dt']), jsyaml_schema);

              if (dt.hasOwnProperty('dataset')) {
                load_datatemplate(dt['dt'], qs, dt['dataset']);
              }
              else {
                load_datatemplate(dt['dt'], qs, null);
              }
              dt_id = qs.dt;

              document.getElementById('update').classList.remove('d-none');
              document.getElementById('get').classList.add('d-none');
              document.getElementById('mdd').disabled = false;

              document.getElementById('protect').classList.remove('disabled');
              if (dt.hasOwnProperty('dt_password') || dt.hasOwnProperty('dt_mpassword')) {
                document.getElementById('protect_text').innerHTML = 'Update Protection';
              }

              if (dt.hasOwnProperty('updated')) {
                revision = dt.revision;
                set_status('green', 'Revision ' + revision, 'Updated ' + dayjs.unix(dt.updated).fromNow(), 30000, true);
              }
              else {
                revision = 1;
              }

              reset_location('/dt/' + dt_id);
            }
            catch (e) {
              console.log(e);
              set_status("darkred", "INTERNAL ERROR", e);
              reset_location('');
            }
          }
          else {
            var sT = (this.statusText.length == 0) ? getStatusText(this.status) : this.statusText;
            set_status("darkred", "HTTP ERROR " + this.status, sT);
            reset_location('');
          }
          document.getElementById('lbuttons').classList.remove('d-none');
          loaded = true;
          clear_wait();
        };

        xHR.onerror = function() {
          set_status("darkred", "ERROR", "XMLHttpRequest.onError()");
          reset_location('');
          document.getElementById('lbuttons').classList.remove('d-none');
          loaded = true;
          clear_wait();
        };
        xHR.ontimeout = function() {
          set_status("darkred", "ERROR", "XMLHttpRequest.onTimeout()");
          reset_location('');
          document.getElementById('lbuttons').classList.remove('d-none');
          loaded = true;
          clear_wait();
        };

        xHR.timeout = 10000;
        if (dt_password != null) {
          xHR.setRequestHeader("X-Dt-Password", dt_password);
        }
        xHR.send(null);
      }
      else {
        document.getElementById('lbuttons').classList.remove('d-none');
        loaded = true;
      }
    }
    catch (ex) {
      console.log(ex);
      set_status("darkred", "ERROR", ex);
      document.getElementById('lbuttons').classList.remove('d-none');
      loaded = true; onChange(null, true);
    }
  }

  window.onload = function() {
    try {
      dayjs.extend(window.dayjs_plugin_relativeTime);
  
      if (!window.location.pathname.startsWith('/dt/')) {
        var xHR = new XMLHttpRequest();
        xHR.open("GET", "/jinjafx.html" + window.location.search, true);
        xHR.send(null);
      }
  
      document.getElementById('delete_ds').onclick = function() { jinjafx('delete_dataset'); };
      document.getElementById('add_ds').onclick = function() { jinjafx('add_dataset'); };
      document.getElementById('get').onclick = function() { jinjafx('get_link'); };
      document.getElementById('get2').onclick = function() { jinjafx('get_link'); };
      document.getElementById('update').onclick = function() { jinjafx('update_link'); };
      document.getElementById('protect').onclick = function() { jinjafx('protect'); };
  
      if (window.crypto.subtle) {
        document.getElementById('encrypt').classList.remove('d-none');
      }
  
      if (window.showOpenFilePicker) {
        document.getElementById('import').onclick = async() => {
          clear_status();
          fe.focus();
  
          if ((!dirty) || (confirm("Are You Sure?") === true)) {
            const [h] = await window.showOpenFilePicker({
              types: [{
                description: 'JinjaFx DataTemplates',
                accept: { 'text/plain': ['.txt', '.dt'] }
              }]
            });
  
            const fh = await h.getFile();
            const contents = await fh.text();
  
            if (contents.replace(/\r/g, '').indexOf('---\ndt:\n') > -1) {
              var obj = jsyaml.load(contents, jsyaml_schema);
              if (obj != null) {
                pending_dt = obj['dt'];
                apply_dt();
                return true;
              }
            }
            set_status("darkred", "ERROR", "Invalid DataTemplate");
          }
        };
      }
      else {
        document.getElementById('import').onclick = function() {
          clear_status();
          fe.focus();
  
          if ((!dirty) || (confirm("Are You Sure?") === true)) {
            document.getElementById('import_file').click();
          }
        };
  
        document.getElementById('import_file').addEventListener('change', function(e1) {
          var r = new FileReader();
          r.onload = function(e2) {
            if (e2.target.result.replace(/\r/g, '').indexOf('---\ndt:\n') > -1) {
              var obj = jsyaml.load(e2.target.result, jsyaml_schema);
              if (obj != null) {
                pending_dt = obj['dt'];
                apply_dt();
                return true;
              }
            }
            set_status("darkred", "ERROR", "Invalid DataTemplate");
          };
          r.readAsText(e1.target.files[0]);
        }, false);
      }
  
      document.getElementById('export').onclick = function() { jinjafx('export'); };
      document.getElementById('generate').onclick = function() { jinjafx('generate'); };
      document.getElementById('encrypt').onclick = function() {
        clear_status();
        new bootstrap.Modal(document.getElementById('vault_encrypt'), {
          keyboard: false
        }).show();
      };
  
      sobj = document.getElementById("status");
  
      window.onresize = function() {
        document.getElementById("content").style.height = (window.innerHeight - 155) + "px";
      };
  
      window.onresize();

      var gExtraKeys = {
        "Alt-F": "findPersistent",
        "Ctrl-F": "findPersistent",
        "Cmd-F": "findPersistent",
        "F11": function(cm) {
          cm.setOption("fullScreen", !cm.getOption("fullScreen"));
        },
        "Cmd-Enter": function(cm) {
          cm.setOption("fullScreen", !cm.getOption("fullScreen"));
        },
        "Esc": function(cm) {
          if (cm.getOption("fullScreen")) {
            cm.setOption("fullScreen", false);
          }
        },
        "Ctrl-S": function(cm) {
          if (!document.getElementById('update').classList.contains('d-none')) {
            jinjafx('update_link');
          }
          else {
            set_status("darkred", "ERROR", "No Link to Update");
          }
        },
        "Cmd-S": function(cm) {
          if (!document.getElementById('update').classList.contains('d-none')) {
            jinjafx('update_link');
          }
          else {
            set_status("darkred", "ERROR", "No Link to Update");
          }
        },
        "Ctrl-G": function(cm) {
          jinjafx('generate');
        },
        "Cmd-G": function(cm) {
          jinjafx('generate');
        },
        "Ctrl-D": false,
        "Cmd-D": false
      };

      document.body.style.display = "block";
  
      CodeMirror.defineMode("data", cmDataMode);
      window.cmData = CodeMirror.fromTextArea(data, {
        tabSize: 2,
        scrollbarStyle: "null",
        styleSelectedText: false,
        extraKeys: gExtraKeys,
        mode: "data",
        viewportMargin: 80,
        smartIndent: false
      });
  
      window.cmgVars = CodeMirror.fromTextArea(t_gvars, {
        tabSize: 2,
        scrollbarStyle: "null",
        styleSelectedText: false,
        extraKeys: gExtraKeys,
        mode: "yaml",
        viewportMargin: 80,
        smartIndent: false,
        showTrailingSpace: true
      });
  
      window.cmVars = CodeMirror.fromTextArea(vars, {
        tabSize: 2,
        scrollbarStyle: "null",
        styleSelectedText: false,
        extraKeys: gExtraKeys,
        mode: "yaml",
        viewportMargin: 80,
        smartIndent: false,
        showTrailingSpace: true
      });
  
      CodeMirror.registerHelper("fold", "jinja2", function(cm, start) {
        var startLine = cm.getLine(start.line);
        var tokenStack = 1;
  
        if ((startLine.indexOf('{#') != -1) && (startLine.indexOf('#}') == -1)) {
          for (var ln = start.line + 1; (tokenStack > 0) && (ln <= cm.lastLine()); ln++) {
            var theLine = cm.getLine(ln);
  
            if (theLine.indexOf('#}') != -1) {
              if (--tokenStack == 0) {
                return {
                  from: CodeMirror.Pos(start.line, startLine.indexOf('{#') + 2),
                  to: CodeMirror.Pos(ln, theLine.indexOf('#}'))
                };
              }
            }
          }
        }
        else if (cm.getTokenTypeAt(CodeMirror.Pos(start.line, 0)) != 'comment') {
          var smatch = startLine.match(/{%([+-]?[ \t]*(if|for|macro|call|filter))[ \t]+/);
          if (smatch) {
            var eregexp = new RegExp('{%([+-]?[ \t]*)end' + smatch[2] + '[ \t]*[+-]?%}');
  
            if (!startLine.match(eregexp)) {
              var sregexp = new RegExp('{%[+-]?[ \t]*' + smatch[2] + '[ \t]+');
  
              for (var ln = start.line + 1; (tokenStack > 0) && (ln <= cm.lastLine()); ln++) {
                if (cm.getTokenTypeAt(CodeMirror.Pos(ln, 0)) != 'comment') {
                  var theLine = cm.getLine(ln);
                  var sm = theLine.match(sregexp);
                  var ematch = theLine.match(eregexp);
  
                  if (sm && !ematch) {
                    tokenStack += 1;
                  }
                  else if (!sm && ematch) {
                    if (--tokenStack == 0) {
                      return {
                        from: CodeMirror.Pos(start.line, smatch.index + 2 + smatch[1].length),
                        to: CodeMirror.Pos(ln, ematch.index + 2 + ematch[1].length)
                      };
                    }
                  }
                }
              }
            }
          }
        }
        return undefined;
      });
  
      function cmOutputMode() {
        return {
          startState: function() {
            return { 'comment': false, 'type': 0, 'output': 0 }
          },
          token: function(stream, state) {
            if (stream.match(/{#/)) {
              state.comment = true;
              return null;
            }
            else if (stream.match(/#}/)) {
              state.comment = false;
              return null;
            }
            if (!state.comment) {
              if (stream.match(/<(?=output(?::\S+)? [^><]+>)/i)) {
                state.type = 1;
                state.output = 1;
                return "jfx-output-left";
              }
              else if (stream.match(/<(?=\/output *>)/i)) {
                state.type = 2;
                state.output = 1;
                return "jfx-output-left";
              }
              else if (state.type > 0) {
                if ((state.type == 1) && stream.match(/>(?=\[-?[0-9]+\])/)) {
                  state.output = 10000;
                  return "jfx-output";
                }
                else if (stream.match(/>/)) {
                  state.type = state.output = 0;
                  return "jfx-output-right";
                }
                else if ((state.output >= 10000) && stream.match(/]/)) {
                  state.type = state.output = 0;
                  return "jfx-output-right";
                }
                else if ((state.output == 7) && stream.match(/:(?:html|markdown|md) /)) {
                  return "jfx-output-tag";
                }
                else if (stream.match(/./)) {
                  return (state.output++ > 10000) ? "jfx-output-number" : "jfx-output";
                }
              }
            }
            stream.next();
          }
        };
      }
  
      CodeMirror.defineMode("template", function(config, parserConfig) {
        return CodeMirror.overlayMode(CodeMirror.getMode(config, "jinja2"), cmOutputMode(), true);
      });
  
      window.cmTemplate = CodeMirror.fromTextArea(template, {
        lineNumbers: true,
        tabSize: 2,
        autofocus: true,
        scrollbarStyle: "null",
        styleSelectedText: false,
        extraKeys: gExtraKeys,
        mode: "template",
        viewportMargin: 80,
        smartIndent: false,
        showTrailingSpace: true,
        foldGutter: true,
        foldOptions: {
          rangeFinder: CodeMirror.helpers.fold.jinja2,
          widget: ' \u22EF '
        },
        gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"]
      });
  
      fe = window.cmTemplate;
      window.cmData.on("focus", function() { fe = window.cmData });
      window.cmVars.on("focus", function() { fe = window.cmVars; onDataBlur() });
      window.cmgVars.on("focus", function() { fe = window.cmgVars; onDataBlur() });
      window.cmTemplate.on("focus", function() { fe = window.cmTemplate; onDataBlur() });
  
      document.getElementById('header').onclick = onDataBlur;
      document.getElementById('push').onclick = onDataBlur;
      document.getElementById('footer').onclick = onDataBlur;
  
      document.getElementById("csv").onclick = function() {
        window.cmData.getWrapperElement().style.display = 'block';
        document.getElementById("csv").style.display = 'none';
        window.cmData.refresh();
        window.cmData.focus();
  
        if (cDataPos != null) {
          window.cmData.setSelection(cDataPos[0], cDataPos[1]);
          window.cmData.scrollIntoView({from: cDataPos[0], to: cDataPos[1]}, 20);
          cDataPos = null;
        }
        csv_on = false;
      };
  
      window.cmData.on("beforeChange", onPaste);
      window.cmTemplate.on("beforeChange", onPaste);
      window.cmVars.on("beforeChange", onPaste);
      window.cmgVars.on("beforeChange", onPaste);
  
      window.cmData.on("change", onChange);
      window.cmVars.on("change", onChange);
      window.cmgVars.on("change", onChange);
      window.cmTemplate.on("change", onChange);
  
      var hsplit = Split(["#cdata", "#cvars"], {
        direction: "horizontal",
        cursor: "col-resize",
        sizes: [60, 40],
        snapOffset: 0,
        minSize: 45,
        onDragStart: remove_info
      });
  
      var vsplit = Split(["#top", "#ctemplate"], {
        direction: "vertical",
        cursor: "row-resize",
        sizes: [40, 60],
        snapOffset: 0,
        minSize: 30,
        onDragStart: remove_info
      });
  
      document.getElementById('jinjafx_input').addEventListener('shown.bs.modal', function (e) {
        var focusable = document.getElementById('jinjafx_input_form').querySelectorAll('input,select');
        if (focusable.length) {
          focusable[0].focus();
        }
      });
  
      document.getElementById('ml-input-reset').onclick = function(e) {
        document.getElementById('jinjafx_input_form').innerHTML = r_input_form;
        var focusable = document.getElementById('jinjafx_input_form').querySelectorAll('input,select');
        if (focusable.length) {
          focusable[0].focus();
        }
      };
  
      document.getElementById('ml-input-ok').onclick = function(e) {
        if (document.getElementById('input_form').checkValidity() !== false) {
          e.preventDefault();
          jinput.hide();
  
          var vars = {};
          document.getElementById('input_form').querySelectorAll('input,select').forEach(function(e, i) {
            if (e.getAttribute('data-var') != null) {
              if (e.dataset.var.match(/\S/)) {
                var v = e.value;
                if ((e.tagName == 'INPUT') && ((e.type == 'checkbox') || (e.type == 'radio'))) {
                  v = e.checked;
                }
                if (vars.hasOwnProperty(e.dataset.var)) {
                  vars[e.dataset.var].push(v);
                }
                else {
                  vars[e.dataset.var] = [v];
                }
              }
            }
          });
  
          var vars_yml = 'jinjafx_input:\r\n';
          Object.keys(vars).forEach(function(v) {
            for (i = 0; i < vars[v].length; i++) {
              if (typeof vars[v][i] !== "boolean") {
                vars[v][i] = '"' + vars[v][i].replace(/"/g, '\\x22') + '"';
              }
            }
            if (vars[v].length > 1) {
              vars_yml += '  ' + v + ': [' + vars[v].join(', ') + ']\r\n';
            }
            else {
              vars_yml += '  ' + v + ': ' + vars[v][0] + '\r\n';
            }
          });
          dt.vars += '\r\n' + vars_yml;
          jinjafx_generate();
        }
      };
  
      document.getElementById('jinjafx_input').addEventListener('hidden.bs.modal', function (e) {
        fe.focus();
      });
  
      document.getElementById('vault_input').addEventListener('shown.bs.modal', function (e) {
        document.getElementById("vault").focus();
      });
  
      document.getElementById('vault_encrypt').addEventListener('shown.bs.modal', function (e) {
        document.getElementById("vault_string").focus();
      });
  
      document.getElementById('vault_string').onkeyup = function(e) {
        if (e.which == 13) {
          document.getElementById('ml-vault-encrypt-ok').click();
        }
      };
  
      document.getElementById('vault_encrypt').addEventListener('hidden.bs.modal', function (e) {
        clear_status();
        document.getElementById("vault_string").value = '';
        if (document.getElementById("password_vault1").value != document.getElementById("password_vault2").value) {
          document.getElementById("password_vault1").value = '';
          document.getElementById("password_vault2").value = '';
          document.getElementById('password_vault2').classList.remove('is-invalid');
          document.getElementById('password_vault2').classList.remove('is-valid');
          document.getElementById("password_vault2").disabled = true;
        }
        fe.focus();
      });
  
      document.getElementById('ml-vault-ok').onclick = function() {
        dt.vpw = e(document.getElementById("vault").value);
        if (dt_id != '') {
          window.open("/output.html?dt=" + dt_id, "_blank");
        }
        else {
          window.open("/output.html", "_blank");
        }
      };
  
      document.getElementById('vault').onkeyup = function(e) {
        if (e.which == 13) {
          document.getElementById('ml-vault-ok').click();
        }
      };
  
      document.getElementById('protect_dt').addEventListener('shown.bs.modal', function (e) {
        document.getElementById("password_open1").focus();
      });
  
      document.getElementById('vault_output').addEventListener('shown.bs.modal', function (e) {
        document.getElementById("vault_text").focus();
        document.getElementById("vault_text").select();
      });
  
      document.getElementById('vault_output').addEventListener('hidden.bs.modal', function (e) {
        fe.focus();
      });
  
      document.getElementById('ml-vault-encrypt-ok').onclick = function() {
        clear_status();
        if (document.getElementById('vault_string').value.match(/\S/)) {
          if (document.getElementById('password_vault1').value.match(/\S/)) {
            if (document.getElementById('password_vault1').value == document.getElementById('password_vault2').value) {
              bootstrap.Modal.getOrCreateInstance(document.getElementById('vault_encrypt')).hide()
  
              ansible_vault_encrypt(document.getElementById('vault_string').value, document.getElementById('password_vault1').value).then(function(x) {
                document.getElementById('vault_text').value = x;
              });
  
              new bootstrap.Modal(document.getElementById('vault_output'), {
                keyboard: false
              }).show();
            }
            else {
              set_status("darkred", "ERROR", "Password Verification Failed");
              document.getElementById('password_vault2').focus();
              return false;
            }
          }
          else {
            set_status("darkred", "ERROR", "Password is Required");
            document.getElementById('password_vault1').focus();
            return false;
          }
        }
        else {
          set_status("darkred", "ERROR", "Nothing to Encrypt");
          document.getElementById('vault_string').focus();
          return false;
        }
      };
  
      document.getElementById('ml-protect-dt-ok').onclick = function() {
        dt_opassword = null;
        dt_mpassword = null;
  
        if (document.getElementById('password_open1').value.match(/\S/)) {
          if (document.getElementById('password_open1').value == document.getElementById('password_open2').value) {
            dt_opassword = document.getElementById('password_open2').value;
          }
          else {
            set_status("darkred", "ERROR", "Password Verification Failed");
            return false;
          }
        }
  
        if (document.getElementById('password_modify1').value.match(/\S/)) {
          if (document.getElementById('password_modify1').value == document.getElementById('password_modify2').value) {
            dt_mpassword = document.getElementById('password_modify2').value;
          }
          else {
            set_status("darkred", "ERROR", "Password Verification Failed");
            dt_opassword = null;
            return false;
          }
        }
  
        if ((dt_opassword != null) || (dt_mpassword != null)) {
          if (dt_opassword === dt_mpassword) {
            dt_mpassword = null;
          }
          document.getElementById('protect_text').innerHTML = 'Update Protection';
          window.addEventListener('beforeunload', onBeforeUnload);
          document.title = 'JinjaFx [unsaved]';
          dirty = true;
          set_status("green", "OK", "Protection Set - Update Required", 10000);
          dt_password = null;
        }
        else {
          set_status("darkred", "ERROR", "Invalid Password");
        }
      };
  
      document.getElementById('protect_dt').addEventListener('hidden.bs.modal', function (e) {
        document.getElementById("password_open1").value = '';
        document.getElementById("password_open2").value = '';
        document.getElementById("password_open2").disabled = true;
        document.getElementById("password_modify1").value = '';
        document.getElementById("password_modify2").value = '';
        document.getElementById("password_modify2").disabled = true;
        fe.focus();
      });
  
      document.getElementById('protect_input').addEventListener('shown.bs.modal', function (e) {
        document.getElementById("in_protect").focus();
        protect_ok = false;
      });
  
      document.getElementById('ml-protect-ok').onclick = function() {
        protect_ok = true;
      };
  
      document.getElementById('in_protect').onkeyup = function(e) {
        if (e.which == 13) {
          document.getElementById('ml-protect-ok').click();
        }
      };
  
      document.getElementById('protect_input').addEventListener('hidden.bs.modal', function (e) {
        if (protect_ok == true) {
          dt_password = document.getElementById("in_protect").value;
          if (dt_password.match(/\S/)) {
            if (protect_action == 1) {
              try_to_load();
            }
            else {
              update_link(dt_id);
            }
          }
          else {
            if (protect_action == 1) {
              reset_location('');
              dt_password = null;
            }
            loaded = true;
            document.getElementById('lbuttons').classList.remove('d-none');
            set_status("darkred", "ERROR", "Invalid Password");
          }
        }
        else {
          if (protect_action == 1) {
            reset_location('');
            document.getElementById('lbuttons').classList.remove('d-none');
            dt_password = null;
            loaded = true;
          }
          else {
            set_status("#e64c00", "OK", "Link Not Updated");
          }
        }
        document.getElementById("in_protect").value = '';
        clear_wait();
      });
  
      document.getElementById('dataset_input').addEventListener('shown.bs.modal', function (e) {
        document.getElementById("ds_name").focus();
      });
  
      document.getElementById('ml-dataset-ok').onclick = function() {
        var new_ds = document.getElementById("ds_name").value;
  
        if (new_ds.match(/^[A-Z][A-Z0-9_ -]*$/i)) {
          if (!datasets.hasOwnProperty(new_ds)) {
            datasets[new_ds] = [CodeMirror.Doc('', 'data'), CodeMirror.Doc('', 'yaml')];
            rebuild_datasets();
            //window.addEventListener('beforeunload', onBeforeUnload);
            //if (document.getElementById('get_link').value != 'false') {
            //  document.title = 'JinjaFx [unsaved]';
            //}
            //dirty = true;
          }
          switch_dataset(new_ds, true);
        }
        else {
          set_status("darkred", "ERROR", "Invalid Data Set Name");
        }
      };
  
      document.getElementById('ds_name').onkeyup = function(e) {
        if (e.which == 13) {
          document.getElementById('ml-dataset-ok').click();
        }
      };
  
      function check_open() {
        if (document.getElementById('password_open1').value == document.getElementById('password_open2').value) {
          document.getElementById('password_open2').classList.remove('is-invalid');
          document.getElementById('password_open2').classList.add('is-valid');
        }
        else {
          document.getElementById('password_open2').classList.remove('is-valid');
          document.getElementById('password_open2').classList.add('is-invalid');
        }
      };
  
      function check_vault() {
        if (document.getElementById('password_vault1').value == document.getElementById('password_vault2').value) {
          document.getElementById('password_vault2').classList.remove('is-invalid');
          document.getElementById('password_vault2').classList.add('is-valid');
        }
        else {
          document.getElementById('password_vault2').classList.remove('is-valid');
          document.getElementById('password_vault2').classList.add('is-invalid');
        }
      };
  
      document.getElementById('password_vault1').onkeyup = function(e) {
        if (document.getElementById('password_vault1').value.match(/\S/)) {
          if (document.getElementById('password_vault2').disabled == true) {
            document.getElementById('password_vault2').disabled = false;
            document.getElementById('password_vault2').classList.add('is-invalid');
          }
          else {
            check_vault();
          }
        }
        else {
          document.getElementById('password_vault2').disabled = true;
          document.getElementById('password_vault2').value = '';
          document.getElementById('password_vault2').classList.remove('is-valid');
          document.getElementById('password_vault2').classList.remove('is-invalid');
        }
      };
  
      document.getElementById('password_vault2').onkeyup = function(e) {
        check_vault();
      };
  
      document.getElementById('password_open1').onkeyup = function(e) {
        if (document.getElementById('password_open1').value.match(/\S/)) {
          if (document.getElementById('password_open2').disabled == true) {
            document.getElementById('password_open2').disabled = false;
            document.getElementById('password_open2').classList.add('is-invalid');
          }
          else {
            check_open();
          }
        }
        else {
          document.getElementById('password_open2').disabled = true;
          document.getElementById('password_open2').value = '';
          document.getElementById('password_open2').classList.remove('is-valid');
          document.getElementById('password_open2').classList.remove('is-invalid');
        }
      };
  
      document.getElementById('password_open2').onkeyup = function(e) {
        check_open();
      };
  
      function check_modify() {
        if (document.getElementById('password_modify1').value == document.getElementById('password_modify2').value) {
          document.getElementById('password_modify2').classList.remove('is-invalid');
          document.getElementById('password_modify2').classList.add('is-valid');
        }
        else {
          document.getElementById('password_modify2').classList.remove('is-valid');
          document.getElementById('password_modify2').classList.add('is-invalid');
        }
      }
  
      document.getElementById('password_modify1').onkeyup = function(e) {
        if (document.getElementById('password_modify1').value.match(/\S/)) {
          if (document.getElementById('password_modify2').disabled == true) {
            document.getElementById('password_modify2').disabled = false;
            document.getElementById('password_modify2').classList.add('is-invalid');
          }
          else {
            check_modify();
          }
        }
        else {
          document.getElementById('password_modify2').disabled = true;
          document.getElementById('password_modify2').value = '';
          document.getElementById('password_modify2').classList.remove('is-valid');
          document.getElementById('password_modify2').classList.remove('is-invalid');
        }
      };
  
      document.getElementById('password_modify2').onkeyup = function(e) {
        check_modify();
      };
  
      document.querySelectorAll('.modal').forEach(function(elem, i) {
        elem.onkeydown = function(e) {
          if (e.keyCode === 9) {
            var focusable = elem.querySelectorAll('input,select,textarea,button');
            if (focusable.length) {
              var first = focusable[0];
              var last = focusable[focusable.length - 1];
  
              if ((e.target === first) && e.shiftKey) {
                last.focus();
                e.preventDefault();
              }
              else if ((e.target === last) && !e.shiftKey) {
                first.focus();
                e.preventDefault();
              }
            }
          }
        };
      });
  
      if (window.location.pathname.startsWith('/dt/') && (window.location.pathname.length > 4)) {
        qs['dt'] = decodeURIComponent(window.location.pathname.substr(4));
  
        if (document.getElementById('get_link').value != 'false') {
          try_to_load();
  
          document.getElementById('lbuttons').classList.remove('d-none');
  
          if (fe != window.cmData) {
            onDataBlur();
          }
        }
        else {
          set_status("darkred", "HTTP ERROR 503", "Service Unavailable");
          reset_location('');
          loaded = true;
        }
      }
      else if (window.location.href.indexOf('?') > -1) {
        var v = window.location.href.substr(window.location.href.indexOf('?') + 1).split('&');
  
        for (var i = 0; i < v.length; i++) {
          var p = v[i].split('=');
          qs[p[0].toLowerCase()] = decodeURIComponent(p.length > 1 ? p[1] : '');
        }
  
        if (qs.hasOwnProperty('dt')) {
          if (document.getElementById('get_link').value != 'false') {
            try_to_load();
  
            document.getElementById('lbuttons').classList.remove('d-none');
  
            if (fe != window.cmData) {
              onDataBlur();
            }
          }
          else {
            set_status("darkred", "HTTP ERROR 503", "Service Unavailable");
            reset_location('');
            loaded = true;
          }
        }
        else {
          reset_location('');
          loaded = true;
        }
      }
      else {
        if (document.getElementById('get_link').value != 'false') {
          document.getElementById('lbuttons').classList.remove('d-none');
        }
        document.getElementById('template_info').style.visibility = 'visible';
        loaded = true;
      }
    }
    catch (e) {
      if (e.stack.includes(e.name)) {
        document.write('<pre>' + quote(e.stack) + '</pre>');
      }
      else {
        document.write('<pre>' + quote(e.name) + ': ' + quote(e.message) + '<br />' + quote(e.stack) + '</pre>');
      }
    }
  };

  function remove_info() {
    document.getElementById('template_info').classList.add('fade-out');
    document.getElementById('template_info').style.zIndex = -1000;
  }

  function set_wait() {
    fe.setOption('readOnly', 'nocursor');
    var e = document.getElementById("csv").getElementsByTagName("th");
    for (var i = 0; i < e.length; i++) {
      e[i].style.background = '#eee';
    }
    document.getElementById("csv").style.background = '#eee';
    window.cmData.getWrapperElement().style.background = '#eee';
    window.cmTemplate.getWrapperElement().style.background = '#eee';
    window.cmVars.getWrapperElement().style.background = '#eee';
    window.cmgVars.getWrapperElement().style.background = '#eee';
    document.getElementById('overlay').style.display = 'block';
  }

  function clear_wait() {
    document.getElementById('overlay').style.display = 'none';
    window.cmVars.getWrapperElement().style.background = '';
    window.cmgVars.getWrapperElement().style.background = '';
    window.cmTemplate.getWrapperElement().style.background = '';
    window.cmData.getWrapperElement().style.background = '';
    document.getElementById("csv").style.background = '#fff';
    var e = document.getElementById("csv").getElementsByTagName("th");
    for (var i = 0; i < e.length; i++) {
      e[i].style.background = 'none';
    }
    fe.setOption('readOnly', false);
    fe.focus();
  }

  function escapeRegExp(s) {
    return s.replace(/[\\^$.*+?()[\]{}|]/g, '\\$&');
  }

  function get_csv_astable(datarows) {
    var tc = (datarows[0].match(/\t/g) || []).length;
    var cc = (datarows[0].match(/,/g) || []).length;
    var delim = new RegExp(cc > tc ? '[ \\t]*,[ \\t]*' : ' *\\t *');
    var hrow = datarows[0].split(delim);

    var table = '<table class="table table-responsive table-hover table-sm">';
    table += '<thead><tr>';
    for (var col = 0; col < hrow.length; col++) {
      table += '<th>' + quote(hrow[col]) + '</th>';
    }
    table += '</tr></thead><tbody>';

    for (var row = 1; row < datarows.length; row++) {
      var rowdata = datarows[row].split(delim);

      if (rowdata.length != hrow.length) {
        table += '<tr class="bg-danger">';
      }
      else {
        table += '<tr>';
      }

      for (var col = 0; col < hrow.length; col++) {
        var value = ((col < rowdata.length) ? quote(rowdata[col]) : '');
        table += '<td>' + (!value.match(/\S/) ? '&nbsp;' : value) + '</td>';
      }
      table += '</tr>';
    }
    table += '</tbody></table>';
    return table;
  }

  function onDataBlur() {
    var datarows = window.cmData.getValue().trim().split(/\r?\n/).filter(function(e) {
      return !e.match(/^[ \t]*#/) && e.match(/\S/);
    });
    if (datarows.length > 1) {
      document.getElementById("csv").innerHTML = get_csv_astable(datarows);
      document.getElementById("csv").style.display = 'block';
      window.cmData.getWrapperElement().style.display = 'none';
      csv_on = true;
    }
    else {
      window.cmData.getWrapperElement().style.display = 'block';
      document.getElementById("csv").style.display = 'none';
      window.cmData.refresh();
      csv_on = false;
    }
  }

  function apply_dt() {
    load_datatemplate(pending_dt, null, null);
    reset_location('');
    dt_id = '';
    dt_password = null;
    dt_opassword = null;
    dt_mpassword = null;
    input_form = null;
    document.getElementById('update').classList.add('d-none');
    document.getElementById('get').classList.remove('d-none');
    document.getElementById('mdd').disabled = true;
    document.getElementById('protect').classList.add('disabled');
    document.getElementById('protect').innerHTML = 'Protect Link';
  }

  function onPaste(cm, change) {
    if (change.origin === "paste") {
      var t = change.text.join('\n');

      if (t.replace(/\r/g, '').indexOf('---\ndt:\n') > -1) {
        var obj = jsyaml.load(t, jsyaml_schema);
        if (obj != null) {
          change.cancel();
          pending_dt = obj['dt'];

          if (dirty) {
            if (confirm("Are You Sure?") === true) {
              apply_dt();
            }
          }
          else {
            apply_dt();
          }
        }
      }
    }
  }

  function onBeforeUnload(e) {
    e.returnValue = 'Are you sure?';
  }

  function onChange(editor, errflag) {
    if (loaded) {
      if (!dirty && (errflag !== true)) {
        window.addEventListener('beforeunload', onBeforeUnload);
        if (document.getElementById('get_link').value != 'false') {
          document.title = 'JinjaFx [unsaved]';
        }
        dirty = true;
      }
      if (tinfo) {
        if (editor == window.cmTemplate) {
          document.getElementById('template_info').classList.add('fade-out');
          document.getElementById('template_info').style.zIndex = -1000;
          tinfo = false;
        }
      }
    }
  }

  function load_datatemplate(_dt, _qs, _ds) {
    try {
      current_ds = 'Default';

      window.cmgVars.setValue("");

      if (_dt.hasOwnProperty("datasets")) {
        datasets = {};

        Object.keys(_dt.datasets).forEach(function(ds) {
          var data = _dt.datasets[ds].hasOwnProperty("data") ? _dt.datasets[ds].data : "";
          var vars = _dt.datasets[ds].hasOwnProperty("vars") ? _dt.datasets[ds].vars : "";
          datasets[ds] = [CodeMirror.Doc(data, 'data'), CodeMirror.Doc(vars, 'yaml')];
        });

        if ((_ds == null) || !datasets.hasOwnProperty(_ds)) {
          current_ds = Object.keys(datasets)[0];
        }
        else {
          current_ds = _ds;
        }
        window.cmData.swapDoc(datasets[current_ds][0]);
        window.cmVars.swapDoc(datasets[current_ds][1]);

        if (_dt.hasOwnProperty("global")) {
          window.cmgVars.setValue(_dt.global);
        }
      }
      else {
        datasets = {
          'Default': [CodeMirror.Doc('', 'data'), CodeMirror.Doc('', 'yaml')]
        };

        datasets['Default'][0].setValue(_dt.hasOwnProperty("data") ? _dt.data : "");
        window.cmData.swapDoc(datasets['Default'][0]);
        datasets['Default'][1].setValue(_dt.hasOwnProperty("vars") ? _dt.vars : "");
        window.cmVars.swapDoc(datasets['Default'][1]);
      }
      window.cmTemplate.setValue(_dt.hasOwnProperty("template") ? _dt.template : "");

      window.cmData.getDoc().clearHistory();
      window.cmVars.getDoc().clearHistory();
      window.cmgVars.getDoc().clearHistory();
      window.cmTemplate.getDoc().clearHistory();

      rebuild_datasets();
      loaded = true;
    }
    catch (ex) {
      console.log(ex);
      set_status("darkred", "ERROR", ex);
      loaded = true; onChange(null, true);
    }
    if (fe != window.cmData) {
      onDataBlur();
    }
  }

  function clear_status() {
    clearTimeout(tid);
    sobj.innerHTML = "";
  }

  function set_status(color, title, message, delay, mline) {
    clearTimeout(tid);
    if (typeof delay !== 'undefined') {
      tid = setTimeout(function() { sobj.innerHTML = "" }, delay);
    }
    else {
      tid = setTimeout(function() { sobj.innerHTML = "" }, 5000);
    }
    sobj.style.color = color;
    if (typeof mline !== 'undefined') {
      sobj.innerHTML = "<strong>" + quote(title) + "</strong><br /><span class=\"small\">" + quote(message) + "</span>";
    }
    else {
      sobj.innerHTML = "<strong>" + quote(title) + "</strong> " + quote(message);
    }
  }

  function cmDataMode() {
    return {
      startState: function() {
        return { n: 0 };
      },
      token: function(stream, state) {
        if (stream.sol() && stream.match(/[ \t]*#/)) {
          stream.skipToEnd();
          return "comment";
        }
        else if ((state.n == 0) && stream.match(/\S/)) {
          state.n = 1;
          stream.skipToEnd();
          return "jfx-header";
        }
        stream.next();
      }
    };
  }
})();
