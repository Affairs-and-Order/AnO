// ============================================================
// To activate the active class on the links
// ============================================================
// Get the options menu element
var optnCard = document.getElementById("optnCard");

// Get all links with class="option" inside the menu
var optns = optnCard.getElementsByClassName("option");

// Loop through the links and add the active class to the current/clicked link
for (var i = 0; i < optns.length; i++) {
  optns[i].addEventListener("click", function() {
    var current = document.getElementsByClassName("active");
    current[0].className = current[0].className.replace(" active", "");
    this.className += " active";
  });
}
