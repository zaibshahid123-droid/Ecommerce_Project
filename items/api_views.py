from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from mongoengine.errors import DoesNotExist, ValidationError
from .models import Item
from .serializers import ItemSerializer


@api_view(['GET', 'POST'])
def item_list_api(request):
    if request.method == 'GET':
        items = Item.objects.all()
        serializer = ItemSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save()
            image_file = request.FILES.get('image')
            if image_file:
                item.image = image_file
                item.save()
            return Response(
                ItemSerializer(item, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _get_item_or_404_api(pk):
    try:
        return Item.objects.get(id=pk)
    except (DoesNotExist, ValidationError):
        return None


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def item_detail_api(request, pk):
    item = _get_item_or_404_api(pk)
    if item is None:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ItemSerializer(item, context={'request': request})
        return Response(serializer.data)

    if request.method == 'PUT':
        # Full update — every non-read-only field is required
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            image_file = request.FILES.get('image')
            if image_file:
                item.image = image_file
                item.save()
            return Response(ItemSerializer(item, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PATCH':
        # Partial update — only send the fields you want to change
        serializer = ItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            image_file = request.FILES.get('image')
            if image_file:
                item.image = image_file
                item.save()
            return Response(ItemSerializer(item, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)