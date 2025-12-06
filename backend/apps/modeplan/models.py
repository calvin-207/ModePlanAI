from django.db import models
from utils.models import CoreModel,BaseModel

class MConversation(CoreModel):
    """
    店铺信息
    """
    code = models.CharField(verbose_name="会话编码", max_length=32, unique=True, db_index=True)
    name = models.CharField(verbose_name="会话名称", max_length=32, blank=True, null=True)
    deleting = models.BooleanField(verbose_name='是否删除', default=False)
    editing = models.BooleanField(verbose_name='是否编辑中', default=False)

    class Meta:
        ordering = ['-create_datetime']
        db_table = "ai_conversations"
        verbose_name = "AI会话"
        verbose_name_plural = verbose_name

class MConversationLog(CoreModel):

    class LTYPE:

        REQUEST = 'request'
        RESPONSE = 'response'

    begin_time = models.DateTimeField(null=True, blank=True, help_text="生产时间", verbose_name="生产时间")
    end_time = models.DateTimeField(null=True, blank=True, help_text="结束时间", verbose_name="结束时间")
    mConversation = models.ForeignKey(MConversation, verbose_name='会话信息', on_delete=models.CASCADE)
    role = models.CharField(verbose_name='角色', max_length=32, blank=True, null=True)
    ltype = models.CharField(verbose_name='会话类型', max_length=32, blank=True, null=True)
    meno = models.TextField(verbose_name="会话内容")

    class Meta:
        db_table = "ai_conversations_logs"
        verbose_name = "AI会话记录"
        ordering = ['-create_datetime']
        verbose_name_plural = verbose_name
