import sys
import heapq

def solve():
    input_data = sys.stdin.read().splitlines()
    if not input_data:
        return
        
    first_line = input_data[0].split()
    w = int(first_line[0])
    n = int(first_line[1])
    
    all_jobs = []
    for i in range(1, n + 1):
        if i >= len(input_data):
            break
        parts = input_data[i].split()
        if not parts:
            continue
        arrival_time = int(parts[0])
        job_id = parts[1]
        priority = int(parts[2])
        duration = int(parts[3])
        resources = int(parts[4])
        all_jobs.append((arrival_time, i, job_id, priority, duration, resources))
        
    all_jobs.sort(key=lambda x: x[0])
    
    ready_queue = []
    workers_heap = [(0, f"W{i}") for i in range(1, w + 1)]
    heapq.heapify(workers_heap)
    
    job_idx = 0
    total_wait_time = 0.0
    output_reports = []
    
    while job_idx < n or ready_queue:
        if not ready_queue:
            current_time = max(all_jobs[job_idx][0], workers_heap[0][0])
        else:
            current_time = workers_heap[0][0]
            
        while job_idx < n and all_jobs[job_idx][0] <= current_time:
            arr_t, arr_idx, j_id, prio, dur, res = all_jobs[job_idx]
            heapq.heappush(ready_queue, (-prio, arr_t, arr_idx, j_id, dur))
            job_idx += 1
            
        while ready_queue and workers_heap[0][0] <= current_time:
            worker_avail_time, worker_id = heapq.heappop(workers_heap)
            prio_inv, arr_t, arr_idx, j_id, dur = heapq.heappop(ready_queue)
            
            start_time = max(worker_avail_time, arr_t)
            finish_time = start_time + dur
            waiting_time = start_time - arr_t
            total_wait_time += waiting_time
            
            output_reports.append(f"{j_id} {worker_id} {start_time} {finish_time}")
            heapq.heappush(workers_heap, (finish_time, worker_id))
            
    for report in output_reports:
        print(report)
        
    avg_wait = total_wait_time / n if n > 0 else 0.0
    print(f"AVG_WAIT {avg_wait:.2f}")

if __name__ == '__main__':
    solve()
