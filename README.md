# shift-scheduling
Shift Scheduling for workforce

To run, you have to install IPython and PuLP.
Then, in ipython:

    run model.py
    problem = model_problem(quarters=quarters, workers_data=worker_data)
    
It will take around a minute to solve, depending on the computer.
Then, we will have, for every worker in worker_data, a dictionary called "schedule", where it tells which period corresponds to each worker.

This work was done adapting the idea from: https://www.me.utexas.edu/~jensen/ORMM/models/unit/linear/subunits/workforce/index.html, adding constraints where it was needed.
