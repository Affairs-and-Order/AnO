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

    document.getElementById("militaryleft").classList.add("militaryleftclick");
    document.getElementById("land").classList.add("landclick");

    console.log("jQuery ready");

});
//
function militaryleft() {

    document.getElementById("militaryleft").classList.add("militaryleftclick");
    document.getElementById("land").classList.add("landclick");

    //

    document.getElementById("militarycenter").classList.remove("militarycenterclick");
    document.getElementById("air").classList.remove("airclick");

    document.getElementById("militaryright").classList.remove("militaryrightclick");
    document.getElementById("water").classList.remove("waterclick");
}
//
function militarycenter() {

    document.getElementById("militarycenter").classList.add("militarycenterclick");
    document.getElementById("air").classList.add("airclick");

    //

    document.getElementById("militaryleft").classList.remove("militaryleftclick");
    document.getElementById("land").classList.remove("landclick");

    document.getElementById("militaryright").classList.remove("militaryrightclick");
    document.getElementById("water").classList.remove("waterclick");
}
//
function militaryright() {

    document.getElementById("militaryright").classList.add("militaryrightclick");
    document.getElementById("water").classList.add("waterclick");

    //

    document.getElementById("militaryleft").classList.remove("militaryleftclick");
    document.getElementById("land").classList.remove("landclick");

    document.getElementById("militarycenter").classList.remove("militarycenterclick");
    document.getElementById("air").classList.remove("airclick");
}