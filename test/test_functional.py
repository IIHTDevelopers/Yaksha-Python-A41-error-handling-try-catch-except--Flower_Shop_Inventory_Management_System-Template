import pytest
from datetime import datetime, timedelta
import inspect
import re
from test.TestUtils import TestUtils
from flower_shop_inventory_management_system import (
    Flower, Inventory, Order, FlowerShopException, InvalidFlowerDataError, 
    InvalidOrderError, OutOfStockError, ExpiredFlowerError, generate_daily_report
)

class TestFunctional:
    """Streamlined test cases covering all core functionality."""
    
    def test_exception_hierarchy_and_flower_class(self):
        """Test exception hierarchy and Flower class implementation."""
        try:
            # Test exception hierarchy
            assert issubclass(InvalidFlowerDataError, FlowerShopException)
            assert issubclass(InvalidOrderError, FlowerShopException)
            assert issubclass(OutOfStockError, FlowerShopException)
            assert issubclass(ExpiredFlowerError, FlowerShopException)
            
            # Test error codes and messages
            base_exception = FlowerShopException("Test message", "FS001")
            assert str(base_exception) == "[FS001] Test message"
            
            # Test flower creation with validation
            flower = Flower("Rose", 4.99, 50, 7)
            assert flower.name == "Rose"
            assert flower.price == 4.99
            assert flower.quantity == 50
            assert flower.freshness_date > datetime.now()
            
            # Test validation methods
            with pytest.raises(InvalidFlowerDataError):
                Flower("", 4.99, 50)  # Empty name
                
            with pytest.raises(InvalidFlowerDataError):
                Flower("Rose", "abc", 50)  # Non-numeric price
                
            # Verify exception chaining
            try:
                Flower("Rose", "abc", 50)
            except InvalidFlowerDataError as e:
                assert e.__cause__ is not None or "from" in inspect.getsource(Flower.validate_price)
            
            TestUtils.yakshaAssert("test_exception_hierarchy_and_flower_class", True, "functional")
        except Exception as e:
            TestUtils.yakshaAssert("test_exception_hierarchy_and_flower_class", False, "functional")
            raise e
    
    def test_inventory_and_order_operations(self):
        """Test inventory operations and order processing."""
        try:
            # Create inventory and add flowers
            inventory = Inventory()
            rose = Flower("Rose", 4.99, 50)
            tulip = Flower("Tulip", 3.49, 30)
            
            assert inventory.add_flower(rose) is True
            assert "Rose" in inventory.flowers
            assert inventory.check_stock("Rose") == 50
            
            # Verify transaction log
            assert len(inventory.transaction_log) == 1
            assert inventory.transaction_log[0]['status'] == "completed"
            
            # Test remove_flower
            assert inventory.remove_flower("Rose", 10) is True
            assert inventory.check_stock("Rose") == 40
            
            # Test transaction rollback
            initial_quantity = inventory.check_stock("Rose")
            try:
                inventory.remove_flower("Rose", -5)  # Invalid quantity
                assert False, "Should raise InvalidFlowerDataError"
            except InvalidFlowerDataError:
                assert inventory.check_stock("Rose") == initial_quantity  # Verify rollback
            
            # Test order processing
            inventory.add_flower(tulip)
            order = Order("John Smith", inventory)
            order.add_item("Rose", 5)
            order.add_item("Tulip", 3)
            
            initial_rose_stock = inventory.check_stock("Rose")
            initial_tulip_stock = inventory.check_stock("Tulip")
            
            result = order.process()
            
            # Verify results
            assert order.status == "processed"
            assert inventory.check_stock("Rose") == initial_rose_stock - 5
            assert inventory.check_stock("Tulip") == initial_tulip_stock - 3
            
            # Test errors and logging
            try:
                inventory.remove_flower("Rose", 100)  # More than available
            except OutOfStockError:
                pass
                
            # Check error logs
            failed_transactions = [t for t in inventory.transaction_log if t['status'] == 'failed']
            assert len(failed_transactions) >= 1
            assert 'error' in failed_transactions[0]
            
            TestUtils.yakshaAssert("test_inventory_and_order_operations", True, "functional")
        except Exception as e:
            TestUtils.yakshaAssert("test_inventory_and_order_operations", False, "functional")
            raise e
    
    def test_try_except_else_finally_pattern(self):
        """Test proper implementation of try-except-else-finally pattern."""
        try:
            # Import module
            import flower_shop_inventory_management_system as module
            
            # Simple presence check for required blocks
            methods_to_check = {
                # Class initialization methods
                "Flower.__init__": ["try", "except", "else"],
                "Order.__init__": ["try", "except", "else"],
                
                # Key operations
                "Inventory.add_flower": ["try", "except", "else", "finally"],
                "Inventory.remove_flower": ["try", "except", "else", "finally"],
                "Inventory.check_stock": ["try", "except", "else"],
                "Order.add_item": ["try", "except", "else", "finally"],
                "Order.process": ["try", "except", "else", "finally"],
                "Order._rollback_inventory": ["try", "except", "finally"],
                "generate_daily_report": ["try", "except", "else", "finally"]
            }
            
            missing_patterns = []
            
            for method_path, required_blocks in methods_to_check.items():
                class_name, method_name = method_path.split('.') if '.' in method_path else ('', method_path)
                
                # Get method
                if class_name:
                    cls = getattr(module, class_name)
                    method = cls.__init__ if method_name == "__init__" else getattr(cls, method_name)
                else:
                    method = getattr(module, method_name)
                
                # Get source code
                source = inspect.getsource(method)
                
                # Check for required blocks
                blocks_present = {}
                blocks_present["try"] = "try:" in source
                blocks_present["except"] = "except" in source
                blocks_present["else"] = "else:" in source
                blocks_present["finally"] = "finally:" in source
                
                # Check if any required blocks are missing
                missing_blocks = [block for block in required_blocks if not blocks_present[block]]
                
                if missing_blocks:
                    missing_patterns.append(f"{method_path} missing {', '.join(missing_blocks)}")
            
            # Make sure no methods are missing required patterns
            assert len(missing_patterns) == 0, f"Missing patterns: {', '.join(missing_patterns)}"
            
            # Test execution flow
            class TrackingInventory(Inventory):
                def __init__(self):
                    super().__init__()
                    self.call_log = []
                
                def add_flower(self, flower):
                    self.call_log.append("add_flower_start")
                    try:
                        self.call_log.append("add_flower_try")
                        if not isinstance(flower, Flower):
                            self.call_log.append("add_flower_raising")
                            raise InvalidFlowerDataError("Invalid flower object", "I003")
                    except FlowerShopException as e:
                        self.call_log.append("add_flower_except")
                        transaction = {
                            'type': 'add',
                            'flower_name': getattr(flower, 'name', 'Unknown'),
                            'quantity': getattr(flower, 'quantity', 0),
                            'status': 'failed',
                            'error': str(e)
                        }
                        self.transaction_log.append(transaction)
                        raise
                    else:
                        self.call_log.append("add_flower_else")
                        transaction = {
                            'type': 'add',
                            'flower_name': getattr(flower, 'name', 'Unknown'),
                            'quantity': getattr(flower, 'quantity', 0),
                            'status': 'completed'
                        }
                        self.transaction_log.append(transaction)
                        return True
                    finally:
                        self.call_log.append("add_flower_finally")
            
            # Test success flow
            tracking_inventory = TrackingInventory()
            tracking_flower = Flower("Daisy", 3.99, 25)
            
            tracking_inventory.add_flower(tracking_flower)
            assert "add_flower_start" in tracking_inventory.call_log
            assert "add_flower_try" in tracking_inventory.call_log
            assert "add_flower_else" in tracking_inventory.call_log
            assert "add_flower_finally" in tracking_inventory.call_log
            
            # Test error flow
            tracking_inventory.call_log.clear()
            try:
                tracking_inventory.add_flower("Not a flower")
                assert False, "Should have raised an exception"
            except InvalidFlowerDataError:
                pass
                
            assert "add_flower_start" in tracking_inventory.call_log
            assert "add_flower_try" in tracking_inventory.call_log
            assert "add_flower_raising" in tracking_inventory.call_log
            assert "add_flower_except" in tracking_inventory.call_log
            assert "add_flower_finally" in tracking_inventory.call_log
                
            TestUtils.yakshaAssert("test_try_except_else_finally_pattern", True, "functional")
        except Exception as e:
            TestUtils.yakshaAssert("test_try_except_else_finally_pattern", False, "functional")
            raise e
    
    def test_resource_cleanup_and_exception_chaining(self):
        """Test resource cleanup and exception chaining."""
        try:
            # Test report generation with cleanup
            inventory = Inventory()
            inventory.add_flower(Flower("Rose", 4.99, 50))
            inventory.add_flower(Flower("Tulip", 3.49, 3))  # Low stock
            
            # Capture stdout to verify finally block execution
            import sys
            from io import StringIO
            
            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()
            
            try:
                report = generate_daily_report(inventory)
            finally:
                sys.stdout = old_stdout
                output = mystdout.getvalue()
                
            # Verify report structure and finally block execution
            assert 'date' in report
            assert report['inventory_count'] == 2
            assert len(report['stock_alerts']) == 1
            assert "Report generation process completed" in output
            
            # Test exception chaining
            try:
                Flower("Rose", "not-a-number", 50)
            except InvalidFlowerDataError as e:
                assert e.__cause__ is not None
            
            # Test rollback of failed operations
            order = Order("Test", inventory)
            order.add_item("Rose", 5)
            
            # Create mock methods for testing
            original_remove = inventory.remove_flower
            def failing_remove(flower_name, quantity):
                raise OutOfStockError(flower_name, quantity, 0)
            
            original_rollback = order._rollback_inventory
            rollback_called = False
            def tracking_rollback(processed_items):
                nonlocal rollback_called
                rollback_called = True
                return original_rollback(processed_items)
            
            # Apply mock methods
            inventory.remove_flower = failing_remove
            order._rollback_inventory = tracking_rollback
            
            # Process order - should fail
            try:
                order.process()
            except InvalidOrderError:
                pass
                
            # Verify rollback was called and restore methods
            assert rollback_called
            inventory.remove_flower = original_remove
            order._rollback_inventory = original_rollback
            
            TestUtils.yakshaAssert("test_resource_cleanup_and_exception_chaining", True, "functional")
        except Exception as e:
            TestUtils.yakshaAssert("test_resource_cleanup_and_exception_chaining", False, "functional")
            raise e