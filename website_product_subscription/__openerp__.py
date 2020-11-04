# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Houssine Bakkali <houssine@coopiteasy.be>
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Website Product Subscription",
    "version": "9.0.2.1.0",
    "depends": [
        "base",
        "website",
        "portal",
        "website_recaptcha_reloaded",
        "product_subscription",
    ],
    "author": "Coop IT Easy SCRLfs",
    "category": "Sales",
    "description": """
    This module add the product subscription forms on the website. It will
     allow to subscribe online for a subscription template.
    """,
    "data": [
        "data/cron.xml",
        "views/res_company.xml",
        "views/subscription_template_view.xml",
        "views/become_subscriber_menu.xml",
        "templates/components.xml",
        "templates/subscribe_thanks.xml",
        "templates/subscribe_form.xml",
        "templates/subscribe_gift_form.xml",
        "templates/subscribe_generic_form.xml",
    ],
    "installable": True,
}
