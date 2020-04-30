# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Product Subscription - Multiple Subscribers",
    "version": "9.0.1.0.0",
    "description": "Allow subscription for multiple subscribers",
    "category": "Sales",
    "author": "Coop IT Easy SCRLfs",
    "website": "https://coopiteasy.be",
    "license": "AGPL-3",
    "depends": ["product_subscription", "website_product_subscription"], #
    "data": [
        "templates/product_subscription_template.xml",
        "views/subscription_views.xml",
    ],
    "demo": [],
    "installable": True,
}
