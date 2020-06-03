//navbar events
function menubardrop() {

    document.getElementById("menubar").classList.toggle("menubarclick");

    document.getElementById("menubardiv").classList.toggle("menubardivshow");

    //    

    document.getElementById("bar1").classList.toggle("barclick1");

    document.getElementById("bar2").classList.toggle("barclick2");

    document.getElementById("bar3").classList.toggle("barclick3");

    document.body.classList.toggle("body");
}


//
$(document).ready(function() {

    document.getElementById("militaryland").classList.add("militarylandclick");
    document.getElementById("land").classList.add("landclick");

    console.log("jQuery ready");

});
//
function militaryland() {

    document.getElementById("militaryland").classList.add("militarylandclick");
    document.getElementById("land").classList.add("landclick");

    //

    document.getElementById("militaryair").classList.remove("militaryairclick");
    document.getElementById("air").classList.remove("airclick");

    document.getElementById("militarywater").classList.remove("militarywaterclick");
    document.getElementById("water").classList.remove("waterclick");

    document.getElementById("militaryspecial").classList.remove("militaryspecialclick");
    document.getElementById("special").classList.remove("specialclick");
}
//
function militaryair() {
    document.getElementById("militaryair").classList.add("militaryairclick");
    document.getElementById("air").classList.add("airclick");

    //

    document.getElementById("militaryland").classList.remove("militarylandclick");
    document.getElementById("land").classList.remove("landclick");

    document.getElementById("militarywater").classList.remove("militarywaterclick");
    document.getElementById("water").classList.remove("waterclick");

    document.getElementById("militaryspecial").classList.remove("militaryspecialclick");
    document.getElementById("special").classList.remove("specialclick");
}
//
function militarywater() {

    document.getElementById("militarywater").classList.add("militarywaterclick");
    document.getElementById("water").classList.add("waterclick");

    //

    document.getElementById("militaryland").classList.remove("militarylandclick");
    document.getElementById("land").classList.remove("landclick");

    document.getElementById("militaryair").classList.remove("militaryairclick");
    document.getElementById("air").classList.remove("airclick");

    document.getElementById("militaryspecial").classList.remove("militaryspecialclick");
    document.getElementById("special").classList.remove("specialclick");
}
//
function militaryspecial() {


    document.getElementById("militaryspecial").classList.add("militaryspecialclick");
    document.getElementById("special").classList.add("specialclick");

    //
    document.getElementById("militaryland").classList.remove("militarylandclick");
    document.getElementById("land").classList.remove("landclick");

    document.getElementById("militaryair").classList.remove("militaryairclick");
    document.getElementById("air").classList.remove("airclick");

    document.getElementById("militarywater").classList.remove("militarywaterclick");
    document.getElementById("water").classList.remove("waterclick");

}