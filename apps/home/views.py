from django.views.generic import TemplateView


class HomeIndexView(TemplateView):
    template_name = "home/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = "Reception"
        content = "Défilepsie reception"
        context = {
            "title": title,
            "content": content,
        }
        return context
