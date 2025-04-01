import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.utils import random_begin_timestamp, random_end_timestamp, validate_date_format
from marshmallow import ValidationError

class TestUtils(unittest.TestCase):
    
    def test_validate_date_format_success(self):
        try:
            validate_date_format("2025-03-14T09:39:34.551914")
        except ValidationError:
            self.fail("validate_date_format raised ValidationError unexpectedly!")
        
        try:
            validate_date_format("2025-03-14 09:39:34")
        except ValidationError:
            self.fail("validate_date_format raised ValidationError unexpectedly!")
            
        try:    
            validate_date_format("2025-03-14T09:39")
        except ValidationError:
            self.fail("validate_date_format raised ValidationError unexpectedly!")

    def test_validate_date_format_error(self):

        with self.assertRaises(ValidationError):
            validate_date_format("invalid-date")
        
        