from operator import itemgetter
import pandas
import pulp

from example_inputs import (
    periods,
#    quarters,
    worker_data,
)

AM_PERIODS = 42
AM_QUARTERS = 28

# Divide week in 42 4-hour periods. 0 = Monday 0-4, 1 = Monday 4-8, 2 = Monday 8-12........ 39 = Sunday 12-16, 40 = Sunday 16-20, 41 = Sunday 20-24
# 

# workers_data = {
#   worker1: {
#       "period_avail": [0, 1, 1, 1, 0, 0,........, 1, 1, 0, 0]. Length 42,
#       "skill_level": int in 0-100 
#   }
# }

# quarters = [5, 4, 10, .... , 8, 9, 12] Amount of workers needed for each quarter of day. Length 28

def model_problem():

    workerdf = pandas.read_excel("workers.xlsx", header=0) 
    workers_data = {}
    for iteration in workerdf.iterrows(): 
        row = iteration[1] 
        name = row[0] 
        workers_data[name] = {} 
        workers_data[name]["skill_level"] = row[1] 
        workers_data[name]["period_avail"] = [] 
        for day in range(7): 
            for period in range(6): 
                workers_data[name]["period_avail"].append(
                    int((period*4 >= row[2 + day * 2]) and ((period+1)*4 <= row[2 + day*2 + 1]))
                )

    quarters = pandas.read_excel("./quarter.xlsx", header=0).loc[0].tolist()

    problem = pulp.LpProblem("ScheduleWorkers", pulp.LpMinimize)

    workerid = 0
    for worker in workers_data.keys():
        workerstr = str(workerid)
        periodid = 0

        workers_data[worker]["worked_periods"] = []
        workers_data[worker]["rest_periods"] = []
        workers_data[worker]["weekend_periods"] = []

        for period in workers_data[worker]["period_avail"]:
            
            periodstr = str(periodid)
            # worked periods: worker W works in period P
            workers_data[worker]["worked_periods"].append(
                pulp.LpVariable("x_{}_{}".format(workerstr, periodstr), cat=pulp.LpBinary, upBound=period)
            )
            # rest periods: worker W takes a 12-hour rest starting on period P
            workers_data[worker]["rest_periods"].append(
                pulp.LpVariable("d_{}_{}".format(workerstr, periodstr), cat=pulp.LpBinary)
            )
            # weekend periods: worker W takes a 48-hour rest starting on period P
            workers_data[worker]["weekend_periods"].append(
                pulp.LpVariable("f_{}_{}".format(workerstr, periodstr), cat=pulp.LpBinary)
            )

            periodid += 1

        workerid += 1

    # Create objective function (amount of turns worked)
    objective_function = None
    for worker in workers_data.keys():
        objective_function += sum(workers_data[worker]["worked_periods"])
    
    problem += objective_function

    # Every quarter minimum workers constraint
    for quarter in range(AM_QUARTERS):
        workquartsum = None
        for worker in workers_data.keys():
            workquartsum += workers_data[worker]["worked_periods"][quarter + quarter // 2] + workers_data[worker]["worked_periods"][quarter + quarter // 2 + 1]
        
        problem += workquartsum >= quarters[quarter]
            
    # No worker with skill <= 25 is left alone
    for period in range(AM_PERIODS):
        skillperiodsum = None
        for worker in workers_data.keys():
            skillperiodsum += workers_data[worker]["worked_periods"][period] * workers_data[worker]["skill_level"]
        
        problem += skillperiodsum >= 26

    # Each worker must have one 12-hour break per day
    for day in range(7):
        for worker in workers_data.keys():
            problem += sum(workers_data[worker]["rest_periods"][day * 6:(day + 1) * 6]) >= 1

    # If a worker takes a 12-hour break, can't work in the immediate 3 periods

    for period in range(AM_PERIODS):
        for worker in workers_data.keys():
            access_list = [period, (period + 1) % 42, (period + 2) % 42]
            problem += sum(list(itemgetter(*access_list)(workers_data[worker]["worked_periods"]))) <= 3 * (1 - workers_data[worker]["rest_periods"][period])

    # A worker can't work more than 12 hours every 24 hours
    for period in range(AM_PERIODS):
        for worker in workers_data.keys():
            access_list = [period, (period + 1)  % 42, (period + 2) % 42, (period + 3) % 42, (period + 4) % 42, (period + 5) % 42]
            problem += sum(list(itemgetter(*access_list)(workers_data[worker]["worked_periods"]))) <= 3

    # Each worker must have one 48-hour break per week

    for worker in workers_data.keys():
        problem += sum(workers_data[worker]["weekend_periods"]) == 1

    # If a worker takes a 48-hour break, can't work in the inmediate 12 periods

    for period in range(AM_PERIODS):
        for worker in workers_data.keys():
            for miniperiod in range(12):
                problem += workers_data[worker]["worked_periods"][(period + miniperiod) % AM_PERIODS] <= (1 - workers_data[worker]["weekend_periods"][period])
        problem += workers_data[worker]["worked_periods"][(period + 12) % AM_PERIODS] >= workers_data[worker]["weekend_periods"][period]

    try:
        problem.solve()
    except Exception as e:
        print("Can't solve problem: {}".format(e))

    for worker in workers_data.keys(): 
        workers_data[worker]["schedule"] = [] 
        for element in range(len(workers_data[worker]["worked_periods"])):
            if workers_data[worker]["worked_periods"][element].varValue == 1:
                workers_data[worker]["schedule"].append(periods[element])

    return problem, workers_data

if __name__ == "__main__":
    problem, workers_data = model_problem()

    f = open("./schedule.csv", "w")
    for worker in workers_data.keys():
        f.write(worker)
        for element in workers_data[worker]["schedule"]:
            f.write(", " + element)
        f.write("\n")
    f.close()
