function deleteRow(button) {
  var row = button.parentNode.parentNode;
  row.parentNode.removeChild(row);
}
function duplicateRow(button) {
  var row = button.parentNode.parentNode.parentNode;
  var cloneRow =row.cloneNode(true);
  const elements = document.querySelectorAll('input[name$="87"]');
  const lastRow = elements[elements.length - 1];
  var lastName = lastRow.getAttribute('name');
  if (lastName) {
    var newPrefix = lastName.replace(/^(\d+)_\d+$/, function(match, p1) {
        return (parseInt(p1, 10) + 1) + "_";
    });
    var cell = cloneRow.children;
    for (var i = 0; i < cell.length; i++) {
        var input = cell[i].querySelector('input');
        if (input) {
            var name = input.getAttribute('name');
            if (name) {
                var suffix = name.split('_')[1];
                var newName = newPrefix + suffix;
                input.setAttribute('name', newName);
            }
        }
    }
}
  lastRow.parentNode.parentElement.after(cloneRow);
}

function setupButton(selector, type, value, color = null, onClick = null) {
  document.querySelectorAll(selector).forEach(elm => {
    elm.type = type;
    elm.value = value;
    if (onClick) {
      elm.setAttribute('onclick', onClick);
    }else{
      elm.classList.add("disabled")
    }
  });
}


window.addEventListener('load', function () {
	setupButton('input[name$="_2"]', 'button', 'X', 'red', 'deleteRow(this)');
  const id = document.querySelector('input[name$="_3"]');
  if (id.value) // if _id exists, disable Duplicate function
  {
    setupButton('input[name$="_1"]', 'button', 'Dupl', null, null);
  }else{
    setupButton('input[name$="_1"]', 'button', 'Dupl', null, 'duplicateRow(this)');
  }
});