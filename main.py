from os import listdir

from src.data_reader import read_excel_data
from src.cg import ColumnGeneration
from src.conflict_counter import get_blocking_coalitions, get_blocking_pairs
from src.ip import get_ip_solution


file_names = [f for f in listdir('data/')]

for file_name in file_names:
    print("==================================================================")
    print(file_name)
    (students,
     courses,
     course_preferences,
     student_preferences,
     course_pref_pos,
     student_pref_pos,
     course_2_group_size,
     course_2_group_range) = read_excel_data('data/' + file_name)

    num_of_students = len(students)
    num_of_courses = len(courses)

    solution_ip = get_ip_solution(
        courses, students, course_2_group_range, course_2_group_size,
        student_preferences, course_preferences, student_pref_pos,
        course_pref_pos, num_of_students, time_limit=3600)

    if len(solution_ip) > 3:
        (sol_ip,
         course_to_num_of_groups_ip,
         total_utility_ip,
         solving_time_ip,
         solver_solving_time_ip) = solution_ip

        blocking_courses_ip, _ = get_blocking_coalitions(
            courses, students, student_pref_pos, sol_ip, course_2_group_size,
            course_2_group_range, course_to_num_of_groups_ip)

        blocking_pairs_ip = get_blocking_pairs(
            courses, students, student_pref_pos, course_pref_pos, sol_ip,
            course_2_group_size, course_2_group_range,
            course_to_num_of_groups_ip)

        print(f"Total solving time:{solving_time_ip}, "
              f"solver's solving time: {solver_solving_time_ip}, "
              f"number of blocking courses: {len(blocking_courses_ip)}, "
              f"number of blocking pairs: {len(blocking_pairs_ip)}, "
              f"total utility: {-total_utility_ip}")
    else:
        print("Solution is not found")
        print(f"Total solving time:{solution_ip[1]}, "
              f"solver's solving time: {solution_ip[2]} ")

    cg = ColumnGeneration(students,
                          courses,
                          course_2_group_size,
                          course_2_group_range,
                          student_preferences,
                          course_preferences,
                          student_pref_pos,
                          course_pref_pos,
                          num_of_students,
                          num_of_courses)

    (sol_cg, course_to_num_of_groups_cg, total_utuluty_cg, solving_time_cg,
     solver_solving_time_cg) = cg.run(time_limit=3600)

    if sol_cg:

        blocking_courses_cg, _ = get_blocking_coalitions(
            courses, students, student_pref_pos, sol_cg, course_2_group_size,
            course_2_group_range, course_to_num_of_groups_cg)

        blocking_pairs_cg = get_blocking_pairs(courses,
                                               students,
                                               student_pref_pos,
                                               course_pref_pos,
                                               sol_cg,
                                               course_2_group_size,
                                               course_2_group_range,
                                               course_to_num_of_groups_cg)

        print(f"Total solving time:{solving_time_cg}, "
              f"solver's solving time: {solver_solving_time_cg}, "
              f"number of blocking courses: {len(blocking_courses_cg)}, "
              f"number of blocking pairs: {len(blocking_pairs_cg)}, "
              f"total utility: {-total_utuluty_cg}")
    else:
        print("Solution is not found")
        print(f"Total solving time:{solving_time_cg}, "
              f"solver's solving time: {solver_solving_time_cg}, ")

