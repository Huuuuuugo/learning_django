from django.contrib import admin

from .models import Question, Choice


# class that will be used to display a model as part of another model on the create/edit page
class ChoiceInLine(admin.TabularInline):
    model = Choice
    extra = 2


class QuestionAdmin(admin.ModelAdmin):
    # defines all the information that will be displayed on the page listing all the entries on the data base
    # also allows sorting by any of these values (although arbitrary functions need some extra steps for that)
    list_display = ["question_text", "pub_date", "was_published_recently"]

    # associate field groups of the model to named sections on the create/edit page
    fieldsets = (
        ("Question Details", {"fields": ["question_text"]}),
        ("Date", {"fields": ["pub_date"], "classes": ["collapse"]}),
    )

    # reference to another model that should be rendered as a section of the current model on the create/edit page
    inlines = [ChoiceInLine]

    # allows entries to be filtered by the fields in the list (the filter is based on the type of the function)
    list_filter = ["pub_date"]

    # allows searches on the specified fields
    search_fields = ["question_text"]


admin.site.register(Question, QuestionAdmin)
