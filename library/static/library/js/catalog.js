
function colorize_menu(elements, curent) {
    for (var i = 0; i < elements.length; i++) {
        elements[i].style.backgroundColor = null;
    }
    curent.style.backgroundColor = "#243FFF";
}

function wait(bool) {
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
            library_post({
                'action': 'pdf',
                'document': this.id
            });
        };
    }
}

function send(msg, addr, action) {
    $.ajax({
        type: 'POST',
        url: addr,
        data: msg,
        success: action,
        error: function(xhr, str){
            console.log(str);
        }
    });
}

function library_post(options) {
    let token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    let msg = { csrfmiddlewaretoken: token};
    let addr, action;
    switch (options['action'])
    {
       case "pdf":
           addr = "/load_url";
           msg = Object.assign({}, msg, {'document': options['document']});
           action = function(data) {
                $('#content')[0].src = '/viewer?file='+data["url"];
           };
           send(msg, addr, action);
           break;
       case "menu":
           addr = "/load_menu";
           msg = Object.assign({}, msg, {'periodic': options['periodic'], "search-string": options['search-string']});
           action = function(data) {
                show_menu(data);
           };
           send(msg, addr, action);
           break;
       case "autocomplete":
           addr = "/load_autocomplete";
           msg = Object.assign({}, msg, {'periodic': options['periodic']});
           action = function(data) {
                init_autocomplete(data);
           };
           send(msg, addr, action);
           break;
       default:
           alert('Error');
           break;
    }
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

function init_autocomplete(menuitems) {
    new Autocomplete('#autocomplete', {
        search: input => {
            if (input.length < 1) { return [] }
                return menuitems.filter(menuitem => {
                    return menuitem.toLowerCase().startsWith(input.toLowerCase())
                })
        }
    })
}

$( document ).ready(function() {
    $('#search-string').val('');
    wait(true);
    $('form').submit(function(e) {
        $("#nav-list").empty();
        $("#nav-list").removeData();
        wait(true);
        library_post({
            'action': 'menu',
            'periodic': $('#periodic').val(),
            'search-string': $('#search-string').val()
        });
        $('#search-string').val('');
        return false;
    });
    library_post({
        'action': 'menu',
        'periodic': $('#periodic').val(),
        'str': $('#search-string').val()
    });
    library_post({
        'action': 'autocomplete',
        'periodic': $('#periodic').val()
    });
    set_events();

    // https://www.youtube.com/watch?v=Ch85i8yNT6E
    // https://github.com/trevoreyre/autocomplete/tree/master/packages/autocomplete-js

});



