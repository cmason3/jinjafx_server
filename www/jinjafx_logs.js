(function() {
  let interval = 60;
  let auth_ok = false;
  let key = '';

  function scroll() {
    let e = document.getElementById('container');
    e.scrollTop = e.scrollHeight;
  }

  function update() {
    var xHR = new XMLHttpRequest();
    xHR.open("GET", '/get_logs', true);

    xHR.onload = function() {
      if (this.status == 200) {
        auth_ok = true;
        sessionStorage.setItem('jfx_weblog_key', key);
        document.getElementById('container').innerHTML = xHR.responseText;
        scroll();
        setTimeout(update, interval * 1000);
      }
      else if ((this.status == 401) && !auth_ok) {
        new bootstrap.Modal(document.getElementById('password_input'), {
          keyboard: false
        }).show();
      }
      else {
        document.getElementById('container').innerHTML = 'HTTP ERROR ' + this.status;
      }
    };

    xHR.onerror = function() {
      document.getElementById('container').innerHTML = 'XMLHttpRequest ERROR';
      setTimeout(update, interval * 1000);
    };

    xHR.ontimeout = function() {
      document.getElementById('container').innerHTML = 'XMLHttpRequest TIMEOUT';
      setTimeout(update, interval * 1000);
    };

    xHR.timeout = 3000;
    xHR.setRequestHeader("X-WebLog-Password", key);
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
      key = document.getElementById("in_password").value;
      update();
    });

    document.getElementById('in_password').addEventListener('keyup', function(e) {
      if (e.which == 13) {
        document.getElementById('ml-password-ok').click();
      }
    });

    let qs = new URLSearchParams(window.location.search);

    if (qs.has('key')) {
      key = qs.get('key');
      window.history.replaceState({}, document.title, window.location.pathname);
      sessionStorage.removeItem('jfx_weblog_key');
      update();
    }
    else if (sessionStorage.getItem('jfx_weblog_key')) {
      key = sessionStorage.getItem('jfx_weblog_key');
      update();
    }
    else {
      new bootstrap.Modal(document.getElementById('password_input'), {
        keyboard: false
      }).show();
    }
  };
})();
