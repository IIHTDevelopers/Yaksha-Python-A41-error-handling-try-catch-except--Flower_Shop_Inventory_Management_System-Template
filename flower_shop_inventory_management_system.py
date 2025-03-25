"""
Flower Shop Inventory Management System
Version 1.0

This module demonstrates comprehensive error and exception handling focusing on:
1. try: The code that might raise an exception
2. except: Handling specific exceptions when they occur
3. else: Code to run when no exceptions occur
4. finally: Cleanup code that always runs regardless of exceptions
"""

import re
from datetime import datetime, timedelta

# Custom Exception Hierarchy
class FlowerShopException(Exception):
    """Base exception class for all flower-shop-related exceptions."""
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

# Validation Exceptions
class InvalidFlowerDataError(FlowerShopException):
    """Exception raised for invalid flower data formats or values."""
    pass

class InvalidOrderError(FlowerShopException):
    """Exception raised when an order is invalid."""
    def __init__(self, reason):
        super().__init__(f"Invalid order: {reason}", "E001")

# Inventory Exceptions
class OutOfStockError(FlowerShopException):
    """Exception raised when requested flowers are not in stock."""
    def __init__(self, flower_name, requested, available):
        super().__init__(
            f"Insufficient stock for {flower_name}. "
            f"Requested: {requested}, Available: {available}.", 
            "I001"
        )

class ExpiredFlowerError(FlowerShopException):
    """Exception raised when flowers are past their freshness date."""
    def __init__(self, flower_name, expiry_date):
        super().__init__(
            f"Flower '{flower_name}' has expired. Freshness date: {expiry_date}",
            "I002"
        )

class Flower:
    """Represents a flower with its attributes and validation."""
    
    def __init__(self, name, price, quantity, freshness_days=7):
        """Initialize a new flower with validation."""
        try:
            self.validate_name(name)
            self.validate_price(price)
            self.validate_quantity(quantity)
        except (ValueError, TypeError) as e:
            # Handle syntax errors during validation
            raise InvalidFlowerDataError(f"Invalid flower data: {str(e)}", "F001") from e
        else:
            # Only execute if no exceptions were raised
            self.name = name
            self.price = float(price)
            self.quantity = int(quantity)
            self.freshness_date = datetime.now() + timedelta(days=freshness_days)
    
    def validate_name(self, name):
        """Validate flower name."""
        if not isinstance(name, str) or not name.strip():
            raise InvalidFlowerDataError("Flower name cannot be empty", "F002")
        
        if not re.match(r'^[a-zA-Z\s\-\']+$', name):
            raise InvalidFlowerDataError(
                f"Invalid flower name format: '{name}'. "
                f"Must contain only letters, spaces, hyphens, and apostrophes.", 
                "F003"
            )
    
    def validate_price(self, price):
        """Validate flower price."""
        try:
            price_float = float(price)
            if price_float <= 0:
                raise InvalidFlowerDataError("Price must be positive", "F004")
        except (ValueError, TypeError) as e:
            raise InvalidFlowerDataError(f"Invalid price format: '{price}'", "F005") from e
    
    def validate_quantity(self, quantity):
        """Validate flower quantity."""
        try:
            quantity_int = int(quantity)
            if quantity_int < 0:
                raise InvalidFlowerDataError("Quantity cannot be negative", "F006")
        except (ValueError, TypeError) as e:
            raise InvalidFlowerDataError(f"Invalid quantity format: '{quantity}'", "F007") from e
    
    def is_fresh(self):
        """Check if the flower is still fresh."""
        # Include the current day as fresh (use <= instead of <)
        return datetime.now().date() <= self.freshness_date.date()
    
    def __str__(self):
        """String representation of the flower."""
        return f"{self.name}: ${self.price:.2f}, {self.quantity} in stock, fresh until {self.freshness_date.strftime('%Y-%m-%d')}"

class Inventory:
    """Manages the flower shop inventory."""
    
    def __init__(self):
        """Initialize an empty inventory."""
        self.flowers = {}  # Dictionary of flower_name: Flower object
        self.transaction_log = []

    def add_flower(self, flower):
        """Add a flower to the inventory with try-except-else-finally pattern."""
        transaction = {
            'type': 'add',
            'flower_name': getattr(flower, 'name', 'Unknown'),
            'quantity': getattr(flower, 'quantity', 0),
            'status': 'pending'
        }
        
        try:
            # Code that might raise exceptions
            if not isinstance(flower, Flower):
                raise InvalidFlowerDataError("Invalid flower object", "I003")
            
            # Check if flower already exists, update quantity if it does
            if flower.name in self.flowers:
                old_quantity = self.flowers[flower.name].quantity
                self.flowers[flower.name].quantity += flower.quantity
                
                # Logical error check
                if self.flowers[flower.name].quantity <= old_quantity:
                    raise FlowerShopException("Logical error: Quantity didn't increase", "L001")
            else:
                self.flowers[flower.name] = flower
                
        except FlowerShopException as e:
            # Exception handling block
            transaction['status'] = 'failed'
            transaction['error'] = str(e)
            self.transaction_log.append(transaction)
            raise
            
        else:
            # Code that runs if no exceptions were raised
            transaction['status'] = 'completed'
            self.transaction_log.append(transaction)
            return True
            
        finally:
            # Cleanup code that always runs
            print(f"Flower transaction {'completed' if transaction['status'] == 'completed' else 'failed'}: {transaction['flower_name']}")
    
    def remove_flower(self, flower_name, quantity):
        """Remove flowers from inventory with try-except-else-finally pattern."""
        transaction = {
            'type': 'remove',
            'flower_name': flower_name,
            'quantity': None,
            'status': 'pending'
        }
        
        inventory_updated = False
        old_quantity = 0
        
        try:
            # Validate inputs
            if not isinstance(flower_name, str) or not flower_name.strip():
                raise InvalidFlowerDataError("Flower name cannot be empty", "I004")
            
            try:
                quantity = int(quantity)
                transaction['quantity'] = quantity
                if quantity <= 0:
                    raise InvalidFlowerDataError("Quantity must be positive", "I005")
            except (ValueError, TypeError) as e:
                raise InvalidFlowerDataError(f"Invalid quantity: {quantity}", "I006") from e
            
            # Check if flower exists
            if flower_name not in self.flowers:
                raise FlowerShopException(f"Flower not found: {flower_name}", "I007")
            
            flower = self.flowers[flower_name]
            
            # Check freshness
            if not flower.is_fresh():
                raise ExpiredFlowerError(flower_name, flower.freshness_date)
            
            # Check stock
            if quantity > flower.quantity:
                raise OutOfStockError(flower_name, quantity, flower.quantity)
            
            # Update inventory
            old_quantity = flower.quantity
            flower.quantity -= quantity
            inventory_updated = True
            
            # Logical error check
            if flower.quantity >= old_quantity:
                raise FlowerShopException("Logical error: Quantity didn't decrease", "L002")
                
        except FlowerShopException as e:
            # Exception handling
            transaction['status'] = 'failed'
            transaction['error'] = str(e)
            
            # Rollback if inventory was modified
            if inventory_updated:
                self.flowers[flower_name].quantity = old_quantity
                
            raise
            
        else:
            # Code that runs if no exceptions were raised
            transaction['status'] = 'completed'
            return True
            
        finally:
            # Cleanup code that always runs, regardless of exceptions
            self.transaction_log.append(transaction)
            print(f"Inventory transaction logged: {transaction['type']} {transaction['flower_name']}")
        
    def check_stock(self, flower_name):
        """Check the stock level for a specific flower."""
        try:
            # Attempt to access flower
            if flower_name not in self.flowers:
                raise FlowerShopException(f"Flower not found: {flower_name}", "I008")
                
        except FlowerShopException:
            # Re-raise the exception
            raise
            
        else:
            # Return stock if no exceptions occurred
            return self.flowers[flower_name].quantity
    
    def get_all_flowers(self):
        """Get a list of all flowers in inventory."""
        return list(self.flowers.values())
    
    def get_transaction_log(self):
        """Get the transaction log."""
        return self.transaction_log

class Order:
    """Manages customer orders with error handling."""
    
    def __init__(self, customer_name, inventory):
        """Initialize a new order."""
        try:
            # Validate inputs
            if not isinstance(customer_name, str) or not customer_name.strip():
                raise InvalidOrderError("Customer name cannot be empty")
            
            if not isinstance(inventory, Inventory):
                raise FlowerShopException("Invalid inventory object", "O001")
                
        except FlowerShopException:
            # Re-raise exceptions
            raise
            
        else:
            # Initialize if no exceptions
            self.customer_name = customer_name
            self.inventory = inventory
            self.items = {}  # Dictionary of flower_name: quantity
            self.status = "new"
            self.total_price = 0.0
    
    def add_item(self, flower_name, quantity):
        """Add an item to the order with full try-except-else-finally pattern."""
        flower = None
        
        try:
            # Check order status
            if self.status != "new":
                raise InvalidOrderError("Cannot modify a processed order")
            
            # Validate inputs
            if not isinstance(flower_name, str) or not flower_name.strip():
                raise InvalidFlowerDataError("Flower name cannot be empty", "O002")
            
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    raise InvalidFlowerDataError("Quantity must be positive", "O003")
            except (ValueError, TypeError) as e:
                raise InvalidFlowerDataError(f"Invalid quantity: {quantity}", "O004") from e
            
            # Check if flower exists and has sufficient stock
            if flower_name not in self.inventory.flowers:
                raise FlowerShopException(f"Flower not found: {flower_name}", "O005")
            
            flower = self.inventory.flowers[flower_name]
            
            # Check freshness
            if not flower.is_fresh():
                raise ExpiredFlowerError(flower_name, flower.freshness_date)
            
            # Calculate available quantity (accounting for stock already in this order)
            current_order_quantity = self.items.get(flower_name, 0)
            available = flower.quantity - current_order_quantity
            
            if quantity > available:
                raise OutOfStockError(flower_name, quantity, available)
                
        except FlowerShopException:
            # Re-raise all shop exceptions
            raise
        except Exception as e:
            # Catch unexpected errors
            raise FlowerShopException(f"Error adding item: {str(e)}", "O006") from e
            
        else:
            # Update order if no exceptions
            if flower_name in self.items:
                self.items[flower_name] += quantity
            else:
                self.items[flower_name] = quantity
            
            # Update total price
            self.total_price += flower.price * quantity
            return self.total_price
            
        finally:
            # Log the attempt (always runs)
            print(f"Order item {'added' if flower and flower_name in self.items else 'failed'}: {flower_name}")
    
    def process(self):
        """Process the order, removing items from inventory."""
        # Keep track of processed items for rollback
        processed_items = []
        
        try:
            # Validate order
            if not self.items:
                raise InvalidOrderError("Cannot process an empty order")
            
            if self.status != "new":
                raise InvalidOrderError("Order has already been processed")
            
            # Process each item in the order
            for flower_name, quantity in self.items.items():
                self.inventory.remove_flower(flower_name, quantity)
                processed_items.append((flower_name, quantity))
                
        except FlowerShopException as e:
            # Handle exception and rollback
            self.status = "failed"
            self._rollback_inventory(processed_items)
            raise InvalidOrderError(f"Order processing failed: {str(e)}")
            
        else:
            # Update status if successful
            self.status = "processed"
            
            # Return order details
            return {
                'customer': self.customer_name,
                'items': {name: qty for name, qty in self.items.items()},
                'total': self.total_price,
                'status': self.status
            }
            
        finally:
            # Always log the order processing attempt
            print(f"Order processing completed with status: {self.status}")
        
    def _rollback_inventory(self, processed_items):
        """Roll back inventory changes for processed items."""
        rollback_success = True
        
        try:
            for flower_name, quantity in processed_items:
                flower = self.inventory.flowers[flower_name]
                flower.quantity += quantity  # Return items to inventory
                
        except Exception as e:
            # Log the error but don't raise - this is cleanup code
            print(f"Error during rollback: {str(e)}")
            rollback_success = False
            
        finally:
            # Always report rollback status
            print(f"Inventory rollback {'successful' if rollback_success else 'incomplete'}")
            return rollback_success
    
    def __str__(self):
        """String representation of the order."""
        items_str = ", ".join([f"{qty} {name}" for name, qty in self.items.items()])
        return f"Order for {self.customer_name}: {items_str}. Total: ${self.total_price:.2f} ({self.status})"

def generate_daily_report(inventory):
    """Generate a daily sales and inventory report."""
    report_data = None
    
    try:
        # Get current date
        today = datetime.now().date()
        today_str = today.strftime("%Y-%m-%d")
        
        # Initialize report
        report = {
            'date': today_str,
            'inventory_count': len(inventory.flowers),
            'transactions': {},
            'stock_alerts': []
        }
        
        # Process transaction log
        sales = 0
        restocks = 0
        
        for transaction in inventory.transaction_log:
            if transaction['status'] == 'completed':
                if transaction['type'] == 'remove':
                    sales += transaction['quantity']
                elif transaction['type'] == 'add':
                    restocks += transaction['quantity']
        
        report['transactions']['sales'] = sales
        report['transactions']['restocks'] = restocks
        
        # Generate stock alerts for low inventory (less than 5)
        for flower in inventory.get_all_flowers():
            if flower.quantity < 5:
                report['stock_alerts'].append({
                    'flower': flower.name,
                    'current_stock': flower.quantity,
                    'price': flower.price
                })
                
        report_data = report
        
    except Exception as e:
        # Handle any exceptions that occur during report generation
        raise FlowerShopException(f"Failed to generate report: {str(e)}", "R001") from e
        
    else:
        # Only execute if no exceptions occurred
        print(f"Report generated successfully for {today_str}")
        return report_data
        
    finally:
        # Always execute, whether exception occurred or not
        print("Report generation process completed")

def main():
    """Main function demonstrating error handling with try-except-else-finally."""
    print("Flower Shop Inventory Management System")
    print("=======================================")
    
    # Initialize inventory
    inventory = Inventory()
    
    try:
        # Demonstrate flower creation and validation
        print("\n1. Adding flowers to inventory...")
        
        rose = Flower("Rose", 4.99, 50, 5)
        tulip = Flower("Tulip", 3.49, 30, 7)
        lily = Flower("Lily", 5.99, 20, 4)
        
        inventory.add_flower(rose)
        inventory.add_flower(tulip)
        inventory.add_flower(lily)
        
        # Demonstrate input validation failures
        print("\n2. Demonstrating syntax error handling...")
        try:
            invalid_flower = Flower("Rose@", -5.99, "ten")
        except InvalidFlowerDataError as e:
            print(f"   Caught error: {e}")
        
        # Demonstrate runtime exception handling
        print("\n3. Demonstrating runtime error handling...")
        try:
            # Try to remove more roses than available
            inventory.remove_flower("Rose", 100)
        except OutOfStockError as e:
            print(f"   Caught error: {e}")
        
        # Demonstrate successful order processing
        print("\n4. Processing a valid order...")
        order = Order("John Smith", inventory)
        order.add_item("Rose", 5)
        order.add_item("Tulip", 3)
        
        print(f"   Order created: {order}")
        
        result = order.process()
        
    except Exception as e:
        # Handle any unexpected exceptions
        print(f"An error occurred: {e}")
        
    else:
        # Code to run if no exceptions occurred
        print("All operations completed successfully!")
        print(f"Final inventory: {len(inventory.flowers)} flower types")
        
    finally:
        # Cleanup code that always runs
        print("\nThank you for using the Flower Shop Inventory System!")
        print("Session ended at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

if __name__ == "__main__":
    main()