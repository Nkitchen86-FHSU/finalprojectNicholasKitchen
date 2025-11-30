from django.utils import timezone
from datetime import datetime, timedelta
from .models import FeedingSchedule, Notification


def check_feeding_schedules():
    now = timezone.now()

    schedules = FeedingSchedule.objects.filter(next_run__lte=now)

    for schedule in schedules:
        owner = schedule.myanimal.owner
        animal = schedule.myanimal

        # Create notification
        Notification(owner=owner, message=f"It's time to feed {animal.name}")

        # Recalculate next_run
        next_run = calculate_next_run(schedule)
        schedule.next_run = next_run
        schedule.save()

def calculate_next_run(schedule):
    now = timezone.now()

    # For Every X Hours
    if schedule.frequency == schedule.EVERY_X_HOURS:
        return now + timedelta(hours=schedule.hours_interval)

    # Require a time of day. If none, then set next feeding forward a day.
    if not schedule.time_of_day:
        return now + timedelta(days=1)

    today = now.date()
    time_today = timezone.make_aware(datetime.combine(today, schedule.time_of_day))

    # For Daily
    if schedule.frequency == schedule.DAILY:
        if time_today > now:
            return time_today
        return time_today + timedelta(days=1)

    # For Weekly
    if schedule.frequency == schedule.WEEKLY and schedule.day_of_week:
        target = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'].index(schedule.day_of_week)
        today_wd = today.weekday()

        days_ahead = (target - today_wd) % 7
        if days_ahead == 0 and time_today < now:
            days_ahead = 7

        run_date = today + timedelta(days=days_ahead)
        return timezone.make_aware(datetime.combine(run_date, schedule.time_of_day))

    # Fallback
    return now + timedelta(days=1)