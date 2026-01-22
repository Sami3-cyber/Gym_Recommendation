"""
Mock Supabase Client for local development/testing without credentials
Mimics the supabase-py interface but stores data in memory.
"""
from uuid import uuid4
from datetime import datetime

class MockResponse:
    def __init__(self, data):
        self.data = data

class MockQueryBuilder:
    def __init__(self, table_name, db):
        self.table_name = table_name
        self.db = db
        self.filters = []
        self.order_by = None
        self.action = 'select'
        self.insert_data = None
        self.update_data = None
    
    def select(self, columns="*"):
        self.action = 'select'
        return self
    
    def insert(self, data):
        self.insert_data = data if isinstance(data, list) else [data]
        self.action = 'insert'
        return self
    
    def update(self, data):
        self.update_data = data
        self.action = 'update'
        return self
    
    def delete(self):
        self.action = 'delete'
        return self
    
    def eq(self, column, value):
        self.filters.append((column, value))
        return self
        
    def order(self, column, desc=False):
        self.order_by = (column, desc)
        return self
        
    def execute(self):
        # Handle Insert separately as it's not a query on existing data
        if self.action == 'insert':
            inserted_items = []
            for item in self.insert_data:
                # Copy to avoid modifying the input dict
                new_item = item.copy()
                # Auto-generate ID if missing
                if 'id' not in new_item:
                    new_item['id'] = str(uuid4())
                # Auto-generate timestamps
                if 'created_at' not in new_item:
                    new_item['created_at'] = datetime.now().isoformat()
                
                self.db.data[self.table_name].append(new_item)
                inserted_items.append(new_item)
            return MockResponse(inserted_items)

        # Start with all data for Select/Update/Delete
        results = self.db.data.get(self.table_name, [])
        
        # Apply filters
        filtered_results = []
        for row in results:
            match = True
            for col, val in self.filters:
                if row.get(col) != val:
                    match = False
                    break
            if match:
                filtered_results.append(row)
        
        if self.action == 'update':
            for row in filtered_results:
                row.update(self.update_data)
            return MockResponse(filtered_results)
        
        elif self.action == 'delete':
            # Filter the master list
            self.db.data[self.table_name] = [r for r in results if r not in filtered_results]
            return MockResponse(filtered_results)
        
        elif self.action == 'select':
            # Apply Sorting
            if self.order_by:
                col, desc = self.order_by
                filtered_results.sort(key=lambda x: str(x.get(col, "")), reverse=desc)
            return MockResponse(filtered_results)
            
        return MockResponse([])

class MockClient:
    def __init__(self):
        self.data = {
            "users": [],
            "favorites": [],
            "history": []
        }
        print("⚠️ Using In-Memory Mock Database (Data will be lost on restart)")

    def table(self, table_name):
        if table_name not in self.data:
            self.data[table_name] = []
        return MockQueryBuilder(table_name, self)
