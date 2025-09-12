"""
Signal for post_save and post_delete Course Progress Tracking
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from core.models import LectureProgress, CourseProgress, Lecture


@receiver(post_save, sender=LectureProgress)
def update_course_progress_on_lecture_save(sender, instance, created, **kwargs):
    """
    Signal handler: Called automatically AFTER a LectureProgress is saved.
    This runs every time someone marks a lecture complete/incomplete.
    """

    course = instance.lecture.section.course

    course_progress, created = CourseProgress.objects.get_or_create(
        student= instance.student,
        course=course,
        defaults={
            'total_lectures': Lecture.objects.filter(section__course=course).count()
        }
    )

    course_progress.update_progress()


@receiver(post_delete, sender=LectureProgress)
def update_course_progress_on_lecture_delete(sender, instance, **kwargs):
    """
    Signal handler: Called automatically AFTER a LectureProgress is deleted.
    """
    try:
        course = instance.lecture.section.course
        course_progress = CourseProgress.objects.get(
            student=instance.student,
            course=course
        )

        course_progress.update_progress()
    except CourseProgress.DoesNotExist:
        pass
