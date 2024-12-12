import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.db import DatabaseError
from .models import Robot


# Create your views here.
@csrf_exempt
def create_robot(req):
    """
        Handle the creation of a new robot entry in the database.

        This view function processes POST requests to create a new robot
        with the specified model, version, and creation date. It expects
        a JSON payload with the required fields.

        Parameters:
        req (HttpRequest): The HTTP request object containing the POST data.

        Returns:
        JsonResponse: A JSON response indicating the result of the operation.
                      - On success, returns a 201 status with a message and the robot ID.
                      - On failure, returns an appropriate error message and status code:
                        - 400 for missing fields, invalid JSON, or invalid date format.
                        - 405 if the request method is not POST.
                        - 500 for database errors or unexpected exceptions.
    """
    if req.method == "POST":
        try:
            data = json.loads(req.body)

            model = data.get('model')
            version = data.get('version')
            created_str = data.get('created')

            if not model or not version or not created_str:
                return JsonResponse(
                    {'error': "Missing required fields"},
                    status=400
                )

            created = parse_datetime(created_str)
            if not created:
                return JsonResponse(
                    {'error': "Invalid date format"},
                    status=400
                )

            serial = f"{model}{version}"

            robot = Robot.objects.create(
                serial=serial,
                model=model,
                version=version,
                created=created
            )

            return JsonResponse(
                {
                    'message': "Robot created succesfully",
                    "id": robot.id
                },
                status=201
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except DatabaseError as e:
            return JsonResponse(
                {"error": f"Database error: {str(e)}"},
                status=500
            )
        except Exception as e:
            return JsonResponse(
                {"error": f"Unexpected error: {str(e)}"},
                status=500
            )
    else:
        return JsonResponse(
            {'error': "Only POST method is allowed"},
            status=405
        )
