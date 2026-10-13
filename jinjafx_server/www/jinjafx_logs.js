(function() {
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

  function add(str) {
    document.querySelector('pre').innerHTML += ansiToRGB(quote(str)) + '<br />';
    window.scrollTo({ 'left': 0, 'top': document.body.scrollHeight, 'behavior': 'instant' });
  }

  window.addEventListener('load', () => {
    let qs = new URLSearchParams(window.location.search);

    if (qs.has('key')) {
      document.cookie = 'JinjaFx-WebLog-Key=' + qs.get('key') + '; max-age=86400; path=/';
      window.history.replaceState({}, document.title, window.location.pathname);
    }

    const es = new EventSource('/_logs');

    es.addEventListener('error', (e) => {
      es.close();
      add('\033[31mError: Unable to Connect to Event Source\033[0m');
    });

    es.addEventListener('401', (e) => {
      es.close();
      new bootstrap.Modal(document.getElementById('password_input'), {
        keyboard: false
      }).show();
    });

    es.addEventListener('message', (e) => {
      add(e.data); // FIXME
    });

    es.addEventListener('log', (e) => {
      add(e.data);
    });

    document.getElementById('password_input').addEventListener('shown.bs.modal', function (e) {
      document.getElementById("in_password").focus();
    });
  
    document.getElementById('ml-password-ok').addEventListener('click', function (e) {
      if (document.getElementById("in_password").value.trim().length) {
        document.cookie = 'JinjaFx-WebLog-Key=' + document.getElementById("in_password").value + '; max-age=86400; path=/';
        window.location.reload();
      }
      else {
        document.getElementById("in_password").focus();
      }
    });

    document.getElementById('in_password').addEventListener('keyup', function(e) {
      if (e.key === 'Enter') {
        document.getElementById('ml-password-ok').click();
      }
    });
  });
})();
