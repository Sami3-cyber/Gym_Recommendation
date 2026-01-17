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
    
    def select(self, columns="*"):
        return self
    
    def insert(self, data):
        if not isinstance(data, list):
            data = [data]
        
        for item in data:
            # Auto-generate ID if missing
            if 'id' not in item:
                item['id'] = str(uuid4())
            # Auto-generate timestamps
            if 'created_at' not in item:
                item['created_at'] = datetime.now().isoformat()
            
            self.db.data[self.table_name].append(item)
            
        return MockResponse(data)
    
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
        # Start with all data
        results = self.db.data.get(self.table_name, [])
        
        # Apply filters
        filtered_results = []
        for row in results:
            match = True
            for col, val in self.filters:
                # Handle nested dicts or simple values
                row_val = row.get(col)
                if row_val != val:
                    match = False
                    break
            if match:
                filtered_results.append(row)
        
        # Handle Actions (Update/Delete)
        if hasattr(self, 'action'):
            if self.action == 'update':
                for row in filtered_results:
                    row.update(self.update_data)
                return MockResponse(filtered_results)
            
            elif self.action == 'delete':
                # Rebuild the table keeping only non-matching rows
                # This is modifying the list in-place which is tricky during iteration
                # So we rebuild the master list
                keep_rows = []
                for row in results:
                    keep = False
                    # Check if this row IS NOT in the filtered results
                    # Simple way: check ID
                    if row not in filtered_results:
                        keep_rows.append(row)
                        
                self.db.data[self.table_name] = keep_rows
                return MockResponse(filtered_results)
        
        # Apply Sorting (for Select)
        if self.order_by:
            col, desc = self.order_by
            filtered_results.sort(key=lambda x: x.get(col, ""), reverse=desc)
            
        return MockResponse(filtered_results)

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

