import os
import json
import logging

from django.db import models
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

USER = "ubuntu"


class Deploy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=32)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    args = models.TextField()

    @classmethod
    def begin(cls, user, action, flags):
        obj = cls.objects.create(user=user, action=action, args=json.dumps(flags))
        if action == "deploy_prod":
            obj.trigger_deployment_prod()
        elif action == "deploy_celery":
            obj.trigger_deployment_celery()
        return obj

    def trigger_deployment_prod(self):
        args = self.clean_args_prod(json.loads(self.args))
        flags = " ".join(args)

        cmd = "python3.7 -u {squadrun_home}/deploy.py {flags} > {logfile}".format(
            logfile=self.get_logfile_path(),
            flags=flags,
            squadrun_home=f"/home/{USER}/squadrun",
        )
        logger.warn("running cmd: {}".format(cmd))
        os.chdir(f"/home/{USER}/squadrun/")
        os.system(cmd)

    def trigger_deployment_celery(self):
        cmd = "python3.7 -u {squadrun_home}/deploy.py --only-celery > {logfile}".format(
            logfile=self.get_logfile_path(),
            squadrun_home=f"/home/{USER}/squadrun",
        )
        logger.warn("running cmd: {}".format(cmd))
        os.chdir(f"/home/{USER}/squadrun/")
        os.system(cmd)

    def get_logfile_path(self) -> str:
        return f"/home/{USER}/deploylogs/{self.pk}.log"

    @staticmethod
    def get_args_choices():
        return {
            "flag_prod_choices": {
                "run_migration",
                "reread_supervisor",
                "deploy_biz",
                "skip_cache_invalidation",
                "run_compress",
            },
            "flag_celery_choices": set([]),
        }

    @classmethod
    def clean_args_prod(cls, flags):
        args = []
        if "reread_supervisor" in flags:
            args.append("--reread")

        if "run_compress" in flags:
            args.append("--compress")

        if "run_migration" in flags:
            args.append("--migrate")

        if "skip_cache_invalidation" in flags:
            args.append("--skip-cache-invalidation")

        if "deploy_biz" in flags:
            args.append("--include-biz")

        return args
