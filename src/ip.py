import pulp
import time


def get_ip_solution(courses,
                    students,
                    course_2_group_range,
                    course_2_group_size,
                    student_preferences,
                    course_preferences,
                    student_pref_pos,
                    course_pref_pos,
                    num_of_students,
                    time_limit=300):
    start_time = time.time()
    print("!!!start optimizing!!!")
    model = pulp.LpProblem("Model", pulp.LpMinimize)

    print(f"Elapsed time: {round(time.time() - start_time, 2)}, "
          f" model has been created.")
    idx = [(s, c) for s in students for c in courses]
    vars_x = pulp.LpVariable.dicts('x', idx, cat='Binary')

    vars_b = pulp.LpVariable.dicts('b', idx, cat='Binary')
    vars_y = pulp.LpVariable.dicts('y', courses, cat='Binary')

    vars_z = {}
    for c in courses:
        vars_z[c] = pulp.LpVariable(f"z_{c}", cat=pulp.LpInteger,
                                    lowBound=course_2_group_range[c]["lower"],
                                    upBound=course_2_group_range[c]["upper"])

    vars_f = {}
    for c in courses:
        if course_2_group_range[c]["lower"] < course_2_group_range[c]["upper"]:
            vars_f[c] = pulp.LpVariable(f"f_{c}", cat=pulp.LpBinary)

    print(f"Elapsed time: {round(time.time() - start_time, 2)}, "
          f"variables have been created.")

    of_max_utility = (pulp.lpSum((- len(courses) + student_pref_pos[s][c])
                                 * var
                                 for (s, c), var in vars_x.items())
                      + 1_000 * pulp.lpSum(var for var in vars_b.values())
                      + 1_000 * pulp.lpSum(course_2_group_size[c]["lower"]
                                           * vars_y[c]
                                           for c in courses))

    model += of_max_utility

    print(
        f"Elapsed time: {round(time.time() - start_time, 2)}, "
        f"objective function has been created.")

    for s in students:
        model += pulp.lpSum(vars_x[s, c] for c in courses) == 1

    print(
        f"Elapsed time: {round(time.time() - start_time, 2)}, "
        f"student assignment constraints have been created.")

    for c in courses:
        model += (course_2_group_size[c]["lower"] * vars_z[c] <=
                  pulp.lpSum(vars_x[s, c] for s in students))
        model += (course_2_group_size[c]["upper"] * vars_z[c] >=
                  pulp.lpSum(vars_x[s, c] for s in students))

    print(
        f"Elapsed time: {round(time.time() - start_time, 2)}, "
        f"course size constraints have been created.")

    for (s, c), var in vars_x.items():
        model += ((course_2_group_range[c]["upper"]
                   * course_2_group_size[c]["upper"] * var +
                   course_2_group_size[c]["upper"]
                   * course_2_group_range[c]["upper"] *
                   pulp.lpSum(vars_x[s, c_] for c_ in
                              student_preferences[s][
                              : student_pref_pos[s][c]]) +
                  pulp.lpSum(vars_x[s_, c] for s_ in
                             course_preferences[c][: course_pref_pos[c][s]]))
                  >= course_2_group_size[c]["upper"] * vars_z[c]
                  - course_2_group_size[c]["upper"]
                  * course_2_group_range[c]["upper"] * vars_b[s, c])

    print(
        f"Elapsed time: {round(time.time() - start_time, 2)}, "
        f"blocking pairs constraints have been created.")

    for c in courses:
        if course_2_group_range[c]["lower"] < course_2_group_range[c]["upper"]:
            model += (pulp.lpSum(vars_x[s, c_] for s in students for c_ in
                                 student_preferences[s][
                                 student_pref_pos[s][c] + 1:])
                      <= course_2_group_size[c]["lower"] - 1
                      + num_of_students * (1 - vars_f[c])
                      + num_of_students * vars_y[c])

    for c in vars_f:
        model += (course_2_group_range[c]["upper"] <= vars_z[c]
                  + course_2_group_range[c]["upper"] * vars_f[c])

    print(
        f"Elapsed time: {round(time.time() - start_time, 2)}, "
        f"blocking coalitions constraints have been created.")

    # model.solve(pulp.CPLEX(msg=True,
    #                        options=['set mip limits solution 1']))

    model.solve(pulp.CPLEX(msg=True, timeLimit=time_limit))
    if model.status == 1:
        sol = [(int(s), int(c)) for (s, c), var in vars_x.items()
               if round(var.varValue) == 1]

        matching = {s: c for s, c in sol}
        course_to_num_of_groups = {c: round(var.varValue)
                                   for c, var in vars_z.items()}

        total_utility = sum((- len(courses) + student_pref_pos[s][c])
                            * round(var.varValue) for (s, c), var in
                            vars_x.items())

        return (matching, course_to_num_of_groups, total_utility,
                round(time.time() - start_time, 2),
                round(model.solutionTime, 2))

    return (None,
            round(time.time() - start_time, 2),
            round(model.solutionTime, 2))
