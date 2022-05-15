$(function() {
  var form = $('#upload-form');
  var actionUrl = form.attr('action');
  var upload_btn = $("#upload-btn");
  var train_preview_wrapper = $("#train-preview-wrapper");
  var test_preview_wrapper = $("#test-preview-wrapper");
  var train_header = $("#train-header");
  var test_header = $("#test-header");
  var train_btn_wrapper = $('#train-btn-wrapper');
  var train_btn = $("#train-btn");
  var predict_btn_wrapper = $("#predict-btn-wrapper");
  var predict_btn = $("#predict-btn")
  var train_csv_filename, test_csv_filename ,result_csv_filename;
  var result_header = $("#result-header");
  var download_btn_wrapper = $("#download-btn-wrapper");
  var summary_wrapper = $("#summary-wrapper");
  var sources_wrapper = $("#sources-wrapper");
  var result_preview_wrapper = $("#result-preview-wrapper");
  var upload_form_wrapper = $("#upload-form-wrapper");
  var training_btn_wrapper = $("#training-btn-wrapper");
  var download_btn = $("#download-btn");

  upload_btn.click(function() {
    var form_data = new FormData($('#upload-form')[0]);
    $.ajax({
      type: "POST",
      url: actionUrl,
      data: form_data,
      contentType: false,
      cache: false,
      processData: false,
      success: function(data) {
        if(!train_header.is(":hidden")){
          train_preview_wrapper.removeAttr("hidden");

          train_csv_filename = data['csv_filename'];

          $('#train-preview').DataTable( {
            "scrollX": true,
            "ajax": '../' + data['upload_folder'] + '/' +  data['json_filename'],
            "destroy": true,
            "columns": [
                { "data": "Level" },
                { "data": "Date and Time" },
                { "data": "Source" },
                { "data": "Event ID" },
                { "data": "Task Category" },
                { "data": "Description" }
            ]
          });

          if (train_btn.is(":disabled")) {
            train_btn.removeAttr("disabled");
          }
        }

        else if(!test_header.is(":hidden")){
          test_preview_wrapper.removeAttr("hidden");
          predict_btn.removeAttr("disabled");

          test_csv_filename = data['csv_filename'];

          $('#test-preview').DataTable( {
            "scrollX": true,
            "ajax": '../' + data['upload_folder'] + '/' +  data['json_filename'],
            "destroy": true,
            "columns": [
                { "data": "Date and Time" },
                { "data": "Source" },
                { "data": "Event ID" },
                { "data": "Task Category" },
                { "data": "Description" }
            ]
          });

          if(train_btn.is(":disabled")){
            train_btn.removeAttr("disabled");
          }
        }

        
      }
    })
  });

  train_btn.click(function () {
    upload_btn.attr("disabled", true);
    train_btn.replaceWith('<button class="btn btn-secondary" type="button" disabled>\
                        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>\
                        Training Model\
                    </button>')
    $.ajax({
      type: "POST",
      url: '/train_classifier',
      data: {'train_csv_filename': train_csv_filename},
      success: function(data) {
        train_header.attr("hidden", true);
        upload_btn.removeAttr("disabled");
        test_header.removeAttr("hidden");
        train_preview_wrapper.attr("hidden", true);
        train_btn_wrapper.attr("hidden", true);
        predict_btn_wrapper.removeAttr("hidden");
      },
    })
  });

  predict_btn.click(function () {
    upload_btn.attr("disabled", true);
    predict_btn.replaceWith('<button class="btn btn-secondary" type="button" disabled>\
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>\
                    Getting Results Ready\
                </button>');

    $.ajax({
      type: "POST",
      url: '/generate_results',
      data: {'test_csv_filename': test_csv_filename},
      success: function(data) {
        test_header.attr("hidden", true);
        result_header.removeAttr("hidden");
        predict_btn_wrapper.attr("hidden", true);
        download_btn_wrapper.removeAttr("hidden");
        summary_wrapper.removeAttr("hidden");
        sources_wrapper.removeAttr("hidden");
        test_preview_wrapper.attr("hidden", true);
        result_preview_wrapper.removeAttr("hidden");
        upload_form_wrapper.attr("hidden", true);

        result_csv_filename = data['csv_filename'];
        var json_filename = data['json_filename'];
        var upload_folder = data['upload_folder'];
        json_file_path = '../' + upload_folder + '/' + json_filename;
        createCharts(json_file_path);

        $('#result-preview').DataTable( {
          "scrollX": true,
          "ajax": json_file_path,
          "columns": [
              { "data": "Level"},
              { "data": "Date and Time" },
              { "data": "Source" },
              { "data": "Event ID" },
              { "data": "Task Category" },
              { "data": "Description" }
          ]
        } );
      },
    })
  }); 

  download_btn.click(function() {
      window.location.href = "static/files/" + result_csv_filename;
  })
})

function createCharts(file_path) {
    $.getJSON(file_path, function(json) {
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
                    padding: 50
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
                    padding: 50
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
                    padding: 50
                }
            }
        }

        const polar_chart = new Chart(
            $('#polar_chart'),
            config_polar
        )
    });
}