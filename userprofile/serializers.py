from rest_framework import serializers
from .models import Address, DiscountCode


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["id", "user", "title", "city", "state", "full_address", "postal_code", "is_default"]
        extra_kwargs = {"user": {"read_only": True}}

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.method == "POST":
            count = Address.objects.filter(user=request.user).count()
            if count >= 5:
                raise serializers.ValidationError("حداکثر می‌توانید ۵ آدرس ذخیره کنید.")
        return attrs


class DiscountCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCode
        fields = ["id", "code", "percentage", "is_active", "is_used", "expires_at"]
