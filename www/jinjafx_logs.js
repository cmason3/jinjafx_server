(function() {
  let interval = 60;

  function scroll() {
    let e = document.getElementById('container');
    e.scrollTop = e.scrollHeight;
  }

  function update() {
    var xHR = new XMLHttpRequest();
    xHR.open("GET", '/logs?raw', true);

    xHR.onload = function() {
      if (this.status == 200) {
        document.getElementById('container').innerHTML = xHR.responseText;
        scroll();
        setTimeout(update, interval * 1000);
      }
      else if (this.status == 401) {
        new bootstrap.Modal(document.getElementById('password_input'), {
          keyboard: false
        }).show();
      }
      else {
        alert("eek");
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
    xHR.send();
  }

  document.getElementById('password_input').addEventListener('shown.bs.modal', function (e) {
    document.getElementById("in_password").focus();
  });

  document.getElementById('password_input').addEventListener('hidden.bs.modal', function (e) {
    document.getElementById("in_password").value = '';
  });

  document.getElementById('in_password').onkeyup = function(e) {
    if (e.which == 13) {
      document.getElementById('ml-password-ok').click();
    }
  };

  document.getElementById('ml-password-ok').onclick = function() {
    window.location.search = '?' + document.getElementById("in_password").value;
  };  

  window.onresize = scroll;
  window.onload = function() {
    update();
  };
})();
