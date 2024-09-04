function deleteRow(button) {
  var row = button.parentNode.parentNode;
  row.parentNode.removeChild(row);
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