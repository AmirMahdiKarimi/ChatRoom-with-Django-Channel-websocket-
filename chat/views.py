from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as dj_login, logout as dj_logout
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView, CreateAPIView, ListAPIView, DestroyAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from channels.layers import get_channel_layer
from .serializers import LoginSerializer, GPCreateSerializer, GPListSerializer, GPDestroySerializer, SendMessageSerializer
from .models import Group, CustomUser, Message

def lobby(request):
    if request.user.is_authenticated:
        groups = Group.objects.values_list('name', flat=True)
        data = {'groups_detail': []}
        for gp in groups:
            channel_layer = get_channel_layer()
            online_members = channel_layer.groups.get(f'chat_{gp}', {}).items()
            data['groups_detail'].append({'name': gp, 'count': len(online_members)})
        return render(request, "chat/lobby.html", data)
    data = {
        'message': "Login first! ",
        'redirect_url': reverse('login')
    }
    return render(request, 'auth/fail_auth.html', data)

def room(request, room_name):
    if request.user.is_authenticated:
        return render(request, "chat/room.html", {"room_name": room_name})
    data = {
        'message': "Login first! ",
        'redirect_url': reverse('login')
    }
    return render(request, 'auth/fail_auth.html', data)
    

class LoginAPIView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user:
            dj_login(request, user)
            data = {
                'redirect_url': reverse('chat')
            }
            return redirect(reverse('chat'))
        return Response({'error': 'Invalid credentials'}, status=403)
    

class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated, )
    

    def get(self, request):
        dj_logout(request)
        data={'message': "Logged out succesfuly.", 'redirect_url': reverse('login')}
        status = 200

        return Response(data=data, status=status)


class GPCreateAPIView(CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = GPCreateSerializer


class GPListAPIView(ListAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = GPListSerializer
    queryset = Group.objects.all()


class GPDestroyAPIView(DestroyAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = GPDestroySerializer
    queryset = Group.objects.all()
    
    def get(self, request, *args, **kwargs):
        name = request.query_params.get('name')
        if name:
            try:
                group = Group.objects.get(name=name)
                group.delete()
                return Response({'message': 'Group deleted successfully.'}, status=200)
            except Group.DoesNotExist:
                return Response({'message': 'Group not found.'}, status=404)
        else:
            return Response({'message': 'Invalid request. Name parameter is required.'}, status=400)


class SendMessageCreateAPIView(CreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = SendMessageSerializer

    