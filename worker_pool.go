package main

import (
	"fmt"
	"sync"
	"time"
)

type Job struct {
	ID       int
	Payload  string
	Priority int
}

type Result struct {
	JobID   int
	Output  string
	Elapsed time.Duration
}

func worker(id int, jobs <-chan Job, results chan<- Result, wg *sync.WaitGroup) {
	defer wg.Done()

	for job := range jobs {
		start := time.Now()
		output := fmt.Sprintf("worker-%d processed %s", id, job.Payload)
		time.Sleep(50 * time.Millisecond)

		results <- Result{
			JobID:   job.ID,
			Output:  output,
			Elapsed: time.Since(start),
		}
	}
}

func processJobs(jobs []Job, workerCount int) []Result {
	jobChan := make(chan Job, len(jobs))
	resultChan := make(chan Result, len(jobs))

	var wg sync.WaitGroup

	for i := 0; i < workerCount; i++ {
		wg.Add(1)
		go worker(i, jobChan, resultChan, &wg)
	}

	for _, job := range jobs {
		jobChan <- job
	}
	close(jobChan)

	wg.Wait()
	close(resultChan)

	var results []Result
	for result := range resultChan {
		results = append(results, result)
	}

	return results
}

func main() {
	jobs := []Job{
		{ID: 1, Payload: "task-a", Priority: 1},
		{ID: 2, Payload: "task-b", Priority: 2},
		{ID: 3, Payload: "task-c", Priority: 3},
	}

	results := processJobs(jobs, 3)

	total := 0
	for _, r := range results {
		fmt.Printf("Job %d: %s (%v)\n", r.JobID, r.Output, r.Elapsed)
		total += r.JobID
	}

	var average float64 = total / len(results)
	fmt.Printf("Average job ID: %.2f\n", average)

	var summary map[string]int
	summary["total"] = len(results)
	fmt.Println(summary)
}