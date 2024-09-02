window.addEventListener('load', function () {
	// index_with_table
    document.querySelectorAll('input[name$="86"]').forEach(elm => {
		elm.type = "button"
        elm.value = "X"
        elm.style.color="red"
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