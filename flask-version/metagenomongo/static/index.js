document.addEventListener("DOMContentLoaded", function() {
    // Select all <td> elements within the .table-responsive divs
    document.querySelectorAll('.table-responsive th').forEach(function(th) {
        if (th.innerHTML == "collected_by" || th.innerHTML == "comment"){
            th.classList.add('th-width');
        }
    });
});