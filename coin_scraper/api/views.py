# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Job, Task
# from .tasks import scrape_coin_data
# from uuid import uuid4

# class StartScraping(APIView):
#     def post(self, request):
#         coins = request.data.get('coins', [])
#         if not all(isinstance(coin, str) for coin in coins):
#             return Response({"error": "Invalid input, only strings are allowed"}, status=status.HTTP_400_BAD_REQUEST)
        
#         job_id = str(uuid4())
#         job = Job.objects.create(job_id=job_id)
        
#         for coin in coins:
#             Task.objects.create(job=job, coin=coin, status='pending')
#             scrape_coin_data.delay(job_id, coin)
        
#         return Response({"job_id": job_id}, status=status.HTTP_202_ACCEPTED)

# class ScrapingStatus(APIView):
#     def get(self, request, job_id):
#         job = Job.objects.filter(job_id=job_id).first()
#         if not job:
#             return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
        
#         tasks = job.tasks.all()
#         task_data = [{"coin": task.coin, "output": task.output} for task in tasks]
        
#         return Response({"job_id": job_id, "tasks": task_data}, status=status.HTTP_200_OK)



from rest_framework.decorators import api_view
from rest_framework.response import Response
from .scraper import fetch_coin_data

@api_view(['GET'])
def coin_detail(request, coin_name):
    data = fetch_coin_data(coin_name)
    return Response(data)
