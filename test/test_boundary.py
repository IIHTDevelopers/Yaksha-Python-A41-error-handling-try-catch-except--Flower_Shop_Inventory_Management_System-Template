import unittest
import os
import sys
import importlib
from datetime import datetime, timedelta
from io import StringIO
from test.TestUtils import TestUtils

def check_file_exists(filename):
    """Check if a file exists in the current directory."""
    return os.path.exists(filename)

def safely_import_module(module_name):
    """Safely import a module, returning None if import fails."""
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None

def check_function_exists(module, function_name):
    """Check if a function exists in a module."""
    return hasattr(module, function_name) and callable(getattr(module, function_name))

def check_class_exists(module, class_name):
    """Check if a class exists in a module."""
    return hasattr(module, class_name) and isinstance(getattr(module, class_name), type)

def safely_call_function(module, function_name, *args, **kwargs):
    """Safely call a function, returning None if it fails."""
    if not check_function_exists(module, function_name):
        return None
    try:
        # Suppress output during testing
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            result = getattr(module, function_name)(*args, **kwargs)
        finally:
            sys.stdout = old_stdout
        return result
    except Exception:
        sys.stdout = old_stdout
        return None

def safely_create_instance(module, class_name, *args, **kwargs):
    """Safely create an instance, returning None if it fails."""
    if not check_class_exists(module, class_name):
        return None
    try:
        # Suppress output during testing
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            cls = getattr(module, class_name)
            result = cls(*args, **kwargs)
        finally:
            sys.stdout = old_stdout
        return result
    except Exception:
        sys.stdout = old_stdout
        return None

class TestFlowerShopBoundary(unittest.TestCase):
    def setUp(self):
        """Standard setup for all test methods"""
        self.test_obj = TestUtils()
        self.module_obj = safely_import_module("skeleton")
        if self.module_obj is None:
            self.module_obj = safely_import_module("solution")

    def test_boundary_conditions_comprehensive(self):
        """Comprehensive boundary testing for all classes."""
        try:
            if self.module_obj is None:
                self.test_obj.yakshaAssert("test_boundary_conditions_comprehensive", False, "boundary")
                print("test_boundary_conditions_comprehensive = Failed")
                return

            # Test Flower boundary conditions
            if not check_class_exists(self.module_obj, "Flower"):
                self.test_obj.yakshaAssert("test_boundary_conditions_comprehensive", False, "boundary")
                print("test_boundary_conditions_comprehensive = Failed")
                return

            # Valid flower creation
            valid_flower = safely_create_instance(self.module_obj, "Flower", "Rose", 4.99, 50)
            if valid_flower is None:
                self.test_obj.yakshaAssert("test_boundary_conditions_comprehensive", False, "boundary")
                print("test_boundary_conditions_comprehensive = Failed")
                return

            # Check basic attributes
            if not hasattr(valid_flower, 'name') or valid_flower.name != "Rose":
                self.test_obj.yakshaAssert("test_boundary_conditions_comprehensive", False, "boundary")
                print("test_boundary_conditions_comprehensive = Failed")
                return
            if not hasattr(valid_flower, 'price') or valid_flower.price != 4.99:
                self.test_obj.yakshaAssert("test_boundary_conditions_comprehensive", False, "boundary")
                print("test_boundary_conditions_comprehensive = Failed")
                return
            if not hasattr(valid_flower, 'quantity') or valid_flower.quantity != 50:
                self.test_obj.yakshaAssert("test_boundary_conditions_comprehensive", False, "boundary")
                print("test_boundary_conditions_comprehensive = Failed")
                return

            # Test minimum valid values
            min_flower = safely_create_instance(self.module_obj, "Flower", "Lily", 0.01, 1, 1)
            if min_flower is None:
                self.test_obj.yakshaAssert("test_boundary_conditions_comprehensive", False, "boundary")
                print("test_boundary_conditions_comprehensive = Failed")
                return

            # Test valid complex flower names
            valid_names = ["White Rose", "Bird-of-Paradise", "Queen Anne's Lace"]
            for name in valid_names:
                name_flower = safely_create_instance(self.module_obj, "Flower", name, 5.99, 20)
                if name_flower is None:
                    self.test_obj.yakshaAssert("test_boundary_conditions_comprehensive", False, "boundary")
                    print("test_boundary_conditions_comprehensive = Failed")
                    return

            # Test invalid boundary cases - should all fail
            invalid_cases = [
                ("", 4.99, 50),  # empty name
                ("   ", 4.99, 50),  # whitespace name
                ("Rose@123", 4.99, 50),  # invalid characters
                ("Rose", 0, 50),  # zero price
                ("Rose", -4.99, 50),  # negative price
                ("Rose", 4.99, -1),  # negative quantity
                ("Rose", "abc", 50),  # non-numeric price
                ("Rose", 4.99, "ten"),  # non-numeric quantity
            ]

            for name, price, quantity in invalid_cases:
                invalid_flower = safely_create_instance(self.module_obj, "Flower", name, price, quantity)
                if invalid_flower is not None:
                    self.test_obj.yakshaAssert("test_boundary_conditions_comprehensive", False, "boundary")
                    print("test_boundary_conditions_comprehensive = Failed")
                    return

            # Test Inventory boundaries
            if check_class_exists(self.module_obj, "Inventory"):
                inventory = safely_create_instance(self.module_obj, "Inventory")
                if inventory is None:
                    self.test_obj.yakshaAssert("test_boundary_conditions_comprehensive", False, "boundary")
                    print("test_boundary_conditions_comprehensive = Failed")
                    return

                # Test basic attributes
                if not hasattr(inventory, 'flowers') or not isinstance(inventory.flowers, dict):
                    self.test_obj.yakshaAssert("test_boundary_conditions_comprehensive", False, "boundary")
                    print("test_boundary_conditions_comprehensive = Failed")
                    return
                if not hasattr(inventory, 'transaction_log') or not isinstance(inventory.transaction_log, list):
                    self.test_obj.yakshaAssert("test_boundary_conditions_comprehensive", False, "boundary")
                    print("test_boundary_conditions_comprehensive = Failed")
                    return

                # Test with valid flower
                if valid_flower is not None and check_function_exists(inventory, "add_flower"):
                    add_result = safely_call_function(inventory, "add_flower", valid_flower)
                    if add_result is False:
                        self.test_obj.yakshaAssert("test_boundary_conditions_comprehensive", False, "boundary")
                        print("test_boundary_conditions_comprehensive = Failed")
                        return

            self.test_obj.yakshaAssert("test_boundary_conditions_comprehensive", True, "boundary")
            print("test_boundary_conditions_comprehensive = Passed")

        except Exception:
            self.test_obj.yakshaAssert("test_boundary_conditions_comprehensive", False, "boundary")
            print("test_boundary_conditions_comprehensive = Failed")

    def test_freshness_and_stock_boundaries(self):
        """Test freshness validation and stock boundary conditions."""
        try:
            if self.module_obj is None:
                self.test_obj.yakshaAssert("test_freshness_and_stock_boundaries", False, "boundary")
                print("test_freshness_and_stock_boundaries = Failed")
                return

            if not check_class_exists(self.module_obj, "Flower"):
                self.test_obj.yakshaAssert("test_freshness_and_stock_boundaries", False, "boundary")
                print("test_freshness_and_stock_boundaries = Failed")
                return

            # Test flower that expires today (boundary condition)
            expires_today = safely_create_instance(self.module_obj, "Flower", "Daisy", 2.99, 20, 0)
            if expires_today is not None and check_function_exists(expires_today, "is_fresh"):
                is_fresh_today = safely_call_function(expires_today, "is_fresh")
                if is_fresh_today is False:  # Should be fresh on expiry day
                    self.test_obj.yakshaAssert("test_freshness_and_stock_boundaries", False, "boundary")
                    print("test_freshness_and_stock_boundaries = Failed")
                    return

            # Test expired flower
            expired_flower = safely_create_instance(self.module_obj, "Flower", "Orchid", 8.99, 10, 7)
            if expired_flower is not None:
                # Manually set expiry to yesterday
                expired_flower.freshness_date = datetime.now() - timedelta(days=1)
                if check_function_exists(expired_flower, "is_fresh"):
                    is_fresh_expired = safely_call_function(expired_flower, "is_fresh")
                    if is_fresh_expired is True:  # Should not be fresh
                        self.test_obj.yakshaAssert("test_freshness_and_stock_boundaries", False, "boundary")
                        print("test_freshness_and_stock_boundaries = Failed")
                        return

            self.test_obj.yakshaAssert("test_freshness_and_stock_boundaries", True, "boundary")
            print("test_freshness_and_stock_boundaries = Passed")

        except Exception:
            self.test_obj.yakshaAssert("test_freshness_and_stock_boundaries", False, "boundary")
            print("test_freshness_and_stock_boundaries = Failed")

    def test_order_and_processing_boundaries(self):
        """Test order creation and processing boundary conditions."""
        try:
            if self.module_obj is None:
                self.test_obj.yakshaAssert("test_order_and_processing_boundaries", False, "boundary")
                print("test_order_and_processing_boundaries = Failed")
                return

            if not check_class_exists(self.module_obj, "Order") or not check_class_exists(self.module_obj, "Inventory"):
                self.test_obj.yakshaAssert("test_order_and_processing_boundaries", False, "boundary")
                print("test_order_and_processing_boundaries = Failed")
                return

            # Create test inventory
            test_inventory = safely_create_instance(self.module_obj, "Inventory")
            if test_inventory is None:
                self.test_obj.yakshaAssert("test_order_and_processing_boundaries", False, "boundary")
                print("test_order_and_processing_boundaries = Failed")
                return

            # Test valid order creation
            valid_order = safely_create_instance(self.module_obj, "Order", "John Smith", test_inventory)
            if valid_order is None:
                self.test_obj.yakshaAssert("test_order_and_processing_boundaries", False, "boundary")
                print("test_order_and_processing_boundaries = Failed")
                return

            # Test invalid order parameters - should all fail
            invalid_orders = [
                ("", test_inventory),  # empty name
                ("   ", test_inventory),  # whitespace name
                (None, test_inventory),  # None name
                ("John", None),  # None inventory
            ]

            for customer, inventory in invalid_orders:
                invalid_order = safely_create_instance(self.module_obj, "Order", customer, inventory)
                if invalid_order is not None:
                    self.test_obj.yakshaAssert("test_order_and_processing_boundaries", False, "boundary")
                    print("test_order_and_processing_boundaries = Failed")
                    return

            self.test_obj.yakshaAssert("test_order_and_processing_boundaries", True, "boundary")
            print("test_order_and_processing_boundaries = Passed")

        except Exception:
            self.test_obj.yakshaAssert("test_order_and_processing_boundaries", False, "boundary")
            print("test_order_and_processing_boundaries = Failed")

if __name__ == '__main__':
    unittest.main()