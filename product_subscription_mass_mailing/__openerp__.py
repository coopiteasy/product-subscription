# -*- coding: utf-8 -*-
# Copyright 2019 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Product Subscription - Mass Mailing',
    'version': '9.0.1.0.0',
    'description': 'Define criteria to send email to subscribers',
    'category': 'Sales',
    'author': 'Coop IT Easy SCRL',
    'website': 'https://coopiteasy.be',
    'license': 'AGPL-3',
    'depends': [
        'mail',
        'mass_mailing',
        'product_subscription',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/mailing_criterium.xml',
        'views/subscription.xml',
        'data/cron.xml',
    ],
    'demo': [],
    'installable': True,
}
