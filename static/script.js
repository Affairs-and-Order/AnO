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


//MILITARY SLIDER
$(document).ready(function() {

    document.getElementById("militaryland").classList.add("militarylandclick");
    document.getElementById("land").classList.add("landclick");

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
//COALITION SLIDER
$(document).ready(function() {

    document.getElementById("coalitiongeneral").classList.add("coalitiongeneralclick");
    document.getElementById("general").classList.add("generalclick");

});
//
function coalitiongeneral() {


    document.getElementById("coalitiongeneral").classList.add("coalitiongeneralclick");
    document.getElementById("general").classList.add("generalclick");

    //

    document.getElementById("coalitionabout").classList.remove("coalitionaboutclick");
    document.getElementById("about").classList.remove("aboutclick");

    document.getElementById("coalitionjoin").classList.remove("coalitionjoinclick");
    document.getElementById("join").classList.remove("joinclick");

    document.getElementById("coalitionleader").classList.remove("coalitionleaderclick");
    document.getElementById("leader").classList.remove("leaderclick");

    document.getElementById("coalitionmember").classList.remove("coalitionmemberclick");
    document.getElementById("member").classList.remove("member");


}
//
function coalitionabout() {



    document.getElementById("coalitionabout").classList.add("coalitionaboutclick");
    document.getElementById("about").classList.add("aboutclick");

    //

    document.getElementById("coalitiongeneral").classList.remove("coalitiongeneralclick");
    document.getElementById("general").classList.remove("generalclick");

    document.getElementById("coalitionjoin").classList.remove("coalitionjoinclick");
    document.getElementById("join").classList.remove("joinclick");

    document.getElementById("coalitionleader").classList.remove("coalitionleaderclick");
    document.getElementById("leader").classList.remove("leaderclick");

    document.getElementById("coalitionmember").classList.remove("coalitionmemberclick");
    document.getElementById("member").classList.remove("member");


}
//
function coalitionjoin() {

    document.getElementById("coalitionjoin").classList.add("coalitionjoinclick");
    document.getElementById("join").classList.add("joinclick");

    //

    document.getElementById("coalitiongeneral").classList.remove("coalitiongeneralclick");
    document.getElementById("general").classList.remove("generalclick");

    document.getElementById("coalitionabout").classList.remove("coalitionaboutclick");
    document.getElementById("about").classList.remove("aboutclick");

    document.getElementById("coalitionleader").classList.remove("coalitionleaderclick");
    document.getElementById("leader").classList.remove("leaderclick");

    document.getElementById("coalitionmember").classList.remove("coalitionmemberclick");
    document.getElementById("member").classList.remove("member");


}
//
function coalitionleader() {

    document.getElementById("coalitionleader").classList.add("coalitionleaderclick");
    document.getElementById("leader").classList.add("leaderclick");

    //

    document.getElementById("coalitiongeneral").classList.remove("coalitiongeneralclick");
    document.getElementById("general").classList.remove("generalclick");

    document.getElementById("coalitionabout").classList.remove("coalitionaboutclick");
    document.getElementById("about").classList.remove("aboutclick");

    document.getElementById("coalitionjoin").classList.remove("coalitionjoinclick");
    document.getElementById("join").classList.remove("joinclick");

    document.getElementById("coalitionmember").classList.remove("coalitionmemberclick");
    document.getElementById("member").classList.remove("member");


}

function coalitionmember() {

    document.getElementById("coalitionmember").classList.add("coalitionmemberclick");
    document.getElementById("member").classList.add("member");

    //

    document.getElementById("coalitiongeneral").classList.remove("coalitiongeneralclick");
    document.getElementById("general").classList.remove("generalclick");

    document.getElementById("coalitionabout").classList.remove("coalitionaboutclick");
    document.getElementById("about").classList.remove("aboutclick");

    document.getElementById("coalitionjoin").classList.remove("coalitionjoinclick");
    document.getElementById("join").classList.remove("joinclick");

    document.getElementById("coalitionleader").classList.remove("coalitionleaderclick");
    document.getElementById("leader").classList.remove("leaderclick");

}