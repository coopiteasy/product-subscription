# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Subscription Web Access",
    "version": "9.0.2.0.1",
    "depends": ["product_subscription", "website_product_subscription"], #
    "author": "Coop IT Easy SCRLfs",
    "category": "Sales",
    "website": "https://www.coopiteasy.be",
    "description": """
    Adds fields and process to tell wether partner has access to the web
    version on the subscription.
    """,
    "data": [
        "data/cron.xml",
        "security/ir.model.access.csv",
        "views/subscription.xml",
        "views/res_partner.xml",
        "views/res_config.xml",
        "templates/product_subscription.xml",
    ],
    "demo": ["demo/demo.xml"],
    "installable": True,
}
