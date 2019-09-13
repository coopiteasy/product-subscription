# coding: utf-8


def migrate(cr, version):
    """Set the new webaccess field if it is empty."""
    cr.execute(
        """
        UPDATE product_subscription_request
        SET websubscriber = subscriber
        WHERE websubscriber IS NULL
        """
    )
