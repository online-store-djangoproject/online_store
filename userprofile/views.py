from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Address, DiscountCode
from .serializers import AddressSerializer


class AddressListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        return {"request": self.request}

    def perform_create(self, serializer):
        is_first = not Address.objects.filter(user=self.request.user).exists()
        serializer.save(user=self.request.user, is_default=serializer.validated_data.get("is_default", is_first))


class AddressUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        return {"request": self.request}


class ValidateDiscountCodeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code", "").strip()
        if not code:
            return Response({"valid": False, "message": "لطفاً کد تخفیف را وارد کنید."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            discount_code = DiscountCode.objects.get(code__iexact=code)
        except DiscountCode.DoesNotExist:
            return Response({"valid": False, "message": "کد تخفیف نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)
        if not discount_code.can_be_used_by(request.user):
            return Response({"valid": False, "message": "کد تخفیف قابل استفاده نیست."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "valid": True,
            "discount_percentage": discount_code.percentage,
            "message": f"کد تخفیف معتبر است؛ {discount_code.percentage}٪ تخفیف اعمال می‌شود.",
        })


class RequestDiscountCodeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"message": "کد تخفیف باید توسط مدیر سایت در پنل Django ساخته و فعال شود."})
