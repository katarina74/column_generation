import time

import pulp
import numpy as np


class ColumnGeneration:
    def __init__(self,
                 students,
                 courses,
                 course_2_group_size,
                 course_2_group_range,
                 student_preferences,
                 course_preferences,
                 student_pref_pos,
                 course_pref_pos,
                 num_of_students,
                 num_of_courses):
        self.start_time = time.time()
        self.students = students
        self.courses = courses
        self.course_2_group_size = course_2_group_size
        self.course_2_group_range = course_2_group_range
        self.student_preferences = student_preferences
        self.course_preferences = course_preferences
        self.student_pref_pos = student_pref_pos
        self.course_pref_pos = course_pref_pos
        self.num_of_students = num_of_students
        self.num_of_courses = num_of_courses

        self.subproblem = self.get_subproblem()
        self.get_pair_2_cons()
        self.get_con_2_index()

    def get_con_2_index(self):
        self.subproblem_con_2_index = []
        j = 0
        for c in self.courses:
            con_2_index = {1: {},
                           2: {}}
            for i, s in enumerate(self.students):
                con_2_index[1][(s, c)] = int(i + c
                                             * self.num_of_students)
            if (self.course_2_group_range[c]["lower"]
                    < self.course_2_group_range[c]["upper"]):
                con_2_index[2] = (j +
                                  self.num_of_students * self.num_of_courses)
                j += 1
            self.subproblem_con_2_index.append(con_2_index)

    def get_pair_2_cons(self):
        self.pair_2_cons_1 = {(s, c): [] for s, c in self.pairs}

        for (s, c) in self.pair_2_cons_1:
            self.pair_2_cons_1[s, c].append([self.course_2_group_size[c][
                                                 "upper"] *
                                             self.course_2_group_range[c][
                                                 "upper"], (s, c)])

            map(lambda c_: self.pair_2_cons_1[s, c_].append(
                [self.course_2_group_size[c_]["upper"]
                 * self.course_2_group_range[c_]["upper"], (s, c)]),
                self.student_preferences[s][:self.student_pref_pos[s][c]])

            map(lambda s_: self.pair_2_cons_1[s_, c].append([1, (s, c)]),
                self.course_preferences[c][:self.course_pref_pos[c][s]])

        self.pair_2_cons_2 = {(s, c): [] for s in self.students
                                for c in self.courses}
        for c in self.courses:
            for s in self.students:
                # for c_ in self.student_preferences[s][self.student_pref_pos[s
                #                                       ][c] + 1:]:
                #     self.pair_2_cons_2[s, c_].append([1, c])
                map(lambda c_: self.pair_2_cons_2[s, c_].append([1, c]),
                    self.student_preferences[s][self.student_pref_pos[s][c]
                                                + 1:])

    def get_subproblem(self):
        model = pulp.LpProblem(f"subproblem", pulp.LpMinimize)
        self.pairs = [(s, c) for s in self.students for c in self.courses]
        vars_x = pulp.LpVariable.dicts('x', self.pairs,
                                       cat=pulp.LpBinary)

        vars_z = {}
        for c in self.courses:
            vars_z[c] = pulp.LpVariable(f"z_{c}", cat=pulp.LpInteger,
                                        lowBound=self.course_2_group_range[c][
                                            "lower"],
                                        upBound=self.course_2_group_range[c][
                                            "upper"])

        vars_f = {}
        for c in self.courses:
            if self.course_2_group_range[c]["lower"] \
                    < self.course_2_group_range[c]["upper"]:
                vars_f[c] = pulp.LpVariable(f"f_{c}", cat=pulp.LpBinary)

        self.sub_vars = {"x": vars_x, "z": vars_z, "f": vars_f}

        for s in self.students:
            model += pulp.lpSum(vars_x[s, c] for c in self.courses) == 1

        for c in self.courses:
            model += (self.course_2_group_size[c]["lower"] * vars_z[c] <=
                      pulp.lpSum(vars_x[s, c] for s in self.students))
            model += (self.course_2_group_size[c]["upper"] * vars_z[c] >=
                      pulp.lpSum(vars_x[s, c] for s in self.students))

        for c in vars_f:
            model += (self.course_2_group_range[c]["upper"] <= vars_z[c]
                      + self.course_2_group_range[c]["upper"] * vars_f[c])

        print(f"Elapsed time: {round(time.time() - self.start_time, 2)}, "
              f"subproblem has been created.")

        return model

    def set_objective_for_subproblem(self, pi_list):
        self.subproblem.setObjective(pulp.lpSum(
            pulp.lpSum(
                (-self.num_of_courses + self.student_pref_pos[s][c] -
                 pulp.lpSum(mul * pi_list[self.subproblem_con_2_index[c_][
                     1][s_, c_]]
                 for mul, (s_, c_) in self.pair_2_cons_1[s, c])
                 - pulp.lpSum(mul * pi_list[self.subproblem_con_2_index[c_][
                            2]] for mul, c_ in self.pair_2_cons_2[s, c]))
                * self.sub_vars["x"][s, c]
                for s in self.students for c in self.courses))

            + pulp.lpSum(self.course_2_group_size[c]["upper"]
                         * pulp.lpSum(pi_list[self.subproblem_con_2_index[c][
                            1][s, c]] for s in self.students)
                         * self.sub_vars["z"][c]
                         for c in self.courses)

            + pulp.lpSum(self.num_of_students * pi_list[
                         self.subproblem_con_2_index[c][2]]
                         * self.sub_vars["f"][c]
                         for c in self.sub_vars["f"])

            + 0.0001 * pulp.lpSum(self.sub_vars["f"][c]
                                  for c in self.sub_vars["f"])
            - pi_list[-1])

    def get_master_problem_lp(self):
        print(f"Elapsed time: {round(time.time() - self.start_time, 2)}, "
              f"master LP has been created.")
        model = pulp.LpProblem("master_LP", pulp.LpMinimize)
        self.obj = pulp.LpConstraintVar()
        model.setObjective(self.obj)
        self.constraints = []

        for c in self.courses:
            for s in self.students:
                self.constraints.append(
                    pulp.LpConstraintVar(f"con_2_{s}_{c}",
                                         pulp.LpConstraintGE,
                                         0))
                model += self.constraints[-1]

        print(f"Elapsed time: {round(time.time() - self.start_time, 2)}, "
              f"blocking pairs constraints have been created.")

        for c in self.courses:
            if self.course_2_group_range[c]["lower"] < \
                          self.course_2_group_range[c]["upper"]:
                self.constraints.append(
                    pulp.LpConstraintVar(f"con_3_{c}",
                                         pulp.LpConstraintLE,
                                         self.course_2_group_size[c]["lower"]
                                         - 1))
                model += self.constraints[-1]

        print(f"Elapsed time: {round(time.time() - self.start_time, 2)}, "
              f"blocking coalitions constraints have been created.")

        self.constraints.append(pulp.LpConstraintVar(f"con_4",
                                                     pulp.LpConstraintEQ,
                                                     1))
        model += self.constraints[-1]

        self.lambda_vars = []
        # for q in range(0):
        #     self.lambda_vars.append(pulp.LpVariable(f'lambda_0', lowBound=0,
        #                                             cat=pulp.LpBinary,
        #                                             e=1 * self.constraints[
        #                                              self.num_of_students
        #                                              * self.num_of_courses
        #                                              + self.num_of_courses]))

        self.vars_mu_1= [
            pulp.LpVariable(f'mu_1_{s}_{c}',
                            lowBound=0,
                            e=(1_000 * self.obj
                               + self.course_2_group_size[c]["upper"]
                               * self.course_2_group_range[c]["upper"]
                               * self.constraints[c * self.num_of_students
                                                  + s]))
            for s in range(self.num_of_students)
            for c in range(self.num_of_courses)]

        print(f"Elapsed time: {round(time.time() - self.start_time, 2)}, "
              f"dummy variables 1 have been created.")

        self.vars_mu_2 = []

        i = 0
        for c in self.courses:
            if (self.course_2_group_range[c]["lower"]
                    < self.course_2_group_range[c]["upper"]):
                self.vars_mu_2.append(pulp.LpVariable(f'mu_2_{c}',
                                      lowBound=0,
                                      e=(1_000
                                         * self.course_2_group_size[c]["lower"]
                                         * self.obj
                                         - self.num_of_students
                                         * self.constraints[
                                             self.num_of_students
                                             * self.num_of_courses + i])))
                i += 1

        print(f"Elapsed time: {round(time.time() - self.start_time, 2)}, "
              f"dummy variables 2 have been created.")

        self.var_mu_3 = pulp.LpVariable(f'mu_3', lowBound=0,
                                        e=(1_000_000_000 * self.obj +
                                           self.constraints[-1]))

        return model

    def run(self, time_limit=300):
        master_obj_value = 10_000_000_000
        master_obj_value_prev = 100_000_000_000
        obj_value = -np.inf

        self.lambda_to_solution = {}

        sol_time = 0

        master_lp = self.get_master_problem_lp()
        print(f"Elapsed time: {round(time.time() - self.start_time, 2)}, "
              f"master LP has been created.")

        of_master = np.array([
            -self.num_of_courses + self.student_pref_pos[s][c]
            for s in self.students for c in self.courses])

        k = 0

        print("Elapsed time, ", "master obj. value, ",
              "subproblem obj. value, ",
              "abs master obj. value - prev. master obj. value")
        while -10e-8 >= obj_value and \
                abs(master_obj_value - master_obj_value_prev) > 0.9:

            master_lp.solve(pulp.CPLEX(msg=False,
                                       options=['set lpmethod 4']))

            sol_time += master_lp.solutionTime

            pi_list = np.array(list(map(lambda con: con.pi,
                                        master_lp.constraints.values())))

            k += 1

            self.set_objective_for_subproblem(pi_list)

            self.subproblem.solve(pulp.CPLEX(msg=False))

            if self.subproblem.status != 1:
                break

            sol_time += self.subproblem.solutionTime
            solution_x = {(s, c): round(self.sub_vars["x"][s, c].varValue)
                          for s in self.students for c in self.courses}
            solution_z = {c: self.sub_vars["z"][c].varValue
                          for c in self.courses}
            solution_f = {c: self.sub_vars["f"][c].varValue
                          for c in self.courses if
                          self.course_2_group_range[c]["lower"]
                          < self.course_2_group_range[c]["upper"]}

            # for c in solution_f:
            #     if (solution_f[c] == 1 and self.sub_vars["z"][c].varValue
            #             == self.course_2_group_range[c]["upper"]):
            #         print(c)

            solution_x_array = np.array(list(solution_x.values()))

            # print(self.subproblem.objective.value())

            master_obj_value_prev = master_obj_value
            master_obj_value = master_lp.objective.value()
            obj_value = (self.subproblem.objective.value()
                         - 0.0001 * sum(solution_f.values()))
            print(round(time.time() - self.start_time, 2),
                  round(master_obj_value, 2),
                  round(obj_value, 2),
                  round(abs(master_obj_value_prev - master_obj_value), 2)
                  )

            if time.time() - self.start_time >= time_limit - 1 and k > 1:
                break

            if self.subproblem.objective.value() < 0:
                e = (np.dot(of_master, solution_x_array) * self.obj +

                     + pulp.lpSum(solution_x[s, c]
                                  * self.course_2_group_size[c]["upper"]
                                  * self.course_2_group_range[c]["upper"]
                                  * self.constraints[c * self.num_of_students
                                                     + s]
                                  for s in self.students
                                  for c in self.courses)

                     + pulp.lpSum(sum(solution_x[s, c_]
                                  * self.course_2_group_size[c]["upper"]
                                  * self.course_2_group_range[c]["upper"]
                                  * self.constraints[self.num_of_students
                                                     * c + s]
                                  for c_ in self.student_preferences[s][
                                            :self.student_pref_pos[s][c]])
                                  for s in self.students for c in self.courses)

                     + pulp.lpSum(sum(solution_x[s_, c]
                                  for s_ in
                                  self.course_preferences[c][
                                  :self.course_pref_pos[c][s]])
                                  * self.constraints[self.num_of_students
                                                     * c + s]
                                  for s in self.students for c in self.courses)

                     + pulp.lpSum(-solution_z[c] * self.course_2_group_size[c][
                            "upper"] * self.constraints[
                            self.num_of_students * c + s]
                                  for s in self.students for c in self.courses)

                     + pulp.lpSum((sum(solution_x[s, _c] for s in
                                       self.students for _c in
                                       self.student_preferences[s][
                                       self.student_pref_pos[s][c] + 1:])
                                   - self.num_of_students
                                   * (1 - solution_f[c]))
                                  * self.constraints[self.num_of_students
                                                     * self.num_of_courses + i]
                                  for i, c in enumerate(solution_f))

                     + self.constraints[
                                        self.num_of_students
                                        * self.num_of_courses
                                        + len(solution_f)
                     ])

                lambda_new = pulp.LpVariable(f'lambda_{k}',
                                             lowBound=0,
                                             # cat=pulp.LpBinary,
                                             e=e)
                self.lambda_to_solution[lambda_new] = {**solution_x,
                                                       **solution_z}
                self.lambda_vars.append(lambda_new)

        master_ip = master_lp
        for var in self.lambda_vars:
            var.cat = pulp.LpBinary
        for var in self.vars_mu_1 + self.vars_mu_2 + [self.var_mu_3]:
            var.cat = pulp.LpBinary

        master_ip.solve(pulp.CPLEX(msg=True))
        sol_time += master_ip.solutionTime

        sol = None
        for lambda_var in self.lambda_vars:
            if abs(lambda_var.varValue - 1) <= 0.1:
                sol = [(int(s), int(c)) for s in self.students
                       for c in self.courses
                       if self.lambda_to_solution[lambda_var][s, c] == 1]

        matching = None
        if sol:
            matching = {s: c for s, c in sol}

        course_to_num_of_groups = None
        for lambda_var in self.lambda_vars:
            if abs(lambda_var.varValue - 1) <= 0.1:
                course_to_num_of_groups = {c: self.lambda_to_solution[
                    lambda_var][c] for c in self.courses}

        total_utility = None
        if sol:
            total_utility = sum((- len(self.courses) +
                                 self.student_pref_pos[s][c])
                                for s, c in sol)

        end_time = time.time()

        return (matching, course_to_num_of_groups, total_utility,
                end_time - self.start_time, sol_time)
