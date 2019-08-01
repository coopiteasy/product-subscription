# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Subscription",
    "version": "1.0",
    "depends": [
        "sale",
        "partner_firstname",
        "account_analytic_distribution",
        "l10n_be_invoice_bba",  # todo delocalize
        "email_template_config",
        "mail",
    ],
    "author": "Houssine BAKKALI <houssine@coopiteasy.be>",
    "category": "Sales",
    "website": "www.coopiteasy.be",
    "description": """
    This module manages the subscription for a quantity of product 
    for which we need to invoice the whole amount at the subscription time
    and the delivery needs to be split in the time. This module has been 
    developed for a magazine that publish a new edition every 3 months.
    """,
    'data': [
        'security/ir.model.access.csv',
        'data/product_subscription_data.xml',
        'data/email_templates.xml',
        'views/subscription_views.xml',
        'views/product_views.xml',
        'views/res_partner_views.xml',
        'views/product_release_view.xml',
    ],
    'installable': True,
}
