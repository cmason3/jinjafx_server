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
    xHR.send();
  }

  window.onresize = scroll;
  window.onload = function() {
    update();
  };
})();
