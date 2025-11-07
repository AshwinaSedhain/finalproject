# dashboard_generator.py
"""
Dashboard Analytics Generator
Generates dynamic dashboard data based on database schema and content
"""

import json
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Import LLM manager for intelligent metric generation
try:
    from chatbot.llm_manager import FreeLLMManager
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Warning: LLM manager not available, using fallback metric generation")

class DashboardGenerator:
    """Generates dashboard analytics data from database."""
    
    # Light, vibrant color palette for bar charts
    BAR_CHART_COLORS = [
        "#2dd4bf",  # light teal
        "#fb923c",  # light orange
        "#60a5fa",  # light blue
        "#a78bfa",  # light purple
        "#f472b6",  # light pink
        "#4ade80",  # light green
        "#34d399",  # emerald
        "#fbbf24",  # amber
        "#818cf8",  # indigo
        "#ec4899",  # rose
    ]
    
    def __init__(self, db_url: str, knowledge_base: Dict):
        self.db_url = db_url
        self.knowledge_base = knowledge_base
        self.engine = None
        try:
            self.engine = create_engine(db_url)
        except Exception as e:
            print(f"Warning: Could not connect to database: {e}")
    
    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard data."""
        print("[Dashboard] Starting dashboard generation...")
        if not self.engine:
            print("[Dashboard] No engine, returning default")
            return self._get_default_dashboard()
        
        try:
            # Analyze database structure
            print("[Dashboard] Inspecting database...")
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            if not tables:
                print("[Dashboard] No tables found, returning default")
                return self._get_default_dashboard()
            
            print(f"[Dashboard] Found {len(tables)} tables, using first table")
            # Find primary table (usually the first one or the one with most data)
            primary_table = self._find_primary_table(tables)
            print(f"[Dashboard] Primary table: {primary_table}")
            
            # Generate metrics (returns both formatted metrics and raw values)
            print("[Dashboard] Generating metrics...")
            metrics_result = self._generate_metrics(primary_table, tables)
            metrics = metrics_result["metrics"]
            metric_values = metrics_result["values"]  # Raw numeric values for pie chart
            print("[Dashboard] Metrics generated")
            print(f"[Dashboard] Metric values received: Revenue={metric_values.get('revenue')}, Expenses={metric_values.get('expenses')}, Loss={metric_values.get('loss')}, Profit={metric_values.get('profit')}")
            print(f"[Dashboard] Metric values types: Revenue={type(metric_values.get('revenue'))}, Loss={type(metric_values.get('loss'))}, Loss value={metric_values.get('loss')}, Loss > 0: {metric_values.get('loss', 0) > 0}")
            
            # Generate top selling products chart (replaces table data)
            print("[Dashboard] Generating top selling chart...")
            try:
                top_selling_chart = self._generate_top_selling_products(primary_table, tables)
                print("[Dashboard] Top selling chart generated")
            except Exception as e:
                print(f"[Dashboard] Error generating top selling chart: {e}")
                top_selling_chart = {
                "data": [{"type": "bar", "orientation": "h", "x": [], "y": [], "marker": {"color": self.BAR_CHART_COLORS}}],
                "layout": {"title": "Top Selling Products", "xaxis": {"title": "Total Sales"}, "yaxis": {"title": "Product"}, "height": 400}
                }
            
            # Generate pie chart data using the same values from metrics
            print("[Dashboard] Generating pie chart from metrics data...")
            try:
                pie_chart = self._generate_pie_chart_from_metrics(metric_values)
                print("[Dashboard] Pie chart generated from metrics")
            except Exception as e:
                print(f"[Dashboard] Error generating pie chart: {e}")
                import traceback
                traceback.print_exc()
                pie_chart = {
                "data": [{"type": "pie", "values": [0, 0], "labels": ["Revenue", "Expenses"], "marker": {"colors": ["#2dd4bf", "#a78bfa"]}}],
                "layout": {"title": "", "showlegend": True}
                }
            
            # Generate additional charts for comprehensive dashboard
            print("[Dashboard] Generating sales by category chart...")
            sales_by_category_chart = self._generate_sales_by_category(primary_table, tables)
            
            print("[Dashboard] Generating sales by product group chart...")
            sales_by_group_chart = self._generate_sales_by_product_group(primary_table, tables)
            
            print("[Dashboard] Generating sales by division pie chart...")
            sales_by_division_chart = self._generate_sales_by_division(primary_table, tables)
            
            print("[Dashboard] Generating unsold items list...")
            unsold_items = self._generate_unsold_items(primary_table, tables)
            
            # Calculate unsold items percentage and update metrics
            total_items = len(unsold_items) + 10  # Approximate total (will be improved)
            unsold_count = len(unsold_items)
            unsold_percentage = (unsold_count / total_items * 100) if total_items > 0 else 0.0
            
            # Update unsold items % metric if it exists, or add it
            unsold_metric_exists = False
            for metric in metrics:
                if metric.get('label') == 'Unsold Items %':
                    metric['value'] = f"{unsold_percentage:.2f}"
                    unsold_metric_exists = True
                    break
            
            if not unsold_metric_exists and len(metrics) < 6:
                # Add unsold items % metric
                metrics.append({
                    "label": "Unsold Items %",
                    "value": f"{unsold_percentage:.2f}",
                    "unit": "%",
                    "color": "#10b981",
                    "icon": "📊"
                })
            
            # Determine business type
            print("[Dashboard] Determining business type...")
            business_type = self._detect_business_type()
            print("[Dashboard] Dashboard generation complete!")
            
            return {
                "businessType": business_type,
                "metrics": metrics[:6],  # Ensure exactly 6 metrics
                "topSellingChart": top_selling_chart,
                "salesByCategoryChart": sales_by_category_chart,
                "salesByGroupChart": sales_by_group_chart,
                "pieChart": pie_chart,
                "salesByDivisionChart": sales_by_division_chart,
                "unsoldItems": unsold_items
            }
        except Exception as e:
            print(f"[Dashboard] Error generating dashboard: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_dashboard()
    
    def _get_default_metrics(self) -> List[Dict]:
        """Return default metrics when generation fails."""
        return [
            {"label": "Total Revenue", "value": "0", "unit": "", "color": "#2dd4bf", "icon": "💰"},
            {"label": "Total Purchases", "value": "0", "unit": "", "color": "#60a5fa", "icon": "🛒"},
            {"label": "Total Loss", "value": "0", "unit": "", "color": "#fb923c", "icon": "📉"},
            {"label": "Total Records", "value": "0", "unit": "", "color": "#a78bfa", "icon": "📊"}
        ]
    
    def _get_default_top_selling_chart(self) -> Dict:
        """Return default top selling chart when generation fails."""
        return {
            "data": [{
                "type": "bar",
                "orientation": "h",
                "x": [],
                "y": [],
                "marker": {"color": "#10b981"}
            }],
            "layout": {
                "title": "Top Selling Products",
                "xaxis": {"title": "Total Sales"},
                "yaxis": {"title": "Product"},
                "height": 400
            }
        }
    
    def _get_default_pie_chart(self) -> Dict:
        """Return default pie chart when generation fails."""
        return {
            "data": [{
                "type": "pie",
                "values": [0, 0],
                "labels": ["Revenue", "Expenses"],
                "marker": {
                    "colors": ["#10b981", "#8b5cf6"]
                }
            }],
            "layout": {
                "title": "",
                "showlegend": True
            }
        }
    
    def _find_primary_table(self, tables: List[str]) -> str:
        """Find the primary table (usually the one with most data)."""
        # Just use the first table - avoid slow COUNT(*) queries
        # COUNT(*) on large tables can be very slow
        return tables[0] if tables else "unknown"
    
    def _validate_identifier(self, identifier: str) -> bool:
        """Validate that identifier is safe (only alphanumeric, underscore, no SQL injection)."""
        if not identifier or not isinstance(identifier, str):
            return False
        # Allow only alphanumeric, underscore, and dash (common in table/column names)
        import re
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', identifier))
    
    def _get_table_size_estimate(self, conn, table_name: str) -> int:
        """Get approximate table size quickly."""
        # Validate table name to prevent SQL injection
        if not self._validate_identifier(table_name):
            print(f"[Dashboard] Invalid table name: {table_name}")
            return 150000  # Default to medium-large table
        
        try:
            # Try PostgreSQL's reltuples (very fast, approximate count)
            # Using parameterized query would be better, but relname needs to be in WHERE clause
            # Since table_name is validated, it's safe
            result = conn.execute(text(f"SELECT reltuples::BIGINT FROM pg_class WHERE relname = '{table_name}'"))
            count = int(result.scalar() or 0)
            if count > 0:
                return count
        except Exception as e:
            print(f"[Dashboard] Could not get reltuples for {table_name}: {e}")
        
        # Fallback: assume it's a medium-sized table (will use LIMIT for safety)
        # We don't want to do COUNT(*) here as it can be very slow on large tables
        return 150000  # Default to medium-large table (will use LIMIT)
    
    def _generate_metrics(self, primary_table: str, all_tables: List[str]) -> List[Dict]:
        """Generate analytics overview metrics intelligently based on actual database schema."""
        metrics = []
        
        # Validate primary table name
        if not self._validate_identifier(primary_table):
            print(f"[Dashboard] Invalid primary table name: {primary_table}")
            return self._get_default_metrics()
        
        try:
            with self.engine.connect() as conn:
                inspector = inspect(self.engine)
                columns_info = inspector.get_columns(primary_table)
                columns = [col['name'] for col in columns_info]
                # Validate all column names
                columns = [col for col in columns if self._validate_identifier(col)]
                column_types = {col['name']: str(col['type']) for col in columns_info if self._validate_identifier(col['name'])}
                
                if not columns:
                    print(f"[Dashboard] No valid columns found in table {primary_table}")
                    return self._get_default_metrics()
                
                # Get table size estimate to decide on query strategy
                table_size = self._get_table_size_estimate(conn, primary_table)
                use_limit = table_size > 100000  # Use LIMIT only for large tables
                limit_value = 200000 if use_limit else None  # Increased limit for better accuracy
                
                print(f"[Dashboard] Table {primary_table} estimated size: {table_size}, using_limit: {use_limit}")
                
                # Use knowledge base to understand column meanings
                table_kb = self.knowledge_base.get(primary_table, {})
                column_descriptions = table_kb.get('columns', {})
                
                print(f"[Dashboard] Available columns: {columns[:10]}...")  # Log first 10 columns
                
                # Intelligently find columns using knowledge base descriptions
                date_col = self._find_column_smart(columns, column_descriptions, 
                    ['date', 'created', 'timestamp', 'time', 'updated', 'modified'], 
                    ['date', 'time', 'timestamp', 'datetime'])
                
                numeric_cols = self._find_numeric_columns(columns, column_types, column_descriptions)
                status_col = self._find_column_smart(columns, column_descriptions,
                    ['status', 'state', 'stock_status', 'condition', 'type'], 
                    ['varchar', 'text', 'character'])
                
                # PRIORITY METRICS: Total Revenue, Total Purchases, Total Loss, Total Expenses
                # Find relevant columns first
                revenue_col = None
                purchase_col = None
                cost_col = None
                expense_col = None  # Separate expense column (recurring expenses)
                
                for num_col in numeric_cols:
                    col_desc = column_descriptions.get(num_col, {}).get('description', '').lower()
                    col_lower = num_col.lower()
                    
                    # Find revenue column (prioritize revenue, sales, income, then amount/price)
                    if not revenue_col:
                        if any(word in col_desc or word in col_lower for word in ['revenue', 'sales', 'income']):
                            revenue_col = num_col
                        elif not revenue_col and any(word in col_desc or word in col_lower for word in ['amount', 'total', 'price', 'value']):
                            revenue_col = num_col
                    
                    # Find purchase/order column
                    if not purchase_col:
                        if any(word in col_desc or word in col_lower for word in ['purchase', 'order', 'transaction']):
                            purchase_col = num_col
                        elif any(word in col_desc or word in col_lower for word in ['quantity']):
                            purchase_col = num_col
                    
                    # Find expense column (recurring expenses, separate from loss)
                    if not expense_col:
                        expense_keywords = ['expense', 'operating', 'overhead']
                        if any(word in col_desc or word in col_lower for word in expense_keywords):
                            if 'expense' in col_lower or 'expense' in col_desc:
                                expense_col = num_col
                    
                    # Find cost/loss column (one-time losses, broader search)
                    if not cost_col:
                        loss_keywords = ['loss', 'writeoff', 'bad debt', 'depreciation', 'discount', 'refund', 'return']
                        # Also check for cost if expense_col is not set
                        if not expense_col:
                            loss_keywords.extend(['cost', 'spent', 'outgoing', 'payment', 'fee', 'charge', 'debit', 'withdrawal', 'deduction'])
                        if any(word in col_desc or word in col_lower for word in loss_keywords):
                            cost_col = num_col
                
                # Metric 1: Calculate Total Revenue
                revenue_value = None
                if revenue_col and self._validate_identifier(revenue_col):
                    print(f"[Dashboard] Using revenue column: {revenue_col}")
                    try:
                        if use_limit and limit_value:
                            # Use LIMIT for large tables
                            sum_query = f"""
                                SELECT SUM(\"{revenue_col}\") 
                                FROM (
                                    SELECT \"{revenue_col}\" 
                                    FROM {primary_table} 
                                    WHERE \"{revenue_col}\" IS NOT NULL 
                                    LIMIT {limit_value}
                                ) subquery
                            """
                        else:
                            # Full query for small tables
                            sum_query = f"SELECT SUM(\"{revenue_col}\") FROM {primary_table} WHERE \"{revenue_col}\" IS NOT NULL"
                        
                        result = conn.execute(text(sum_query))
                        revenue_value = result.scalar()
                        print(f"[Dashboard] Revenue calculated: {revenue_value}")
                    except Exception as e:
                        print(f"[Dashboard] Error calculating revenue: {e}")
                        revenue_value = None
                else:
                    print(f"[Dashboard] No revenue column found. Available numeric columns: {[c for c in numeric_cols[:5]]}")
                
                metrics.append({
                    "label": "Total Revenue",
                    "value": self._format_number(revenue_value) if revenue_value is not None and revenue_value > 0 else "0",
                    "unit": "",
                    "color": "#10b981",  # green
                    "icon": "💰"
                })
                
                # Metric 2: Calculate Total Purchases
                purchase_value = None
                if purchase_col and self._validate_identifier(purchase_col):
                    print(f"[Dashboard] Using purchase column: {purchase_col}")
                    try:
                        if 'quantity' in purchase_col.lower():
                            # Sum quantity column
                            if use_limit and limit_value:
                                sum_query = f"""
                                    SELECT SUM(\"{purchase_col}\") 
                                    FROM (
                                        SELECT \"{purchase_col}\" 
                                        FROM {primary_table} 
                                        WHERE \"{purchase_col}\" IS NOT NULL 
                                        LIMIT {limit_value}
                                    ) subquery
                                """
                            else:
                                sum_query = f"SELECT SUM(\"{purchase_col}\") FROM {primary_table} WHERE \"{purchase_col}\" IS NOT NULL"
                            result = conn.execute(text(sum_query))
                            purchase_value = result.scalar()
                        else:
                            # Count records
                            if use_limit:
                                # For large tables, use approximate count
                                try:
                                    count_query = f"SELECT reltuples::BIGINT FROM pg_class WHERE relname = '{primary_table}'"
                                    result = conn.execute(text(count_query))
                                    purchase_value = int(result.scalar() or 0)
                                except Exception as e:
                                    print(f"[Dashboard] Error in approximate count, using LIMIT fallback: {e}")
                                    # Fallback: count with LIMIT
                                    count_query = f"SELECT COUNT(*) FROM (SELECT 1 FROM {primary_table} LIMIT {limit_value}) subquery"
                                    result = conn.execute(text(count_query))
                                    purchase_value = result.scalar()
                            else:
                                # Full count for small tables
                                count_query = f"SELECT COUNT(*) FROM {primary_table}"
                                result = conn.execute(text(count_query))
                                purchase_value = result.scalar()
                        print(f"[Dashboard] Purchases calculated: {purchase_value}")
                    except Exception as e:
                        print(f"[Dashboard] Error calculating purchases: {e}")
                        import traceback
                        traceback.print_exc()
                else:
                    if purchase_col:
                        print(f"[Dashboard] Purchase column '{purchase_col}' failed validation")
                    else:
                        print(f"[Dashboard] No purchase column found")
                
                # If no purchase column, use count
                if purchase_value is None:
                    print(f"[Dashboard] No purchase column, using row count")
                    try:
                        if use_limit:
                            # Approximate count for large tables
                            try:
                                count_query = f"SELECT reltuples::BIGINT FROM pg_class WHERE relname = '{primary_table}'"
                                result = conn.execute(text(count_query))
                                purchase_value = int(result.scalar() or 0)
                            except Exception as e:
                                print(f"[Dashboard] Error in approximate count fallback: {e}")
                                purchase_value = table_size  # Use estimate
                        else:
                            # Full count for small tables
                            count_query = f"SELECT COUNT(*) FROM {primary_table}"
                            result = conn.execute(text(count_query))
                            purchase_value = result.scalar() or 0
                    except Exception as e:
                        print(f"[Dashboard] Error in purchase count fallback: {e}")
                        purchase_value = 0
                
                metrics.append({
                    "label": "Total Purchases",
                    "value": self._format_number(purchase_value) if purchase_value else "0",
                    "unit": "",
                    "color": "#3b82f6",  # blue
                    "icon": "🛒"
                })
                
                # Metric 3: Calculate Total Loss (one-time losses)
                loss_value = None
                if cost_col and self._validate_identifier(cost_col):
                    print(f"[Dashboard] Using loss column: {cost_col}")
                    try:
                        if use_limit and limit_value:
                            loss_query = f"""
                                SELECT SUM(\"{cost_col}\") 
                                FROM (
                                    SELECT \"{cost_col}\" 
                                    FROM {primary_table} 
                                    WHERE \"{cost_col}\" IS NOT NULL 
                                    LIMIT {limit_value}
                                ) subquery
                            """
                        else:
                            loss_query = f"SELECT SUM(\"{cost_col}\") FROM {primary_table} WHERE \"{cost_col}\" IS NOT NULL"
                        
                        result = conn.execute(text(loss_query))
                        loss_value = result.scalar()
                        print(f"[Dashboard] Loss calculated: {loss_value}")
                    except Exception as e:
                        print(f"[Dashboard] Error calculating loss: {e}")
                        loss_value = None
                else:
                    if cost_col:
                        print(f"[Dashboard] Loss column '{cost_col}' failed validation")
                    print(f"[Dashboard] No loss column found")
                
                # Calculate Total Expenses (recurring expenses, separate from loss)
                expenses_value_metric = None
                if expense_col and self._validate_identifier(expense_col):
                    print(f"[Dashboard] Using expense column: {expense_col}")
                    try:
                        if use_limit and limit_value:
                            expense_query = f"""
                                SELECT SUM(\"{expense_col}\") 
                                FROM (
                                    SELECT \"{expense_col}\" 
                                    FROM {primary_table} 
                                    WHERE \"{expense_col}\" IS NOT NULL 
                                    LIMIT {limit_value}
                                ) subquery
                            """
                        else:
                            expense_query = f"SELECT SUM(\"{expense_col}\") FROM {primary_table} WHERE \"{expense_col}\" IS NOT NULL"
                        
                        result = conn.execute(text(expense_query))
                        expenses_value_metric = result.scalar()
                        print(f"[Dashboard] Expenses calculated: {expenses_value_metric}")
                    except Exception as e:
                        print(f"[Dashboard] Error calculating expenses: {e}")
                        expenses_value_metric = None
                else:
                    if expense_col:
                        print(f"[Dashboard] Expense column '{expense_col}' failed validation")
                    print(f"[Dashboard] No expense column found")
                
                # If no cost column but we have revenue, try to find any expense-related column
                if loss_value is None and revenue_value is not None:
                    print(f"[Dashboard] No cost column found, searching for alternative expense columns...")
                    # Try to find any expense-related column with broader search
                    for num_col in numeric_cols:
                        if num_col != revenue_col and self._validate_identifier(num_col):
                            col_desc = column_descriptions.get(num_col, {}).get('description', '').lower()
                            col_lower = num_col.lower()
                            # Broader keyword matching
                            expense_keywords = ['expense', 'cost', 'outgoing', 'spent', 'payment', 'fee', 'charge', 
                                              'debit', 'withdrawal', 'deduction', 'discount', 'refund', 'return']
                            if any(word in col_desc or word in col_lower for word in expense_keywords):
                                print(f"[Dashboard] Found potential expense column: {num_col} (desc: {col_desc})")
                                try:
                                    if use_limit and limit_value:
                                        loss_query = f"""
                                            SELECT SUM(\"{num_col}\") 
                                            FROM (
                                                SELECT \"{num_col}\" 
                                                FROM {primary_table} 
                                                WHERE \"{num_col}\" IS NOT NULL 
                                                LIMIT {limit_value}
                                            ) subquery
                                        """
                                    else:
                                        loss_query = f"SELECT SUM(\"{num_col}\") FROM {primary_table} WHERE \"{num_col}\" IS NOT NULL"
                                    result = conn.execute(text(loss_query))
                                    calculated_loss = result.scalar()
                                    if calculated_loss and calculated_loss > 0:
                                        loss_value = calculated_loss
                                        print(f"[Dashboard] Successfully calculated loss from {num_col}: {loss_value}")
                                        break
                                except Exception as e:
                                    print(f"[Dashboard] Error trying expense column {num_col}: {e}")
                                    continue
                    
                    # If still no loss found, try looking for negative values in revenue column (returns/refunds)
                    if loss_value is None or loss_value == 0:
                        print(f"[Dashboard] Trying to find negative values in revenue column as expenses...")
                        if revenue_col and self._validate_identifier(revenue_col):
                            try:
                                if use_limit and limit_value:
                                    negative_query = f"""
                                        SELECT ABS(SUM(\"{revenue_col}\")) 
                                        FROM (
                                            SELECT \"{revenue_col}\" 
                                            FROM {primary_table} 
                                            WHERE \"{revenue_col}\" < 0 
                                            LIMIT {limit_value}
                                        ) subquery
                                    """
                                else:
                                    negative_query = f"SELECT ABS(SUM(\"{revenue_col}\")) FROM {primary_table} WHERE \"{revenue_col}\" < 0"
                                result = conn.execute(text(negative_query))
                                negative_sum = result.scalar()
                                if negative_sum and negative_sum > 0:
                                    loss_value = negative_sum
                                    print(f"[Dashboard] Found negative values (returns/refunds) as loss: {loss_value}")
                            except Exception as e:
                                print(f"[Dashboard] Error checking negative values: {e}")
                
                metrics.append({
                    "label": "Total Loss",
                    "value": self._format_number(loss_value) if loss_value is not None and loss_value > 0 else "0",
                    "unit": "",
                    "color": "#ef4444",  # red
                    "icon": "📉"
                })
                
                # Metric 4: Total Records Count (always available)
                try:
                    # Use smart query strategy for large tables
                    if use_limit and limit_value:
                        # For large tables, use approximate count
                        try:
                            count_query = f"SELECT reltuples::BIGINT FROM pg_class WHERE relname = '{primary_table}'"
                            result = conn.execute(text(count_query))
                            total_count = int(result.scalar() or 0)
                            if total_count == 0:
                                # Fallback to actual count if estimate is 0
                                count_query = f"SELECT COUNT(*) FROM {primary_table}"
                                result = conn.execute(text(count_query))
                                total_count = result.scalar() or 0
                        except Exception as e:
                            print(f"[Dashboard] Error in approximate count, using full count: {e}")
                            count_query = f"SELECT COUNT(*) FROM {primary_table}"
                            result = conn.execute(text(count_query))
                            total_count = result.scalar() or 0
                    else:
                        # Full count for small tables
                        count_query = f"SELECT COUNT(*) FROM {primary_table}"
                        result = conn.execute(text(count_query))
                        total_count = result.scalar() or 0
                    
                    print(f"[Dashboard] Total Records calculated: {total_count}")
                    metrics.append({
                        "label": "Total Records",
                        "value": f"{total_count:,}",
                        "unit": "",
                        "color": "#8b5cf6",  # purple
                        "icon": "📊"
                    })
                except Exception as e:
                    print(f"[Dashboard] Error getting total count: {e}")
                    import traceback
                    traceback.print_exc()
                    metrics.append({
                        "label": "Total Records",
                        "value": "0",
                        "unit": "",
                        "color": "#8b5cf6",
                        "icon": "📊"
                    })
                
                
        except Exception as e:
            print(f"Error generating metrics: {e}")
            import traceback
            traceback.print_exc()
        
        # Calculate profit from the values we have
        profit_value = None
        if revenue_value is not None:
            total_costs = (expenses_value_metric or 0) + (loss_value or 0)
            profit_value = revenue_value - total_costs
            if profit_value < 0:
                profit_value = 0  # Don't show negative profit
        
        # Ensure we have exactly 4 metrics
        # We should already have 4 metrics from above, but just in case
        if len(metrics) < 4:
            metric_labels = ["Total Revenue", "Total Purchases", "Total Loss", "Total Records"]
            metric_colors = ["#2dd4bf", "#60a5fa", "#fb923c", "#a78bfa", "#f472b6", "#4ade80"]
            metric_icons = ["💰", "🛒", "📉", "📊"]
            
            existing_labels = [m.get("label", "") for m in metrics]
            for idx in range(4):
                if len(metrics) >= 4:
                    break
                label = metric_labels[idx]
                if label not in existing_labels:
                    metrics.append({
                        "label": label,
                        "value": "0",
                        "unit": "",
                        "color": metric_colors[idx],
                        "icon": metric_icons[idx]
                    })
        
        # Return both formatted metrics and raw values for pie chart
        # CRITICAL: Ensure loss_value is properly converted to float (not None)
        loss_value_final = float(loss_value or 0) if loss_value is not None else 0.0
        revenue_value_final = float(revenue_value or 0) if revenue_value is not None else 0.0
        expenses_value_final = float(expenses_value_metric or 0) if expenses_value_metric is not None else 0.0
        profit_value_final = float(profit_value or 0) if profit_value is not None else 0.0
        
        print(f"[Dashboard] Returning metric values - Revenue: {revenue_value_final}, Expenses: {expenses_value_final}, Loss: {loss_value_final}, Profit: {profit_value_final}")
        print(f"[Dashboard] Loss value check - Original: {loss_value}, Final: {loss_value_final}, Type: {type(loss_value_final)}, > 0: {loss_value_final > 0}")
        
        # Add additional metrics: Receipt count, Quantity, Cost, Unsold Items %
        # Metric 5: Receipt/Order count
        receipt_count = purchase_value if purchase_value else 0
        metrics.append({
            "label": "Receipt",
            "value": self._format_number(receipt_count),
            "unit": "",
            "color": "#ef4444",
            "icon": "📄"
        })
        
        # Metric 6: Quantity (if available)
        quantity_value = purchase_value if purchase_col and 'quantity' in purchase_col.lower() else 0
        metrics.append({
            "label": "Quantity",
            "value": self._format_number(quantity_value),
            "unit": "",
            "color": "#8b5cf6",
            "icon": "🛒"
        })
        
        # Metric 7: Cost (expenses + loss)
        cost_total = expenses_value_final + loss_value_final
        metrics.append({
            "label": "Cost",
            "value": self._format_number(cost_total),
            "unit": "",
            "color": "#f59e0b",
            "icon": "💰"
        })
        
        # Metric 8: Unsold Items % (will be calculated dynamically)
        # For now, set a placeholder - will be calculated from unsold items
        unsold_percentage = 0.0
        
        return {
            "metrics": metrics[:6],  # Return exactly 6 metrics (Revenue, Purchases, Loss, Profit, Receipt, Quantity)
            "values": {
                "revenue": revenue_value_final,
                "expenses": expenses_value_final,
                "loss": loss_value_final,  # CRITICAL: Always include loss if it exists
                "profit": profit_value_final
            }
        }
    
    def _find_column_smart(self, columns: List[str], column_descriptions: Dict, 
                          keywords: List[str], type_hints: List[str] = None) -> Optional[str]:
        """Intelligently find column using both name and description."""
        # First try exact keyword match
        for keyword in keywords:
            for col in columns:
                if keyword.lower() in col.lower():
                    return col
        
        # Then try description match
        for col, col_info in column_descriptions.items():
            if col in columns:
                desc = col_info.get('description', '').lower()
                for keyword in keywords:
                    if keyword in desc:
                        return col
        
        return None
    
    def _find_numeric_columns(self, columns: List[str], column_types: Dict, 
                             column_descriptions: Dict) -> List[str]:
        """Find all numeric columns."""
        numeric_cols = []
        numeric_types = ['integer', 'int', 'bigint', 'smallint', 'numeric', 'decimal', 
                        'real', 'double', 'float', 'money']
        
        for col in columns:
            col_type = column_types.get(col, '').lower()
            if any(nt in col_type for nt in numeric_types):
                # Skip ID columns
                if 'id' not in col.lower() or col.lower() == 'id':
                    numeric_cols.append(col)
        
        return numeric_cols
    
    def _get_today_count(self, conn, table: str, date_col: str, col_type: str) -> Optional[int]:
        """Get count of records from today."""
        # Validate identifiers
        if not self._validate_identifier(table) or not self._validate_identifier(date_col):
            return None
        
        queries = [
            f"SELECT COUNT(*) FROM {table} WHERE DATE(\"{date_col}\") = CURRENT_DATE",
            f"SELECT COUNT(*) FROM {table} WHERE \"{date_col}\"::date = CURRENT_DATE",
            f"SELECT COUNT(*) FROM {table} WHERE \"{date_col}\" >= CURRENT_DATE::date AND \"{date_col}\" < (CURRENT_DATE + INTERVAL '1 day')::date",
        ]
        
        for query in queries:
            try:
                result = conn.execute(text(query))
                return result.scalar()
            except Exception as e:
                print(f"[Dashboard] Error in today count query: {e}")
                continue
        return None
    
    def _get_week_count(self, conn, table: str, date_col: str, col_type: str) -> Optional[int]:
        """Get count of records from last 7 days."""
        # Validate identifiers
        if not self._validate_identifier(table) or not self._validate_identifier(date_col):
            return None
        
        queries = [
            f"SELECT COUNT(*) FROM {table} WHERE \"{date_col}\" >= CURRENT_DATE - INTERVAL '7 days'",
            f"SELECT COUNT(*) FROM {table} WHERE \"{date_col}\"::date >= CURRENT_DATE - INTERVAL '7 days'",
        ]
        
        for query in queries:
            try:
                result = conn.execute(text(query))
                return result.scalar()
            except Exception as e:
                print(f"[Dashboard] Error in week count query: {e}")
                continue
        return None
    
    def _get_status_counts(self, conn, table: str, status_col: str) -> Dict[str, int]:
        """Get counts by status."""
        # Validate identifiers
        if not self._validate_identifier(table) or not self._validate_identifier(status_col):
            return {}
        
        try:
            query = f"SELECT \"{status_col}\", COUNT(*) as count FROM {table} GROUP BY \"{status_col}\" ORDER BY count DESC LIMIT 5"
            result = conn.execute(text(query))
            return {row[0]: row[1] for row in result if row[0]}
        except Exception as e:
            print(f"[Dashboard] Error getting status counts: {e}")
            return {}
    
    def _get_date_metric_label(self, date_col: str, description: str) -> str:
        """Generate appropriate label for date-based metric."""
        desc_lower = description.lower()
        col_lower = date_col.lower()
        
        if 'created' in col_lower or 'created' in desc_lower:
            return "Today's New Records"
        elif 'updated' in col_lower or 'modified' in desc_lower:
            return "Updated Today"
        else:
            return "Today's Records"
    
    def _get_numeric_metric_label(self, col_name: str, description: str, operation: str) -> str:
        """Generate appropriate label for numeric metric."""
        desc_lower = description.lower()
        col_lower = col_name.lower()
        
        if operation == 'sum':
            if 'total' in desc_lower or 'total' in col_lower:
                return "Total"
            elif 'amount' in desc_lower or 'amount' in col_lower:
                return "Total Amount"
            elif 'quantity' in desc_lower or 'quantity' in col_lower:
                return "Total Quantity"
            elif 'stock' in desc_lower or 'stock' in col_lower:
                return "Total Stock"
            elif 'revenue' in desc_lower or 'revenue' in col_lower:
                return "Total Revenue"
            elif 'sales' in desc_lower or 'sales' in col_lower:
                return "Total Sales"
            else:
                return f"Total {col_name.replace('_', ' ').title()}"
        else:  # avg
            return f"Average {col_name.replace('_', ' ').title()}"
    
    def _format_number(self, value: float) -> str:
        """Format number for display."""
        if value >= 1000000:
            return f"{value/1000000:.1f}M"
        elif value >= 1000:
            return f"{value/1000:.1f}K"
        else:
            return f"{int(value):,}"
    
    def _generate_top_selling_products(self, primary_table: str, all_tables: List[str]) -> Dict:
        """Generate top selling products chart data."""
        # Default empty chart
        default_chart = {
            "data": [{
                "type": "bar",
                "orientation": "h",
                "x": [],
                "y": [],
                "marker": {"color": "#10b981"}
            }],
            "layout": {
                "title": "Top Selling Products",
                "xaxis": {"title": "Total Sales"},
                "yaxis": {"title": "Product"},
                "height": 400
            }
        }
        
        try:
            with self.engine.connect() as conn:
                inspector = inspect(self.engine)
                columns_info = inspector.get_columns(primary_table)
                columns = [col['name'] for col in columns_info]
                column_types = {col['name']: str(col['type']) for col in columns_info}
                
                # Use knowledge base to understand column meanings
                table_kb = self.knowledge_base.get(primary_table, {})
                column_descriptions = table_kb.get('columns', {})
                
                # Find product name column - EXCLUDE person/customer names
                # First, try to find product-specific columns
                name_col = None
                
                # Priority 1: Product-specific columns
                product_keywords = ['product_name', 'item_name', 'product', 'item', 'title', 'product_title']
                for keyword in product_keywords:
                    for col in columns:
                        if keyword.lower() in col.lower():
                            col_desc = column_descriptions.get(col, {}).get('description', '').lower()
                            # Exclude if it's clearly a person/customer name
                            if not any(word in col_desc for word in ['customer', 'person', 'user', 'client', 'buyer', 'purchaser']):
                                name_col = col
                                break
                    if name_col:
                        break
                
                # Priority 2: Generic name column, but exclude person-related
                if not name_col:
                    for col in columns:
                        col_type = column_types.get(col, '').lower()
                        if 'varchar' in col_type or 'text' in col_type or 'character' in col_type:
                            col_desc = column_descriptions.get(col, {}).get('description', '').lower()
                            col_lower = col.lower()
                            
                            # Skip if it's clearly a person/customer name
                            if any(word in col_lower or word in col_desc for word in ['customer', 'person', 'user', 'client', 'buyer', 'purchaser', 'first_name', 'last_name', 'full_name']):
                                continue
                            
                            # Prefer columns that might be product names
                            if any(word in col_lower for word in ['name', 'title']):
                                name_col = col
                                break
                
                # Find quantity/sales column
                quantity_col = None
                amount_col = None
                numeric_cols = self._find_numeric_columns(columns, column_types, column_descriptions)
                
                for num_col in numeric_cols:
                    col_desc = column_descriptions.get(num_col, {}).get('description', '').lower()
                    col_lower = num_col.lower()
                    
                    # Find quantity column
                    if not quantity_col and any(word in col_desc or word in col_lower for word in ['quantity', 'qty', 'sold', 'sales', 'count']):
                        quantity_col = num_col
                    
                    # Find amount/revenue column
                    if not amount_col and any(word in col_desc or word in col_lower for word in ['amount', 'revenue', 'total', 'price', 'value']):
                        amount_col = num_col
                
                # If we have a name column, group by it
                if name_col and self._validate_identifier(name_col):
                    # Determine which metric to use (quantity or amount)
                    metric_col = quantity_col if quantity_col else amount_col
                    
                    if metric_col and self._validate_identifier(metric_col):
                        # Get table size for query strategy
                        table_size = self._get_table_size_estimate(conn, primary_table)
                        use_limit = table_size > 100000
                        limit_value = 200000 if use_limit else None
                        
                        if use_limit and limit_value:
                            # Group by product name and sum the metric (with LIMIT for large tables)
                            query = f"""
                                SELECT 
                                    "{name_col}" as product_name,
                                    SUM("{metric_col}") as total_sales
                                FROM (
                                    SELECT "{name_col}", "{metric_col}"
                                    FROM {primary_table}
                                    WHERE "{name_col}" IS NOT NULL AND "{metric_col}" IS NOT NULL
                                    LIMIT {limit_value}
                                ) subquery
                                GROUP BY "{name_col}"
                                ORDER BY total_sales DESC
                                LIMIT 10
                            """
                        else:
                            # Full query for small tables
                            query = f"""
                                SELECT 
                                    "{name_col}" as product_name,
                                    SUM("{metric_col}") as total_sales
                                FROM {primary_table}
                                WHERE "{name_col}" IS NOT NULL AND "{metric_col}" IS NOT NULL
                                GROUP BY "{name_col}"
                                ORDER BY total_sales DESC
                                LIMIT 10
                            """
                    else:
                        # Just count by product name (no metric column available)
                        if not self._validate_identifier(name_col):
                            return default_chart
                        
                        # Get table size for query strategy
                        table_size = self._get_table_size_estimate(conn, primary_table)
                        use_limit = table_size > 100000
                        limit_value = 200000 if use_limit else None
                        
                        if use_limit and limit_value:
                            # Just count by product name (with LIMIT for large tables)
                            query = f"""
                                SELECT 
                                    "{name_col}" as product_name,
                                    COUNT(*) as total_sales
                                FROM (
                                    SELECT "{name_col}"
                                    FROM {primary_table}
                                    WHERE "{name_col}" IS NOT NULL
                                    LIMIT {limit_value}
                                ) subquery
                                GROUP BY "{name_col}"
                                ORDER BY total_sales DESC
                                LIMIT 10
                            """
                        else:
                            # Full query for small tables
                            query = f"""
                                SELECT 
                                    "{name_col}" as product_name,
                                    COUNT(*) as total_sales
                                FROM {primary_table}
                                WHERE "{name_col}" IS NOT NULL
                                GROUP BY "{name_col}"
                                ORDER BY total_sales DESC
                                LIMIT 10
                            """
                    
                    df = pd.read_sql(query, conn)
                    
                    if not df.empty:
                        # Create horizontal bar chart data
                        return {
                            "data": [{
                                "type": "bar",
                                "orientation": "h",
                                "x": df['total_sales'].tolist(),
                                "y": df['product_name'].tolist(),
                                "marker": {
                                    "color": "#10b981"
                                },
                                "text": df['total_sales'].tolist(),
                                "textposition": "outside"
                            }],
                            "layout": {
                                "title": "Top Selling Products",
                                "xaxis": {"title": "Total Sales"},
                                "yaxis": {"title": "Product", "autorange": "reversed"},
                                "height": 400,
                                "margin": {"l": 150, "r": 50, "t": 50, "b": 50}
                            }
                        }
                
                # Fallback: If no name column, try to find category/type (but not person names)
                category_col = None
                for col in columns:
                    col_type = column_types.get(col, '').lower()
                    if 'varchar' in col_type or 'text' in col_type or 'character' in col_type:
                        col_lower = col.lower()
                        col_desc = column_descriptions.get(col, {}).get('description', '').lower()
                        
                        # Skip person/customer columns
                        if any(word in col_lower or word in col_desc for word in ['customer', 'person', 'user', 'client', 'buyer', 'purchaser', 'first_name', 'last_name', 'full_name']):
                            continue
                        
                        # Look for category/type columns
                        if any(word in col_lower for word in ['category', 'type', 'status', 'brand', 'model']):
                            category_col = col
                            break
                
                # Re-determine metric_col for fallback
                metric_col = quantity_col if quantity_col else amount_col
                
                if category_col and metric_col and self._validate_identifier(category_col) and self._validate_identifier(metric_col):
                    # Get table size for query strategy
                    table_size = self._get_table_size_estimate(conn, primary_table)
                    use_limit = table_size > 100000
                    limit_value = 200000 if use_limit else None
                    
                    if use_limit and limit_value:
                        query = f"""
                            SELECT 
                                "{category_col}" as category,
                                SUM("{metric_col}") as total_sales
                            FROM (
                                SELECT "{category_col}", "{metric_col}"
                                FROM {primary_table}
                                WHERE "{category_col}" IS NOT NULL AND "{metric_col}" IS NOT NULL
                                LIMIT {limit_value}
                            ) subquery
                            GROUP BY "{category_col}"
                            ORDER BY total_sales DESC
                            LIMIT 10
                        """
                    else:
                        query = f"""
                            SELECT 
                                "{category_col}" as category,
                                SUM("{metric_col}") as total_sales
                            FROM {primary_table}
                            WHERE "{category_col}" IS NOT NULL AND "{metric_col}" IS NOT NULL
                            GROUP BY "{category_col}"
                            ORDER BY total_sales DESC
                            LIMIT 10
                        """
                    df = pd.read_sql(query, conn)
                    
                    if not df.empty:
                        # Assign different light colors to each bar
                        num_bars = len(df)
                        bar_colors = [self.BAR_CHART_COLORS[i % len(self.BAR_CHART_COLORS)] for i in range(num_bars)]
                        
                        return {
                            "data": [{
                                "type": "bar",
                                "orientation": "h",
                                "x": df['total_sales'].tolist(),
                                "y": df['category'].tolist(),
                                "marker": {"color": bar_colors},
                                "text": df['total_sales'].tolist(),
                                "textposition": "outside"
                            }],
                            "layout": {
                                "title": "Top Selling Products",
                                "xaxis": {"title": "Total Sales"},
                                "yaxis": {"title": "Category", "autorange": "reversed"},
                                "height": 400,
                                "margin": {"l": 150, "r": 50, "t": 50, "b": 50}
                            }
                        }
                
                # Final fallback: return empty chart
                return default_chart
                
        except Exception as e:
            print(f"Error generating top selling products: {e}")
            import traceback
            traceback.print_exc()
            return default_chart
    
    def _generate_pie_chart_from_metrics(self, metric_values: Dict[str, float]) -> Dict:
        """Generate pie chart directly from metrics values (ensures consistency).
        
        The pie chart shows the financial breakdown:
        - Revenue: Total income
        - Expenses: Recurring costs (if separate from loss)
        - Loss: One-time losses, write-offs, refunds (ALWAYS shown if > 0)
        - Profit: Net profit (Revenue - Expenses - Loss)
        
        Note: Profit = Revenue - Expenses - Loss, so we show all components for transparency.
        """
        # Convert all values to float, handling None and 0 properly
        revenue_value = float(metric_values.get("revenue", 0) or 0)
        expenses_value = float(metric_values.get("expenses", 0) or 0)
        loss_value = float(metric_values.get("loss", 0) or 0)
        profit_value = float(metric_values.get("profit", 0) or 0)
        
        print(f"[Dashboard] Generating pie chart from metrics - Revenue: {revenue_value}, Expenses: {expenses_value}, Loss: {loss_value}, Profit: {profit_value}")
        print(f"[Dashboard] Loss value type: {type(loss_value)}, value: {loss_value}, > 0 check: {loss_value > 0}")
        
        # Build pie chart data - only include segments with values > 0
        pie_values = []
        pie_labels = []
        pie_colors = []
        
        # Color scheme: Revenue (light teal), Expenses (light purple), Loss (light orange), Profit (light blue)
        colors_map = {
            "Revenue": "#2dd4bf",    # light teal
            "Expenses": "#a78bfa",   # light purple
            "Loss": "#fb923c",       # light orange
            "Profit": "#60a5fa"      # light blue
        }
        
        # Pie chart structure: Show all financial components
        # - Revenue (total income)
        # - Expenses (recurring costs, if any)
        # - Loss (one-time losses, ALWAYS shown if > 0 to match metrics)
        # - Profit (net result after all costs)
        
        # Add Revenue (total income)
        if revenue_value > 0:
            pie_values.append(revenue_value)
            pie_labels.append("Revenue")
            pie_colors.append(colors_map["Revenue"])
            print(f"[Dashboard] Adding Revenue to pie chart: {revenue_value}")
        
        # Add Expenses (recurring costs, separate from loss)
        if expenses_value > 0:
            pie_values.append(expenses_value)
            pie_labels.append("Expenses")
            pie_colors.append(colors_map["Expenses"])
            print(f"[Dashboard] Adding Expenses to pie chart: {expenses_value}")
        
        # CRITICAL: ALWAYS show Loss if it exists (> 0)
        # This ensures the pie chart matches the metrics data
        # Loss represents one-time losses, write-offs, refunds, etc.
        # Even if Loss is small compared to Revenue, it must be shown
        if loss_value > 0:
            pie_values.append(loss_value)
            pie_labels.append("Loss")
            pie_colors.append(colors_map["Loss"])
            print(f"[Dashboard] ✓ Adding Loss to pie chart: {loss_value} (CRITICAL: always shown when > 0 to match metrics)")
        else:
            print(f"[Dashboard] ✗ Loss value is 0 or None, not adding to pie chart. loss_value={loss_value}, type={type(loss_value)}")
        
        # Add Profit (calculated as Revenue - Expenses - Loss)
        # Profit shows the net result after all costs
        # This is what remains after expenses and loss are deducted from revenue
        if profit_value > 0:
            pie_values.append(profit_value)
            pie_labels.append("Profit")
            pie_colors.append(colors_map["Profit"])
            print(f"[Dashboard] Adding Profit to pie chart: {profit_value}")
        
        print(f"[Dashboard] Pie chart will have {len(pie_values)} segments")
        
        # If we have at least one segment with data
        if len(pie_values) > 0 and sum(pie_values) > 0:
            # If only one segment, add a minimal "Other" segment for visualization
            if len(pie_values) == 1:
                other_value = pie_values[0] * 0.01
                pie_values.append(other_value)
                pie_labels.append("Other")
                pie_colors.append("#e5e7eb")  # gray
                print(f"[Dashboard] Only one segment found, adding minimal 'Other' segment for visualization")
            
            # CRITICAL: Print all values being sent to pie chart for debugging
            print(f"[Dashboard] FINAL pie chart data - Values: {pie_values}, Labels: {pie_labels}, Colors: {pie_colors}")
            print(f"[Dashboard] Total of all values: {sum(pie_values)}")
            for i, (val, label) in enumerate(zip(pie_values, pie_labels)):
                percentage = (val / sum(pie_values)) * 100 if sum(pie_values) > 0 else 0
                print(f"[Dashboard]   Segment {i+1}: {label} = {val:,.0f} ({percentage:.2f}%)")
            
            # CRITICAL: Create pull array to make Loss slice visible by pulling it out
            # Find Loss index and pull it out to make it visible even if very small
            pull_array = [0] * len(pie_values)
            loss_index = None
            for i, label in enumerate(pie_labels):
                if label == "Loss":
                    loss_index = i
                    break
            
            # Pull out Loss slice to make it visible (0.2 = 20% pull)
            if loss_index is not None:
                pull_array[loss_index] = 0.2
                print(f"[Dashboard] Pulling out Loss slice at index {loss_index} to make it visible")
            
            return {
                "data": [{
                    "type": "pie",
                    "values": pie_values,
                    "labels": pie_labels,
                    "textinfo": "percent+label",
                    "textposition": "outside",
                    "marker": {
                        "colors": pie_colors
                    },
                    "hovertemplate": "<b>%{label}</b><br>Value: %{value:,.0f}<br>Percentage: %{percent:.1%}<extra></extra>",
                    # CRITICAL: Pull out Loss slice to make it visible even if very small
                    "pull": pull_array,  # Pull Loss slice out
                    "hole": 0,  # Full pie, not donut
                    # Ensure small slices are visible by using textinfo
                    "textfont": {"size": 12},
                    # Make sure Loss slice is visible even if very small
                    "insidetextorientation": "radial"
                }],
                "layout": {
                    "title": "Financial Overview",
                    "showlegend": True,
                    "legend": {
                        "orientation": "v",
                        "x": 1.05,
                        "y": 0.5
                    },
                    # Ensure small slices are visible
                    "piecolorway": pie_colors
                }
            }
        else:
            # If no data, return a visible "No Data" chart
            print(f"[Dashboard] No financial data available for pie chart")
            return {
                "data": [{
                    "type": "pie",
                    "values": [1],
                    "labels": ["No Data Available"],
                    "marker": {
                        "colors": ["#e5e7eb"]
                    },
                    "textinfo": "label",
                    "hovertemplate": "No financial data available<extra></extra>"
                }],
                "layout": {
                    "title": "Financial Overview",
                    "showlegend": False
                }
            }
    
    def _generate_pie_chart_data(self, primary_table: str) -> Optional[Dict]:
        """Generate pie chart data based on actual revenue and loss calculations."""
        # Validate primary table name
        if not self._validate_identifier(primary_table):
            print(f"[Dashboard] Invalid primary table name for pie chart: {primary_table}")
            return self._get_default_pie_chart()
        
        try:
            with self.engine.connect() as conn:
                inspector = inspect(self.engine)
                columns_info = inspector.get_columns(primary_table)
                columns = [col['name'] for col in columns_info]
                # Validate all column names
                columns = [col for col in columns if self._validate_identifier(col)]
                column_types = {col['name']: str(col['type']) for col in columns_info if self._validate_identifier(col['name'])}
                
                if not columns:
                    print(f"[Dashboard] No valid columns found for pie chart in table {primary_table}")
                    return self._get_default_pie_chart()
                
                # Use knowledge base to understand column meanings
                table_kb = self.knowledge_base.get(primary_table, {})
                column_descriptions = table_kb.get('columns', {})
                
                # Find revenue and cost columns (same logic as metrics)
                numeric_cols = self._find_numeric_columns(columns, column_types, column_descriptions)
                
                revenue_col = None
                cost_col = None
                expense_col = None  # Separate expense column (recurring expenses)
                
                for num_col in numeric_cols:
                    col_desc = column_descriptions.get(num_col, {}).get('description', '').lower()
                    col_lower = num_col.lower()
                    
                    # Find revenue column
                    if not revenue_col:
                        if any(word in col_desc or word in col_lower for word in ['revenue', 'sales', 'income']):
                            revenue_col = num_col
                        elif not revenue_col and any(word in col_desc or word in col_lower for word in ['amount', 'total', 'price', 'value']):
                            revenue_col = num_col
                    
                    # Find expense column (recurring expenses, separate from loss)
                    if not expense_col:
                        expense_keywords = ['expense', 'cost', 'spent', 'outgoing', 'payment', 'fee', 
                                          'charge', 'debit', 'withdrawal', 'deduction', 'operating', 'overhead']
                        if any(word in col_desc or word in col_lower for word in expense_keywords):
                            # Prefer 'expense' over 'cost' for recurring expenses
                            if 'expense' in col_lower or 'expense' in col_desc:
                                expense_col = num_col
                    
                    # Find cost/loss column (one-time losses, broader search)
                    if not cost_col:
                        loss_keywords = ['loss', 'writeoff', 'bad debt', 'depreciation', 'discount', 'refund', 'return']
                        # Also check for cost if expense_col is not set
                        if not expense_col:
                            loss_keywords.extend(['cost', 'spent', 'outgoing', 'payment', 'fee', 'charge', 'debit', 'withdrawal', 'deduction'])
                        if any(word in col_desc or word in col_lower for word in loss_keywords):
                            cost_col = num_col
                
                # Get table size to decide query strategy
                table_size = self._get_table_size_estimate(conn, primary_table)
                use_limit = table_size > 100000
                limit_value = 200000 if use_limit else None
                
                # Calculate revenue
                revenue_value = 0
                if revenue_col and self._validate_identifier(revenue_col):
                    try:
                        if use_limit and limit_value:
                            sum_query = f"""
                                SELECT SUM(\"{revenue_col}\") 
                                FROM (
                                    SELECT \"{revenue_col}\" 
                                    FROM {primary_table} 
                                    WHERE \"{revenue_col}\" IS NOT NULL 
                                    LIMIT {limit_value}
                                ) subquery
                            """
                        else:
                            sum_query = f"SELECT SUM(\"{revenue_col}\") FROM {primary_table} WHERE \"{revenue_col}\" IS NOT NULL"
                        result = conn.execute(text(sum_query))
                        revenue_value = result.scalar() or 0
                        print(f"[Dashboard] Revenue for pie chart: {revenue_value}")
                    except Exception as e:
                        print(f"[Dashboard] Error calculating revenue for pie chart: {e}")
                        revenue_value = 0
                else:
                    if revenue_col:
                        print(f"[Dashboard] Revenue column '{revenue_col}' failed validation for pie chart")
                    else:
                        print(f"[Dashboard] No revenue column found for pie chart")
                
                # Calculate loss (one-time losses)
                loss_value = 0
                if cost_col and self._validate_identifier(cost_col):
                    try:
                        if use_limit and limit_value:
                            loss_query = f"""
                                SELECT SUM(\"{cost_col}\") 
                                FROM (
                                    SELECT \"{cost_col}\" 
                                    FROM {primary_table} 
                                    WHERE \"{cost_col}\" IS NOT NULL 
                                    LIMIT {limit_value}
                                ) subquery
                            """
                        else:
                            loss_query = f"SELECT SUM(\"{cost_col}\") FROM {primary_table} WHERE \"{cost_col}\" IS NOT NULL"
                        result = conn.execute(text(loss_query))
                        loss_value = result.scalar() or 0
                        print(f"[Dashboard] Loss for pie chart: {loss_value}")
                    except Exception as e:
                        print(f"[Dashboard] Error calculating loss for pie chart: {e}")
                        loss_value = 0
                
                # Calculate expenses (recurring expenses, separate from loss)
                expenses_value = 0
                if expense_col and self._validate_identifier(expense_col):
                    try:
                        if use_limit and limit_value:
                            expense_query = f"""
                                SELECT SUM(\"{expense_col}\") 
                                FROM (
                                    SELECT \"{expense_col}\" 
                                    FROM {primary_table} 
                                    WHERE \"{expense_col}\" IS NOT NULL 
                                    LIMIT {limit_value}
                                ) subquery
                            """
                        else:
                            expense_query = f"SELECT SUM(\"{expense_col}\") FROM {primary_table} WHERE \"{expense_col}\" IS NOT NULL"
                        result = conn.execute(text(expense_query))
                        expenses_value = result.scalar() or 0
                        print(f"[Dashboard] Expenses for pie chart: {expenses_value}")
                    except Exception as e:
                        print(f"[Dashboard] Error calculating expenses for pie chart: {e}")
                        expenses_value = 0
                
                # If no expense column found but we have revenue, try to find alternative expense columns
                if expenses_value == 0 and revenue_value > 0:
                    print(f"[Dashboard] No expense column found for pie chart, searching for alternative expense columns...")
                    for num_col in numeric_cols:
                        if num_col != revenue_col and num_col != cost_col and self._validate_identifier(num_col):
                            col_desc = column_descriptions.get(num_col, {}).get('description', '').lower()
                            col_lower = num_col.lower()
                            # Broader keyword matching for expenses
                            expense_keywords = ['expense', 'cost', 'outgoing', 'spent', 'payment', 'fee', 'charge', 
                                              'debit', 'withdrawal', 'deduction', 'operating', 'overhead']
                            if any(word in col_desc or word in col_lower for word in expense_keywords):
                                print(f"[Dashboard] Found potential expense column for pie chart: {num_col}")
                                try:
                                    if use_limit and limit_value:
                                        expense_query = f"""
                                            SELECT SUM(\"{num_col}\") 
                                            FROM (
                                                SELECT \"{num_col}\" 
                                                FROM {primary_table} 
                                                WHERE \"{num_col}\" IS NOT NULL 
                                                LIMIT {limit_value}
                                            ) subquery
                                        """
                                    else:
                                        expense_query = f"SELECT SUM(\"{num_col}\") FROM {primary_table} WHERE \"{num_col}\" IS NOT NULL"
                                    result = conn.execute(text(expense_query))
                                    calculated_expense = result.scalar() or 0
                                    if calculated_expense > 0:
                                        expenses_value = calculated_expense
                                        print(f"[Dashboard] Successfully calculated expenses for pie chart from {num_col}: {expenses_value}")
                                        break
                                except Exception as e:
                                    print(f"[Dashboard] Error trying expense column {num_col} in pie chart: {e}")
                                    continue
                
                # If no loss column found, try to find alternative loss columns
                if loss_value == 0 and revenue_value > 0:
                    print(f"[Dashboard] No loss column found for pie chart, searching for alternative loss columns...")
                    for num_col in numeric_cols:
                        if num_col != revenue_col and num_col != expense_col and self._validate_identifier(num_col):
                            col_desc = column_descriptions.get(num_col, {}).get('description', '').lower()
                            col_lower = num_col.lower()
                            # Keywords for losses
                            loss_keywords = ['loss', 'writeoff', 'bad debt', 'depreciation', 'discount', 'refund', 'return']
                            if any(word in col_desc or word in col_lower for word in loss_keywords):
                                print(f"[Dashboard] Found potential loss column for pie chart: {num_col}")
                                try:
                                    if use_limit and limit_value:
                                        loss_query = f"""
                                            SELECT SUM(\"{num_col}\") 
                                            FROM (
                                                SELECT \"{num_col}\" 
                                                FROM {primary_table} 
                                                WHERE \"{num_col}\" IS NOT NULL 
                                                LIMIT {limit_value}
                                            ) subquery
                                        """
                                    else:
                                        loss_query = f"SELECT SUM(\"{num_col}\") FROM {primary_table} WHERE \"{num_col}\" IS NOT NULL"
                                    result = conn.execute(text(loss_query))
                                    calculated_loss = result.scalar() or 0
                                    if calculated_loss > 0:
                                        loss_value = calculated_loss
                                        print(f"[Dashboard] Successfully calculated loss for pie chart from {num_col}: {loss_value}")
                                        break
                                except Exception as e:
                                    print(f"[Dashboard] Error trying loss column {num_col} in pie chart: {e}")
                                    continue
                    
                    # If still no loss found, try looking for negative values in revenue column (returns/refunds)
                    if loss_value == 0:
                        print(f"[Dashboard] Trying to find negative values in revenue column for pie chart...")
                        if revenue_col and self._validate_identifier(revenue_col):
                            try:
                                if use_limit and limit_value:
                                    negative_query = f"""
                                        SELECT ABS(SUM(\"{revenue_col}\")) 
                                        FROM (
                                            SELECT \"{revenue_col}\" 
                                            FROM {primary_table} 
                                            WHERE \"{revenue_col}\" < 0 
                                            LIMIT {limit_value}
                                        ) subquery
                                    """
                                else:
                                    negative_query = f"SELECT ABS(SUM(\"{revenue_col}\")) FROM {primary_table} WHERE \"{revenue_col}\" < 0"
                                result = conn.execute(text(negative_query))
                                negative_sum = result.scalar() or 0
                                if negative_sum > 0:
                                    loss_value = negative_sum
                                    print(f"[Dashboard] Found negative values (returns/refunds) for pie chart: {loss_value}")
                            except Exception as e:
                                print(f"[Dashboard] Error checking negative values for pie chart: {e}")
                
                # Expenses and Loss are separate - don't overwrite expenses with loss
                # If expenses_value is still 0 but we found loss, we can use loss as expenses for visualization
                # But keep them separate if both exist
                if expenses_value == 0 and loss_value > 0:
                    # If no separate expense column found, use loss as expenses for visualization
                    expenses_value = loss_value
                    print(f"[Dashboard] Using loss as expenses for pie chart visualization")
                
                # Calculate profit (Revenue - Expenses - Loss)
                # Profit = Revenue - (Expenses + Loss)
                total_costs = expenses_value + loss_value
                profit_value = revenue_value - total_costs if revenue_value else None
                if profit_value is not None and profit_value < 0:
                    profit_value = 0  # Don't show negative profit as a separate segment
                elif profit_value is not None:
                    print(f"[Dashboard] Profit calculated: {profit_value} (Revenue: {revenue_value}, Expenses: {expenses_value}, Loss: {loss_value})")
                
                # Build pie chart data adaptively based on available data
                pie_values = []
                pie_labels = []
                pie_colors = []
                
                # Color scheme: Revenue (light teal), Expenses (light purple), Loss (light orange), Profit (light blue)
                colors_map = {
                    "Revenue": "#2dd4bf",    # light teal
                    "Expenses": "#a78bfa",   # light purple
                    "Loss": "#fb923c",       # light orange
                    "Profit": "#60a5fa"      # light blue
                }
                
                # Add segments only if they have meaningful values (> 0)
                # Always try to show revenue first (even if 0, we'll handle it)
                if revenue_value is not None and revenue_value > 0:
                    pie_values.append(revenue_value)
                    pie_labels.append("Revenue")
                    pie_colors.append(colors_map["Revenue"])
                    print(f"[Dashboard] Adding Revenue to pie chart: {revenue_value}")
                else:
                    print(f"[Dashboard] Revenue is 0 or None (value: {revenue_value}), skipping from pie chart")
                
                if expenses_value and expenses_value > 0:
                    pie_values.append(expenses_value)
                    pie_labels.append("Expenses")
                    pie_colors.append(colors_map["Expenses"])
                    print(f"[Dashboard] Adding Expenses to pie chart: {expenses_value}")
                
                # Loss is separate from expenses (if both exist, show both)
                # Loss typically represents one-time losses, while expenses are recurring
                # Only show loss separately if it's different from expenses (not the same column)
                if loss_value and loss_value > 0:
                    # Check if loss and expenses are from different sources
                    # If expenses_value was set from loss_value (fallback), they're the same - don't show both
                    # But if we have separate expense_col and cost_col, show both
                    if expenses_value != loss_value:
                        # They're different - show both
                        pie_values.append(loss_value)
                        pie_labels.append("Loss")
                        pie_colors.append(colors_map["Loss"])
                        print(f"[Dashboard] Adding Loss to pie chart: {loss_value} (separate from expenses)")
                    elif expenses_value == 0:
                        # Only loss exists, expenses will be shown as 0, so show loss
                        pie_values.append(loss_value)
                        pie_labels.append("Loss")
                        pie_colors.append(colors_map["Loss"])
                        print(f"[Dashboard] Adding Loss to pie chart: {loss_value}")
                
                if profit_value is not None and profit_value > 0:
                    pie_values.append(profit_value)
                    pie_labels.append("Profit")
                    pie_colors.append(colors_map["Profit"])
                    print(f"[Dashboard] Adding Profit to pie chart: {profit_value}")
                
                print(f"[Dashboard] Pie chart segments: {len(pie_values)} segments, total value: {sum(pie_values)}")
                
                # Show pie chart if we have at least one segment with data
                if len(pie_values) > 0 and sum(pie_values) > 0:
                    # If only one segment, add a small "Other" segment for visualization
                    if len(pie_values) == 1:
                        # Add a minimal "Other" segment (1% of total) so pie chart shows properly
                        other_value = pie_values[0] * 0.01
                        pie_values.append(other_value)
                        pie_labels.append("Other")
                        pie_colors.append("#e5e7eb")  # gray
                        print(f"[Dashboard] Only one segment found, adding minimal 'Other' segment for visualization")
                    
                    return {
                        "data": [{
                            "type": "pie",
                            "values": pie_values,
                            "labels": pie_labels,
                            "textinfo": "percent+label",
                            "textposition": "outside",
                            "marker": {
                                "colors": pie_colors
                            },
                            "hovertemplate": "<b>%{label}</b><br>Value: %{value:,.0f}<br>Percentage: %{percent:.1%}<extra></extra>"
                        }],
                        "layout": {
                            "title": "Financial Overview",
                            "showlegend": True,
                            "legend": {
                                "orientation": "v",
                                "x": 1.05,
                                "y": 0.5
                            }
                        }
                    }
                else:
                    # If no data, return a visible "No Data" chart instead of blank
                    print(f"[Dashboard] No financial data available for pie chart (revenue: {revenue_value}, expenses: {expenses_value}, loss: {loss_value})")
                    return {
                        "data": [{
                            "type": "pie",
                            "values": [1],
                            "labels": ["No Data Available"],
                            "marker": {
                                "colors": ["#e5e7eb"]
                            },
                            "textinfo": "label",
                            "hovertemplate": "No financial data available<extra></extra>"
                        }],
                        "layout": {
                            "title": "Financial Overview",
                            "showlegend": False
                        }
                    }
        except Exception as e:
            print(f"[Dashboard] Error generating pie chart: {e}")
            import traceback
            traceback.print_exc()
            # Return a visible error chart instead of blank
            return {
                "data": [{
                    "type": "pie",
                    "values": [1],
                    "labels": ["Error Loading Data"],
                    "marker": {
                        "colors": ["#ef4444"]
                    },
                    "textinfo": "label",
                    "hovertemplate": "Error loading financial data<extra></extra>"
                }],
                "layout": {
                    "title": "Financial Overview",
                    "showlegend": False
                }
            }
    
    def _generate_top_items(self, primary_table: str) -> List[Dict]:
        """Generate top items list."""
        try:
            with self.engine.connect() as conn:
                inspector = inspect(self.engine)
                columns = [col['name'] for col in inspector.get_columns(primary_table)]
                
                name_col = self._find_column(columns, ['name', 'product', 'item', 'title'])
                amount_col = self._find_column(columns, ['amount', 'quantity', 'stock', 'used', 'total'])
                
                # Validate identifiers before using in query
                if name_col and amount_col and self._validate_identifier(name_col) and self._validate_identifier(amount_col) and self._validate_identifier(primary_table):
                    query = f"SELECT \"{name_col}\", \"{amount_col}\" FROM {primary_table} ORDER BY \"{amount_col}\" DESC LIMIT 7"
                    df = pd.read_sql(query, conn)
                    
                    if not df.empty:
                        max_val = df[amount_col].max()
                        items = []
                        colors = ["#2dd4bf", "#2dd4bf", "#a78bfa", "#a78bfa", "#fb923c", "#fb923c", "#f472b6"]
                        
                        for idx, row in df.iterrows():
                            items.append({
                                "name": str(row[name_col]),
                                "used": int(row[amount_col]) if pd.notna(row[amount_col]) else 0,
                                "total": int(max_val * 1.2) if max_val > 0 else 250,
                                "color": colors[idx % len(colors)]
                            })
                        return items
        except Exception as e:
            print(f"Error generating top items: {e}")
        
        # Default top items
        return [
            {"name": "Item 1", "used": 155, "total": 250, "color": "bg-teal-600"},
            {"name": "Item 2", "used": 180, "total": 250, "color": "bg-teal-600"},
            {"name": "Item 3", "used": 105, "total": 250, "color": "bg-purple-600"},
        ]
    
    def _find_column(self, columns: List[str], keywords: List[str]) -> Optional[str]:
        """Find column matching keywords."""
        for keyword in keywords:
            for col in columns:
                if keyword.lower() in col.lower():
                    return col
        return columns[0] if columns else None
    
    def _detect_business_type(self) -> str:
        """Detect business type from database schema."""
        if not self.knowledge_base:
            return "Business"
        
        table_names = list(self.knowledge_base.keys())
        table_names_lower = [name.lower() for name in table_names]
        
        if any('product' in name or 'inventory' in name or 'stock' in name for name in table_names_lower):
            return "Inventory"
        if any('customer' in name or 'client' in name for name in table_names_lower):
            return "CRM"
        if any('sale' in name or 'transaction' in name or 'order' in name for name in table_names_lower):
            return "E-commerce"
        if any('employee' in name or 'hr' in name or 'staff' in name for name in table_names_lower):
            return "HR"
        
        return "Business"
    
    def _get_top_items_title(self) -> str:
        """Get title for top items based on business type."""
        business_type = self._detect_business_type()
        if business_type == "Inventory":
            return "Most Used Items This Week"
        return "Top Items This Week"
    
    def _generate_sales_by_category(self, primary_table: str, all_tables: List[str]) -> Dict:
        """Generate sales by category horizontal bar chart."""
        default_chart = {
            "data": [{"type": "bar", "orientation": "h", "x": [], "y": [], "marker": {"color": self.BAR_CHART_COLORS}}],
            "layout": {"title": "Sales by Item Category", "xaxis": {"title": "Sales"}, "yaxis": {"title": "Category"}, "height": 300}
        }
        
        try:
            with self.engine.connect() as conn:
                inspector = inspect(self.engine)
                columns_info = inspector.get_columns(primary_table)
                columns = [col['name'] for col in columns_info]
                table_kb = self.knowledge_base.get(primary_table, {})
                column_descriptions = table_kb.get('columns', {})
                
                # Find category column
                category_col = self._find_column_smart(columns, column_descriptions, 
                    ['category', 'item_category', 'product_category', 'type', 'item_type'])
                
                # Find sales/revenue column
                sales_col = self._find_column_smart(columns, column_descriptions,
                    ['sales', 'revenue', 'amount', 'total', 'price', 'value'])
                
                if category_col and sales_col and self._validate_identifier(category_col) and self._validate_identifier(sales_col):
                    query = f"""
                        SELECT "{category_col}", SUM("{sales_col}") as total_sales
                        FROM {primary_table}
                        WHERE "{sales_col}" IS NOT NULL
                        GROUP BY "{category_col}"
                        ORDER BY total_sales DESC
                        LIMIT 20
                    """
                    df = pd.read_sql(query, conn)
                    if not df.empty:
                        # Assign different light colors to each bar
                        num_bars = len(df)
                        bar_colors = [self.BAR_CHART_COLORS[i % len(self.BAR_CHART_COLORS)] for i in range(num_bars)]
                        
                        return {
                            "data": [{
                                "type": "bar",
                                "orientation": "h",
                                "x": df['total_sales'].tolist(),
                                "y": df[category_col].tolist(),
                                "marker": {"color": bar_colors}
                            }],
                            "layout": {
                                "title": "Sales by Item Category",
                                "xaxis": {"title": "Sales"},
                                "yaxis": {"title": "Category"},
                                "height": 300,
                                "margin": {"l": 150, "r": 20, "t": 40, "b": 40}
                            }
                        }
        except Exception as e:
            print(f"[Dashboard] Error generating sales by category: {e}")
        
        return default_chart
    
    def _generate_sales_by_product_group(self, primary_table: str, all_tables: List[str]) -> Dict:
        """Generate sales by product group horizontal bar chart."""
        default_chart = {
            "data": [{"type": "bar", "orientation": "h", "x": [], "y": [], "marker": {"color": self.BAR_CHART_COLORS}}],
            "layout": {"title": "Sales by Product Group", "xaxis": {"title": "Sales"}, "yaxis": {"title": "Product Group"}, "height": 300}
        }
        
        try:
            with self.engine.connect() as conn:
                inspector = inspect(self.engine)
                columns_info = inspector.get_columns(primary_table)
                columns = [col['name'] for col in columns_info]
                table_kb = self.knowledge_base.get(primary_table, {})
                column_descriptions = table_kb.get('columns', {})
                
                # Find product group column
                group_col = self._find_column_smart(columns, column_descriptions,
                    ['product_group', 'group', 'product_group_name', 'item_group', 'segment'])
                
                # Find sales/revenue column
                sales_col = self._find_column_smart(columns, column_descriptions,
                    ['sales', 'revenue', 'amount', 'total', 'price', 'value'])
                
                if group_col and sales_col and self._validate_identifier(group_col) and self._validate_identifier(sales_col):
                    query = f"""
                        SELECT "{group_col}", SUM("{sales_col}") as total_sales
                        FROM {primary_table}
                        WHERE "{sales_col}" IS NOT NULL
                        GROUP BY "{group_col}"
                        ORDER BY total_sales DESC
                        LIMIT 20
                    """
                    df = pd.read_sql(query, conn)
                    if not df.empty:
                        # Assign different light colors to each bar
                        num_bars = len(df)
                        bar_colors = [self.BAR_CHART_COLORS[i % len(self.BAR_CHART_COLORS)] for i in range(num_bars)]
                        
                        return {
                            "data": [{
                                "type": "bar",
                                "orientation": "h",
                                "x": df['total_sales'].tolist(),
                                "y": df[group_col].tolist(),
                                "marker": {"color": bar_colors}
                            }],
                            "layout": {
                                "title": "Sales by Product Group",
                                "xaxis": {"title": "Sales"},
                                "yaxis": {"title": "Product Group"},
                                "height": 300,
                                "margin": {"l": 150, "r": 20, "t": 40, "b": 40}
                            }
                        }
        except Exception as e:
            print(f"[Dashboard] Error generating sales by product group: {e}")
        
        return default_chart
    
    def _generate_sales_by_division(self, primary_table: str, all_tables: List[str]) -> Dict:
        """Generate sales by division pie chart."""
        default_chart = {
            "data": [{"type": "pie", "values": [], "labels": [], "marker": {"colors": ["#2dd4bf", "#fb923c", "#60a5fa", "#a78bfa", "#f472b6"]}}],
            "layout": {"title": "Sales by Division", "showlegend": True, "height": 300}
        }
        
        try:
            with self.engine.connect() as conn:
                inspector = inspect(self.engine)
                columns_info = inspector.get_columns(primary_table)
                columns = [col['name'] for col in columns_info]
                table_kb = self.knowledge_base.get(primary_table, {})
                column_descriptions = table_kb.get('columns', {})
                
                # Find division column
                division_col = self._find_column_smart(columns, column_descriptions,
                    ['division', 'item_division', 'product_division', 'category', 'type'])
                
                # Find sales/revenue column
                sales_col = self._find_column_smart(columns, column_descriptions,
                    ['sales', 'revenue', 'amount', 'total', 'price', 'value'])
                
                if division_col and sales_col and self._validate_identifier(division_col) and self._validate_identifier(sales_col):
                    query = f"""
                        SELECT "{division_col}", SUM("{sales_col}") as total_sales
                        FROM {primary_table}
                        WHERE "{sales_col}" IS NOT NULL
                        GROUP BY "{division_col}"
                        ORDER BY total_sales DESC
                    """
                    df = pd.read_sql(query, conn)
                    if not df.empty:
                        return {
                            "data": [{
                                "type": "pie",
                                "values": df['total_sales'].tolist(),
                                "labels": df[division_col].tolist(),
                                "marker": {"colors": ["#2dd4bf", "#fb923c", "#60a5fa", "#a78bfa", "#f472b6"]}
                            }],
                            "layout": {
                                "title": "Sales by Division",
                                "showlegend": True,
                                "height": 300
                            }
                        }
        except Exception as e:
            print(f"[Dashboard] Error generating sales by division: {e}")
        
        return default_chart
    
    def _generate_unsold_items(self, primary_table: str, all_tables: List[str]) -> List[Dict]:
        """Generate list of unsold items."""
        try:
            with self.engine.connect() as conn:
                inspector = inspect(self.engine)
                columns_info = inspector.get_columns(primary_table)
                columns = [col['name'] for col in columns_info]
                table_kb = self.knowledge_base.get(primary_table, {})
                column_descriptions = table_kb.get('columns', {})
                
                # Find quantity/sales column to identify unsold items
                quantity_col = self._find_column_smart(columns, column_descriptions,
                    ['quantity', 'qty', 'amount', 'sales', 'sold'])
                
                # Find product name column
                name_col = self._find_column_smart(columns, column_descriptions,
                    ['product_name', 'item_name', 'product', 'item', 'name', 'title'])
                
                # Find ID column
                id_col = self._find_column_smart(columns, column_descriptions,
                    ['id', 'item_id', 'product_id', 'item_code', 'product_code'])
                
                if quantity_col and name_col and self._validate_identifier(quantity_col) and self._validate_identifier(name_col):
                    # Find items with zero or null quantity/sales
                    query = f"""
                        SELECT "{id_col if id_col and self._validate_identifier(id_col) else 'NULL'} as id", 
                               "{name_col}" as name
                        FROM {primary_table}
                        WHERE ("{quantity_col}" IS NULL OR "{quantity_col}" = 0)
                        LIMIT 50
                    """
                    df = pd.read_sql(query, conn)
                    if not df.empty:
                        return [{"id": str(row.get('id', '')), "name": str(row.get('name', ''))} 
                               for _, row in df.iterrows()]
        except Exception as e:
            print(f"[Dashboard] Error generating unsold items: {e}")
        
        return []
    
    def _get_default_dashboard(self) -> Dict[str, Any]:
        """Return default dashboard when database is not available."""
        return {
            "businessType": "Business",
            "metrics": [
                {"label": "Receipt", "value": "0", "unit": "", "color": "#f472b6", "icon": "📄"},
                {"label": "Sales", "value": "0", "unit": "", "color": "#2dd4bf", "icon": "💰"},
                {"label": "Quantity", "value": "0", "unit": "", "color": "#a78bfa", "icon": "🛒"},
                {"label": "Cost", "value": "0", "unit": "", "color": "#fb923c", "icon": "💰"},
                {"label": "Profit", "value": "0", "unit": "", "color": "#60a5fa", "icon": "📈"},
                {"label": "Unsold Items %", "value": "0.00", "unit": "%", "color": "#2dd4bf", "icon": "📊"}
            ],
            "topSellingChart": {
                "data": [{
                    "type": "bar",
                    "orientation": "h",
                    "x": [],
                    "y": [],
                    "marker": {"color": self.BAR_CHART_COLORS}
                }],
                "layout": {
                    "title": "Top Selling Products",
                    "xaxis": {"title": "Total Sales"},
                    "yaxis": {"title": "Product"},
                    "height": 400
                }
            },
            "salesByCategoryChart": {
                "data": [{"type": "bar", "orientation": "h", "x": [], "y": [], "marker": {"color": self.BAR_CHART_COLORS}}],
                "layout": {"title": "Sales by Item Category", "xaxis": {"title": "Sales"}, "yaxis": {"title": "Category"}, "height": 300}
            },
            "salesByGroupChart": {
                "data": [{"type": "bar", "orientation": "h", "x": [], "y": [], "marker": {"color": self.BAR_CHART_COLORS}}],
                "layout": {"title": "Sales by Product Group", "xaxis": {"title": "Sales"}, "yaxis": {"title": "Product Group"}, "height": 300}
            },
            "pieChart": {
                "data": [{
                    "type": "pie",
                    "values": [60, 25, 15],
                    "labels": ["Revenue", "Expenses", "Loss"],
                    "marker": {"colors": ["#2dd4bf", "#a78bfa", "#fb923c"]}
                }],
                "layout": {"title": "", "showlegend": True}
            },
            "salesByDivisionChart": {
                "data": [{"type": "pie", "values": [], "labels": [], "marker": {"colors": ["#2dd4bf", "#fb923c", "#60a5fa", "#a78bfa", "#f472b6"]}}],
                "layout": {"title": "Sales by Division", "showlegend": True, "height": 300}
            },
            "unsoldItems": []
        }

