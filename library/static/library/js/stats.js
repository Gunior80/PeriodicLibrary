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

function CreateChart(json, year = '') {
    let canvas;
    let data = {
        labels: Object.keys(json),
        datasets: []
    };
    let color = 0;
    let pushed = false;
    if (!year) {
        let root = document.getElementById('stats');
        canvas = document.createElement("canvas");
        canvas.id = "MainChart";
        canvas.height = "70";
        root.appendChild(canvas);
        root.insertBefore(canvas, root.children[0]);
    }
    else {
        let ul = document.getElementById('tabs_root');
        let li = document.createElement("li");
        let a = document.createElement("a");
        a.href = '#tabs-'+year;
        a.textContent = year;
        li.appendChild(a);
        ul.appendChild(li);

        let root = document.getElementById('tabs');
        let div = document.createElement("div");
        div.id = 'tabs-'+year;
        root.appendChild(div);

        canvas = document.createElement("canvas");
        canvas.height = "70";
        canvas.id = "MonthlyChart_"+year;
        div.appendChild(canvas);
    }

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

export function draw(json) {

    let root = document.getElementById('stats');
    let tabs = document.createElement("div");
    tabs.id = 'tabs';
    root.appendChild(tabs);
    let ul = document.createElement("ul");
    ul.id = 'tabs_root';
    tabs.appendChild(ul);
    CreateChart(json);
    let years = Object.keys(json);
    for (let year of years) {
        CreateChart(json[year]['months'], year);
    }
    $( "#tabs" ).tabs();
}