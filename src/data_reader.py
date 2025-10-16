import numpy as np
import pandas as pd

from src.data_generator import DataGenerator


def parse_info_sheet(info_df):
    courses = list(info_df.index)
    course_2_group_size = {c: {"lower": 0, "upper": 0} for c in courses}
    for c, min_, max_ in zip(courses, info_df.min_group_size,
                             info_df.max_group_size):
        course_2_group_size[c]["lower"] = min_
        course_2_group_size[c]["upper"] = max_

    course_2_group_range = {c: {"lower": 0, "upper": 0} for c in courses}
    for c, min_, max_ in zip(courses, info_df.min_number_of_groups,
                             info_df.max_number_of_groups):
        course_2_group_range[c]["lower"] = min_
        course_2_group_range[c]["upper"] = max_
    return course_2_group_size, course_2_group_range


def get_preferences_by_df(df):
    main_agents = list(df.index)
    over_agents = list(df.columns)
    preferences = {ma: np.zeros(len(over_agents)) for ma in main_agents}
    for ma, positions in zip(main_agents, df.values):
        for a, pos in zip(over_agents, positions):
            preferences[ma][pos] = int(a)
    return len(main_agents), main_agents, preferences


def read_excel_data(file_name):
    info_df = pd.read_excel(file_name,
                            sheet_name="info",
                            index_col="course")
    students_prefs_df = pd.read_excel(file_name,
                                      sheet_name="students' preferences",
                                      index_col="student\course")

    courses_prefs_df = pd.read_excel(file_name,
                                     sheet_name="courses' preferences",
                                     index_col="course\student")

    course_2_group_size, course_2_group_range = parse_info_sheet(info_df)
    num_of_students, students, student_preferences = get_preferences_by_df(
        students_prefs_df)
    num_of_courses, courses, course_preferences = get_preferences_by_df(
        courses_prefs_df)

    student_pref_pos = DataGenerator.get_preferences_positions(
        student_preferences)
    course_pref_pos = DataGenerator.get_preferences_positions(
        course_preferences)

    return (students,
            courses,
            course_preferences,
            student_preferences,
            course_pref_pos,
            student_pref_pos,
            course_2_group_size,
            course_2_group_range)
