from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel


class HomePage(Page):
    subpage_types = ['core.ServicesIndexPage',]


class ServicesIndexPage(Page):
    subpage_types = ['core.ServicePage',]


class ServicePage(Page):
    subpage_types = []

    overview = RichTextField()

    content_panels = Page.content_panels + [FieldPanel('overview'),]
