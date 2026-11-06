"""Read only document content; report aggregate character lengths without text or IDs."""
import heapq
import json
import sys
import pyarrow.parquet as pq

lengths = []
count = total = maximum = 0
for batch in pq.ParquetFile(sys.argv[1]).iter_batches(batch_size=256, columns=['content']):
    for item in batch.column(0).to_pylist():
        size = len(item)
        count += 1
        total += size
        maximum = max(maximum, size)
        if len(lengths) < 128:
            heapq.heappush(lengths, size)
        else:
            heapq.heappushpop(lengths, size)
print(json.dumps({'documents': count, 'total_characters': total, 'max_characters': maximum,
                  'largest_128_min_characters': min(lengths),
                  'largest_128_total_characters': sum(lengths)}))
