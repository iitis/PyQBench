# Allowing for a asynchronous execution and delayed retrieval of job results

## Deciders

- Konrad Jałowiecki

## Description

At the start of the project we were planning to use Braket, and hence we didn't anticipate long 
waiting times in IBMQ queues. Long waiting times provide a serious problem for our synchronous 
model of execution, since if the machine crashes while waiting for results we will waste 
precious resources (mostly time). We aim to remedy this by introducing optional asynchronous 
mode of execution and delayed retrieval of results.

This ADR only concerns IBMQ jobs, and the second ADR, if needed, will be provided for Braket jobs.

## Outcome

There are several things that needs to happen in order to make asynchronous execution possible:

- it has to be possible to declare mode of execution (sync or async)
- the results file has to accommodate storage of JOB ID's
- a command for retrieving job results needs to be provided by the CLI
- (optionally) CLI can provide command for querying status of given results file

### Declaring mode of execution

All backend descriptions provide `async` property. For some backends it will always default to 
`False`. For IBMQ backends it will be configurable, with the default being `False`. the following 
shows the possible configuration of IBMQ backend:

```yaml
name: ibmq-belem
async: true
provider:
  hub: ibmq-hub
  group: open
  project: main
```

If the backend description is configured with `async=True`, the function responsible for running 
the job needs to only submit the jobs and not query synchronously for their result.

### Changes to the result model

The `histogram` field can now contain `IBMQJobDescription` object instead of dictionary. These 
object contain a single field, `ibmq_job_id` of string type. The following is an exemplary part 
of the results file storing asynchronous results:

```yaml
results:
  - target: 0
    ancilla: 1
    measurement_counts:
      - phi: 0
        histogram:
          job_id: <job_id>
      - phi: 1
        histogram: 
          job_id: <job_id>
      - phi: 2
        histogram:
          job_id: <job_id>
```

### New commands in CLI

The CLI for Fourier discrimination should provide the following new commands.

- `resolve <async-result> <sync-result>`: this command should query the status of jobs and 
  produce the synchronous results file (i.e. one with histograms in form of dictionary). If the 
  job has not completed yet, it should raise an error.
- `status <async-result>` should inform user if the async result can be resolved now.

Note that because of the time constraints at this moment, we assume that all jobs succeed 
eventually. We will handle failures later if we are lucky enough to have some more time.
