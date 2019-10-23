# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Product Subscription Delivery",
    "version": "1.0",
    "depends": ["product_subscription", "delivery"],
    "author": "Coop IT Easy SCRL",
    "category": "Sales",
    "website": "www.coopiteasy.be",
    "description": """
    This module allows to manager delivery method on production subscription to have
    it set on the invoice without passing by the sale order.
    """,
    "data": ["views/subscription_views.xml", "views/invoice_views.xml"],
    "installable": True,
}
