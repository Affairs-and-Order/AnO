//navbar events
function menubardrop() {

    document.getElementById("menubar").classList.toggle("menubarclick");

    document.getElementById("menubardiv").classList.toggle("menubardivshow");

    //    

    document.getElementById("bar1").classList.toggle("barclick1");

    document.getElementById("bar2").classList.toggle("barclick2");

    document.getElementById("bar3").classList.toggle("barclick3");
}

var modalOpen = false;

//loginshow
function loginshow() {

    // this is required so people cant open multiple modals at once

    if (modalOpen == false) {
        document.getElementById("logindiv").classList.toggle("logindivshow");
        modalOpen = true;
    } else {
        return;
    }

    document.getElementById("signupdiv").classList.remove("signupdivshow");

}
//loginclose
function loginclose() {

    document.getElementById("logindiv").classList.toggle("logindivshow");
    modalOpen = false;

}
//signupshow
function signupshow() {

     // this is required so people cant open multiple modals at once

    if (modalOpen == false) {
        document.getElementById("signupdiv").classList.toggle("signupdivshow");
        modalOpen = true;
    } else {
        return;
    }

    document.getElementById("logindiv").classList.remove("logindivshow");

}
//signupclose
function signupclose() {

    document.getElementById("signupdiv").classList.toggle("signupdivshow");
    modalOpen = false;

}
//
$(document).ready(function() {
    console.log("jQuery ready");

});