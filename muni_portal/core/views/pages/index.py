import logging

from django.views import generic

logger = logging.getLogger(__name__)


class IndexView(generic.TemplateView):
    template_name = "index.html"
