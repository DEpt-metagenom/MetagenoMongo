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
  const user_name1 = document.getElementById('user_name1');
  const user_name2 = document.getElementById('user_name2');
  user_name1.addEventListener('input', function() {
    const inputValue = user_name1.value;
    user_name2.value = inputValue;
  })
});