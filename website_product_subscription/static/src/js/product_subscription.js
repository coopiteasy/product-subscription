odoo.define('website_product_subscription.oe_product_subscription', function (require) {
    $(document).ready(function () {
        "use strict";
        var ajax = require('web.ajax');

        function toggle_company_fields() {
            var is_company = $("input[name='is_company']").is(":checked");

            if (is_company) {
                $(".field-company_name").show('quick');
                $("input[name='company_name']").prop("required", true);
                $(".field-vat").show('quick');
                $(".field-invoice_address").show('quick');
            } else {
                $(".field-company_name").hide('quick');
                $("input[name='company_name']").prop("required", false);
                $(".field-vat").hide('quick');
                $(".field-invoice_address").hide('quick');
                $("input[name='invoice_address']").prop("checked", false);
            }
        }

        function toggle_gift_fields() {
            var is_gift = $("input[name='is_gift']").is(":checked");

            if (is_gift) {
                $("div[name='subscriber_info']").show('quick');
                $("input[name='subscriber_firstname']").prop("required", true);
                $("input[name='subscriber_lastname']").prop("required", true);
                $("input[name='subscriber_login']").prop("required", true);
                $("input[name='subscriber_confirm_login']").prop("required", true);
                $("input[name='subscriber_street']").prop("required", true);
                $("input[name='subscriber_zip_code']").prop("required", true);
                $("input[name='subscriber_city']").prop("required", true);
            } else {
                $("div[name='subscriber_info']").hide('quick');
                $("input[name='subscriber_firstname']").prop("required", false);
                $("input[name='subscriber_lastname']").prop("required", false);
                $("input[name='subscriber_login']").prop("required", false);
                $("input[name='subscriber_confirm_login']").prop("required", false);
                $("input[name='subscriber_street']").prop("required", false);
                $("input[name='subscriber_zip_code']").prop("required", false);
                $("input[name='subscriber_city']").prop("required", false);
            }
        }

        function toggle_company_invoice_fields() {
            var invoice_address = $("input[name='invoice_address']").is(":checked");

            if (invoice_address) {
                $(".title-inv_address").show('quick');
                $(".field-inv_street").show('quick');
                $("input[name='inv_street']").prop("required", true);
                $(".field-inv_zip_code").show('quick');
                $("input[name='inv_zip_code']").prop("required", true);
                $(".field-inv_city").show('quick');
                $("input[name='inv_city']").prop("required", true);
                $(".field-inv_country_id").show('quick');
                $("input[name='inv_country_id']").prop("required", true);
            } else {
                $(".title-inv_address").hide('quick');
                $(".field-inv_street").hide('quick');
                $("input[name='inv_street']").prop("required", false);
                $(".field-inv_zip_code").hide('quick');
                $("input[name='inv_zip_code']").prop("required", false);
                $(".field-inv_city").hide('quick');
                $("input[name='inv_city']").prop("required", false);
                $(".field-inv_country_id").hide('quick');
                $("input[name='inv_country_id']").prop("required", false);
            }
        }

        function display_subscription_presentation_text() {
            var sub_template_id = $("#subscription").val();
            ajax.jsonRpc("/subscription/field/presentation_text", 'call', {
				'sub_template_id': sub_template_id
	  		 })
	  		.then(function (data) {
	  			$('#subscription_presentation_text').html(data[sub_template_id].presentation_text);
	        });
        }
        
        display_subscription_presentation_text();
        
        $(".oe_subscribe_form").each(function () {
            toggle_company_fields();
            toggle_company_invoice_fields();
            toggle_gift_fields();
        });

        // fixme select within .oe_subscribe_form
        $("input[name='is_gift']").change(function(ev) {
            toggle_gift_fields();
        });

        $("input[name='is_company']").change(function(ev) {
            toggle_company_fields();
            toggle_company_invoice_fields();
        });

        $("input[name='invoice_address']").change(function(ev) {
            toggle_company_invoice_fields();
        });

        $("select[id='subscription']").change(function(ev) {
            display_subscription_presentation_text();
        });

        $(".oe_product_subscription").each(function () {

            function hide_display() {
                var gift = $("input[name='gift']:checked").val();
                var logged = $("input[name='logged']:checked").val();

                if(gift == "on") {
                    $("div[name='subscriber_info_label']").show('quick');
                    $("div[name='delivery_label']").hide('quick');
                    $("div[name='subscriber_firstname']").show('quick');
                    $("div[name='subscriber_lastname']").show('quick');
                    $("div[name='subscriber_email']").show('quick');
                    $("input[name='subscriber_firstname']").prop('required',true);
                    $("input[name='subscriber_lastname']").prop('required',true);
                    $("input[name='subscriber_email']").prop('required',true);
                } else {
                    $("div[name='subscriber_info_label']").hide('quick');
                    $("div[name='delivery_label']").show('quick');
                    $("div[name='subscriber_firstname']").hide('quick');
                    $("div[name='subscriber_lastname']").hide('quick');
                    $("div[name='subscriber_email']").hide('quick');
                    $("input[name='subscriber_firstname']").prop('required',false);
                    $("input[name='subscriber_lastname']").prop('required',false);
                    $("input[name='subscriber_email']").prop('required',false);
                }
                //alert(logged);
                if(logged == "on" ){
                    $("div[name='email_confirmation_container']").hide('quick');
                    $("input[name='email_confirmation']").prop('required',false);
                    if(gift != 'on'){
                        $("div[name='street_number_container']").hide('quick');
                        $("input[name='street_number']").prop('required',false);
                        $("div[name='box_container']").hide('quick');
                        $("input[name='box']").prop('required',false);
                    }
                }
            }
            hide_display();

            function hide_display_company() {
                var is_company = $("input[name='is_company']:checked").val();

                console.log("in hide_display_company()");
                console.log(is_company);

                if(is_company == "on") {
                    console.log("show company");
                    $("div[name='company']").show('quick');
                    $("div[name='vat_number']").show('quick');
                    $("input[name='company']").prop('required', true);
                } else {
                    console.log("hide company");
                    $("div[name='company']").hide('quick');
                    $("div[name='vat_number']").hide('quick');
                    $("input[name='company']").prop('required', false);
                }
            }
            hide_display_company();

            $("input[name='gift']").click(function(ev) {
                hide_display();
            });
            $("input[name='is_company']").click(function(ev) {
                hide_display_company();
            });
        });
    });
});
