function correct(){
  data = []
  document.querySelectorAll('table td').forEach(elm => {
		data.push(elm.innerHTML);
	});
  document.querySelectorAll('.form-control').forEach(elm => {
		elm.value = data.shift();
	});
}

window.addEventListener('load', function () {
	document.querySelectorAll('table td').forEach(elm => {
		elm.contentEditable = true;
	});
  const table = document.querySelector('table');
  let correct_btn = document.getElementById('correct_btn');
  correct_btn.addEventListener('click', correct);
});