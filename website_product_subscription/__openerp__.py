# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Website Product Subscription",
    "version": "9.0.1.0.2",
    "depends": [
        "base",
        "website",
        "portal",
        "website_recaptcha_reloaded",
        "product_subscription",
    ],
    "author": "Coop IT Easy SCRL",
    "category": "Sales",
    "description": """
    This module add the product subscription forms on the website. It will
     allow to subscribe online for a subscription template.
    """,
    "data": [
        "views/res_company.xml",
        "views/subscription_template_view.xml",
        "views/product_subscription_template.xml",  # todo remove
        "templates/subscription_base.xml",
        "templates/new_subscription_generic.xml",
        "templates/new_subscription_basic.xml",
        "templates/new_subscription_gift.xml",
    ],
    "installable": True,
}
