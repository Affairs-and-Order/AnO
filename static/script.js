/*
ATTEMPT TO MAKE RESOURCEBAR STAY OPEN ON REFRESH

    $(document).ready(function() {
        $(".resourcediv").click(function() {
            var id = $(this).attr("id");

            $('#' + id).find(".resourcedivcontentshow").removeClass("resourcedivcontentshow");
            $('#' + id).addClass("resourcedivcontentshow");
            localStorage.setItem("selectedolditem", id);
        });

        var selectedolditem = localStorage.getItem('selectedolditem');

        if (selectedolditem != null) {
            $('#' + id).find(".resourcedivcontentshow").removeClass("resourcedivcontentshow");
            $('#' + id).addClass("resourcedivcontentshow");
        }
    });
    */
AOS.init();
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
function resourcedivcontentshow() {

    document.getElementById("resourcediv").classList.toggle("resourcedivshow");
    document.getElementById("resourcedivcontent").classList.toggle("resourcedivcontentshow");

}
//SCROLLBAR ANIMATION
window.onscroll = function() { scrolltop() };

function scrolltop() {

    if (document.body.scrollTop > 1 || document.documentElement.scrollTop > 1) {

        document.getElementById("navbar").style.backgroundColor = "rgb(56, 105, 179)";

        document.getElementById("menu").style.transition = "all 0.2s";

    } else {

        document.getElementById("navbar").style.backgroundColor = "rgb(56, 105, 179)";

        document.getElementById("menu").style.transition = "all 0.2s";

    }
}
//resourcediv stay open
/*
var clicked = false

function resourcedivcontentshow() {
    clicked = true
}​
function resourcedivcontentshow() {
    if (clicked = true) {
        alert('Test is true');
        document.getElementById("resourcediv").classList.add("resourcedivshow");
    } else {
        alert('Test is false');
    }
} */
//COUNTRY SLIDER
$(document).ready(function() {

    document.getElementById("countryview").classList.add("countryviewclick");
    document.getElementById("view").classList.add("viewclick");

});
//
function revenuehide() {

    document.getElementById("countryrevenue").classList.add("hidden");

}
//
function newshide() {

    document.getElementById("countrynews").classList.add("hidden");

}
//
function edithide() {

    document.getElementById("countryedit").classList.add("hidden");

}
//
function actionshide() {

    document.getElementById("countryactions").classList.add("hidden");

}
//
function countryview() {


    document.getElementById("countryview").classList.add("countryviewclick");
    document.getElementById("view").classList.add("viewclick");

    //

    document.getElementById("countryrevenue").classList.remove("countryrevenueclick");
    document.getElementById("revenue").classList.remove("revenueclick");

    document.getElementById("countrynews").classList.remove("countrynewsclick");
    document.getElementById("news").classList.remove("newsclick");

    document.getElementById("countryactions").classList.remove("countryactionsclick");
    document.getElementById("actions").classList.remove("actionsclick");

    document.getElementById("countryedit").classList.remove("countryeditclick");
    document.getElementById("edit").classList.remove("editclick");

}
//
function countryrevenue() {

    document.getElementById("countryrevenue").classList.add("countryrevenueclick");
    document.getElementById("revenue").classList.add("revenueclick");


    //

    document.getElementById("countryview").classList.remove("countryviewclick");
    document.getElementById("view").classList.remove("viewclick");

    document.getElementById("countrynews").classList.remove("countrynewsclick");
    document.getElementById("news").classList.remove("newsclick");

    document.getElementById("countryactions").classList.remove("countryactionsclick");
    document.getElementById("actions").classList.remove("actionsclick");

    document.getElementById("countryedit").classList.remove("countryeditclick");
    document.getElementById("edit").classList.remove("editclick");

}
//
function countrynews() {

    document.getElementById("countrynews").classList.add("countrynewsclick");
    document.getElementById("news").classList.add("newsclick");

    //

    document.getElementById("countryview").classList.remove("countryviewclick");
    document.getElementById("view").classList.remove("viewclick");

    document.getElementById("countryrevenue").classList.remove("countryrevenueclick");
    document.getElementById("revenue").classList.remove("revenueclick");



    document.getElementById("countryactions").classList.remove("countryactionsclick");
    document.getElementById("actions").classList.remove("actionsclick");

    document.getElementById("countryedit").classList.remove("countryeditclick");
    document.getElementById("edit").classList.remove("editclick");

}
//
function countryactions() {

    document.getElementById("countryactions").classList.add("countryactionsclick");
    document.getElementById("actions").classList.add("actionsclick");

    //

    document.getElementById("countryview").classList.remove("countryviewclick");
    document.getElementById("view").classList.remove("viewclick");

    document.getElementById("countryrevenue").classList.remove("countryrevenueclick");
    document.getElementById("revenue").classList.remove("revenueclick");

    document.getElementById("countrynews").classList.remove("countrynewsclick");
    document.getElementById("news").classList.remove("newsclick");

    document.getElementById("countryedit").classList.remove("countryeditclick");
    document.getElementById("edit").classList.remove("editclick");

}
//
function countryedit() {

    document.getElementById("countryedit").classList.add("countryeditclick");
    document.getElementById("edit").classList.add("editclick");

    //

    document.getElementById("countryview").classList.remove("countryviewclick");
    document.getElementById("view").classList.remove("viewclick");

    document.getElementById("countryrevenue").classList.remove("countryrevenueclick");
    document.getElementById("revenue").classList.remove("revenueclick");

    document.getElementById("countrynews").classList.remove("countrynewsclick");
    document.getElementById("news").classList.remove("newsclick");

    document.getElementById("countryactions").classList.remove("countryactionsclick");
    document.getElementById("actions").classList.remove("actionsclick");

}
//PROVINCE SLIDER
$(document).ready(function() {

    document.getElementById("provincecity").classList.add("provincecityclick");
    document.getElementById("city").classList.add("cityclick");

});
//
function provincecity() {


    document.getElementById("provincecity").classList.add("provincecityclick");
    document.getElementById("city").classList.add("cityclick");

    //

    document.getElementById("provinceland").classList.remove("provincelandclick");
    document.getElementById("land").classList.remove("landclick");

}
//
function provinceland() {


    document.getElementById("provinceland").classList.add("provincelandclick");
    document.getElementById("land").classList.add("landclick");

    //

    document.getElementById("provincecity").classList.remove("provincecityclick");
    document.getElementById("city").classList.remove("cityclick");
}
//CITY SLIDER
$(document).ready(function() {

    document.getElementById("cityelectricity").classList.add("cityelectricityclick");
    document.getElementById("electricity").classList.add("electricityclick");

});
//
function cityelectricity() {


    document.getElementById("cityelectricity").classList.add("cityelectricityclick");
    document.getElementById("electricity").classList.add("electricityclick");

    //

    document.getElementById("cityretail").classList.remove("cityretailclick");
    document.getElementById("retail").classList.remove("retailclick");

    document.getElementById("cityworks").classList.remove("cityworksclick");
    document.getElementById("works").classList.remove("worksclick");

}
//
function cityretail() {

    document.getElementById("cityretail").classList.add("cityretailclick");
    document.getElementById("retail").classList.add("retailclick");

    //

    document.getElementById("cityelectricity").classList.remove("cityelectricityclick");
    document.getElementById("electricity").classList.remove("electricityclick");

    document.getElementById("cityworks").classList.remove("cityworksclick");
    document.getElementById("works").classList.remove("worksclick");

}
//
function cityworks() {

    document.getElementById("cityworks").classList.add("cityworksclick");
    document.getElementById("works").classList.add("worksclick");

    //

    document.getElementById("cityelectricity").classList.remove("cityelectricityclick");
    document.getElementById("electricity").classList.remove("electricityclick");

    document.getElementById("cityretail").classList.remove("cityretailclick");
    document.getElementById("retail").classList.remove("retailclick");

}
//
//LAND SLIDER
$(document).ready(function() {

    document.getElementById("landmilitary").classList.add("landmilitaryclick");
    document.getElementById("military").classList.add("militaryclick");

});
//
function landmilitary() {


    document.getElementById("landmilitary").classList.add("landmilitaryclick");
    document.getElementById("military").classList.add("militaryclick");

    //

    document.getElementById("landindustry").classList.remove("landindustryclick");
    document.getElementById("industry").classList.remove("industryclick");

    document.getElementById("landprocessing").classList.remove("landprocessingclick");
    document.getElementById("processing").classList.remove("processingclick");

}
//
function landindustry() {

    document.getElementById("landindustry").classList.add("landindustryclick");
    document.getElementById("industry").classList.add("industryclick");

    //

    document.getElementById("landmilitary").classList.remove("landmilitaryclick");
    document.getElementById("military").classList.remove("militaryclick");

    document.getElementById("landprocessing").classList.remove("landprocessingclick");
    document.getElementById("processing").classList.remove("processingclick");

}
//
function landprocessing() {

    document.getElementById("landprocessing").classList.add("landprocessingclick");
    document.getElementById("processing").classList.add("processingclick");

    //

    document.getElementById("landmilitary").classList.remove("landmilitaryclick");
    document.getElementById("military").classList.remove("militaryclick");

    document.getElementById("landindustry").classList.remove("landindustryclick");
    document.getElementById("industry").classList.remove("industryclick");

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

function joinhide() {

    document.getElementById("coalitionjoin").classList.add("hidden");

}

function leaderhide() {

    document.getElementById("coalitionleader").classList.add("hidden");

}

function memberhide() {

    document.getElementById("coalitionmember").classList.add("hidden");

}
//
function coalitiongeneral() {


    document.getElementById("coalitiongeneral").classList.add("coalitiongeneralclick");
    document.getElementById("general").classList.add("generalclick");

    //

    document.getElementById("coalitionjoin").classList.remove("coalitionjoinclick");
    document.getElementById("join").classList.remove("joinclick");

    document.getElementById("coalitionleader").classList.remove("coalitionleaderclick");
    document.getElementById("leader").classList.remove("leaderclick");

    document.getElementById("coalitionmember").classList.remove("coalitionmemberclick");
    document.getElementById("member").classList.remove("memberclick");


}
//
function coalitionjoin() {

    document.getElementById("coalitionjoin").classList.add("coalitionjoinclick");
    document.getElementById("join").classList.add("joinclick");

    //

    document.getElementById("coalitiongeneral").classList.remove("coalitiongeneralclick");
    document.getElementById("general").classList.remove("generalclick");


}
//
function coalitionleader() {

    document.getElementById("coalitionleader").classList.add("coalitionleaderclick");
    document.getElementById("leader").classList.add("leaderclick");

    //

    document.getElementById("coalitiongeneral").classList.remove("coalitiongeneralclick");
    document.getElementById("general").classList.remove("generalclick");

}

function coalitionmember() {

    document.getElementById("coalitionmember").classList.add("coalitionmemberclick");
    document.getElementById("member").classList.add("memberclick");

    //

    document.getElementById("coalitiongeneral").classList.remove("coalitiongeneralclick");
    document.getElementById("general").classList.remove("generalclick");

}
//UPGRADES SLIDER
$(document).ready(function() {

    document.getElementById("upgradeseconomic").classList.add("upgradeseconomicclick");
    document.getElementById("economic").classList.add("economicclick");

});
//
function upgradeseconomic() {

    document.getElementById("upgradeseconomic").classList.add("upgradeseconomicclick");
    document.getElementById("economic").classList.add("economicclick");

    //

    document.getElementById("upgradesmilitary").classList.remove("upgradesmilitaryclick");
    document.getElementById("military").classList.remove("militaryclick");

}
//
function upgradesmilitary() {

    document.getElementById("upgradesmilitary").classList.add("upgradesmilitaryclick");
    document.getElementById("military").classList.add("militaryclick");

    //

    document.getElementById("upgradeseconomic").classList.remove("upgradeseconomicclick");
    document.getElementById("economic").classList.remove("economicclick");

}
// the below 3 functions don't work, the scripts have been paraphrased in countries.html
// var imageBackground = function(event) {
//     var output = document.getElementById('imageBackground');
//     output.src = URL.createObjectURL(event.target.files[0]);
//     output.style.width = "20vw";
//     output.style.height = "11.25vw";
//     output.onload = function() {
//         URL.revokeObjectURL(output.src) // free memory
//     }
// };

// var imageBackground2 = function(event) {
//     var output = document.getElementById('imageBackground2');
//     output.src = URL.createObjectURL(event.target.files[0]);
//     output.style.width = "20vw";
//     output.style.height = "11.25vw";
//     output.onload = function() {
//         URL.revokeObjectURL(output.src) // free memory
//     }
// };
// var imageBackground3 = function(event) {
//     var output = document.getElementById('imageBackground3');
//     output.src = URL.createObjectURL(event.target.files[0]);
//     output.style.width = "20vw";
//     output.style.height = "11.25vw";
//     output.onload = function() {
//         URL.revokeObjectURL(output.src) // free memory
//     }
// };

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

$(document).ready(function() {
    var val = parseInt($('#resourcetag').html());
    //Use the code in the answer above to replace the commas.
    val = numberWithCommas(val);
    $('#resourcetag').text(val);
});



/**/

// function to set a given theme/color-scheme
function setTheme(themeName) {
    localStorage.setItem('theme', themeName);
    document.documentElement.className = themeName;
}

// function to toggle between light and dark theme
function toggleTheme() {
    if (localStorage.getItem('theme') === 'theme-dark') {
        setTheme('theme-light');
    } else {
        setTheme('theme-dark');
    }
}

// Immediately invoked function to set the theme on initial load
(function() {
    if (localStorage.getItem('theme') === 'theme-dark') {
        setTheme('theme-dark');
        document.getElementById('slider').checked = false;
    } else {
        setTheme('theme-light');
        document.getElementById('slider').checked = true;
    }
})();

/*Warchoose stuff*/



// Filter checked inputs and make ready to send by POST request
function assign_parameters() {
    const all_inputs = document.querySelectorAll("input[type=checkbox]");
    const hidden_inputs = document.getElementById("next_button").querySelectorAll("input[type=hidden]");
    let next_hidden = 0;
    let elements = all_inputs.length;

    for (let i = 0; i < elements; i++) {
        if (all_inputs[i].checked) {
            hidden_inputs[next_hidden].value = all_inputs[i].value;
            next_hidden++;

            if (next_hidden == 3) {
                return true;
            }
        }
    }

    return false;
}

function submit_special(e) {
    const special_unit = document.querySelector("input[name=special_unit]");
    if (document.getElementById(11).checked) {
        special_unit.value = "nukes";
    } else if (document.getElementById(10).checked) {
        special_unit.value = "icbms"
    }
}

function submit_next(e) {
    if (assign_parameters()) {
        e.target.parentElement.submit();
    }
}

// POST request for wartarget
function war_target() {
    const element = document.getElementsByName("targeted_unit")[0];
    const all_inputs = document.querySelectorAll("input[type=checkbox]");

    if (element) {
        for (let i = 0; i < all_inputs.length; i++) {
            if (all_inputs[i].checked) {
                element.value = all_inputs[i].value;
            }
        }
    }
}

function myFunction() {
    var element = document.getElementById("myDIV");
    element.classList.remove("mystyle");
}