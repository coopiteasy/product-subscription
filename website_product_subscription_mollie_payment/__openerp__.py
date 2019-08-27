# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Website Product Subscription Mollie Payment",
    "version": "9.0.1.0.1",
<<<<<<< Upstream, based on branch '9.0_enable_online_payment' of https://github.com/coopiteasy/product-subscription.git
    "depends": [
        "website_product_subscription",
        "website_product_subscription_online_payment",
        "payment_mollie_official"
        ],
=======
    "depends": ["website_product_subscription_online_payment",
                "payment_mollie_official"],
>>>>>>> f2f6829 [IMP] make it generic
    "author": "Coop IT Easy SCRL",
    "category": "Cooperative management",
    'website': "www.coopiteasy.be",
    "description": """
        This module is the glue to allow product subscription online payment
        "through mollie.
    """,
    'data': [
    ],
    'installable': True,
    'auto_install': True,
}
