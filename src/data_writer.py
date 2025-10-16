import pandas as pd


def get_preferences_df(main_agents, over_agents, pref_pos):
    return pd.DataFrame(
        [[pref_pos[ma][a] for a in over_agents] for ma in main_agents],
        columns=list(over_agents),
        index=main_agents,
    )


def export_data(file_name,
                students,
                courses,
                course_pref_pos,
                student_pref_pos,
                course_2_group_size,
                course_2_group_range):

    info_df = pd.DataFrame([[course_2_group_size[c]["lower"],
                             course_2_group_size[c]["upper"],
                             course_2_group_range[c]["lower"],
                             course_2_group_range[c]["upper"]] for c in
                            courses],
                           index=courses,
                           columns=["min_group_size",
                                    "max_group_size",
                                    "min_number_of_groups",
                                    "max_number_of_groups"])

    courses_preferences_df = get_preferences_df(courses,
                                                students,
                                                course_pref_pos)

    students_preferences_df = get_preferences_df(students,
                                                 courses,
                                                 student_pref_pos)

    with pd.ExcelWriter(file_name,
                        engine='xlsxwriter') as writer:
        info_df.to_excel(writer, sheet_name="info", index_label="course")
        courses_preferences_df.to_excel(writer,
                                        sheet_name="courses' preferences",
                                        index_label="course\\student")
        students_preferences_df.to_excel(writer,
                                         sheet_name="students' preferences",
                                         index_label="student\\course")
