import pytest
from datetime import datetime, timedelta
from test.TestUtils import TestUtils
from flower_shop_inventory_management_system import Flower, Inventory, Order, FlowerShopException, InvalidFlowerDataError, InvalidOrderError, OutOfStockError, ExpiredFlowerError, generate_daily_report

class TestExceptional:
    """Test cases for exceptional conditions in the flower shop inventory system."""
    
    def test_exception_handling(self):
        """Test all exception handling across the flower shop inventory system."""
        try:
            # Test FlowerShopException base class
            error = FlowerShopException("Test error message", "E999")
            assert str(error) == "[E999] Test error message"
            
            error_no_code = FlowerShopException("Test error message")
            assert str(error_no_code) == "Test error message"
            
            # Test specific exception classes
            invalid_data_error = InvalidFlowerDataError("Invalid flower data", "F001")
            assert "Invalid flower data" in str(invalid_data_error)
            assert "F001" in str(invalid_data_error)
            
            order_error = InvalidOrderError("Empty order")
            assert "Invalid order: Empty order" in str(order_error)
            assert "E001" in str(order_error)
            
            out_of_stock = OutOfStockError("Rose", 50, 30)
            assert "Insufficient stock for Rose" in str(out_of_stock)
            assert "Requested: 50, Available: 30" in str(out_of_stock)
            assert "I001" in str(out_of_stock)
            
            expiry_date = datetime.now().strftime("%Y-%m-%d")
            expired = ExpiredFlowerError("Lily", expiry_date)
            assert "Flower 'Lily' has expired" in str(expired)
            assert expiry_date in str(expired)
            assert "I002" in str(expired)
            
            # Test flower validation exceptions
            # Invalid name
            try:
                flower = Flower("", 4.99, 50)  # Empty name
                assert False, "Should raise InvalidFlowerDataError for empty name"
            except InvalidFlowerDataError as e:
                assert "Flower name cannot be empty" in str(e)
                assert "F002" in str(e)
            
            try:
                flower = Flower("Rose@123", 4.99, 50)  # Invalid name format
                assert False, "Should raise InvalidFlowerDataError for invalid name format"
            except InvalidFlowerDataError as e:
                assert "Invalid flower name format" in str(e)
                assert "F003" in str(e)
            
            # Invalid price
            try:
                flower = Flower("Rose", -4.99, 50)  # Negative price
                assert False, "Should raise InvalidFlowerDataError for negative price"
            except InvalidFlowerDataError as e:
                assert "Price must be positive" in str(e)
                assert "F004" in str(e)
            
            try:
                flower = Flower("Rose", "abc", 50)  # Non-numeric price
                assert False, "Should raise InvalidFlowerDataError for non-numeric price"
            except InvalidFlowerDataError as e:
                assert "Invalid price format" in str(e)
                assert "F005" in str(e)
            
            # Invalid quantity
            try:
                flower = Flower("Rose", 4.99, -10)  # Negative quantity
                assert False, "Should raise InvalidFlowerDataError for negative quantity"
            except InvalidFlowerDataError as e:
                assert "Quantity cannot be negative" in str(e)
                assert "F006" in str(e)
            
            try:
                flower = Flower("Rose", 4.99, "fifty")  # Non-numeric quantity
                assert False, "Should raise InvalidFlowerDataError for non-numeric quantity"
            except InvalidFlowerDataError as e:
                assert "Invalid quantity format" in str(e)
                assert "F007" in str(e)
            
            # Test inventory exception handling
            inventory = Inventory()
            
            # Add invalid flower object
            try:
                inventory.add_flower("Not a flower object")
                assert False, "Should raise InvalidFlowerDataError for invalid flower object"
            except InvalidFlowerDataError as e:
                assert "Invalid flower object" in str(e)
                assert "I003" in str(e)
            
            # Remove with invalid parameters
            try:
                inventory.remove_flower("", 5)  # Empty flower name
                assert False, "Should raise InvalidFlowerDataError for empty flower name"
            except InvalidFlowerDataError as e:
                assert "Flower name cannot be empty" in str(e)
                assert "I004" in str(e)
            
            try:
                inventory.remove_flower("Rose", 0)  # Zero quantity
                assert False, "Should raise InvalidFlowerDataError for zero quantity"
            except InvalidFlowerDataError as e:
                assert "Quantity must be positive" in str(e)
                assert "I005" in str(e)
            
            try:
                inventory.remove_flower("Rose", "five")  # Non-numeric quantity
                assert False, "Should raise InvalidFlowerDataError for non-numeric quantity"
            except InvalidFlowerDataError as e:
                assert "Invalid quantity" in str(e)
                assert "I006" in str(e)
            
            try:
                inventory.remove_flower("Daisy", 5)  # Non-existent flower
                assert False, "Should raise FlowerShopException for non-existent flower"
            except FlowerShopException as e:
                assert "Flower not found" in str(e)
                assert "I007" in str(e)
            
            # Add valid flowers for further testing
            rose = Flower("Rose", 4.99, 50)
            inventory.add_flower(rose)
            
            # Create expired flower for testing
            orchid = Flower("Orchid", 8.99, 10)
            orchid.freshness_date = datetime.now() - timedelta(days=1)  # Set to yesterday
            inventory.add_flower(orchid)
            
            # Test expired flower removal
            try:
                inventory.remove_flower("Orchid", 5)
                assert False, "Should raise ExpiredFlowerError for expired flowers"
            except ExpiredFlowerError as e:
                assert "has expired" in str(e)
                assert "Orchid" in str(e)
            
            # Test out of stock removal
            try:
                inventory.remove_flower("Rose", 100)  # More than available
                assert False, "Should raise OutOfStockError for excessive removal"
            except OutOfStockError as e:
                assert "Insufficient stock for Rose" in str(e)
                assert "Requested: 100" in str(e)
            
            # Test invalid stock check
            try:
                inventory.check_stock("Daisy")  # Non-existent flower
                assert False, "Should raise FlowerShopException for non-existent flower"
            except FlowerShopException as e:
                assert "Flower not found" in str(e)
                assert "I008" in str(e)
            
            # Test order exception handling
            # Create inventory for order testing
            order_inventory = Inventory()
            order_inventory.add_flower(Flower("Rose", 4.99, 20))
            
            # Invalid customer name
            try:
                Order("", order_inventory)  # Empty customer name
                assert False, "Should raise InvalidOrderError for empty customer name"
            except InvalidOrderError as e:
                assert "Customer name cannot be empty" in str(e)
            
            # Invalid inventory object
            try:
                Order("John Smith", "Not an inventory")
                assert False, "Should raise FlowerShopException for invalid inventory"
            except FlowerShopException as e:
                assert "Invalid inventory object" in str(e)
                assert "O001" in str(e)
            
            # Create valid order for further testing
            order = Order("John Smith", order_inventory)
            
            # Add item with invalid parameters
            try:
                order.add_item("", 5)  # Empty flower name
                assert False, "Should raise InvalidFlowerDataError for empty flower name"
            except InvalidFlowerDataError as e:
                assert "Flower name cannot be empty" in str(e)
                assert "O002" in str(e)
            
            try:
                order.add_item("Rose", 0)  # Zero quantity
                assert False, "Should raise InvalidFlowerDataError for zero quantity"
            except InvalidFlowerDataError as e:
                assert "Quantity must be positive" in str(e)
                assert "O003" in str(e)
            
            try:
                order.add_item("Rose", "five")  # Non-numeric quantity
                assert False, "Should raise InvalidFlowerDataError for non-numeric quantity"
            except InvalidFlowerDataError as e:
                assert "Invalid quantity" in str(e)
                assert "O004" in str(e)
            
            try:
                order.add_item("Daisy", 5)  # Non-existent flower
                assert False, "Should raise FlowerShopException for non-existent flower"
            except FlowerShopException as e:
                assert "Flower not found" in str(e)
                assert "O005" in str(e)
            
            # Add expired flower to inventory and test
            expired_tulip = Flower("Tulip", 3.49, 15)
            expired_tulip.freshness_date = datetime.now() - timedelta(days=1)
            order_inventory.add_flower(expired_tulip)
            
            try:
                order.add_item("Tulip", 5)  # Expired flower
                assert False, "Should raise ExpiredFlowerError for expired flowers"
            except ExpiredFlowerError as e:
                assert "has expired" in str(e)
                assert "Tulip" in str(e)
            
            # Add more than available
            try:
                order.add_item("Rose", 100)  # More than available
                assert False, "Should raise OutOfStockError for excessive order"
            except OutOfStockError as e:
                assert "Insufficient stock for Rose" in str(e)
            
            # Test order processing exceptions
            # Empty order
            empty_order = Order("Jane Doe", order_inventory)
            try:
                empty_order.process()
                assert False, "Should raise InvalidOrderError for empty order"
            except InvalidOrderError as e:
                assert "Cannot process an empty order" in str(e)
            
            # Add some items and process
            order.add_item("Rose", 5)
            order.process()
            
            # Try to process again
            try:
                order.process()
                assert False, "Should raise InvalidOrderError for already processed order"
            except InvalidOrderError as e:
                assert "already been processed" in str(e)
            
            # Test transaction rollback
            # Create inventory and order for rollback testing
            rollback_inventory = Inventory()
            rollback_inventory.add_flower(Flower("Rose", 4.99, 20))
            rollback_inventory.add_flower(Flower("Lily", 5.99, 10))
            
            rollback_order = Order("Bob Johnson", rollback_inventory)
            rollback_order.add_item("Rose", 5)
            
            # Replace remove_flower method to fail after first call
            original_remove = rollback_inventory.remove_flower
            call_count = 0
            
            def failing_remove(flower_name, quantity):
                nonlocal call_count
                if call_count == 0:
                    # First call succeeds (Rose)
                    call_count += 1
                    return original_remove(flower_name, quantity)
                else:
                    # Second call fails (Lily)
                    raise FlowerShopException("Simulated failure", "TEST001")
            
            rollback_inventory.remove_flower = failing_remove
            
            # Add a second item
            rollback_order.add_item("Lily", 3)
            
            # Record initial stock levels
            initial_rose_stock = rollback_inventory.check_stock("Rose")
            initial_lily_stock = rollback_inventory.check_stock("Lily")
            
            try:
                rollback_order.process()
                assert False, "Should raise InvalidOrderError due to simulated failure"
            except InvalidOrderError:
                # Verify rollback occurred for the first flower (Rose)
                assert rollback_inventory.check_stock("Rose") == initial_rose_stock
                assert rollback_inventory.check_stock("Lily") == initial_lily_stock
            
            # Restore original method
            rollback_inventory.remove_flower = original_remove
            
            # Test report generation exceptions
            try:
                # Create an invalid inventory for testing
                class BrokenInventory:
                    def get_all_flowers(self):
                        raise Exception("Simulated failure in get_all_flowers")
                    
                    def get_transaction_log(self):
                        return []
                
                generate_daily_report(BrokenInventory())
                assert False, "Should raise FlowerShopException for report generation failure"
            except FlowerShopException as e:
                assert "Failed to generate report" in str(e)
                assert "R001" in str(e)
            
            TestUtils.yakshaAssert("test_exception_handling", True, "exceptional")
        except Exception as e:
            TestUtils.yakshaAssert("test_exception_handling", False, "exceptional")
            raise e