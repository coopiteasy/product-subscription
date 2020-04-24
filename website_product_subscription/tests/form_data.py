# -*- coding: utf-8 -*-
# Copyright 2020 Coop IT Easy SCRL fs
#   Robin Keunen <robin@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

SR_POST_DATA_BASIC_PERSON = {
    "firstname": u"Enrique",
    "lastname": u"Jones",
    "login": u"enrique@jones.org",
    "confirm_login": u"enrique@jones.org",
    "street": u"Some street",
    "zip_code": u"09876",
    "city": u"bxl",
    "country_id": u"21",  # todo do better
    "subscription": u"1",  # todo do better
    "accepted_condition": "on",
}

SR_POST_DATA_BASIC_COMPANY = {
    "company_name": u"Coop IT Easy",
    "vat": u"BE688967046",
    "firstname": u"Enrique",
    "lastname": u"Jones",
    "login": u"enrique@jones.org",
    "confirm_login": u"enrique@jones.org",
    "street": u"Some street",
    "zip_code": u"09876",
    "city": u"bxl",
    "country_id": u"21",  # todo do better
    "subscription": u"1",  # todo do better
    "accepted_condition": "on",
}

SR_POST_DATA_BASIC_COMPANY_INVOICE = {
    "company_name": u"Coop IT Easy",
    "vat": u"BE688967046",
    "firstname": u"Enrique",
    "lastname": u"Jones",
    "login": u"enrique@jones.org",
    "confirm_login": u"enrique@jones.org",
    "street": u"Some street",
    "zip_code": u"09876",
    "city": u"bxl",
    "country_id": u"21",  # todo do better
    "subscription": u"1",  # todo do better
    "invoice_address": u"on",  # checkbox
    "inv_street": u"Other street",
    "inv_zip_code": u"8765",
    "inv_city": u"Liège",
    "inv_country_id": u"21",
    "accepted_condition": "on",
}

SR_POST_DATA_GIFT_PERSON = {
    "firstname": u"Enrique",
    "lastname": u"Jones",
    "login": u"enrique@jones.org",
    "confirm_login": u"enrique@jones.org",
    "street": u"Some street",
    "zip_code": u"09876",
    "city": u"bxl",
    "country_id": u"21",  # todo do better
    "subscription": u"1",  # todo do better
    "accepted_condition": "on",
    "subscriber_firstname": u"Ella",
    "subscriber_lastname": u"Jones",
    "subscriber_login": u"ella@jones.org",
    "subscriber_confirm_login": u"ella@jones.org",
    "subscriber_street": u"Other street",
    "subscriber_zip_code": u"09876",
    "subscriber_city": u"bxl",
    "subscriber_country_id": u"21",  # todo do better
}

SR_POST_DATA_GIFT_COMPANY = {
    "company_name": u"Coop IT Easy",
    "vat": u"BE688967046",
    "firstname": u"Enrique",
    "lastname": u"Jones",
    "login": u"enrique@jones.org",
    "confirm_login": u"enrique@jones.org",
    "street": u"Some street",
    "zip_code": u"09876",
    "city": u"bxl",
    "country_id": u"21",  # todo do better
    "subscription": u"1",  # todo do better
    "accepted_condition": "on",
    "subscriber_firstname": u"Ella",
    "subscriber_lastname": u"Jones",
    "subscriber_login": u"ella@jones.org",
    "subscriber_confirm_login": u"ella@jones.org",
    "subscriber_street": u"Other street",
    "subscriber_zip_code": u"09876",
    "subscriber_city": u"bxl",
    "subscriber_country_id": u"21",  # todo do better
}

SR_POST_DATA_GENERIC_PERSON_NO_GIFT = {
    "firstname": u"Enrique",
    "lastname": u"Jones",
    "login": u"enrique@jones.org",
    "confirm_login": u"enrique@jones.org",
    "street": u"Some street",
    "zip_code": u"09876",
    "city": u"bxl",
    "country_id": u"21",  # todo do better
    "subscription": u"1",  # todo do better
    "accepted_condition": "on",
}

SR_POST_DATA_GENERIC_COMPANY_NO_GIFT = {
    "company_name": u"Coop IT Easy",
    "vat": u"BE688967046",
    "firstname": u"Enrique",
    "lastname": u"Jones",
    "login": u"enrique@jones.org",
    "confirm_login": u"enrique@jones.org",
    "street": u"Some street",
    "zip_code": u"09876",
    "city": u"bxl",
    "country_id": u"21",  # todo do better
    "subscription": u"1",  # todo do better
    "accepted_condition": "on",
}

SR_POST_DATA_GENERIC_PERSON_GIFT = {
    "firstname": u"Enrique",
    "lastname": u"Jones",
    "login": u"enrique@jones.org",
    "confirm_login": u"enrique@jones.org",
    "street": u"Some street",
    "zip_code": u"09876",
    "city": u"bxl",
    "country_id": u"21",  # todo do better
    "subscription": u"1",  # todo do better
    "accepted_condition": "on",
    "is_gift": "on",
    "subscriber_firstname": u"Ella",
    "subscriber_lastname": u"Jones",
    "subscriber_login": u"ella@jones.org",
    "subscriber_confirm_login": u"ella@jones.org",
    "subscriber_street": u"Other street",
    "subscriber_zip_code": u"09876",
    "subscriber_city": u"bxl",
    "subscriber_country_id": u"21",  # todo do better
}

SR_POST_DATA_GENERIC_COMPANY_GIFT = {
    "company_name": u"Coop IT Easy",
    "vat": u"BE688967046",
    "firstname": u"Enrique",
    "lastname": u"Jones",
    "login": u"enrique@jones.org",
    "confirm_login": u"enrique@jones.org",
    "street": u"Some street",
    "zip_code": u"09876",
    "city": u"bxl",
    "country_id": u"21",  # todo do better
    "subscription": u"1",  # todo do better
    "accepted_condition": "on",
    "is_gift": "on",
    "subscriber_firstname": u"Ella",
    "subscriber_lastname": u"Jones",
    "subscriber_login": u"ella@jones.org",
    "subscriber_confirm_login": u"ella@jones.org",
    "subscriber_street": u"Other street",
    "subscriber_zip_code": u"09876",
    "subscriber_city": u"bxl",
    "subscriber_country_id": u"21",  # todo do better
}
