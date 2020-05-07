//navbar events
function menubardrop() {

    document.getElementById("menubar").classList.toggle("menubarclick");

    document.getElementById("menubardiv").classList.toggle("menubardivshow");

    //    

    document.getElementById("bar1").classList.toggle("barclick1");

    document.getElementById("bar2").classList.toggle("barclick2");

    document.getElementById("bar3").classList.toggle("barclick3");
}
//loginshow
function loginshow() {

    document.getElementById("logindiv").classList.toggle("logindivshow");

    document.getElementById("signupdiv").classList.remove("signupdivshow");

}
//loginclose
function loginclose() {

    document.getElementById("logindiv").classList.toggle("logindivshow");

}
//signupshow
function signupshow() {

    document.getElementById("signupdiv").classList.toggle("signupdivshow");

    document.getElementById("logindiv").classList.remove("logindivshow");

}
//signupclose
function signupclose() {

    document.getElementById("signupdiv").classList.toggle("signupdivshow");

}
//
$(document).ready(function() {
    console.log("jQuery ready");

});