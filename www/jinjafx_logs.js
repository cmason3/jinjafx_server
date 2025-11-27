(function() {
  let interval = 60;
  let m = undefined;
  // let auth_ok = false;
  // let key = '';

  function quote(str) {
    str = str.replaceAll(/&/g, '&amp;');
    str = str.replaceAll(/>/g, '&gt;');
    return str.replaceAll(/</g, '&lt;');
  }

  function ansiToRGB(str) {
    str = str.replaceAll('\033[31m', '<span style="color: rgb(239, 100, 135);">'); // Red
    str = str.replaceAll('\033[32m', '<span style="color: rgb(94, 202, 137);">'); // Green
    str = str.replaceAll('\033[33m', '<span style="color: rgb(253, 216, 119);">'); // Yellow
    str = str.replaceAll('\033[34m', '<span style="color: rgb(101, 174, 247);">'); // Blue
    str = str.replaceAll('\033[35m', '<span style="color: rgb(170, 127, 240);">'); // Magenta
    str = str.replaceAll('\033[36m', '<span style="color: rgb(67, 193, 190);">'); // Cyan
    return str.replaceAll('\033[0m', '</span>');
  }

  function scroll() {
    window.scrollTo(0, document.body.scrollHeight);
    //let e = document.querySelector('pre');
    //e.scrollTop = e.scrollHeight;
  }

  function update() {
    var xHR = new XMLHttpRequest();
    xHR.open("GET", '/get_logs', true);

    xHR.onload = function() {
      if (this.status == 200) {
        // auth_ok = true;
        // sessionStorage.setItem('jfx_weblog_key', key);
        document.querySelector('pre').innerHTML = ansiToRGB(quote(xHR.responseText));
        // document.getElementById('container').innerHTML = xHR.responseText;
        scroll();
        setTimeout(update, interval * 1000);
      }
      else if (this.status == 401) { // && !auth_ok) {
        m = new bootstrap.Modal(document.getElementById('password_input'), {
          keyboard: false
        });
        m.show();
      }
      else {
        document.querySelector('pre').innerHTML = 'HTTP ERROR ' + this.status;
        // document.getElementById('container').innerHTML = 'HTTP ERROR ' + this.status;
      }
    };

    xHR.onerror = function() {
      document.querySelector('pre').innerHTML = 'XMLHttpRequest ERROR';
      // document.getElementById('container').innerHTML = 'XMLHttpRequest ERROR';
      setTimeout(update, interval * 1000);
    };

    xHR.ontimeout = function() {
      document.querySelector('pre').innerHTML = 'XMLHttpRequest TIMEOUT';
      // document.getElementById('container').innerHTML = 'XMLHttpRequest TIMEOUT';
      setTimeout(update, interval * 1000);
    };

    xHR.timeout = 3000;
    // xHR.setRequestHeader("X-WebLog-Password", key);
    xHR.send();
  }

  window.onresize = scroll;
  window.onload = function() {
    document.getElementById('password_input').addEventListener('shown.bs.modal', function (e) {
      document.getElementById("in_password").focus();
    });
  
    document.getElementById('password_input').addEventListener('hidden.bs.modal', function (e) {
      document.getElementById("in_password").value = '';
    });
  
    document.getElementById('ml-password-ok').addEventListener('click', function (e) {
      if (document.getElementById("in_password").value.trim().length) {
        document.cookie = 'JinjaFx-WebLog-Key=' + document.getElementById("in_password").value + '; max-age=86400; path=/';
        // key = document.getElementById("in_password").value;
        m.hide();
        update();
      }
      else {
        document.getElementById("in_password").focus();
      }
    });

    document.getElementById('in_password').addEventListener('keyup', function(e) {
      if (e.which == 13) {
        document.getElementById('ml-password-ok').click();
      }
    });

    let qs = new URLSearchParams(window.location.search);

    if (qs.has('key')) {
      document.cookie = 'JinjaFx-WebLog-Key=' + qs.get('key') + '; max-age=86400; path=/';
      // key = qs.get('key');
      window.history.replaceState({}, document.title, window.location.pathname);
      // sessionStorage.removeItem('jfx_weblog_key');
    }
    update();
    // else if (sessionStorage.getItem('jfx_weblog_key')) {
    //  key = sessionStorage.getItem('jfx_weblog_key');
    //  update();
    // }
    // else {
    //  new bootstrap.Modal(document.getElementById('password_input'), {
    //    keyboard: false
     // }).show();
   // }
  };
})();
