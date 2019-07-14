from django.http import HttpResponse
from django.template import loader
from django.contrib import admin

from .models import BirthdayItem


@admin.register(BirthdayItem)
class BirthdayItemAdmin(admin.ModelAdmin):
    actions = ['download_csv']
    list_display = ('name', 'second_name', 'date_of_birth',)
    list_filter = ('name', 'second_name', 'date_of_birth',)
    date_hierarchy = 'date_of_birth'

    def download_csv(self, request, queryset):
        # Создает месячный отчет по именинникам
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
        try:
            month = queryset[0].date_of_birth.month
        except:
            month = 1

        birthdays_month = BirthdayItem.objects.filter(date_of_birth__month=month)

        t = loader.get_template('birthdays/birthday_men.txt')

        scv_data = {'birthdays_men': birthdays_month}
        response.write(t.render(scv_data))
        return response

    download_csv.short_description = "Скачать список именинников за выбранный месяц"

