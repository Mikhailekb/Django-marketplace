
$(document).ready(function() {
    $('#id_features').change(function() {
        var feature_val_id = $(this).val();
        if(feature_val_id) {
            console.log(feature_val_id)
            $.ajax({
                url: '/get_features/',
                data: {'feature_val_id': feature_val_id},
                success: function(data) {
                    $('#id_features_to').html(data);
                }
            });
        }
    });
});