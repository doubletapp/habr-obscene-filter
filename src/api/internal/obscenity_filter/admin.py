import csv
import io

from django import forms
from django.contrib import admin
from django.core.checks import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from api.internal.obscenity_filter.app import obscenity_filter_service
from api.internal.obscenity_filter.models import ObsceneWord, SuspiciousWord


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(
        label="Upload file",
        widget=forms.ClearableFileInput(
            attrs={
                "class": "form-control",
            }
        ),
        help_text="File must consist of list of words separated with line breaks",
    )


@admin.register(ObsceneWord)
class ObsceneWordsAdmin(admin.ModelAdmin):
    change_list_template = "admin/import_change_list.html"
    readonly_fields = ["normalized_value"]
    list_display = ["value", "normalized_value", "similarity"]
    search_fields = ["value", "normalized_value"]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("import-csv/", self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]

            decoded_file = io.TextIOWrapper(csv_file.file, encoding="utf-8")
            reader = csv.reader(decoded_file)

            for row in reader:
                for word in row:
                    obscenity_filter_service.create_obscene_word(word)

            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "admin/csv_form.html", payload)

    def save_model(self, request, obj, form, change):
        obj.normalized_value = obscenity_filter_service.normalize_word(obj.value)
        super(ObsceneWordsAdmin, self).save_model(request, obj, form, change)


class DefaultStatusFilter(admin.SimpleListFilter):
    title = 'status'
    parameter_name = 'status'

    def choices(self, changelist):
        yield {
            "selected": self.value() is None,
            "query_string": changelist.get_query_string(remove=[self.parameter_name]),
            # "display": _("All"),
        }
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }

    def lookups(self, request, model_admin):
        return SuspiciousWord.SuspiciousWordStatuses.choices

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset.filter(status=SuspiciousWord.SuspiciousWordStatuses.PENDING)
        return queryset.filter(status=self.value())


@admin.register(SuspiciousWord)
class SuspiciousWordAdmin(admin.ModelAdmin):
    readonly_fields = ["value", "status"]
    list_display = ["value", "status", "approve_button", "reject_button"]
    list_display_links = None
    search_fields = ["value"]
    list_filter = (DefaultStatusFilter,)

    def approve_button(self, obj):
        return mark_safe(f'<a class="button" href="/admin/api/suspiciousword/{obj.id}/approve/">Add</a>')

    def reject_button(self, obj):
        return mark_safe(f'<a class="button" href="/admin/api/suspiciousword/{obj.id}/reject/">Decline</a>')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:suspiciousword_id>/approve/', self.admin_site.admin_view(self.approve_view)),
            path('<int:suspiciousword_id>/reject/', self.admin_site.admin_view(self.reject_view)),
        ]
        return custom_urls + urls

    def approve_view(self, request, suspiciousword_id):
        suspicious_word = SuspiciousWord.objects.get(id=suspiciousword_id)
        if suspicious_word.status == SuspiciousWord.SuspiciousWordStatuses.PENDING:
            suspicious_word.status = SuspiciousWord.SuspiciousWordStatuses.ADDED
            suspicious_word.save()
            obscenity_filter_service.create_obscene_word(suspicious_word.value)
            self.message_user(request, "Word was added to obscene dict!", level=messages.INFO)
        else:
            self.message_user(request, "You can manipulate only PENDING words!", level=messages.WARNING)
        return HttpResponseRedirect(f'/admin/api/suspiciousword/')

    def reject_view(self, request, suspiciousword_id):
        suspicious_word = SuspiciousWord.objects.get(id=suspiciousword_id)
        if suspicious_word.status == SuspiciousWord.SuspiciousWordStatuses.PENDING:
            suspicious_word.status = SuspiciousWord.SuspiciousWordStatuses.DECLINED
            suspicious_word.save()
            self.message_user(request, "Word was rejected!", level=messages.INFO)
        else:
            self.message_user(request, "You can manipulate only PENDING words!", level=messages.WARNING)
        return HttpResponseRedirect(f'/admin/api/suspiciousword/')
