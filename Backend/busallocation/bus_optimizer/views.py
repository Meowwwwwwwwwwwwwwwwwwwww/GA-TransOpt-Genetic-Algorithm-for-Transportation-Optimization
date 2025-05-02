from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import BusGAInputSerializer
from .Algorithm.GA import BusGA
from .serializers import InputDataSerializer
from .serializers import InputDataSerializer
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.views import APIView

@api_view(['POST'])
def run_ga(request):
    serializer = InputDataSerializer(data=request.data)
    if serializer.is_valid():
        ga = BusGA(serializer.validated_data)
        result = ga.run()  
        return Response(result)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class BusInputAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = request.data

            # Basic validation
            if 'buses' not in data or 'stops' not in data or 'constraints' not in data:
                return Response({"error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

            # You can save or process the data here as needed
            # For now, return the input data as acknowledgment
            return Response({"message": "Input received successfully", "data": data}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




