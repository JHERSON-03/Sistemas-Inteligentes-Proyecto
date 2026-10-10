from .. import models


def first_name(user: models.User) -> str:
    return user.full_name.split()[0]


def course_out(course: models.Course) -> dict:
    return {"slug": course.slug, "name": course.name, "color": course.color}
