function isInt(value) {
  var x = parseFloat(value);
  return !isNaN(value) && (x | 0) === x;
}

const COLORS = [
  '#4dc9f6',
  '#f67019',
  '#f53794',
  '#537bc4',
  '#acc236',
  '#166a8f',
  '#00a950',
  '#58595b',
  '#8549ba'
];

var a = {"Ё":"YO","Й":"I","Ц":"TS","У":"U","К":"K","Е":"E","Н":"N","Г":"G","Ш":"SH","Щ":"SCH","З":"Z","Х":"H","Ъ":"'","ё":"yo","й":"i","ц":"ts","у":"u","к":"k","е":"e","н":"n","г":"g","ш":"sh","щ":"sch","з":"z","х":"h","ъ":"'","Ф":"F","Ы":"I","В":"V","А":"a","П":"P","Р":"R","О":"O","Л":"L","Д":"D","Ж":"ZH","Э":"E","ф":"f","ы":"i","в":"v","а":"a","п":"p","р":"r","о":"o","л":"l","д":"d","ж":"zh","э":"e","Я":"Ya","Ч":"CH","С":"S","М":"M","И":"I","Т":"T","Ь":"'","Б":"B","Ю":"YU","я":"ya","ч":"ch","с":"s","м":"m","и":"i","т":"t","ь":"'","б":"b","ю":"yu"};
function transliterate(word){
  return word.split('').map(function (char) {
    return a[char] || char;
  }).join("");
}

function CreateChart(json, root, ul, prefix, name) {
    let tabname = transliterate(name).split(' ').join('_')
    let data = {
        labels: Object.keys(json),
        datasets: []
    };
    let color = 0;
    let pushed = false;

    let li = document.createElement("li");
    let a = document.createElement("a");
    a.href = '#tabs-' + prefix +'-'+ tabname;
    a.textContent = name;
    li.appendChild(a);
    ul.appendChild(li);

    let div = document.createElement("div");
    div.id = 'tabs-' + prefix +'-'+ tabname;
    root.appendChild(div);

    let canvas = document.createElement("canvas");
    canvas.height = "70";
    div.appendChild(canvas);

    for (let [mainKey, value] of Object.entries(json)) {
        for (let [key, val] of Object.entries(value)) {
            if (isInt(val)) {
                for (let index = 0; index < data['datasets'].length; ++index) {
                    if (data['datasets'][index]['label'] == key) {
                        data['datasets'][index]['data'].push(val);
                        pushed = true;
                    }
                }
                if (pushed) {pushed = false;}
                else {
                    let  dsColor = COLORS[color];
                    color = color + 1;
                    data['datasets'].push({
                        label: key,
                        backgroundColor: dsColor,
                        borderColor: dsColor,
                        data: [val,],
                    });
                }
            }
        }
    }

    let config = {
        type: 'line',
        data: data,
        options: {}
    };
    let myChart = new Chart(
        canvas,
        config
    );
}

export function allstats(json) {
    let root = document.getElementById('stats');
    let parent_root = root.parentElement;
    parent_root.setAttribute("style","width:80%");
    let ul = document.createElement("ul");

    root.appendChild(ul);

    let text = json['alltime'];
    delete json['alltime'];

    CreateChart(json, root, ul, 'summary', text);
    let years = Object.keys(json);
    for (let text of years.sort().reverse()) {
        CreateChart(json[text]['months'], root, ul, 'monthly',text);
    }
    $( "#stats" ).tabs();
}

export function clientstats(json) {
    let root = document.getElementById('clients_stats');
    let parent_root = root.parentElement;
    parent_root.setAttribute("style","width:80%");
    let ul = document.createElement("ul");
    root.appendChild(ul);
    let text;
    for (let client of json) {
        let name = transliterate(client['name']).split(' ').join('_');
        let li = document.createElement("li");
        let a = document.createElement("a");
        a.href = '#tabs-' + name
        a.textContent = client['name'];
        li.appendChild(a);
        ul.appendChild(li);

        let div = document.createElement("div");
        div.id = 'tabs-' + name;
        root.appendChild(div);

        let client_root = document.createElement("div");
        client_root.id = 'root_'+client['name'].split(' ').join('_');
        div.appendChild(client_root);
        let client_ul = document.createElement("ul");
        client_root.appendChild(client_ul);

        text = client['alltime'];
        delete client['alltime'];
        delete client['name'];

        CreateChart(client, client_root, client_ul, 'client_summary', text);

        let years = Object.keys(client);
        for (let text of years.sort().reverse()) {
            CreateChart(client[text]['months'], client_root, client_ul, 'client_monthly',text);

        }
        $( "#"+client_root.id ).tabs();
    }
    $( "#clients_stats" ).tabs();
}