from django.contrib import admin

from schedules.models import Month, Week, Year


class MonthAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'year',
    )
    list_filter = (
        'year',
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
admin.site.register(Week, WeekAdmin)
admin.site.register(Year)
