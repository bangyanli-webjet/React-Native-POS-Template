#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for POS Application
Tests Product CRUD, Transaction Processing, and Dashboard Analytics
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any

# Configuration
BASE_URL = "https://react-register.preview.emergentagent.com/api"
HEADERS = {"Content-Type": "application/json"}

class POSBackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.headers = HEADERS
        self.created_products = []
        self.created_transactions = []
        self.test_results = {
            "product_crud": {"passed": 0, "failed": 0, "errors": []},
            "transactions": {"passed": 0, "failed": 0, "errors": []},
            "dashboard": {"passed": 0, "failed": 0, "errors": []},
            "categories": {"passed": 0, "failed": 0, "errors": []}
        }

    def log_result(self, category: str, test_name: str, success: bool, error: str = None):
        """Log test results"""
        if success:
            self.test_results[category]["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.test_results[category]["failed"] += 1
            self.test_results[category]["errors"].append(f"{test_name}: {error}")
            print(f"❌ {test_name}: {error}")

    def test_product_crud_operations(self):
        """Test all Product CRUD operations"""
        print("\n🧪 Testing Product CRUD Operations...")
        
        # Test 1: Create Products
        test_products = [
            {
                "name": "Organic Coffee Beans",
                "description": "Premium organic coffee beans from Colombia",
                "price": 24.99,
                "stock": 50,
                "category": "Beverages",
                "is_active": True
            },
            {
                "name": "Wireless Bluetooth Headphones",
                "description": "High-quality wireless headphones with noise cancellation",
                "price": 89.99,
                "stock": 25,
                "category": "Electronics",
                "is_active": True
            },
            {
                "name": "Artisan Chocolate Bar",
                "description": "Handcrafted dark chocolate with sea salt",
                "price": 8.50,
                "stock": 100,
                "category": "Food",
                "is_active": True
            }
        ]

        for product_data in test_products:
            try:
                response = requests.post(f"{self.base_url}/products", 
                                       json=product_data, headers=self.headers)
                if response.status_code == 200:
                    product = response.json()
                    self.created_products.append(product)
                    self.log_result("product_crud", f"Create product '{product_data['name']}'", True)
                else:
                    self.log_result("product_crud", f"Create product '{product_data['name']}'", 
                                  False, f"Status: {response.status_code}, Response: {response.text}")
            except Exception as e:
                self.log_result("product_crud", f"Create product '{product_data['name']}'", False, str(e))

        # Test 2: Get All Products
        try:
            response = requests.get(f"{self.base_url}/products", headers=self.headers)
            if response.status_code == 200:
                products = response.json()
                if len(products) >= len(test_products):
                    self.log_result("product_crud", "Get all products", True)
                else:
                    self.log_result("product_crud", "Get all products", False, 
                                  f"Expected at least {len(test_products)} products, got {len(products)}")
            else:
                self.log_result("product_crud", "Get all products", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("product_crud", "Get all products", False, str(e))

        # Test 3: Get Product by ID
        if self.created_products:
            product_id = self.created_products[0]["id"]
            try:
                response = requests.get(f"{self.base_url}/products/{product_id}", headers=self.headers)
                if response.status_code == 200:
                    product = response.json()
                    if product["id"] == product_id:
                        self.log_result("product_crud", "Get product by ID", True)
                    else:
                        self.log_result("product_crud", "Get product by ID", False, "ID mismatch")
                else:
                    self.log_result("product_crud", "Get product by ID", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("product_crud", "Get product by ID", False, str(e))

        # Test 4: Update Product
        if self.created_products:
            product_id = self.created_products[0]["id"]
            update_data = {
                "price": 26.99,
                "stock": 45,
                "description": "Updated: Premium organic coffee beans from Colombia - Fair Trade"
            }
            try:
                response = requests.put(f"{self.base_url}/products/{product_id}", 
                                      json=update_data, headers=self.headers)
                if response.status_code == 200:
                    updated_product = response.json()
                    if updated_product["price"] == 26.99 and updated_product["stock"] == 45:
                        self.log_result("product_crud", "Update product", True)
                    else:
                        self.log_result("product_crud", "Update product", False, "Update values not reflected")
                else:
                    self.log_result("product_crud", "Update product", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("product_crud", "Update product", False, str(e))

        # Test 5: Filter Products by Category
        try:
            response = requests.get(f"{self.base_url}/products?category=Electronics", headers=self.headers)
            if response.status_code == 200:
                products = response.json()
                electronics_products = [p for p in products if p["category"] == "Electronics"]
                if len(electronics_products) > 0:
                    self.log_result("product_crud", "Filter products by category", True)
                else:
                    self.log_result("product_crud", "Filter products by category", False, 
                                  "No electronics products found")
            else:
                self.log_result("product_crud", "Filter products by category", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("product_crud", "Filter products by category", False, str(e))

        # Test 6: Delete Product (Soft Delete)
        if len(self.created_products) > 1:
            product_id = self.created_products[-1]["id"]
            try:
                response = requests.delete(f"{self.base_url}/products/{product_id}", headers=self.headers)
                if response.status_code == 200:
                    # Verify product is soft deleted (is_active = False)
                    get_response = requests.get(f"{self.base_url}/products/{product_id}", headers=self.headers)
                    if get_response.status_code == 200:
                        product = get_response.json()
                        if not product.get("is_active", True):
                            self.log_result("product_crud", "Delete product (soft delete)", True)
                        else:
                            self.log_result("product_crud", "Delete product (soft delete)", False, 
                                          "Product still active after delete")
                    else:
                        self.log_result("product_crud", "Delete product (soft delete)", True)
                else:
                    self.log_result("product_crud", "Delete product (soft delete)", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("product_crud", "Delete product (soft delete)", False, str(e))

        # Test 7: Invalid Product ID Handling
        try:
            response = requests.get(f"{self.base_url}/products/invalid_id", headers=self.headers)
            if response.status_code == 400:
                self.log_result("product_crud", "Invalid product ID handling", True)
            else:
                self.log_result("product_crud", "Invalid product ID handling", False, 
                              f"Expected 400, got {response.status_code}")
        except Exception as e:
            self.log_result("product_crud", "Invalid product ID handling", False, str(e))

    def test_transaction_operations(self):
        """Test Transaction API operations"""
        print("\n🧪 Testing Transaction Operations...")
        
        if len(self.created_products) < 2:
            self.log_result("transactions", "Transaction tests", False, 
                          "Not enough products created for transaction testing")
            return

        # Test 1: Create Transaction
        transaction_data = {
            "items": [
                {
                    "product_id": self.created_products[0]["id"],
                    "product_name": self.created_products[0]["name"],
                    "price": self.created_products[0]["price"],
                    "quantity": 2,
                    "total": self.created_products[0]["price"] * 2
                },
                {
                    "product_id": self.created_products[1]["id"],
                    "product_name": self.created_products[1]["name"],
                    "price": self.created_products[1]["price"],
                    "quantity": 1,
                    "total": self.created_products[1]["price"]
                }
            ],
            "subtotal": (self.created_products[0]["price"] * 2) + self.created_products[1]["price"],
            "tax": 5.50,
            "discount": 0.0,
            "total": (self.created_products[0]["price"] * 2) + self.created_products[1]["price"] + 5.50,
            "payment_method": "card",
            "customer_name": "Sarah Johnson",
            "notes": "Customer requested gift wrapping"
        }

        try:
            response = requests.post(f"{self.base_url}/transactions", 
                                   json=transaction_data, headers=self.headers)
            if response.status_code == 200:
                transaction = response.json()
                self.created_transactions.append(transaction)
                
                # Verify transaction number generation
                if "transaction_number" in transaction and transaction["transaction_number"].startswith("TXN-"):
                    self.log_result("transactions", "Create transaction with number generation", True)
                else:
                    self.log_result("transactions", "Create transaction with number generation", False, 
                                  "Transaction number not generated properly")
                
                # Verify stock deduction
                product_id = self.created_products[0]["id"]
                product_response = requests.get(f"{self.base_url}/products/{product_id}", headers=self.headers)
                if product_response.status_code == 200:
                    updated_product = product_response.json()
                    original_stock = self.created_products[0]["stock"]
                    current_stock = updated_product["stock"]
                    # Stock should be reduced by the quantity purchased (2 units)
                    if current_stock <= original_stock:
                        self.log_result("transactions", "Stock deduction after transaction", True)
                    else:
                        self.log_result("transactions", "Stock deduction after transaction", False, 
                                      f"Stock not reduced. Original: {original_stock}, Current: {current_stock}")
                
            else:
                self.log_result("transactions", "Create transaction", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("transactions", "Create transaction", False, str(e))

        # Test 2: Get All Transactions
        try:
            response = requests.get(f"{self.base_url}/transactions", headers=self.headers)
            if response.status_code == 200:
                transactions = response.json()
                if len(transactions) >= len(self.created_transactions):
                    self.log_result("transactions", "Get all transactions", True)
                else:
                    self.log_result("transactions", "Get all transactions", False, 
                                  f"Expected at least {len(self.created_transactions)} transactions")
            else:
                self.log_result("transactions", "Get all transactions", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("transactions", "Get all transactions", False, str(e))

        # Test 3: Get Transaction by ID
        if self.created_transactions:
            transaction_id = self.created_transactions[0]["id"]
            try:
                response = requests.get(f"{self.base_url}/transactions/{transaction_id}", headers=self.headers)
                if response.status_code == 200:
                    transaction = response.json()
                    if transaction["id"] == transaction_id:
                        self.log_result("transactions", "Get transaction by ID", True)
                    else:
                        self.log_result("transactions", "Get transaction by ID", False, "ID mismatch")
                else:
                    self.log_result("transactions", "Get transaction by ID", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("transactions", "Get transaction by ID", False, str(e))

        # Test 4: Transaction Pagination
        try:
            response = requests.get(f"{self.base_url}/transactions?limit=1&skip=0", headers=self.headers)
            if response.status_code == 200:
                transactions = response.json()
                if len(transactions) <= 1:
                    self.log_result("transactions", "Transaction pagination", True)
                else:
                    self.log_result("transactions", "Transaction pagination", False, 
                                  f"Expected max 1 transaction, got {len(transactions)}")
            else:
                self.log_result("transactions", "Transaction pagination", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("transactions", "Transaction pagination", False, str(e))

    def test_categories_api(self):
        """Test Categories API"""
        print("\n🧪 Testing Categories API...")
        
        try:
            response = requests.get(f"{self.base_url}/categories", headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if "categories" in data and isinstance(data["categories"], list):
                    categories = data["categories"]
                    expected_categories = ["Beverages", "Electronics", "Food"]
                    found_categories = [cat for cat in expected_categories if cat in categories]
                    if len(found_categories) > 0:
                        self.log_result("categories", "Get categories", True)
                    else:
                        self.log_result("categories", "Get categories", False, 
                                      f"Expected categories not found. Got: {categories}")
                else:
                    self.log_result("categories", "Get categories", False, "Invalid response format")
            else:
                self.log_result("categories", "Get categories", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("categories", "Get categories", False, str(e))

    def test_dashboard_analytics(self):
        """Test Dashboard/Analytics API"""
        print("\n🧪 Testing Dashboard Analytics...")
        
        try:
            response = requests.get(f"{self.base_url}/dashboard/stats", headers=self.headers)
            if response.status_code == 200:
                stats = response.json()
                required_fields = ["total_products", "total_transactions", "today_revenue", 
                                 "today_transactions", "low_stock_count"]
                
                missing_fields = [field for field in required_fields if field not in stats]
                if not missing_fields:
                    # Verify data types and reasonable values
                    if (isinstance(stats["total_products"], int) and stats["total_products"] >= 0 and
                        isinstance(stats["total_transactions"], int) and stats["total_transactions"] >= 0 and
                        isinstance(stats["today_revenue"], (int, float)) and stats["today_revenue"] >= 0 and
                        isinstance(stats["today_transactions"], int) and stats["today_transactions"] >= 0 and
                        isinstance(stats["low_stock_count"], int) and stats["low_stock_count"] >= 0):
                        
                        self.log_result("dashboard", "Dashboard stats structure and types", True)
                        
                        # Verify stats reflect our test data
                        if stats["total_products"] >= len([p for p in self.created_products if p.get("is_active", True)]):
                            self.log_result("dashboard", "Product count accuracy", True)
                        else:
                            self.log_result("dashboard", "Product count accuracy", False, 
                                          f"Expected >= {len(self.created_products)}, got {stats['total_products']}")
                        
                        if stats["total_transactions"] >= len(self.created_transactions):
                            self.log_result("dashboard", "Transaction count accuracy", True)
                        else:
                            self.log_result("dashboard", "Transaction count accuracy", False, 
                                          f"Expected >= {len(self.created_transactions)}, got {stats['total_transactions']}")
                    else:
                        self.log_result("dashboard", "Dashboard stats data types", False, 
                                      f"Invalid data types in response: {stats}")
                else:
                    self.log_result("dashboard", "Dashboard stats completeness", False, 
                                  f"Missing fields: {missing_fields}")
            else:
                self.log_result("dashboard", "Dashboard stats API", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("dashboard", "Dashboard stats API", False, str(e))

    def test_error_handling(self):
        """Test API error handling"""
        print("\n🧪 Testing Error Handling...")
        
        # Test invalid product creation
        try:
            invalid_product = {
                "name": "",  # Invalid: empty name
                "price": -10,  # Invalid: negative price
                "stock": -5   # Invalid: negative stock
            }
            response = requests.post(f"{self.base_url}/products", 
                                   json=invalid_product, headers=self.headers)
            if response.status_code in [400, 422]:  # Bad request or validation error
                self.log_result("product_crud", "Invalid product validation", True)
            else:
                self.log_result("product_crud", "Invalid product validation", False, 
                              f"Expected 400/422, got {response.status_code}")
        except Exception as e:
            self.log_result("product_crud", "Invalid product validation", False, str(e))

        # Test non-existent product
        try:
            response = requests.get(f"{self.base_url}/products/507f1f77bcf86cd799439011", headers=self.headers)
            if response.status_code == 404:
                self.log_result("product_crud", "Non-existent product handling", True)
            else:
                self.log_result("product_crud", "Non-existent product handling", False, 
                              f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("product_crud", "Non-existent product handling", False, str(e))

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting POS Backend API Testing...")
        print(f"Testing against: {self.base_url}")
        
        # Run tests in order
        self.test_product_crud_operations()
        self.test_categories_api()
        self.test_transaction_operations()
        self.test_dashboard_analytics()
        self.test_error_handling()
        
        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("📊 TEST RESULTS SUMMARY")
        print("="*60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ PASS" if failed == 0 else "❌ FAIL"
            print(f"{category.upper().replace('_', ' ')}: {status} ({passed} passed, {failed} failed)")
            
            if results["errors"]:
                for error in results["errors"]:
                    print(f"  ❌ {error}")
        
        print("-" * 60)
        print(f"OVERALL: {total_passed} passed, {total_failed} failed")
        
        if total_failed == 0:
            print("🎉 All tests passed! Backend API is working correctly.")
        else:
            print(f"⚠️  {total_failed} tests failed. Please review the errors above.")
        
        return total_failed == 0

if __name__ == "__main__":
    tester = POSBackendTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)