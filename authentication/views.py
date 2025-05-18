from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from twilio.rest import Client
from .models import CustomUser
from rest_framework.authtoken.models import Token
from django.conf import settings
from django.db import IntegrityError

from django.core import signing

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication


twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

class RegistrationView(APIView):
    def post(self, request):
        data = request.data
        
        if data['password'] != data['confirm_password']:
            return Response({"error": "Les mots de passe ne correspondent pas"}, status=400)
        
        try:
            user = CustomUser.objects.create_user(
                phone_number=data['phone_number'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name']
            )
        except IntegrityError:
            return Response({"error": "Ce numéro de téléphone est déjà utilisé"}, status=400)

        try:
            verification = twilio_client.verify.v2.services(settings.TWILIO_SERVICE_SID) \
                .verifications \
                .create(to=data['phone_number'], channel='sms')
        except Exception as e:
            user.delete()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"message": "Code de vérification envoyé"}, status=status.HTTP_201_CREATED)

class VerificationView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        code = request.data.get('code')
        
        try:
            verification_check = twilio_client.verify.v2.services(settings.TWILIO_SERVICE_SID) \
                .verification_checks \
                .create(to=phone_number, code=code)
            
            if verification_check.status == 'approved':
                user = CustomUser.objects.get(phone_number=phone_number)
                user.is_verified = True
                user.save()
                
                # Génération du token de connexion automatique
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    "message": "Compte vérifié et connecté avec succès",
                    "token": token.key,
                    "user_id": user.id
                }, status=status.HTTP_200_OK)
                
            return Response({"error": "Code invalide"}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class LoginView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        
        user = authenticate(phone_number=phone_number, password=password)
        
        if not user:
            return Response({"error": "Identifiants invalides"}, status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_verified:
            return Response({"error": "Compte non vérifié"}, status=status.HTTP_401_UNAUTHORIZED)
        
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key}, status=status.HTTP_200_OK)
    


class PasswordResetRequestView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        
        try:
            user = CustomUser.objects.get(phone_number=phone_number)
        except CustomUser.DoesNotExist:
            return Response({"error": "Aucun compte associé à ce numéro"}, status=400)
        
        try:
            verification = twilio_client.verify.v2.services(settings.TWILIO_SERVICE_SID) \
                .verifications \
                .create(to=phone_number, channel='sms')
            return Response({"message": "Code de réinitialisation envoyé"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class PasswordResetVerifyConfirmView(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        code = request.data.get('code')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # Vérification du mot de passe
        if new_password != confirm_password:
            return Response({"error": "Les mots de passe ne correspondent pas"}, status=400)
        
        # Vérification du code Twilio
        try:
            verification_check = twilio_client.verify.v2.services(settings.TWILIO_SERVICE_SID) \
                .verification_checks \
                .create(to=phone_number, code=code)
            
            if verification_check.status != 'approved':
                return Response({"error": "Code invalide ou expiré"}, status=400)
                
            # Mise à jour du mot de passe
            user = CustomUser.objects.get(phone_number=phone_number)
            user.set_password(new_password)
            user.save()
            
            return Response({"message": "Mot de passe réinitialisé avec succès"}, status=200)
            
        except Exception as e:
            return Response({"error": str(e)}, status=400)
        

class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Supprime le token de l'utilisateur
            request.user.auth_token.delete()
            return Response({"message": "Déconnexion réussie"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)