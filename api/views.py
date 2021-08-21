from django.contrib.auth.models import User
from api.serializers import ChatRecordsSerializer, UserChannelsSerializer, AllChannelSerializer
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework import status
from users.models import UserChatRecords,UserChannels, FriendChannels, AllChannels
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
import random, string


class UsersChatRecoredsViewSet(viewsets.ModelViewSet):
    permission_classes = ''
    authentication_classes = ''
    queryset = UserChatRecords.objects.all()
    serializer_class = ChatRecordsSerializer

    def retrieve(self, request, *args, **kwargs):
        # pk --> userId
        userId = kwargs['pk']
        userChatObj = UserChatRecords.objects.filter(user = userId).first()
        serializer = ChatRecordsSerializer(userChatObj)
        message = 'Data Successfully fetched'
        if not serializer.data:
            message = "No User Found"
        responseData = {
            'message': message,
            'data': serializer.data,
            'error': None
        }
        return Response(responseData, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        userId = request.data['user']
        user = UserChatRecords.objects.filter(user=userId).first()

        if (user):
            serializer = ChatRecordsSerializer(user)
            return Response(serializer.data)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class UserChannelsViewSet(viewsets.ModelViewSet):
    queryset = UserChannels.objects.all()
    serializer_class = UserChannelsSerializer
    permission_classes = ''
    authentication_classes = ''


    def retrieve(self, request, *args, **kwargs):
        instance = UserChannels.objects.filter(user_id=kwargs['pk']).first()
        serializer = self.get_serializer(instance)
        message = 'Data Successfully fetched'
        if not serializer.data['user']:
            message = "No User Found"
        responseData = {
            'message' : message,
            'data': serializer.data,
            'error' : None
        }
        return Response(responseData,  status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        response = super(UserChannelsViewSet, self).create(request, args, kwargs)
        message = 'Channel Successfully created'

        responseData = {
            'message': message,
            'data': response.data,
            'error': None
        }
        return Response(responseData, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        response = super(UserChannelsViewSet, self).list(request, args, kwargs)
        message = 'Data Successfully fetched'

        responseData = {
            'message': message,
            'data': response.data,
            'error': None
        }
        return Response(responseData, status=status.HTTP_200_OK)


class GetChannelNameViewSet(APIView):
    permission_classes = ''
    authentication_classes = ''

    def get(self, request, *args, **kw):

        condition = True
        result=None

        while condition:
            result = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            condition = FriendChannels.objects.filter(channel=result).exists()

        responseData = {
            'message': 'Channel Name Successfully Created.',
            'data': {'name':result},
            'error': None
        }
        return Response(responseData, status=status.HTTP_200_OK)

class UserDetailsViewSet(APIView):
    permission_classes = ''
    authentication_classes = ''

    def get(self, request, *args, **kw):
        myUsername = request.GET.get('username')
        arg_1 = request.GET.get('id')
        friendUserName = request.GET.get('friendUserName', None)

        message = 'Invalid or missing username.'
        data = {}

        if arg_1:
            if friendUserName:
                UserChannelInstance = UserChannels.objects.filter(user_id=arg_1).first()
                print(UserChannelInstance)
            message = 'User Found'
            user = User.objects.get(id = arg_1)

            data = {
                'id':user.id,
                'first_name' : user.first_name,
                'last_name' : user.last_name,
                'username': user.username
            }

        elif isinstance(myUsername, str):
            user = User.objects.get_by_natural_key(myUsername)
            if friendUserName:
                friend = User.objects.get_by_natural_key(friendUserName)

                UserChannelInstance = UserChannels.objects.filter(
                    user=user, friend__user = friend
                ).values(
                    'id', 'user_id', 'user__username', 'friend__user__username', 'friend__channel'
                ).first()

                data = {
                    'message': "UserDetails Successfully fetched",
                    'data': UserChannelInstance,
                    'error': None,
                }

                # AllChannelsViewSet.formatData(self, UserChannelInstance, message)
                return Response(data, status=status.HTTP_200_OK)

            message = 'User Details Successfully fetched'
            data = {'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'username': user.username}

        responseData = {
            'message': message,
            'data': data,
            'error': None
        }
        return Response(responseData, status=status.HTTP_200_OK)


class AllChannelsViewSet(viewsets.ModelViewSet):
    authentication_classes = ''
    permission_classes = ''

    queryset = AllChannels.objects.all()
    serializer_class = AllChannelSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        message = 'Data Retrieved Successfully'
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            responseData = self.formatData(serializer.data, message)
            return self.get_paginated_response(responseData)

        serializer = self.get_serializer(queryset, many=True)
        responseData = self.formatData(serializer.data, message)

        return Response(responseData)

    def formatData(self, data, message):
        if not data:
            message = "No Data Found"
        responseData = {
            'message': message,
            'data': data,
            'error': None
        }
        return responseData

    def retrieve(self, request, *args, **kwargs):

        queryset = AllChannels.objects.filter(users__user =kwargs['pk'])
        serializer = AllChannelSerializer(queryset, many=True)
        message = 'Data Retrieved Successfully'
        if not serializer.data:
            message = "No Data Found"
        responseData = {
            'message': message,
            'data': serializer.data,
            'error': None
        }
        return Response(responseData, status=status.HTTP_201_CREATED)


    def create(self, request, *args, **kwargs):
        response = super(AllChannelsViewSet, self).create(request, args, kwargs)
        message = 'Channel Successfully created'

        responseData = {
            'message': message,
            'data': response.data,
            'error': None
        }
        return Response(responseData, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        qs = AllChannels.objects.filter(id=kwargs['pk']).first()
        message = 'No Data Found'
        response = {}
        userId = int(request.GET.get('userId', None))
        if qs:
            if (qs.createdBy.id == userId or qs.createdBy.id == request.user.id):
                response = super(AllChannelsViewSet, self).update(request, args, kwargs).data
                message = 'Channel Successfully Updated'
            else:
                message = 'You are not allowed to perform this action'

        responseData = {
            'message': message,
            'data': response,
            'error': None
        }
        return Response(responseData, status=status.HTTP_201_CREATED)