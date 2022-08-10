var full_json;

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
            $('#cover').hide();
            $('#content').show();
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
                $('#content')[0].src = '/viewer/?file='+data["url"];
            };
            send(msg, addr, action);
            break;
        case "menu":
            if (full_json && !options['search-string']) {
                show_menu(full_json);
                break;
            }
            addr = "/load_menu";
            msg = Object.assign({}, msg, {'periodic': options['periodic'], "search-string": options['search-string']});
            action = function(data) {
                if (!options['search-string']) {
                    full_json = data;
                }
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
    var availableTags = menuitems;

    function split( val ) {
        return val.split( /,\s*/ );
    }
    function extractLast( term ) {
        return split( term ).pop();
    }

    $( "#search-string" ).on( "keydown", function( event ) {
        if ( event.keyCode === $.ui.keyCode.TAB &&
        $( this ).autocomplete( "instance" ).menu.active ) {
            event.preventDefault();
        }
    })
    .autocomplete({
        minLength: 0,
        source: function( request, response ) {
            response( $.ui.autocomplete.filter(
            availableTags, extractLast( request.term ) ) );
        },
        focus: function() {
            return false;
        },
        select: function( event, ui ) {
            var terms = split( this.value );
            terms.pop();
            terms.push( ui.item.value );
            terms.push( "" );
            this.value = terms.join( ", " );
            return false;
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

    $('#content').hide();
    set_events();
});



