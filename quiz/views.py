from rest_framework import generics
from django.db.models import Q

from quiz.throttling import CustomRateThrottle
from .models import  FriendRequest, Userkap
from .serializers import FriendRequestSerializer, UserkapSerializer
from email.message import EmailMessage
import smtplib
import ssl
from django.contrib.auth import authenticate
from rest_framework import generics, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SignUpSerializer
from .tokens import create_jwt_pair_for_user
from rest_framework.permissions import IsAuthenticated, AllowAny    
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import Http404, HttpResponse, JsonResponse
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from  quiz.authentication import DjangoUserAuthentication
from rest_framework import viewsets
from rest_framework.response import Response

import secrets
import requests
# from adrf import generics
# from asgiref import sync_to_async
import asyncio
from django.core.cache import cache




class SignUpView(generics.GenericAPIView):
    # throttle_classes = [CustomRateThrottle]
    serializer_class = SignUpSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = []

    def post(self, request: Request):
        data = request.data

        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.save()

            response = {"message": "User Created Successfully", "data": serializer.data}

            return Response(data=response, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [] 

    def post(self, request: Request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(username=email, password=password)
        
        if user is not None:

            tokens = create_jwt_pair_for_user(user)

            response = {"message": "Login Successfull", "tokens": tokens}
            return Response(data=response, status=status.HTTP_200_OK)

        else:
            return Response(data={"message": "Invalid email or password"})

    def get(self, request: Request):
        content = {"user": str(request.user), "auth": str(request.auth)}

        return Response(data=content, status=status.HTTP_200_OK)
    
class UserkapListCreateAPIView(generics.ListAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Userkap.objects.all()
    serializer_class = UserkapSerializer

class UserkapDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Userkap.objects.all()
    serializer_class = UserkapSerializer

class FriendRequestCreateAPIView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        receiver_id = self.request.data.get('receiver_id')
        if receiver_id is None:
            return Response({"error": "Receiver ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            receiver = Userkap.objects.get(id=receiver_id)
        except Userkap.DoesNotExist:
            raise Http404("Receiver user does not exist")
        
        # Set the sender to the authenticated user
        serializer.save(sender=self.request.user, receiver=receiver)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        friend_request_data = response.data
        message = "Friend request sent successfully."
        return Response({"message": message, "friend_request": friend_request_data}, status=response.status_code)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
# class EmailAPIView(APIView):
#     authentication_classes = [BasicAuthentication]
#     permission_classes = [IsAuthenticated]
#     def get(self, request):
#         emsender = 'Abhinaysingh6324@gmail.com'
#         empassword = 'vebd xvch pkxo zuxc'
        
        
#         product_id = request.query_params.get('product_id')
#         emreceiver = request.query_params.get('emreceiver')
#         product_name = request.query_params.get('article_title')
#         product_link = request.query_params.get('article_link')
#         subject = f'Rejected Article: {product_name}: Please review again'
#         body = (
#             f"Hi Writer,\n\nPlease review the article with id = {product_id} at the link = {product_link}"
#             f"and submit it for review to the proofreader.\nThanks and Regards\n Admin."
#         )

#         em = EmailMessage()
#         em['From'] = emsender
#         em['To'] = emreceiver
#         em['Subject'] = subject
#         em.set_content(body)
#         print("email")
#         context = ssl.create_default_context()

#         try:
#             with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
#                 smtp.login(emsender, empassword)
#                 smtp.sendmail(emsender, emreceiver, em.as_string())
                
            
#             full_email = {
#                 'From': em['From'],
#                 'To': em['To'],
#                 'Subject': em['Subject'],
#                 'Content': em.get_content()
#             }
#             return Response({'message': 'Email sent successfully!', 'email_format': full_email})
#         except Exception as e:
#             return Response({'error': str(e)}, status=500)
    
class FriendRequestListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = FriendRequestSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
       
        serializer.save(sender=self.request.user)

    def get_queryset(self):
       
        return FriendRequest.objects.filter(sender=self.request.user)

class SentRequestAcceptedListAPIView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        
        user = self.request.user
        return FriendRequest.objects.filter(is_accepted=True).filter(sender=self.request.user)

class SentRequestPendingListAPIView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        
        user = self.request.user
        return FriendRequest.objects.filter(is_accepted=False).filter(sender=self.request.user)

class RecievedRequestAcceptedListAPIView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
       
        user = self.request.user
        return FriendRequest.objects.filter(is_accepted=True).filter(receiver=self.request.user)

class RecivedRequestPendingListAPIView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        
        user = self.request.user
        return FriendRequest.objects.filter(is_accepted=False).filter(receiver=self.request.user)

class UserSearchAPIView(generics.ListAPIView):
    serializer_class = UserkapSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        keyword = self.request.query_params.get('keyword', '')
        if '@' in keyword:  
            return Userkap.objects.filter(email__icontains=keyword)
        else:
            return Userkap.objects.filter(Q(username__icontains=keyword) | Q(email__icontains=keyword))

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AcceptFriendRequestAPIView(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        
        sender_pk = self.kwargs.get('sender_pk')
        return FriendRequest.objects.filter(receiver=self.request.user, sender_id=sender_pk, is_accepted=False).first()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            instance.is_accepted = True
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response({"message": "No pending friend request found from the specified sender"}, status=status.HTTP_404_NOT_FOUND)

class RejectFriendRequestAPIView(generics.DestroyAPIView):
    queryset = FriendRequest.objects.all()
    serializer_class = FriendRequestSerializer
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    def destroy(self, request, *args, **kwargs):
        sender_pk = kwargs.get('sender_pk')
        
        friend_request = self.get_queryset().filter(sender_id=sender_pk, receiver=request.user).first()
        
        if friend_request:
            friend_request.delete()
            return Response({"message": "Friend request rejected successfully."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "Friend request not found."}, status=status.HTTP_404_NOT_FOUND)