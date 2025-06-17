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

class TestFlowerShopExceptional(unittest.TestCase):
    def setUp(self):
        """Standard setup for all test methods"""
        self.test_obj = TestUtils()
        self.module_obj = safely_import_module("skeleton")
        if self.module_obj is None:
            self.module_obj = safely_import_module("solution")

    def test_exception_hierarchy_and_validation(self):
        """Test complete exception hierarchy and validation exceptions."""
        try:
            if self.module_obj is None:
                self.test_obj.yakshaAssert("test_exception_hierarchy_and_validation", False, "exceptional")
                print("test_exception_hierarchy_and_validation = Failed")
                return

            # Test exception hierarchy
            exception_classes = [
                "FlowerShopException", "InvalidFlowerDataError", "InvalidOrderError", 
                "OutOfStockError", "ExpiredFlowerError"
            ]
            
            for exc_name in exception_classes:
                if not check_class_exists(self.module_obj, exc_name):
                    self.test_obj.yakshaAssert("test_exception_hierarchy_and_validation", False, "exceptional")
                    print("test_exception_hierarchy_and_validation = Failed")
                    return

            # Test FlowerShopException functionality
            if check_class_exists(self.module_obj, "FlowerShopException"):
                # Test with error code
                base_exception = safely_create_instance(self.module_obj, "FlowerShopException", "Test message", "E999")
                if base_exception is not None:
                    error_str = str(base_exception)
                    if "[E999]" not in error_str or "Test message" not in error_str:
                        self.test_obj.yakshaAssert("test_exception_hierarchy_and_validation", False, "exceptional")
                        print("test_exception_hierarchy_and_validation = Failed")
                        return

            # Test Flower validation exceptions
            if check_class_exists(self.module_obj, "Flower"):
                invalid_flowers = [
                    ("", 4.99, 50),  # empty name
                    ("Rose", -1, 50),  # negative price
                    ("Rose", 4.99, -10),  # negative quantity
                ]
                
                for name, price, quantity in invalid_flowers:
                    flower = safely_create_instance(self.module_obj, "Flower", name, price, quantity)
                    if flower is not None:  # Should fail
                        self.test_obj.yakshaAssert("test_exception_hierarchy_and_validation", False, "exceptional")
                        print("test_exception_hierarchy_and_validation = Failed")
                        return

            self.test_obj.yakshaAssert("test_exception_hierarchy_and_validation", True, "exceptional")
            print("test_exception_hierarchy_and_validation = Passed")

        except Exception:
            self.test_obj.yakshaAssert("test_exception_hierarchy_and_validation", False, "exceptional")
            print("test_exception_hierarchy_and_validation = Failed")

    def test_inventory_and_order_exceptions(self):
        """Test inventory and order operation exceptions."""
        try:
            if self.module_obj is None:
                self.test_obj.yakshaAssert("test_inventory_and_order_exceptions", False, "exceptional")
                print("test_inventory_and_order_exceptions = Failed")
                return

            # Test inventory exceptions
            if check_class_exists(self.module_obj, "Inventory"):
                inventory = safely_create_instance(self.module_obj, "Inventory")
                if inventory is None:
                    self.test_obj.yakshaAssert("test_inventory_and_order_exceptions", False, "exceptional")
                    print("test_inventory_and_order_exceptions = Failed")
                    return

                # Test invalid add_flower operations
                invalid_objects = ["not_flower", 123, None]
                for invalid_obj in invalid_objects:
                    if check_function_exists(inventory, "add_flower"):
                        add_result = safely_call_function(inventory, "add_flower", invalid_obj)
                        if add_result is not None:  # Should fail
                            self.test_obj.yakshaAssert("test_inventory_and_order_exceptions", False, "exceptional")
                            print("test_inventory_and_order_exceptions = Failed")
                            return

                # Test invalid remove operations
                remove_result = safely_call_function(inventory, "remove_flower", "NonExistent", 5)
                if remove_result is not None:  # Should fail
                    self.test_obj.yakshaAssert("test_inventory_and_order_exceptions", False, "exceptional")
                    print("test_inventory_and_order_exceptions = Failed")
                    return

            # Test order exceptions
            test_inventory = safely_create_instance(self.module_obj, "Inventory")
            if test_inventory is not None:
                # Test invalid order creation
                invalid_order = safely_create_instance(self.module_obj, "Order", "", test_inventory)
                if invalid_order is not None:  # Should fail
                    self.test_obj.yakshaAssert("test_inventory_and_order_exceptions", False, "exceptional")
                    print("test_inventory_and_order_exceptions = Failed")
                    return

            self.test_obj.yakshaAssert("test_inventory_and_order_exceptions", True, "exceptional")
            print("test_inventory_and_order_exceptions = Passed")

        except Exception:
            self.test_obj.yakshaAssert("test_inventory_and_order_exceptions", False, "exceptional")
            print("test_inventory_and_order_exceptions = Failed")

    def test_transaction_rollback_and_report_exceptions(self):
        """Test transaction logging, rollback, and report generation exceptions."""
        try:
            if self.module_obj is None:
                self.test_obj.yakshaAssert("test_transaction_rollback_and_report_exceptions", False, "exceptional")
                print("test_transaction_rollback_and_report_exceptions = Failed")
                return

            # Test report generation exceptions
            if check_function_exists(self.module_obj, "generate_daily_report"):
                # Test with None inventory
                none_result = safely_call_function(self.module_obj, "generate_daily_report", None)
                if none_result is not None:  # Should fail
                    self.test_obj.yakshaAssert("test_transaction_rollback_and_report_exceptions", False, "exceptional")
                    print("test_transaction_rollback_and_report_exceptions = Failed")
                    return

                # Test with invalid inventory
                invalid_result = safely_call_function(self.module_obj, "generate_daily_report", "not_inventory")
                if invalid_result is not None:  # Should fail
                    self.test_obj.yakshaAssert("test_transaction_rollback_and_report_exceptions", False, "exceptional")
                    print("test_transaction_rollback_and_report_exceptions = Failed")
                    return

            # Test transaction logging structure
            if check_class_exists(self.module_obj, "Inventory"):
                inventory = safely_create_instance(self.module_obj, "Inventory")
                if inventory is not None and hasattr(inventory, "transaction_log"):
                    # Try invalid operation to generate failed transaction
                    safely_call_function(inventory, "remove_flower", "NonExistent", 5)
                    
                    if len(inventory.transaction_log) > 0:
                        latest_transaction = inventory.transaction_log[-1]
                        if latest_transaction.get('status') != 'failed':
                            self.test_obj.yakshaAssert("test_transaction_rollback_and_report_exceptions", False, "exceptional")
                            print("test_transaction_rollback_and_report_exceptions = Failed")
                            return

            self.test_obj.yakshaAssert("test_transaction_rollback_and_report_exceptions", True, "exceptional")
            print("test_transaction_rollback_and_report_exceptions = Passed")

        except Exception:
            self.test_obj.yakshaAssert("test_transaction_rollback_and_report_exceptions", False, "exceptional")
            print("test_transaction_rollback_and_report_exceptions = Failed")

if __name__ == '__main__':
    unittest.main()