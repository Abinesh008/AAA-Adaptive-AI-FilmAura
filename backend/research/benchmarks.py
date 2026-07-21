import asyncio
import time
import os
import sys

# Adjust Python path to allow running research utilities from backend folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research.golden_dataset import GOLDEN_DATASET
from app.retrieval.sdk import retrieval_client
from app.retrieval.evaluation import evaluator
from app.retrieval.registry import discover_plugins

async def run_benchmarks():
    # Make sure plugins are discovered
    discover_plugins()
    
    print("=" * 60)
    print("FILMAURA RETRIEVAL ENGINE BENCHMARK UTILITY")
    print("=" * 60)
    
    metrics_list = []
    
    for idx, entry in enumerate(GOLDEN_DATASET, 1):
        print(f"[{idx}/{len(GOLDEN_DATASET)}] Query: '{entry.query}'")
        
        start_time = time.time()
        failed = False
        results = []
        cache_hit = False
        
        try:
            response = await retrieval_client.search(
                query=entry.query,
                profile="balanced"
            )
            results = response.movies
            cache_status = response.explanation.get("replayed", False)
        except Exception as e:
            print(f"  FAILED: {str(e)}")
            failed = True
            
        latency = round((time.time() - start_time) * 1000, 2)
        
        # Calculate scores
        scores = evaluator.calculate_metrics(results, entry, latency, cache_hit, failed)
        metrics_list.append(scores)
        
        print(f"  Latency: {latency}ms | MRR: {scores['mrr']} | Match: {scores['precision_at_1'] == 1.0}")
        print("-" * 60)
        
    report = evaluator.compile_report(metrics_list)
    
    print("\n" + "=" * 60)
    print("FINAL RETRIEVAL QUALITY PERFORMANCE REPORT")
    print("=" * 60)
    print(f"Total Queries Evaluated : {report.total_queries}")
    print(f"Precision @ 1           : {report.precision_at_1}")
    print(f"Precision @ 5           : {report.precision_at_5}")
    print(f"Recall @ 5              : {report.recall_at_5}")
    print(f"Mean Reciprocal Rank    : {report.mean_reciprocal_rank}")
    print(f"Average Latency         : {report.average_latency_ms}ms")
    print(f"Cache Hit Ratio         : {report.cache_hit_ratio}")
    print(f"Failure Rate            : {report.failure_rate}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
