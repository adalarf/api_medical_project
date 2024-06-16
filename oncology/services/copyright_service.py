from oncology.models import CopyrightInfo


def get_copyright_info(copyright_info_id):
    return CopyrightInfo.objects.get(pk=copyright_info_id)
