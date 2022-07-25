
function colorize_menu(elements, curent){
    for (var i = 0; i < elements.length; i++) {
        elements[i].style.backgroundColor = null;
    }
    curent.style.backgroundColor = "green";
}

function set_events() {
    var elements = document.querySelectorAll(".menu-item");
    for (var i = 0; i < elements.length; i++) {
        elements[i].onclick = function(e){
            colorize_menu(elements, this)
            load_pdf(this.id);
        };
    }
}

function load_pdf(doc){
    let token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    let msg = { csrfmiddlewaretoken: token, document: doc };
    $.ajax({
        type: 'POST',
        url: "/load_url",
        data: msg,
        success: function(data) {
            $('#content')[0].src = '/viewer?file='+data["url"];
        },
        error:  function(xhr, str){
            alert(str);
        }
    });
}

function show_menu(json) {
    $("#nav-list").empty();
    $("#nav-list").removeData();
    $('#nav-list').bstreeview({
        data: json,
        expandIcon: 'fa fa-angle-down fa-fw',
        collapseIcon: 'fa fa-angle-right fa-fw',
        indent: 1.00,
        parentsMarginLeft: '1.00rem',
        openNodeLinkOnNewTab: true
    });
    set_events();
}

function load_menu(periodic, string){
    let token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    let msg = { csrfmiddlewaretoken: token, periodical: periodic, str: string};
    $.ajax({
        type: 'POST',
        url: "/load_menu",
        data: msg,
        success: function(data) {
            show_menu(data['menu']);
        },
        error:  function(xhr, str){
            alert(str);
        }
    });
}

$( document ).ready(function() {
    load_menu(1,"");
    set_events();
});

function search(){

}