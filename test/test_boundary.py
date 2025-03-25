import pytest
from datetime import datetime, timedelta
from test.TestUtils import TestUtils
from flower_shop_inventory_management_system import Flower, Inventory, Order, InvalidFlowerDataError, OutOfStockError, ExpiredFlowerError, FlowerShopException

class TestBoundary:
    """Test cases for boundary conditions in the flower shop inventory system."""
    
    def test_system_boundaries(self):
        """Test all boundary conditions for the flower shop inventory system."""
        try:
            # Test Flower validation boundary conditions
            # Valid flower data
            flower1 = Flower("Rose", 4.99, 50, 7)
            assert flower1.name == "Rose"
            assert flower1.price == 4.99
            assert flower1.quantity == 50
            assert flower1.freshness_date > datetime.now()
            
            # Minimum valid values
            flower2 = Flower("Lily", 0.01, 1, 1)
            assert flower2.name == "Lily"
            assert flower2.price == 0.01
            assert flower2.quantity == 1
            
            # Invalid flower name - empty
            try:
                Flower("", 4.99, 50)
                assert False, "Should raise InvalidFlowerDataError for empty name"
            except InvalidFlowerDataError:
                pass  # Expected behavior
            
            # Invalid flower name - invalid characters
            try:
                Flower("Rose@123", 4.99, 50)
                assert False, "Should raise InvalidFlowerDataError for invalid name"
            except InvalidFlowerDataError:
                pass  # Expected behavior
            
            # Invalid price - zero
            try:
                Flower("Rose", 0, 50)
                assert False, "Should raise InvalidFlowerDataError for zero price"
            except InvalidFlowerDataError:
                pass  # Expected behavior
            
            # Invalid price - negative
            try:
                Flower("Rose", -4.99, 50)
                assert False, "Should raise InvalidFlowerDataError for negative price"
            except InvalidFlowerDataError:
                pass  # Expected behavior
            
            # Invalid price - non-numeric
            try:
                Flower("Rose", "abc", 50)
                assert False, "Should raise InvalidFlowerDataError for non-numeric price"
            except InvalidFlowerDataError:
                pass  # Expected behavior
            
            # Invalid quantity - negative
            try:
                Flower("Rose", 4.99, -10)
                assert False, "Should raise InvalidFlowerDataError for negative quantity"
            except InvalidFlowerDataError:
                pass  # Expected behavior
            
            # Invalid quantity - non-numeric
            try:
                Flower("Rose", 4.99, "fifty")
                assert False, "Should raise InvalidFlowerDataError for non-numeric quantity"
            except InvalidFlowerDataError:
                pass  # Expected behavior
            
            # Test Inventory operations
            inventory = Inventory()
            
            # Add flowers to inventory
            rose = Flower("Rose", 4.99, 50)
            tulip = Flower("Tulip", 3.49, 30)
            
            assert inventory.add_flower(rose) is True
            assert inventory.add_flower(tulip) is True
            
            # Boundary check: zero quantity removal
            try:
                inventory.remove_flower("Rose", 0)
                assert False, "Should raise InvalidFlowerDataError for zero quantity"
            except InvalidFlowerDataError:
                pass  # Expected behavior
            
            # Boundary check: exact stock quantity removal
            initial_quantity = inventory.flowers["Rose"].quantity
            assert inventory.remove_flower("Rose", initial_quantity) is True
            assert inventory.flowers["Rose"].quantity == 0
            
            # Boundary check: remove more than available
            try:
                inventory.remove_flower("Tulip", 100)  # More than available
                assert False, "Should raise OutOfStockError for excessive removal"
            except OutOfStockError:
                pass  # Expected behavior
            
            # Boundary check: check stock of non-existent flower
            try:
                inventory.check_stock("Daisy")  # Doesn't exist
                assert False, "Should raise FlowerShopException for non-existent flower"
            except FlowerShopException:
                pass  # Expected behavior
            
            # Test freshness date boundaries
            # Create a flower that expires today
            expires_today = Flower("Daisy", 2.99, 20, 0)  # 0 days freshness
            
            # Create an expired flower (for testing)
            expired_flower = Flower("Orchid", 8.99, 10, 7)
            expired_flower.freshness_date = datetime.now() - timedelta(days=1)  # Set to yesterday
            
            inventory.add_flower(expires_today)
            inventory.add_flower(expired_flower)
            
            # Check freshness
            assert expires_today.is_fresh() is True  # Should still be fresh today
            assert expired_flower.is_fresh() is False  # Should be expired
            
            # Try to remove expired flower
            try:
                inventory.remove_flower("Orchid", 5)
                assert False, "Should raise ExpiredFlowerError for expired flowers"
            except ExpiredFlowerError:
                pass  # Expected behavior
            
            # Test Order boundaries
            # Create a new inventory for order testing
            order_inventory = Inventory()
            order_inventory.add_flower(Flower("Rose", 4.99, 20))
            order_inventory.add_flower(Flower("Tulip", 3.49, 15))
            
            # Valid order creation
            order = Order("John Smith", order_inventory)
            
            # Invalid customer name
            try:
                Order("", order_inventory)
                assert False, "Should raise InvalidOrderError for empty customer name"
            except FlowerShopException:
                pass  # Expected behavior
            
            # Add items to order
            order.add_item("Rose", 5)
            order.add_item("Tulip", 3)
            
            # Invalid item quantity - zero
            try:
                order.add_item("Rose", 0)
                assert False, "Should raise InvalidFlowerDataError for zero quantity"
            except InvalidFlowerDataError:
                pass  # Expected behavior
            
            # Invalid item quantity - negative
            try:
                order.add_item("Rose", -5)
                assert False, "Should raise InvalidFlowerDataError for negative quantity"
            except InvalidFlowerDataError:
                pass  # Expected behavior
            
            # Invalid item - non-existent flower
            try:
                order.add_item("Daisy", 5)
                assert False, "Should raise FlowerShopException for non-existent flower"
            except FlowerShopException:
                pass  # Expected behavior
            
            # Order more than available
            try:
                order.add_item("Rose", 100)
                assert False, "Should raise OutOfStockError for excessive order"
            except OutOfStockError:
                pass  # Expected behavior
            
            # Test order processing
            result = order.process()
            assert result['status'] == "processed"
            
            # Check inventory after order
            assert order_inventory.check_stock("Rose") == 15  # 20 - 5
            assert order_inventory.check_stock("Tulip") == 12  # 15 - 3
            
            # Try to process the same order again
            try:
                order.process()
                assert False, "Should raise InvalidOrderError for already processed order"
            except FlowerShopException:
                pass  # Expected behavior
            
            # Test empty order processing
            empty_order = Order("Jane Doe", order_inventory)
            try:
                empty_order.process()
                assert False, "Should raise InvalidOrderError for empty order"
            except FlowerShopException:
                pass  # Expected behavior
            
            TestUtils.yakshaAssert("test_system_boundaries", True, "boundary")
        except Exception as e:
            TestUtils.yakshaAssert("test_system_boundaries", False, "boundary")
            raise e