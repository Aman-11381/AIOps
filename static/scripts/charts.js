$.getJSON("../static/files/result.json", function(json) {
    freq = {
        "Information": 0,
        "Warning": 0,
        "Error": 0,
        "Critical": 0
    };

    top_sources = {};

    for(let i=0; i<json.data.length; i++){
        let record = json.data[i]

        freq[record.Level]++;

        if(record.Level == 'Error' || record.Level == 'Critical') {
            if(record.Source in top_sources)
                top_sources[record.Source]++;
            else top_sources[record.Source] = 1;
        }
    }

    let items = Object.keys(top_sources).map(
        (key) => { return [key, top_sources[key]] });

    items.sort(
        (first, second) => { return first[1] - second[1] }
    );

    let sources = items.map(
        (e) => { return e[0] });
    
    let source_count = items.map(
        (e) => { return e[1] });

    sources = sources.slice(-5);
    source_count = source_count.slice(-5);
    
    const data = {
        labels: Object.keys(freq),
        datasets: [{
            data: Object.values(freq),
            backgroundColor: [
                'rgba(54, 162, 235, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(255, 159, 64, 0.2)',
                'rgba(255, 99, 132, 0.2)',
            ],
            borderColor: [
                'rgb(54, 162, 235)',
                'rgb(75, 192, 192)',
                'rgb(255, 159, 64)',
                'rgb(255, 99, 132)',
            ],
            borderWidth: 1
        }]
    }
    
    const config = {
        type: 'bar',
        data: data,
        options: {
            plugins:{
                legend: {
                    display: false
                }
            },
            layout: {
                padding: 20
            }
        }
    };
   
    const bar_chart = new Chart(
        $('#bar_chart'),
        config
    );

    const config_doughnut = {
        type: 'doughnut',
        data: data,
        options: {
            layout: {
                padding: 20
            }
        }
    }

    const doughnut_chart = new Chart(
        $('#doughnut_chart'),
        config_doughnut
    )

    const data_polar = {
        labels: sources,
        datasets: [{
            data: source_count,
            backgroundColor: [
                'rgba(54, 162, 235, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(255, 159, 64, 0.2)',
                'rgba(255, 99, 132, 0.2)',
                'rgba(153, 102, 255, 0.2)',
            ],
            borderColor: [
                'rgb(54, 162, 235)',
                'rgb(75, 192, 192)',
                'rgb(255, 159, 64)',
                'rgb(255, 99, 132)',
                'rgb(153, 102, 255)',
            ],
            borderWidth: 1
        }]
    }

    const config_polar = {
        type: 'polarArea',
        data: data_polar,
        options: {
            layout: {
                padding: 20
            }
        }
    }

    const polar_chart = new Chart(
        $('#polar_chart'),
        config_polar
    )
});

