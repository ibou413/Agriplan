from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny

from django.utils import timezone
from rest_framework import viewsets

from farm_management.models import Farm
from .serializers import NotificationLogSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from datetime import timedelta

from django.utils import timezone
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message
from .models import CalendrierCulture
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from .models import CalendrierCulture, NotificationLog

from .serializers import (
    CultureSerializer, VarieteSerializer, FertilisationSerializer,
    TraitementPhytosanitaireSerializer, EtapeCultureSerializer,
    ParcelleSerializer, CalendrierCultureSerializer
)

from users.models import CustomUser
User= CustomUser
from rest_framework import viewsets
from .models import (
    Culture, Variete, Fertilisation, TraitementPhytosanitaire,
    ProduitPhytosanitaire, EtapeCulture, Parcelle, CalendrierCulture,
)
from .serializers import (
    CultureSerializer, VarieteSerializer, FertilisationSerializer,
    TraitementPhytosanitaireSerializer, ProduitPhytosanitaireSerializer,
    EtapeCultureSerializer, ParcelleSerializer, CalendrierCultureSerializer,
    NotificationLogSerializer
)

from django.utils import timezone
from .models import CalendrierCulture

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from fcm_django.models import FCMDevice
from rest_framework import status


# Exemple d'API très simple avec Django REST Framework
from rest_framework import serializers, viewsets
from fcm_django.models import FCMDevice





class CultureViewSet(viewsets.ModelViewSet):
    queryset = Culture.objects.all()
    serializer_class = CultureSerializer

class VarieteViewSet(viewsets.ModelViewSet):
    queryset = Variete.objects.all()
    serializer_class = VarieteSerializer

class FertilisationViewSet(viewsets.ModelViewSet):
    queryset = Fertilisation.objects.all()
    serializer_class = FertilisationSerializer

class TraitementPhytosanitaireViewSet(viewsets.ModelViewSet):
    queryset = TraitementPhytosanitaire.objects.all()
    serializer_class = TraitementPhytosanitaireSerializer

class ProduitPhytosanitaireViewSet(viewsets.ModelViewSet):
    queryset = ProduitPhytosanitaire.objects.all()
    serializer_class = ProduitPhytosanitaireSerializer

class EtapeCultureViewSet(viewsets.ModelViewSet):
    queryset = EtapeCulture.objects.all()
    serializer_class = EtapeCultureSerializer

class ParcelleViewSet(viewsets.ModelViewSet):
    queryset = Parcelle.objects.all()
    serializer_class = ParcelleSerializer
    def get_queryset(self):
        queryset = super().get_queryset()
        farm_id = self.request.query_params.get('farm_id')
        if farm_id:
            queryset = queryset.filter(farm__id=farm_id)
        return queryset

class CalendrierCultureViewSet(viewsets.ModelViewSet):
    queryset = CalendrierCulture.objects.all()
    serializer_class = CalendrierCultureSerializer



class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NotificationLog.objects.all()
    serializer_class = NotificationLogSerializer

    def get_queryset(self):
        farm_id = self.request.query_params.get('farm_id')
        queryset = NotificationLog.objects.all()
        if farm_id:
            queryset = queryset.filter(farm_id=farm_id)
        return queryset.order_by('-date_envoi')



class PlanificationAutomatiqueAPIView(APIView):
    ALERTE_JOURS_AVANT = 3  # délai avant envoi de notification

    def post(self, request):
        try:
            # 1. Données reçues
            culture_nom = request.data.get("culture")
            variete_nom = request.data.get("variete")
            surface = float(request.data.get("surface_ha"))
            date_plantation = parse_date(request.data.get("date_plantation"))
            type_culture = request.data.get("type_culture")
            saison = request.data.get("saison")
            farm_id = request.data.get("farm_id")

            # 2. Recherche de la culture et variété
            culture = get_object_or_404(Culture, nom__iexact=culture_nom)
            variete = get_object_or_404(Variete, nom__iexact=variete_nom, culture=culture)

            # 3. Calculs techniques
            rendement_min = culture.rendement_min_t_ha or 0
            rendement_max = culture.rendement_max_t_ha or 0
            semence_ha = culture.quantite_semence_g_ha or 0

            rendement_estime = {
                "min": round(rendement_min * surface, 2),
                "max": round(rendement_max * surface, 2)
            }
            semences_necessaires = round(semence_ha * surface, 2)

            # 4. Récupération des plans associés
            fertilisations = Fertilisation.objects.filter(variete=variete)
            traitements = TraitementPhytosanitaire.objects.filter(variete=variete)
            etapes = EtapeCulture.objects.filter(culture=culture)

            # 5. Création de la parcelle
            parcelle = Parcelle.objects.create(
                farm_id=farm_id,
                variete=variete,
                date_plantation=date_plantation,
                surface_ha=surface,
                type_culture=type_culture,
                saison=saison,
                rendement_min=rendement_estime["min"],
                rendement_max=rendement_estime["max"],
                semences_necessaires_g=semences_necessaires
            )
            parcelle.fertilisations.set(fertilisations)
            parcelle.traitements.set(traitements)
            parcelle.etapes.set(etapes)

            # 6. Génération du calendrier + notifications
            calendrier = []

            # Étapes
            for etape in etapes:
                date_prevue = date_plantation + timedelta(days=etape.delai_apres_plantation)
                calendrier_entry = CalendrierCulture.objects.create(
                    parcelle=parcelle,
                    etape=etape,
                    date_prevue=date_prevue
                )
               
                calendrier.append(calendrier_entry)

            # Fertilisations
            for ferti in fertilisations:
                date_prevue = date_plantation + timedelta(days=ferti.jour)
                calendrier_entry = CalendrierCulture.objects.create(
                    parcelle=parcelle,
                    fertilisation=ferti,
                    date_prevue=date_prevue
                )
                calendrier.append(calendrier_entry)

            # Traitements
            for trt in traitements:
                date_prevue = date_plantation + timedelta(days=trt.jour)
                calendrier_entry = CalendrierCulture.objects.create(
                    parcelle=parcelle,
                    traitement=trt,
                    date_prevue=date_prevue
                )
                
                calendrier.append(calendrier_entry)

            # 7. Réponse
            data = {
                "parcelle": ParcelleSerializer(parcelle).data,
                "culture": CultureSerializer(culture).data,
                "variete": VarieteSerializer(variete).data,
                "fertilisation": FertilisationSerializer(fertilisations, many=True).data,
                "traitements": TraitementPhytosanitaireSerializer(traitements, many=True).data,
                "etapes": EtapeCultureSerializer(etapes, many=True).data,
                "calendrier": CalendrierCultureSerializer(calendrier, many=True).data
            }
            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_cultures(request):
    cultures = Culture.objects.all()
    return Response(CultureSerializer(cultures, many=True).data)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_varietes_by_culture(request, culture_id):
    varietes = Variete.objects.filter(culture_id=culture_id)
    return Response(VarieteSerializer(varietes, many=True).data)


def construire_message(evenement):
    if evenement.etape:
        action = f"Étape : {evenement.etape.nom}"
    elif evenement.fertilisation:
        action = f"Fertilisation : {evenement.fertilisation.type_engrais}"
    elif evenement.traitement:
        action = f"Traitement : {evenement.traitement.type_traitement}"
    else:
        action = "Tâche planifiée"
    return f"📅 {action} prévue aujourd'hui sur la parcelle : {evenement.parcelle.variete.nom}"


def get_image_url(obj, field_name="image"):
    image = getattr(obj, field_name, None)
    if image:
        if hasattr(image, 'url'):
            return image.url
    return None

def construire_data_payload(evenement):
    parcelle = evenement.parcelle
    variete = parcelle.variete

    data = {
        "evenement_id": str(evenement.id),
        "date_prevue": str(evenement.date_prevue),
        "commentaire": evenement.commentaire or "",
        "parcelle": {
            "id": str(parcelle.id),
            "surface_ha": parcelle.surface_ha,
            "type_sol": parcelle.type_sol,
            "climat": parcelle.climat,
            "type_culture": parcelle.type_culture,
            "saison": parcelle.saison,
            "image_url": get_image_url(parcelle, "image_url"),  # si tu as le champ
        },
        "variete": {
            "id": str(variete.id),
            "nom": variete.nom,
            "distance_plantation": variete.distance_plantation,
            "rendement_min": variete.rendement_min,
            "rendement_max": variete.rendement_max,
            "periode_culture": variete.periode_culture,
            "besoins_eau": variete.besoins_eau,
            "image_url": get_image_url(variete)
        },
        "type_evenement": None,
        "details_evenement": None
    }

    if evenement.etape:
        etape = evenement.etape
        data["type_evenement"] = "etape"
        data["details_evenement"] = {
            "id": str(etape.id),
            "nom": etape.nom,
            "description": etape.description,
            "frequence": etape.frequence,
            "delai_apres_plantation": etape.delai_apres_plantation,
            "image_url": get_image_url(etape)
        }

    elif evenement.fertilisation:
        fertilisation = evenement.fertilisation
        data["type_evenement"] = "fertilisation"
        data["details_evenement"] = {
            "id": str(fertilisation.id),
            "jour": fertilisation.jour,
            "type_engrais": fertilisation.type_engrais,
            "dose_ha": fertilisation.dose_ha,
            "mode_application": fertilisation.mode_application or "",
            "image_url": get_image_url(fertilisation, "illustration")
        }

    elif evenement.traitement:
        traitement = evenement.traitement
        produit = traitement.produit
        data["type_evenement"] = "traitement"
        data["details_evenement"] = {
            "id": str(traitement.id),
            "jour": traitement.jour,
            "type_traitement": traitement.type_traitement,
            "cible": traitement.cible,
            "matiere_active": traitement.matiere_active or "",
            "image_url": get_image_url(traitement, "illustration"),
            "produit": {
                "id": str(produit.id) if produit else None,
                "nom_commercial": produit.nom_commercial if produit else "",
                "matiere_active": produit.matiere_active if produit else "",
                "type_produit": produit.type_produit if produit else "",
                "image_url": get_image_url(produit) if produit else None
            } if produit else None
        }

    else:
        data["type_evenement"] = "tache_planifiee"
        data["details_evenement"] = {}

    return data


def envoyer_notification_user(user, message_text, image_url=None, data_payload=None):
    device = FCMDevice.objects.filter(user=user).first()
    if not device:
        print(f"[LOG] Aucun device FCM pour user {user.email}")
        return False, [f"Aucun device FCM enregistré pour l'utilisateur {user.email}"]

    erreurs = []
    notifications_envoyees = 0

    try:
        # Construire la notification Firebase correctement (pas de **kwargs)
        notif_args = {
            "title": "📢 Alerte Culture",
            "body": message_text,
        }
        if image_url:
            notif_args["image"] = image_url

        notif = Notification(**notif_args)

        message = Message(
            notification=notif,
            token=device.registration_id,
            data={k: str(v) for k, v in data_payload.items()} if data_payload else None,
        )

        response = device.send_message(message)
        notifications_envoyees += 1
        print(f"[LOG] Notification envoyée au device {device.id} de user {user.email} (response: {response})")

    except Exception as e:
        erreurs.append(f"Erreur envoi notification Device {device.id} User {user.email} : {str(e)}")
        print(f"[ERREUR] {str(e)}")

    success = notifications_envoyees > 0
    return success, erreurs if erreurs else None



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def envoyer_notifications_culture(request):
    aujourd_hui = timezone.now().date()
    evenements = CalendrierCulture.objects.filter(
        date_prevue=aujourd_hui,
        alerte_envoyee=False
    ).select_related('parcelle__farm__owner', 'parcelle__variete')

    if not evenements.exists():
        return Response({"detail": "Aucune notification à envoyer."}, status=status.HTTP_200_OK)

    notifications_envoyees_count = 0
    erreurs_globales = []

    for evenement in evenements:
        message_text = construire_message(evenement)
        farm = evenement.parcelle.farm
        user = farm.owner
        image_url = getattr(evenement.parcelle, 'image_url', None)  # URL publique HTTPS

        data_payload = construire_data_payload(evenement)
        try:
            with transaction.atomic():
                NotificationLog.objects.create(
                    farm=farm,
                    message=message_text,
                    date_envoi=timezone.now(),
                    canal="app",
                    envoyee=True,
                    data_json=data_payload,  # Sauvegarder la data complète
                )
                success, erreurs = envoyer_notification_user(
                    user,
                    message_text,
                    image_url=image_url,
                    data_payload=data_payload
                )
                if success:
                    evenement.alerte_envoyee = True
                    evenement.save()
                    notifications_envoyees_count += 1
                if erreurs:
                    erreurs_globales.extend(erreurs)
        except Exception as e:
            erreurs_globales.append(f"Erreur transaction notification farm {farm.id} : {str(e)}")

    return Response({
        "notifications_envoyees": notifications_envoyees_count,
        "erreurs": erreurs_globales,
    }, status=status.HTTP_200_OK)
