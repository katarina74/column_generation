def get_blocking_coalitions(courses,
                            students,
                            student_pref_pos,
                            matching,
                            course_2_group_size,
                            course_2_group_range,
                            course_2_number_of_groups):
    blocking_courses = set()
    conflicts = []
    for c in courses:
        if course_2_number_of_groups[c] < course_2_group_range[c]['upper']:
            block_candidates = [s for s in students if student_pref_pos[s][c]
                                < student_pref_pos[s][matching[s]]]
            if len(block_candidates) >= course_2_group_size[c]['lower']:
                blocking_courses.add(c)
                for s in block_candidates:
                    conflicts.append((s, c))
    return blocking_courses, set(conflicts)


def get_course_2_students(courses, matching):
        course_2_students = {c: [] for c in courses}
        for s, c in matching.items():
            if c is not None:
                course_2_students[c].append(s)
        return course_2_students


def get_blocking_pairs(courses,
                       students,
                       student_pref_pos,
                       course_pref_pos,
                       matching,
                       course_2_group_size,
                       course_2_group_range,
                       course_2_number_of_groups):
    conflicts = []
    courses_2_students = get_course_2_students(courses, matching)
    for s in students:
        for c in courses:
            if (student_pref_pos[s][matching[s]] > student_pref_pos[s][c] and
                    course_2_number_of_groups[c]
                    * course_2_group_size[c]['upper']
                    > len(courses_2_students[c])) or (
                            student_pref_pos[s][matching[s]] >
                            student_pref_pos[s][c] and
                            len([s_ for s_ in courses_2_students[c] if
                                 course_pref_pos[c][s] <
                                 course_pref_pos[c][s_]]) > 0):
                conflicts.append((s, c))
    return conflicts
