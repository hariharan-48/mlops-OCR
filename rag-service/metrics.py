"""
Simple Metrics Tracking for Workshop Demo
Tracks basic performance metrics in memory
"""

import time
from datetime import datetime
from typing import Dict, List
from collections import defaultdict

class SimpleMetrics:
    def __init__(self):
        self.metrics = defaultdict(list)
        self.counters = defaultdict(int)
        self.timers = {}
    
    def increment_counter(self, metric_name: str, value: int = 1):
        """Increment a counter metric"""
        self.counters[metric_name] += value
    
    def record_timing(self, metric_name: str, duration: float):
        """Record a timing metric"""
        self.metrics[metric_name].append({
            "value": duration,
            "timestamp": datetime.now().isoformat()
        })
    
    def start_timer(self, metric_name: str):
        """Start a timer"""
        self.timers[metric_name] = time.time()
    
    def end_timer(self, metric_name: str):
        """End a timer and record the duration"""
        if metric_name in self.timers:
            duration = time.time() - self.timers[metric_name]
            self.record_timing(metric_name, duration)
            del self.timers[metric_name]
    
    def get_counter(self, metric_name: str) -> int:
        """Get current value of a counter"""
        return self.counters.get(metric_name, 0)
    
    def get_timing_stats(self, metric_name: str) -> Dict:
        """Get statistics for a timing metric"""
        values = self.metrics.get(metric_name, [])
        if not values:
            return {"count": 0, "avg": 0, "min": 0, "max": 0}
        
        durations = [v["value"] for v in values]
        return {
            "count": len(durations),
            "avg": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations),
            "latest": durations[-1] if durations else 0
        }
    
    def get_all_metrics(self) -> Dict:
        """Get all metrics"""
        return {
            "counters": dict(self.counters),
            "timings": {
                name: self.get_timing_stats(name) 
                for name in self.metrics.keys()
            }
        }

# Global metrics instance
metrics = SimpleMetrics()

# Common metric names
METRIC_QUERIES_TOTAL = "queries_total"
METRIC_QUERIES_SUCCESS = "queries_success"
METRIC_QUERIES_ERROR = "queries_error"
METRIC_QUERY_DURATION = "query_duration_ms"
METRIC_DOCUMENTS_INDEXED = "documents_indexed"
METRIC_DOCUMENTS_TOTAL = "documents_total" 