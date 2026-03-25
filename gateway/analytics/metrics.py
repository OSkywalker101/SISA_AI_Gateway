import aiosqlite
from config import settings
from typing import Dict, Any

async def get_dashboard_metrics() -> Dict[str, Any]:
    """Retrieve summarized metrics for the admin dashboard."""
    metrics = {
        "total_requests": 0,
        "avg_latency": 0.0,
        "total_cost": 0.0,
        "requests_per_model": {},
        "error_count": 0,
        "recent_requests": []
    }
    
    try:
        async with aiosqlite.connect(settings.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            # Aggregate stats
            cursor = await db.execute('''
                SELECT 
                    COUNT(*) as total,
                    AVG(latency_ms) as avg_lat,
                    SUM(cost_estimate_usd) as cost,
                    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as errors
                FROM requests
            ''')
            row = await cursor.fetchone()
            if row and row['total'] > 0:
                metrics["total_requests"] = row['total']
                metrics["avg_latency"] = round(row['avg_lat'] or 0, 2)
                metrics["total_cost"] = round(row['cost'] or 0, 4)
                metrics["error_count"] = row['errors'] or 0

            # Requests per model
            cursor = await db.execute('''
                SELECT model, COUNT(*) as count 
                FROM requests 
                GROUP BY model
            ''')
            rows = await cursor.fetchall()
            for r in rows:
                if r['model']:
                    metrics["requests_per_model"][r['model']] = r['count']

            # Recent requests (last 10)
            cursor = await db.execute('''
                SELECT timestamp, api_key, model, provider, status_code, latency_ms 
                FROM requests 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''')
            rows = await cursor.fetchall()
            metrics["recent_requests"] = [dict(r) for r in rows]
            
    except Exception as e:
        print(f"Error getting metrics: {e}")
        
    return metrics
