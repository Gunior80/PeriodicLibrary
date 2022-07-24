
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

$( document ).ready(function() {
    set_events();
});

function load_pdf(doc){
    let token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    let msg = { csrfmiddlewaretoken: token, document: doc };
    $.ajax({
        type: 'POST',
        url: "/load",
        data: msg,
        success: function(data) {
            $('#content')[0].src = '/viewer?file='+data["url"];
        },
        error:  function(xhr, str){
            alert(str);
        }
    });
}

function search(){
    $("#nav-list").empty();
    $("#nav-list").removeData();
    var json = [{text: "{{ periodic.name }}",nodes: [{text: "{{ year }}",nodes: [{text: "{{ month }}",nodes: [{id: "{{ instance.id }}",class: "menu-item",text: "{{ instance.shortname }}",},]},]},]},];

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