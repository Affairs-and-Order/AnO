//navbar events
function menubardrop() {

    document.getElementById("menubar").classList.toggle("menubarclick");

    document.getElementById("menubardiv").classList.toggle("menubardivshow");

    //    

    document.getElementById("bar1").classList.toggle("barclick1");

    document.getElementById("bar2").classList.toggle("barclick2");

    document.getElementById("bar3").classList.toggle("barclick3");

    //

    document.getElementById("bar1").style.transition = "all 0.2s";

    document.getElementById("bar2").style.transition = "all 0.2s";

    document.getElementById("bar3").style.transition = "all 0.2s";
}
//loginshow
function loginshow() {

    document.getElementById("logindiv").classList.toggle("logindivshow");

}
//loginclose
function loginclose() {

    document.getElementById("logindiv").classList.toggle("logindivshow");

}
//signupshow
function signupshow() {

    document.getElementById("signupdiv").classList.toggle("signupdivshow");

}
//signupclose
function signupclose() {

    document.getElementById("signupdiv").classList.toggle("signupdivshow");

}
//
$(document).ready(function() {
    console.log("jQuery ready");

});