odoo.define('product_subscription_web_access.oe_product_subscription', function (require) {
    $(document).ready(function () {
        "use strict";
        var ajax = require('web.ajax');

        function display_web_access_presentation() {
            var sub_template_id = $("#subscription").val();
            ajax.jsonRpc("/subscription/field/web_access_presentation", 'call', {
				'sub_template_id': sub_template_id
	  		 })
	  		.then(function (data) {
	  			$('#web_access_presentation').html(data[sub_template_id].web_access_presentation);
	        });
        }
        
        display_web_access_presentation();
        
        $("select[id='subscription']").change(function(ev) {
            display_web_access_presentation();
        });
    });
});
