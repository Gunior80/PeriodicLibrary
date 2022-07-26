
function colorize_menu(elements, curent){
    for (var i = 0; i < elements.length; i++) {
        elements[i].style.backgroundColor = null;
    }
    curent.style.backgroundColor = "#243FFF";
}

function wait(bool){
    let el = $("#wait");
    if (bool) {
        el.show();
    }
    else {
        el.hide();;
    }
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
            console.log(str);
        }
    });
}

function show_menu(json) {

    $('#nav-list').bstreeview({
        data: json,
        expandIcon: 'fa fa-angle-down fa-fw',
        collapseIcon: 'fa fa-angle-right fa-fw',
        indent: 1.25,
        parentsMarginLeft: '1.5rem',
        openNodeLinkOnNewTab: true
    });
    wait(false);
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
            console.log(str);
        }
    });
}

$( document ).ready(function() {
    $('#search-string').val('');
    wait(true);
    $('form').submit(function(e) {
        $("#nav-list").empty();
        $("#nav-list").removeData();
        wait(true);
        load_menu($('#periodic').val(), $('#search-string').val());
        $('#search-string').val('');
        return false;
    });
    load_menu($('#periodic').val(), $('#search-string').val());
    set_events();
});



