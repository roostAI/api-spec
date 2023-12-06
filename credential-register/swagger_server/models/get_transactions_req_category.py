# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class GetTransactionsReqCategory(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, code_type: str=None, value: List[str]=None, source: str=None):  # noqa: E501
        """GetTransactionsReqCategory - a model defined in Swagger

        :param code_type: The code_type of this GetTransactionsReqCategory.  # noqa: E501
        :type code_type: str
        :param value: The value of this GetTransactionsReqCategory.  # noqa: E501
        :type value: List[str]
        :param source: The source of this GetTransactionsReqCategory.  # noqa: E501
        :type source: str
        """
        self.swagger_types = {
            'code_type': str,
            'value': List[str],
            'source': str
        }

        self.attribute_map = {
            'code_type': 'codeType',
            'value': 'value',
            'source': 'source'
        }
        self._code_type = code_type
        self._value = value
        self._source = source

    @classmethod
    def from_dict(cls, dikt) -> 'GetTransactionsReqCategory':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The GetTransactionsReq_category of this GetTransactionsReqCategory.  # noqa: E501
        :rtype: GetTransactionsReqCategory
        """
        return util.deserialize_model(dikt, cls)

    @property
    def code_type(self) -> str:
        """Gets the code_type of this GetTransactionsReqCategory.

        either MCC or TransactionCode  # noqa: E501

        :return: The code_type of this GetTransactionsReqCategory.
        :rtype: str
        """
        return self._code_type

    @code_type.setter
    def code_type(self, code_type: str):
        """Sets the code_type of this GetTransactionsReqCategory.

        either MCC or TransactionCode  # noqa: E501

        :param code_type: The code_type of this GetTransactionsReqCategory.
        :type code_type: str
        """

        self._code_type = code_type

    @property
    def value(self) -> List[str]:
        """Gets the value of this GetTransactionsReqCategory.

        it is an array of arrays for MCC  # noqa: E501

        :return: The value of this GetTransactionsReqCategory.
        :rtype: List[str]
        """
        return self._value

    @value.setter
    def value(self, value: List[str]):
        """Sets the value of this GetTransactionsReqCategory.

        it is an array of arrays for MCC  # noqa: E501

        :param value: The value of this GetTransactionsReqCategory.
        :type value: List[str]
        """

        self._value = value

    @property
    def source(self) -> str:
        """Gets the source of this GetTransactionsReqCategory.

        usually - Internal  # noqa: E501

        :return: The source of this GetTransactionsReqCategory.
        :rtype: str
        """
        return self._source

    @source.setter
    def source(self, source: str):
        """Sets the source of this GetTransactionsReqCategory.

        usually - Internal  # noqa: E501

        :param source: The source of this GetTransactionsReqCategory.
        :type source: str
        """

        self._source = source