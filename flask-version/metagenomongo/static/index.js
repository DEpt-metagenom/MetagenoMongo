function setupButton(selector, type, value, color = null, onClick = null) {
  document.querySelectorAll(selector).forEach(elm => {
    elm.type = type;
    elm.value = value;
    if (color) {
      elm.style.color = color;
    }
    if (onClick) {
      elm.setAttribute('onclick', onClick);
    }
  });
}


window.addEventListener('load', function () {
  setupButton('input[name="Delete"]', 'button', 'X', 'red');
  setupButton('input[name="Duplicate"]', 'button', 'Dupl');
});