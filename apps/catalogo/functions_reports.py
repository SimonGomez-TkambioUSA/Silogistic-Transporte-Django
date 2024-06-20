import os
from io import StringIO, BytesIO
from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


# from apps.usuarios.models import Recepcion, Investigacion


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL  # Typically /static/
        sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL  # Typically /media/
        mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri
    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def render_to_pdf(template_src, context_dict={}, watermark=None):
    template_path = template_src
    # if watermark:
    #     try:
    #         orientation = context_dict['orientacion']
    #         size = context_dict['tamanio']
    #         tmp = BytesIO()
    #         watermark_img = Image.open(watermark)
    #         watermark_img = watermark_img.convert('RGBA')
    #
    #         ## letter portrait
    #         if size == '1' and orientation == '1':
    #             img_resize = watermark_img.resize((273, 333))
    #             img_letter = Image.new('RGBA', (612, 791), 'white')
    #             img_letter.paste(img_resize, (169, 229), img_resize)
    #             img_letter.save(tmp, format='PNG')
    #
    #         ## letter landscape
    #         if size == '1' and orientation == '2':
    #             img_resize = watermark_img.resize((273, 273))
    #             img_letter = Image.new('RGBA', (791, 612), 'white')
    #             img_letter.paste(img_resize, (257, 169), img_resize)
    #             img_letter.save(tmp, format='PNG')
    #
    #         ## legal portrait
    #         if size == '2' and orientation == '1':
    #             img_resize = watermark_img.resize((299, 389))
    #             img_legal = Image.new('RGBA', (612, 1009), 'white')
    #             img_legal.paste(img_resize, (155, 309), img_resize)
    #             img_legal.save(tmp, format='PNG')
    #
    #         ## legal landscape
    #         if size == '2' and orientation == '2':
    #             img_resize = watermark_img.resize((296, 299))
    #             img_legal = Image.new('RGBA', (1009, 612), 'white')
    #             img_legal.paste(img_resize, (354, 155), img_resize)
    #             img_legal.save(tmp, format='PNG')
    #
    #         converted_string = base64.b64encode(tmp.getvalue())
    #         context_dict['watermark'] = converted_string.decode('utf-8')
    #         tmp.close()
    #     except Exception as e:
    #         pass
    context = context_dict
    # Create a Django response object, and specify content_type as pdf
    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    result = BytesIO()
    pisa_status = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), result, link_callback=link_callback)
    response = result.getvalue()

    # if error then show some funy view
    # inbox = Inbox.objects.get(pk=1)
    # inbox.documento_firma.save('file.pdf', ContentFile(result.getvalue()), save=True)
    # inbox.save()
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response