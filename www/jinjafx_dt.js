(function() {
  function unquote(str) {
    str = str.replace(/&gt;/g, ">");
    str = str.replace(/&lt;/g, "<");
    str = str.replace(/&quot;/g, "\"");
    str = str.replace(/&apos;/g, "'");
    str = str.replace(/&amp;/g, "&");
    return str;
  }

  window.onload = function() {
    var dt = window.opener.dt;
    window.opener.reset_dt();

    if (Object.keys(dt).length !== 0) {
      var dtx = '# JinjaFx DataTemplate\n# https://github.com/cmason3/jinjafx\n\n';

      dtx += '---\n';
      dtx += 'dt:\n';

      if (dt.hasOwnProperty('datasets')) {
        if (dt.hasOwnProperty('global')) {
          var global = dt.global.match(/\S/) ? window.opener.d(dt.global).replace(/\s+$/g, '') : "";

          if (global == '') {
            dtx += '  global: ""\n\n';
          }
          else {
            dtx += '  global: |2\n';
            dtx += window.opener.quote(global.replace(/^/gm, '    ')) + '\n\n';
          }
        }

        dtx += '  datasets:\n';

        Object.keys(dt.datasets).sort(window.opener.default_on_top).forEach(function(ds) {
          var data = dt.datasets[ds].data.match(/\S/) ? window.opener.d(dt.datasets[ds].data).replace(/\s+$/g, '') : "";
          var vars = dt.datasets[ds].vars.match(/\S/) ? window.opener.d(dt.datasets[ds].vars).replace(/\s+$/g, '') : "";

          dtx += '    "' + ds + '":\n';

          if (data == '') {
            dtx += '      data: ""\n';
          }
          else {
            dtx += '      data: |2\n';
            dtx += window.opener.quote(data.replace(/^/gm, '        ')) + '\n\n';
          }

          if (vars == '') {
            dtx += '      vars: ""\n\n';
          }
          else {
            dtx += '      vars: |2\n';
            dtx += window.opener.quote(vars.replace(/^/gm, '        ')) + '\n\n';
          }
        });
      }
      else {
        var data = dt.data.match(/\S/) ? window.opener.d(dt.data).replace(/\s+$/g, '') : "";
        var vars = dt.vars.match(/\S/) ? window.opener.d(dt.vars).replace(/\s+$/g, '') : "";

        if (data == '') {
          dtx += '  data: ""\n';
        }
        else {
          dtx += '  data: |2\n';
          dtx += window.opener.quote(data.replace(/^/gm, '    ')) + '\n\n';
        }

        if (vars == '') {
          dtx += '  vars: ""\n\n';
        }
        else {
          dtx += '  vars: |2\n';
          dtx += window.opener.quote(vars.replace(/^/gm, '    ')) + '\n\n';
        }
      }

      if (typeof dt.template == "object") {
        dtx += '  template:\n';

        Object.keys(dt.template).sort(window.opener.default_on_top).forEach(function(t) {
          var template = dt.template[t].match(/\S/) ? window.opener.d(dt.template[t]).replace(/\s+$/g, '') : "";

          if (template == '') {
            dtx += '    "' + t + '": ""\n';
          }
          else {
            dtx += '    "' + t + '": |2\n';
            dtx += window.opener.quote(template.replace(/^/gm, '      ')) + '\n\n';
          }
        });
      }
      else {
        var template = dt.template.match(/\S/) ? window.opener.d(dt.template).replace(/\s+$/g, '') : "";

        if (template == '') {
          dtx += '  template: ""\n';
        }
        else {
          dtx += '  template: |2\n';
          dtx += window.opener.quote(template.replace(/^/gm, '    ')) + '\n\n';
        }
      }

      document.getElementById('container').innerHTML = dtx;

      if (window.showSaveFilePicker) {
        document.getElementById('saveas').onclick = async() => {
          const h = await window.showSaveFilePicker({
            suggestedName: 'jinjafx.dt',
            types: [{
              description: 'JinjaFx DataTemplate',
              accept: { 'text/plain': ['.dt', '.txt'] }
            }],
          });

          const b = new Blob([unquote(dtx)])
          const writableStream = await h.createWritable();
          await writableStream.write(b);
          await writableStream.close();
        };
        document.getElementById('saveas').classList.remove('d-none');
      }
    }
  };
})();
