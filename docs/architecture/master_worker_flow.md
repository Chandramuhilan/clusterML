# Master-Worker Flow

## Job Lifecycle

1. **Job Submission**: Client submits job via API/CLI/SDK
2. **Validation**: Master validates job specification
3. **Queuing**: Job enters the scheduling queue
4. **Scheduling**: Scheduler assigns job to available worker(s)
5. **Execution**: Worker executes the job
6. **Reporting**: Worker reports progress and results
7. **Completion**: Master marks job as complete

## Worker Registration

```
Worker                          Master
   │                               │
   │──── Register (capabilities) ──▶│
   │                               │
   │◀─── Acknowledgment ───────────│
   │                               │
   │──── Heartbeat ────────────────▶│
   │                               │
```

## Job Assignment

```
Master                          Worker
   │                               │
   │──── Assign Job ───────────────▶│
   │                               │
   │◀─── Acknowledge ──────────────│
   │                               │
   │◀─── Progress Updates ─────────│
   │                               │
   │◀─── Result ───────────────────│
   │                               │
```
