window.addEventListener('load', function () {
	document.querySelectorAll('table td').forEach(elm => {
		elm.contentEditable = true;
	});
});