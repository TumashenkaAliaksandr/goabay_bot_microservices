from site_app.models import SocialNetwork, InfoFooter


def social_networks(request):
    socials = SocialNetwork.objects.all()
    info_footer = InfoFooter.objects.first()
    return {'social_networks': socials, 'info_footer': info_footer}

