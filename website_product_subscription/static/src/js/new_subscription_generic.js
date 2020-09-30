odoo.define('website_product_subscription.oe_new_subscription_generic', function (require) {
    $(document).ready(function () {
        "use strict";
        var ajax = require('web.ajax');

        function toggle_subscriber_div() {
            var is_gift = $("input[name='is_gift']").is(":checked");

            if (is_gift) {
                $("div[name='subscriber_info']").show('quick');
            } else {
                $("div[name='subscriber_info']").hide('quick');
            }
        }

        $(".oe_new_subscription_generic").each(function () {
            toggle_subscriber_div();
        });

        $("input[name='is_gift']").change(function (ev) {
            toggle_subscriber_div();
        });
    });
})
;
