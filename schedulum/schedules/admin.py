from django.contrib import admin

from schedules.models import Month, Schedule, Week, Year


class MonthAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'year',
    )
    list_filter = (
        'year',
    )


class ScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'author',
    )
    list_filter = (
        'author',
    )


class WeekAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'month',
    )
    list_filter = (
        'month',
    )


admin.site.register(Month, MonthAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Week, WeekAdmin)
admin.site.register(Year)
