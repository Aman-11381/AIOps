// $('div.table-wrapper table tbody tr').each(function(){
$('#train-preview').each(function(){
    let level = $(this).find('td:eq(1)').text()

    if (level == 'Information'){
        $(this).addClass('table-info')
    } else if(level == 'Error'){
        $(this).addClass('table-danger')
    } else if (level == 'Warning'){
        $(this).addClass('table-warning')
    } else {
        $(this).addClass('table-danger')
    }
})