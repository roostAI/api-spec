# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.transfer_recurring_add_request_recurring_options_frequency_duration import TransferRecurringAddRequestRecurringOptionsFrequencyDuration  # noqa: F401,E501
from swagger_server import util


class TransferRecurringAddRequestRecurringOptionsFrequency(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, iterate: str=None, duration: TransferRecurringAddRequestRecurringOptionsFrequencyDuration=None):  # noqa: E501
        """TransferRecurringAddRequestRecurringOptionsFrequency - a model defined in Swagger

        :param iterate: The iterate of this TransferRecurringAddRequestRecurringOptionsFrequency.  # noqa: E501
        :type iterate: str
        :param duration: The duration of this TransferRecurringAddRequestRecurringOptionsFrequency.  # noqa: E501
        :type duration: TransferRecurringAddRequestRecurringOptionsFrequencyDuration
        """
        self.swagger_types = {
            'iterate': str,
            'duration': TransferRecurringAddRequestRecurringOptionsFrequencyDuration
        }

        self.attribute_map = {
            'iterate': 'iterate',
            'duration': 'duration'
        }
        self._iterate = iterate
        self._duration = duration

    @classmethod
    def from_dict(cls, dikt) -> 'TransferRecurringAddRequestRecurringOptionsFrequency':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The transferRecurringAddRequest_recurringOptions_frequency of this TransferRecurringAddRequestRecurringOptionsFrequency.  # noqa: E501
        :rtype: TransferRecurringAddRequestRecurringOptionsFrequency
        """
        return util.deserialize_model(dikt, cls)

    @property
    def iterate(self) -> str:
        """Gets the iterate of this TransferRecurringAddRequestRecurringOptionsFrequency.


        :return: The iterate of this TransferRecurringAddRequestRecurringOptionsFrequency.
        :rtype: str
        """
        return self._iterate

    @iterate.setter
    def iterate(self, iterate: str):
        """Sets the iterate of this TransferRecurringAddRequestRecurringOptionsFrequency.


        :param iterate: The iterate of this TransferRecurringAddRequestRecurringOptionsFrequency.
        :type iterate: str
        """

        self._iterate = iterate

    @property
    def duration(self) -> TransferRecurringAddRequestRecurringOptionsFrequencyDuration:
        """Gets the duration of this TransferRecurringAddRequestRecurringOptionsFrequency.


        :return: The duration of this TransferRecurringAddRequestRecurringOptionsFrequency.
        :rtype: TransferRecurringAddRequestRecurringOptionsFrequencyDuration
        """
        return self._duration

    @duration.setter
    def duration(self, duration: TransferRecurringAddRequestRecurringOptionsFrequencyDuration):
        """Sets the duration of this TransferRecurringAddRequestRecurringOptionsFrequency.


        :param duration: The duration of this TransferRecurringAddRequestRecurringOptionsFrequency.
        :type duration: TransferRecurringAddRequestRecurringOptionsFrequencyDuration
        """

        self._duration = duration