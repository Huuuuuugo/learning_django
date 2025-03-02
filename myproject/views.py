from django.views.generic import RedirectView


class RedirectToPolls(RedirectView):
    pattern_name = "polls:index"
