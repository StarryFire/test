import logging

from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from core.models import Deploy

logger = logging.getLogger(__name__)


class DeployLogView(LoginRequiredMixin, TemplateView):
    template_name = 'log.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        deploy_id = kwargs['deploy_id']

        ctx['ws_endpoint'] = 'wss://{hostname}/ws/deploy/{deploy_id}/tail/'.format(
            hostname=settings.SITE, deploy_id=deploy_id
        )
        ctx['deploy_id'] = deploy_id
        return ctx


class DeployView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        ctx.update(Deploy.get_args_choices())
        return self.render_to_response(ctx)


class DeployProdView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        flags = request.POST.getlist('flags')
        user = request.user
        deploy = Deploy.begin(user=user, action='deploy_prod', flags=flags)

        return HttpResponseRedirect(
            reverse('deploy_log_view', args=(deploy.pk,))
        )


class DeployCeleryView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        flags = request.POST.getlist('flags')
        user = request.user
        deploy = Deploy.begin(user=user, action='deploy_celery', flags=flags)

        return HttpResponseRedirect(
            reverse('deploy_log_view', args=(deploy.pk,))
        )

