# shift-scheduling
### Shift Scheduling for workforce

This is a shift planner, that takes data from Excel files (quarter.xlsx and workers.xlsx) and returns a CSV with weekly shifts for each worker.

### Problem Description

Suppose we have a place that needs to work 24/7, and we have a minimum amount of workers needed to run it on each quarter of day in the week (Monday from 0 to 6, Monday from 6 to 12, ... Sunday from 12 to 18, Sunday from 18 to 24).
We have to create a shift schedule that is subject to certain constraints.

In this case, the constraints added are:
* We have each worker and their weekly availability in an Excel file, along with their "skill level" (from 1 to 100).
* Every worker has to have a 12 hour rest per day.
* Every worker has to have a 24 hour rest per week.
* Every worker has to work at most 12 hours for each day.
* Work days are separated in six 4-hour shifts (0-4, 4-8, 8-12, 12-16, 16-20, 20-24).
* A worker with skill level < 25 can't be left alone.

### Output

This program returns the turns for each worker during the week, according to the constraints, in a CSV file called schedule.csv.

### Execution

To run, you have to install Pandas and PuLP.
Then, in shell:

    python model.py
    
It will take around a minute to solve, depending on the computer.
Then, we will have, for every worker in worker_data, a dictionary called "schedule", where it tells which period corresponds to each worker.

### Some reading

This work was done adapting the idea from: https://www.me.utexas.edu/~jensen/ORMM/models/unit/linear/subunits/workforce/index.html, adding constraints where it was needed.


### NEXT STEPS

Add more flexible shifts, including the capability of scheduling breaks, this can be done following article: https://link.springer.com/article/10.1007/s10479-019-03487-6.
