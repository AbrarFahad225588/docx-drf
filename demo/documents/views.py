import os
import re
import uuid

from django.conf import settings
from lxml import etree
from django.http import FileResponse
from docx import Document
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AHNUApplicationSerializer


# Path to the prepared .docx template with {{variables}}
TEMPLATE_PATH = os.path.join(settings.BASE_DIR, "template_with_variables.docx")


def _has_cjk(text):
    """Check if text contains CJK (Chinese/Japanese/Korean) characters."""
    for ch in text:
        cp = ord(ch)
        if (
            (0x4E00 <= cp <= 0x9FFF) or   # CJK Unified Ideographs
            (0x3400 <= cp <= 0x4DBF) or   # CJK Extension A
            (0xF900 <= cp <= 0xFAFF) or   # CJK Compatibility Ideographs
            (0x3000 <= cp <= 0x303F) or   # CJK Symbols and Punctuation
            (0xFF00 <= cp <= 0xFFEF) or   # Fullwidth Forms
            (0x2E80 <= cp <= 0x2EFF)      # CJK Radicals
        ):
            return True
    return False


def _set_cjk_font(run):
    """Set a Chinese-compatible font on a run for proper CJK rendering."""
    WML = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    nsmap = {'w': WML}

    # Get or create run properties
    rpr = run._element.find(f'{{{WML}}}rPr')
    if rpr is None:
        rpr = etree.SubElement(run._element, f'{{{WML}}}rPr')
        # rPr must be the first child of w:r
        run._element.remove(rpr)
        run._element.insert(0, rpr)

    # Get or create rFonts
    rfonts = rpr.find(f'{{{WML}}}rFonts')
    if rfonts is None:
        rfonts = etree.SubElement(rpr, f'{{{WML}}}rFonts')

    # Set fonts that support Chinese characters
    rfonts.set(f'{{{WML}}}ascii', 'SimSun')
    rfonts.set(f'{{{WML}}}hAnsi', 'SimSun')
    rfonts.set(f'{{{WML}}}eastAsia', 'SimSun')
    rfonts.set(f'{{{WML}}}cs', 'SimSun')
    # Also remove any theme font references that override the explicit font
    for attr in ['asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme']:
        full_attr = f'{{{WML}}}{attr}'
        if full_attr in rfonts.attrib:
            del rfonts.attrib[full_attr]


def _replace_in_runs(cell, replacements):
    """
    Replace {{variable}} placeholders in a table cell,
    handling the case where a placeholder may be split across runs.
    When replacement text contains CJK characters, sets font to SimSun.
    """
    for para in cell.paragraphs:
        # Build the full text from runs
        full_text = "".join(r.text for r in para.runs)

        # Check if any placeholder exists
        changed = False
        new_text = full_text
        for placeholder, value in replacements.items():
            if placeholder in full_text:
                new_text = new_text.replace(placeholder, value)
                changed = True

        if changed:
            # Clear all runs and set the first run to the full text
            # (preserving the formatting of the first run)
            if para.runs:
                para.runs[0].text = new_text
                # If new text has CJK chars, set a CJK-compatible font
                if _has_cjk(new_text):
                    _set_cjk_font(para.runs[0])
                for run in para.runs[1:]:
                    run.text = ""


def _fill_template(template_path, data):
    """
    Open the .docx template, replace all {{variables}} with data values,
    and return the path to the new .docx file.
    """
    doc = Document(template_path)

    # Build replacements map
    replacements = {}
    for field_name, value in data.items():
        placeholder = "{{" + field_name + "}}"
        replacements[placeholder] = str(value) if value is not None else ""

    # Handle composite/alias placeholders that map to multiple fields
    # sex field: combine male/female into sex
    male_val = data.get('male', '□')
    female_val = data.get('female', '□')
    replacements['{{sex}}'] = f"Male {male_val}  Female {female_val}"

    # Chinese name for given_name_cn row
    replacements['{{given_name_cn}}'] = data.get('chinese_name', '')

    # Program type (checkbox style)
    replacements['{{program_type}}'] = data.get('program', '')

    # Referee composite
    referee_parts = []
    if data.get('referee_name'):
        referee_parts.append(f"Name: {data['referee_name']}")
    if data.get('referee_email'):
        referee_parts.append(f"Email: {data['referee_email']}")
    if data.get('referee_tel'):
        referee_parts.append(f"Tel: {data['referee_tel']}")
    if data.get('referee_fax'):
        referee_parts.append(f"Fax: {data['referee_fax']}")
    replacements['{{referee_info}}'] = "  ".join(referee_parts)

    # Replace in all paragraphs
    for para in doc.paragraphs:
        full_text = "".join(r.text for r in para.runs)
        changed = False
        new_text = full_text
        for placeholder, value in replacements.items():
            if placeholder in full_text:
                new_text = new_text.replace(placeholder, value)
                changed = True
        if changed and para.runs:
            para.runs[0].text = new_text
            if _has_cjk(new_text):
                _set_cjk_font(para.runs[0])
            for run in para.runs[1:]:
                run.text = ""

    # Replace in all tables
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                _replace_in_runs(cell, replacements)

    # Save to a temp file
    output_dir = os.path.join(settings.BASE_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"output_{uuid.uuid4().hex}.docx")
    doc.save(output_path)

    return output_path


class GenerateApplicationFormView(APIView):
    """
    POST to generate a filled-in AHNU application form.

    Accepts JSON or form-encoded data with applicant fields.
    Returns a .docx file with all {{variables}} replaced.
    """
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def post(self, request):
        serializer = AHNUApplicationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        if not os.path.exists(TEMPLATE_PATH):
            return Response(
                {"error": "Template file not found on server. Run prepare_template.py first."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            output_path = _fill_template(TEMPLATE_PATH, data)
        except Exception as e:
            return Response(
                {"error": f"Failed to generate document: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Return the file
        filename = f"AHNU_Application_{data.get('sur_name', '')}_{data.get('given_name', '')}_{uuid.uuid4().hex[:8]}.docx"
        response = FileResponse(
            open(output_path, "rb"),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


class DownloadBlankTemplateView(APIView):
    """
    GET to download the blank AHNU application form template (.docx).
    The template contains {{variable}} placeholders for reference.
    """

    def get(self, request):
        if not os.path.exists(TEMPLATE_PATH):
            return Response(
                {"error": "Template file not found on server."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        response = FileResponse(
            open(TEMPLATE_PATH, "rb"),
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        response["Content-Disposition"] = 'attachment; filename="AHNU_Application_Form_Blank.docx"'
        return response


class TemplateFieldsView(APIView):
    """
    GET to list all available template fields and their descriptions.
    Useful for building forms or API clients.
    """

    def get(self, request):
        serializer = AHNUApplicationSerializer()
        fields = {}
        for field_name, field in serializer.fields.items():
            fields[field_name] = {
                "type": field.__class__.__name__,
                "required": field.required,
                "help_text": str(field.help_text),
                "placeholder": f"{{{{{field_name}}}}}",
            }
        return Response(fields)


class GenerateFormPDFView(APIView):
    """
    POST to generate a filled-in AHNU application form as PDF.

    Accepts JSON or form-encoded data with applicant fields.
    Fills the .docx template then converts to PDF via Win32 COM.
    Returns the PDF file.
    """
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def post(self, request):
        serializer = AHNUApplicationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        if not os.path.exists(TEMPLATE_PATH):
            return Response(
                {"error": "Template file not found on server."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Step 1: Fill the .docx template
        try:
            docx_path = _fill_template(TEMPLATE_PATH, data)
        except Exception as e:
            return Response(
                {"error": f"Failed to generate document: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Step 2: Convert .docx -> .pdf via Win32 COM (Word / WPS)
        pdf_path = _docx_to_pdf(docx_path)
        if pdf_path is None:
            return Response(
                {"error": "PDF conversion requires Word or WPS Office. "
                         "Please install one and try again."},
                status=status.HTTP_501_NOT_IMPLEMENTED,
            )

        # Step 3: Return the PDF
        filename = f"AHNU_Application_{data.get('sur_name', '')}_{data.get('given_name', '')}.pdf"
        response = FileResponse(
            open(pdf_path, "rb"),
            content_type="application/pdf",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response


def _docx_to_pdf(docx_path):
    """
    Convert a .docx file to .pdf using Win32 COM (Word or WPS).
    Returns the PDF path on success, or None on failure.
    """
    import win32com.client
    import time
    import gc

    output_dir = os.path.join(settings.BASE_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f"{uuid.uuid4().hex}.pdf")

    word = None
    doc = None
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        doc = word.Documents.Open(os.path.abspath(docx_path))

        # ExportAsFixedFormat ExportFormat: 17 = wdExportFormatPDF
        doc.ExportAsFixedFormat(
            OutputFileName=os.path.abspath(pdf_path),
            ExportFormat=17,
            OpenAfterExport=False,
            OptimizeFor=0,   # wdOptimizeForOnScreen
            Range=0,         # wdExportAllDocument
            From=1,
            To=1,
        )
        doc.Close(SaveChanges=False)
        return pdf_path

    except Exception:
        return None

    finally:
        if doc:
            try:
                doc.Close(SaveChanges=False)
            except Exception:
                pass
        if word:
            try:
                word.Quit()
            except Exception:
                pass
        del doc, word
        gc.collect()
        time.sleep(0.5)
