import os
from django.conf import settings
from account.serializers import ImageUploadForm, FileUploadForm
from utils.shortcuts import rand_str
from utils.api import CSRFExemptAPIView, APIView, validate_serializer
import logging
from options.options import SysOptions
from .ai_assist import get_hint, get_solution
from utils.serializers import AIAssistSerializer
from problem.models import Problem

logger = logging.getLogger(__name__)


class SimditorImageUploadAPIView(CSRFExemptAPIView):
    request_parsers = ()

    def post(self, request):
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.cleaned_data["image"]
        else:
            return self.response({
                "success": False,
                "msg": "Upload failed",
                "file_path": ""})

        suffix = os.path.splitext(img.name)[-1].lower()
        if suffix not in [".gif", ".jpg", ".jpeg", ".bmp", ".png"]:
            return self.response({
                "success": False,
                "msg": "Unsupported file format",
                "file_path": ""})
        img_name = rand_str(10) + suffix
        try:
            with open(os.path.join(settings.UPLOAD_DIR, img_name), "wb") as imgFile:
                for chunk in img:
                    imgFile.write(chunk)
        except IOError as e:
            logger.error(e)
            return self.response({
                "success": False,
                "msg": "Upload Error",
                "file_path": ""})
        return self.response({
            "success": True,
            "msg": "Success",
            "file_path": f"{settings.UPLOAD_PREFIX}/{img_name}"})


class SimditorFileUploadAPIView(CSRFExemptAPIView):
    request_parsers = ()

    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]
        else:
            return self.response({
                "success": False,
                "msg": "Upload failed"
            })

        suffix = os.path.splitext(file.name)[-1].lower()
        file_name = rand_str(10) + suffix
        try:
            with open(os.path.join(settings.UPLOAD_DIR, file_name), "wb") as f:
                for chunk in file:
                    f.write(chunk)
        except IOError as e:
            logger.error(e)
            return self.response({
                "success": False,
                "msg": "Upload Error"})
        return self.response({
            "success": True,
            "msg": "Success",
            "file_path": f"{settings.UPLOAD_PREFIX}/{file_name}",
            "file_name": file.name})


class AIHintAPIView(APIView):
    @validate_serializer(AIAssistSerializer)
    def post(self, request):
        if not SysOptions.ai_assist_enabled:
            return self.error("AI assist is disabled")
        problem_id = request.data.get("problem_id")
        user_attempt = request.data.get("user_attempt")
        try:
            problem = Problem.objects.get(_id=problem_id, visible=True)
        except Problem.DoesNotExist:
            return self.error("Problem does not exist")
        description = "\n".join([
            problem.title,
            problem.description,
            "Input:",
            problem.input_description,
            "Output:",
            problem.output_description,
        ])
        hint = get_hint(description, user_attempt)
        return self.success({"hint": hint})


class AISolutionAPIView(APIView):
    @validate_serializer(AIAssistSerializer)
    def post(self, request):
        if not SysOptions.ai_assist_enabled:
            return self.error("AI assist is disabled")
        problem_id = request.data.get("problem_id")
        user_attempt = request.data.get("user_attempt")
        try:
            problem = Problem.objects.get(_id=problem_id, visible=True)
        except Problem.DoesNotExist:
            return self.error("Problem does not exist")
        description = "\n".join([
            problem.title,
            problem.description,
            "Input:",
            problem.input_description,
            "Output:",
            problem.output_description,
        ])
        solution_data = get_solution(description, user_attempt)
        return self.success(solution_data)
