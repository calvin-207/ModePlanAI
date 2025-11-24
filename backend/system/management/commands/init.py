import logging
from tkinter.constants import S

from django.core.management.base import BaseCommand
from django_tenants.utils import tenant_context
from tenants.models import Client

from main import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    项目初始化命令: python manage.py init
    """

    def add_arguments(self, parser):
        print(parser)
        parser.add_argument(
            "schema_name",
            nargs="*",
            type=str,
        )
        parser.add_argument("-y", nargs="*")
        parser.add_argument("-Y", nargs="*")
        parser.add_argument("-n", nargs="*")
        parser.add_argument("-N", nargs="*")

    def handle(self, *args, **options):
        schema_name = options.get('schema_name')
        if not schema_name or len(schema_name) == 0:
            print('请输入数据库schema_name')
            return 
        else:
            code = schema_name[0]
            if len(code) <= 2:
                print('schema_name长度不能小于3')
                return 
        client = Client.objects.filter(code=code)
        if not client.exists():
            client = Client(name=code, schema_name=code, code=code)
            client.save()
        with tenant_context(Client.objects.get(code=code)):
            is_delete = False
            if isinstance(options.get("y"), list) or isinstance(options.get("Y"), list):
                is_delete = True
            if isinstance(options.get("n"), list) or isinstance(options.get("N"), list):
                is_delete = False
            print(
                f"正在准备初始化数据，{'如有初始化数据，将会不做操作跳过' if not is_delete else '初始数据将会先删除后新增'}..."
            )

            for app in settings.INSTALLED_APPS:
                try:
                    exec(f"""
from {app}.initialize import main
main(is_delete={is_delete})
                    """)
                except ModuleNotFoundError:
                    pass
            print("初始化数据完成！")
