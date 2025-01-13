import os
from PyPDF2 import PdfReader
from docx import Document
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import File

class SearchInFilesView(APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'search',
                openapi.IN_HEADER,
                description="String to search in uploaded files",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: 'application/json'}
    )
    def get(self, request, *args, **kwargs):
        search_string = request.headers.get('search')

        if not search_string:
            return Response({"error": "Search-String header is required"}, status=status.HTTP_400_BAD_REQUEST)

        results = []

        # Iterate over all File objects
        for file_obj in File.objects.all():
            file_path = file_obj.file.path

            if os.path.exists(file_path):
                try:
                    if file_path.endswith('.pdf'):
                        results.extend(self._search_in_pdf(file_path, search_string, file_obj.name))
                    elif file_path.endswith('.docx'):
                        results.extend(self._search_in_docx(file_path, search_string, file_obj.name))
                    elif file_path.endswith('.txt'):
                        results.extend(self._search_in_txt(file_path, search_string, file_obj.name))
                except Exception as e:
                    results.append({
                        "file": file_obj.name,
                        "error": f"Error processing file: {str(e)}"
                    })

        return Response(results, status=status.HTTP_200_OK)

    def _search_in_pdf(self, file_path, search_string, file_name):
        results = []
        with open(file_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                lines = page.extract_text().splitlines()
                for i, line in enumerate(lines):
                    if search_string in line:
                        next_lines = lines[i+1:i+5]
                        results.append({
                            "file": file_name,
                            "found_line": line.strip(),
                            "next_lines": [ln.strip() for ln in next_lines]
                        })
                        break
        return results

    def _search_in_docx(self, file_path, search_string, file_name):
        results = []
        doc = Document(file_path)
        lines = [para.text for para in doc.paragraphs]
        for i, line in enumerate(lines):
            if search_string in line:
                next_lines = lines[i+1:i+5]
                results.append({
                    "file": file_name,
                    "found_line": line.strip(),
                    "next_lines": [ln.strip() for ln in next_lines]
                })
                break
        return results

    def _search_in_txt(self, file_path, search_string, file_name):
        results = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if search_string in line:
                    next_lines = lines[i+1:i+5]
                    results.append({
                        "file": file_name,
                        "found_line": line.strip(),
                        "next_lines": [ln.strip() for ln in next_lines]
                    })
                    break
        return results
