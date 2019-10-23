# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Website Product Subscription Online Payment",
    "version": "9.0.1.0.1",
    "depends": ["website_product_subscription", "website_payment"],
    "author": "Coop IT Easy SCRL",
    "category": "Cooperative management",
    "website": "www.coopiteasy.be",
    "description": """
        This module allows to pay the product subscription online
    """,
    "data": [
        "views/online_payment_template.xml",
        "views/subscription_request_view.xml",
        "views/payment_acquirer_view.xml",
    ],
    "installable": True,
}
