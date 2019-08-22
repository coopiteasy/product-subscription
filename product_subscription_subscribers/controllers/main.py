# -*- coding: utf-8 -*-
from openerp import http
from openerp.http import request
from openerp.tools.translate import _

from openerp.addons.website_product_subscription.controllers.main import WebsiteProductSubscription


class WebsiteProductSubscriptionSubscribers(WebsiteProductSubscription):

    def fill_values(self, values, load_from_user=False):
        values = (
            super(WebsiteProductSubscriptionSubscribers, self)
            .fill_values(values, load_from_user)
        )
        if load_from_user and request.env.user.login != 'public':
            emails = request.env.user.partner_id.child_ids.mapped('email')
            additionnal_subscribers = {
                'additionnal_email_%s' % (i + 1): email for i, email in enumerate(emails)
            }
        else:
            additionnal_subscribers = {
                'additionnal_email_1': values.get('additionnal_email_1', ''),
                'additionnal_email_2': values.get('additionnal_email_2', ''),
                'additionnal_email_3': values.get('additionnal_email_3', ''),
                'additionnal_email_4': values.get('additionnal_email_4', ''),
                'additionnal_email_5': values.get('additionnal_email_5', ''),
                'additionnal_email_6': values.get('additionnal_email_6', ''),
            }

        values.update(additionnal_subscribers)
        return values

    def create_additionnal_subscriber(self, email, subscriber):
        partner = (
            request.env['res.partner']
                   .sudo()
                   .search([('email', '=', email)])
        )
        if partner:
            partner.parent_id = subscriber
            return partner[0]
        else:
            partner = (
                request.env['res.partner']
                       .sudo()
                       .create({
                    'name': email,
                    'email': email,
                    'customer': True,
                    'parent_id': subscriber.id,
            }))
            return partner

    def create_subscription_request(self, **kwargs):
        subscription = (
            super(WebsiteProductSubscriptionSubscribers, self)
            .create_subscription_request(**kwargs)
        )

        additionnal_subscribers = [
            kwargs.get('additionnal_email_1', ''),
            kwargs.get('additionnal_email_2', ''),
            kwargs.get('additionnal_email_3', ''),
            kwargs.get('additionnal_email_4', ''),
            kwargs.get('additionnal_email_5', ''),
            kwargs.get('additionnal_email_6', ''),
        ]
        additionnal_subscribers = filter(lambda el: el, additionnal_subscribers)

        additional_subscriber_ids = [
            self.create_additionnal_subscriber(email, subscription.subscriber).id  # noqa
            for email in additionnal_subscribers
        ]
        subscription.write({
            'additional_subscribers':
                [(6, _,  additional_subscriber_ids)]
        })

        return subscription
