import numpy as np


class DataGenerator:
    def __init__(self,
                 num_of_students=50,
                 num_of_courses=5,
                 min_number_of_stud_in_group=5,
                 max_number_of_stud_in_group=15,
                 min_number_of_groups=0,
                 max_number_of_groups=3,
                 alpha_for_studs=0.5,
                 alpha_for_courses=0.5
                 ):
        self.num_of_students = num_of_students
        self.num_of_courses = num_of_courses
        self.students = np.arange(num_of_students)
        self.courses = np.arange(num_of_courses)
        self.min_number_of_stud_in_group = min_number_of_stud_in_group
        self.max_number_of_stud_in_group = max_number_of_stud_in_group
        self.min_number_of_groups = min_number_of_groups
        self.max_number_of_groups = max_number_of_groups
        self.alpha_for_studs = alpha_for_studs
        self.alpha_for_courses = alpha_for_courses

        # dicts of preferences lists
        self.course_preferences = self.generate_preferences(
            self.courses, self.students, self.num_of_students,
            alpha=self.alpha_for_courses)
        self.student_preferences = self.generate_preferences(
            self.students, self.courses, self.num_of_courses,
            alpha=self.alpha_for_studs)

    @staticmethod
    def generate_preferences(agents, over_agents, num_of_over, alpha=0.5):
        common_vector = np.random.rand(num_of_over)
        return {a: over_agents[((alpha * common_vector
                                 + (1 - alpha)
                                 * np.random.rand(num_of_over)).argsort()
                                )[::-1]]
                for a in agents}

    @staticmethod
    def get_preferences_positions(preferences):
        """generates agent positions in preference lists."""
        return {a: {agent: i for i, agent in enumerate(preferences[a])}
                for a in preferences.keys()}

    def get_course_size_dict(self, min_number, max_number):
        return {course: {"lower": min(min_, max_), "upper": max(min_, max_)}
                for course, [min_, max_] in
                zip(self.courses,
                    np.random.randint(low=min_number,
                                      high=max_number+1,
                                      size=(self.num_of_courses, 2)))}

    def get_group_size_dict(self, min_number, max_number):
        return {c: {"lower": min_number, "upper": max_number}
                for c in self.courses}

    def get_data(self):
        return (self.students,
                self.courses,
                self.course_preferences,
                self.student_preferences,
                self.get_preferences_positions(self.course_preferences),
                self.get_preferences_positions(self.student_preferences),
                self.get_group_size_dict(
                    self.min_number_of_stud_in_group,
                    self.max_number_of_stud_in_group),
                self.get_course_size_dict(
                    self.min_number_of_groups,
                    self.max_number_of_groups))

