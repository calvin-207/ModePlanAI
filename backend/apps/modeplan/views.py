import datetime
import traceback
import uuid
import json

import django_filters
from django.db.models import Q
from django.http import StreamingHttpResponse
from openai import OpenAI
from rest_framework import serializers

from utils.filters import filter_day_combine_time
from utils.serializers import CustomModelSerializer
from utils.viewset import CustomModelViewSet
from .models import MConversationLog, MConversation
from django.conf import settings
from rest_framework.permissions import IsAuthenticated

from utils.apiview import CustomAPIView
from utils.jsonResponse import DetailResponse, ErrorResponse, SuccessResponse
from utils.jwt_auth import JWTAuthentication

class ChatAPIView(CustomAPIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


    def post(self, request, *args, **kwargs):
        system_user = request.user.system_user
        try:
            data = request.body.decode('utf-8')
            data = json.loads(data)
            prompt = data.get("question")
            conversation_id = data.get("conversation_id")

            if not prompt:
                return ErrorResponse({'error': 'Prompt is required'}, msg='请输入您的问题？')


            client = OpenAI(api_key=settings.DEEPSEEK_KEY, base_url="https://api.deepseek.com")
            messages = []
            bulk_create_logs = []
            if conversation_id:
                mConversation = MConversation.objects.get(code=conversation_id)
                # 这里要执行清楚动作。
                MConversationLog.objects.filter(Q(mConversation=mConversation) & Q(ltype='request'))

            else:
                conversation_id = uuid.uuid4().hex
                mConversation = MConversation.objects.create(code=conversation_id, creator=system_user)

                beginMConversationLog=MConversationLog(
                    role = 'system',
                    meno='text',
                    mConversation=mConversation,
                    ltype='request',
                    begin_time=datetime.datetime.now(),
                )
                bulk_create_logs.append(beginMConversationLog)
                messages.append({"role": "user", "content": prompt})

            reqMConversationLog = MConversationLog(
                meno=prompt,
                mConversation=mConversation,
                ltype='request',
                role='user',
                begin_time=datetime.datetime.now(),
            )

            messages.append({"role": "user", "content": prompt})



            bulk_create_logs.append(reqMConversationLog)
            respMConversationLog = MConversationLog(mConversation=mConversation, ltype='response',begin_time=datetime.datetime.now())
            bulk_create_logs.append(respMConversationLog)

            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                stream=True,
            )
            result_content = []
            def generate_response():

                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        result_content.append(content)
                        res = ''.join(result_content)
                        jsonData = json.dumps(dict(answer = f"{res}", conversation_id=mConversation.code))
                        # print('jsonData', jsonData)
                        yield f"""{jsonData}\r\n"""
                else:
                    respMConversationLog.meno=''.join(result_content)
                    respMConversationLog.end_time=datetime.datetime.now()
                    # print('这个是执行写入动作的！')
                    MConversationLog.objects.bulk_create(bulk_create_logs)
            return StreamingHttpResponse(generate_response(), content_type='application/x-ndjson')
        except Exception as e:
            traceback.print_exc()
            return ErrorResponse(msg=str(e))





class MConversationSerializer(CustomModelSerializer):

    messages = serializers.SerializerMethodField(read_only=True)

    def get_messages(self, obj):
        serializer = MConversationLogSerializer(MConversationLog.objects.filter(Q(mConversation=obj) & Q(ltype=MConversationLog.LTYPE.REQUEST)).order_by('-id').first())
        return [serializer.data]

    class Meta:
        model = MConversation
        read_only_fields = ["id", 'editing']
        fields = '__all__'


class MConversationFilterSet(django_filters.rest_framework.FilterSet):
    #开始时间
    beginAt = django_filters.DateTimeFilter(field_name='create_datetime', lookup_expr='gte')  # 指定过滤的字段
    #结束时间
    endAt = django_filters.DateTimeFilter(field_name='create_datetime', method=filter_day_combine_time)
    name = django_filters.CharFilter(field_name='name',lookup_expr='icontains')
    stop_flag = django_filters.CharFilter(field_name='stop_flag',lookup_expr='icontains')
    auto_work_flag = django_filters.CharFilter(field_name='auto_work_flag',lookup_expr='icontains')

    class Meta:
        model = MConversation
        fields = ['beginAt', 'endAt', 'name', 'stop_flag', 'deleting']


class MConversationsViewSet(CustomModelViewSet):
    queryset = MConversation.objects.filter()
    serializer_class = MConversationSerializer
    filterset_class = MConversationFilterSet
    permission_classes = [IsAuthenticated]
    extra_filter_backends = []
    http_method_names = ['get', 'head', 'options','delete', 'put']

    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = self.filter_queryset(self.get_queryset()).filter(creator=user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, request=request)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(data=serializer.data, msg="获取成功")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object_list()
        for it in instance:
            it.deleting = True
            it.save()
        return DetailResponse(data=[], msg="删除成功")

class MConversationLogFilterSet(django_filters.rest_framework.FilterSet):
    #开始时间
    beginAt = django_filters.DateTimeFilter(field_name='create_datetime', lookup_expr='gte')  # 指定过滤的字段
    #结束时间
    endAt = django_filters.DateTimeFilter(field_name='create_datetime', method=filter_day_combine_time)
    name = django_filters.CharFilter(field_name='name',lookup_expr='icontains')
    code = django_filters.CharFilter(field_name='mConversation__code')
    stop_flag = django_filters.CharFilter(field_name='stop_flag',lookup_expr='icontains')
    auto_work_flag = django_filters.CharFilter(field_name='auto_work_flag',lookup_expr='icontains')

    class Meta:
        model = MConversationLog
        fields = ['beginAt', 'endAt', 'name', 'stop_flag', 'auto_work_flag', 'code']


class MConversationLogSerializer(CustomModelSerializer):
    class Meta:
        model = MConversationLog
        read_only_fields = ["id"]
        fields = '__all__'

class MConversationsLogViewSet(CustomModelViewSet):
    queryset = MConversationLog.objects.filter()
    serializer_class = MConversationLogSerializer
    filterset_class = MConversationLogFilterSet
    permission_classes = [IsAuthenticated]
    extra_filter_backends = []

