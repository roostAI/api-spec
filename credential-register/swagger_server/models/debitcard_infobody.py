# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class DebitcardInfobody(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, debit_card_number: str=None, pin: str=None, cvv: str=None, expiry_date: str=None, customer_id: float=None):  # noqa: E501
        """DebitcardInfobody - a model defined in Swagger

        :param debit_card_number: The debit_card_number of this DebitcardInfobody.  # noqa: E501
        :type debit_card_number: str
        :param pin: The pin of this DebitcardInfobody.  # noqa: E501
        :type pin: str
        :param cvv: The cvv of this DebitcardInfobody.  # noqa: E501
        :type cvv: str
        :param expiry_date: The expiry_date of this DebitcardInfobody.  # noqa: E501
        :type expiry_date: str
        :param customer_id: The customer_id of this DebitcardInfobody.  # noqa: E501
        :type customer_id: float
        """
        self.swagger_types = {
            'debit_card_number': str,
            'pin': str,
            'cvv': str,
            'expiry_date': str,
            'customer_id': float
        }

        self.attribute_map = {
            'debit_card_number': 'debitCardNumber',
            'pin': 'pin',
            'cvv': 'cvv',
            'expiry_date': 'expiryDate',
            'customer_id': 'customerId'
        }
        self._debit_card_number = debit_card_number
        self._pin = pin
        self._cvv = cvv
        self._expiry_date = expiry_date
        self._customer_id = customer_id

    @classmethod
    def from_dict(cls, dikt) -> 'DebitcardInfobody':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The debitcardInfobody of this DebitcardInfobody.  # noqa: E501
        :rtype: DebitcardInfobody
        """
        return util.deserialize_model(dikt, cls)

    @property
    def debit_card_number(self) -> str:
        """Gets the debit_card_number of this DebitcardInfobody.


        :return: The debit_card_number of this DebitcardInfobody.
        :rtype: str
        """
        return self._debit_card_number

    @debit_card_number.setter
    def debit_card_number(self, debit_card_number: str):
        """Sets the debit_card_number of this DebitcardInfobody.


        :param debit_card_number: The debit_card_number of this DebitcardInfobody.
        :type debit_card_number: str
        """
        if debit_card_number is None:
            raise ValueError("Invalid value for `debit_card_number`, must not be `None`")  # noqa: E501

        self._debit_card_number = debit_card_number

    @property
    def pin(self) -> str:
        """Gets the pin of this DebitcardInfobody.


        :return: The pin of this DebitcardInfobody.
        :rtype: str
        """
        return self._pin

    @pin.setter
    def pin(self, pin: str):
        """Sets the pin of this DebitcardInfobody.


        :param pin: The pin of this DebitcardInfobody.
        :type pin: str
        """
        if pin is None:
            raise ValueError("Invalid value for `pin`, must not be `None`")  # noqa: E501

        self._pin = pin

    @property
    def cvv(self) -> str:
        """Gets the cvv of this DebitcardInfobody.


        :return: The cvv of this DebitcardInfobody.
        :rtype: str
        """
        return self._cvv

    @cvv.setter
    def cvv(self, cvv: str):
        """Sets the cvv of this DebitcardInfobody.


        :param cvv: The cvv of this DebitcardInfobody.
        :type cvv: str
        """
        if cvv is None:
            raise ValueError("Invalid value for `cvv`, must not be `None`")  # noqa: E501

        self._cvv = cvv

    @property
    def expiry_date(self) -> str:
        """Gets the expiry_date of this DebitcardInfobody.


        :return: The expiry_date of this DebitcardInfobody.
        :rtype: str
        """
        return self._expiry_date

    @expiry_date.setter
    def expiry_date(self, expiry_date: str):
        """Sets the expiry_date of this DebitcardInfobody.


        :param expiry_date: The expiry_date of this DebitcardInfobody.
        :type expiry_date: str
        """
        if expiry_date is None:
            raise ValueError("Invalid value for `expiry_date`, must not be `None`")  # noqa: E501

        self._expiry_date = expiry_date

    @property
    def customer_id(self) -> float:
        """Gets the customer_id of this DebitcardInfobody.


        :return: The customer_id of this DebitcardInfobody.
        :rtype: float
        """
        return self._customer_id

    @customer_id.setter
    def customer_id(self, customer_id: float):
        """Sets the customer_id of this DebitcardInfobody.


        :param customer_id: The customer_id of this DebitcardInfobody.
        :type customer_id: float
        """
        if customer_id is None:
            raise ValueError("Invalid value for `customer_id`, must not be `None`")  # noqa: E501

        self._customer_id = customer_id