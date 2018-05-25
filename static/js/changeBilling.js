function sameBilling(sec, box) {
    var check = document.getElementById('billCheck');
    var div = document.getElementById('billInfo');
    var vis = (box.checked) "block" ? "none";
    document.write(vis);
      div.style.display = vis;
  }
}