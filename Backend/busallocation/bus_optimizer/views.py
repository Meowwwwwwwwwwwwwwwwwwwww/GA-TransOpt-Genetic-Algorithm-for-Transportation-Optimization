from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import BusGAInputSerializer
from .Algorithm.GA import BusGA

@api_view(['POST'])
def run_ga(request):
    serializer = BusGAInputSerializer(data=request.data)
    if serializer.is_valid():
        ga = BusGA(serializer.validated_data)
        result = ga.run()  # Only running the run() function
        return Response(result)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
