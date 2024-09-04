function deleteRow(button) {
  var row = button.parentNode.parentNode;
  row.parentNode.removeChild(row);
}
function duplicateRow(button) {
  var row = button.parentNode.parentNode;
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

window.addEventListener('load', function () {
	// index_with_table
    document.querySelectorAll('input[name$="86"]').forEach(elm => {
		elm.type = "button"
    elm.value = "X"
    elm.style.color="red"
    elm.setAttribute('onclick', 'deleteRow(this)');
	});
    document.querySelectorAll('input[name$="87"]').forEach(elm => {
		elm.type = "button"
    elm.value ="Dupl"
    elm.setAttribute('onclick', 'duplicateRow(this)');
	});
    // index.html
    document.querySelectorAll('input[name="Delete"]').forEach(elm => {
		elm.type = "button"
    elm.value = "X"
    elm.style.color="red"
	});
    document.querySelectorAll('input[name="Duplicate"]').forEach(elm => {
		elm.type = "button"
    elm.value ="Dupl"
	});
});