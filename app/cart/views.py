"""
Views for Cart API
"""
from rest_framework import permissions, generics, status
from rest_framework.authentication import TokenAuthentication
from cart import serializers
from core.models import Cart, Course
from rest_framework.response import Response


class CartViews(generics.CreateAPIView):
    """Views Handling Create and List"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.CartSerializers
    queryset = Cart.objects.select_related('student', 'course').all()


class MyCartViews(generics.ListAPIView):
    """Views Handling Create and List"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.MyCartSerializers
    queryset = Cart.objects.select_related('student', 'course').all()
    lookup_field = Course
    lookup_url_kwarg = 'course_id'

    def get_queryset(self):
        student = self.request.user
        return Cart.objects.filter(student=student)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        total_items = queryset.count()
        total_price = sum(c.course.price for c in queryset)

        return Response({
            'total_items': total_items,
            'total_price': str(total_price),
            'results': serializer.data
        })


class CartRemoveView(generics.DestroyAPIView):
    """
    Delete a course from the current user's cart.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Look up the Cart item for this user and course_id..
        """
        course_id = self.kwargs.get('course_id')
        return Cart.objects.get(course_id=course_id, student=self.request.user)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Removed from cart"}, status=status.HTTP_204_NO_CONTENT)