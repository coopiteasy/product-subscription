# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <Houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Website Product Subscription",
    "version": "1.0",
    "depends": [
        "base",
        "website",
        "portal",
        "website_recaptcha_reloaded",
        "product_subscription",
        # "base_vat",
    ],
    "author": "Coop IT Easy SCRL",
    "category": "Sales",
    "description": """
    This module add the product subscription forms on the website. It will allow
    to subscribe online for a subscription template.
    """,
    'data': [
        'views/product_subscription_template.xml',
    ],
    'installable': True,
}
