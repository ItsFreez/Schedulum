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


admin.site.register(Month, MonthAdmin)
admin.site.register(Week)
admin.site.register(Year)
