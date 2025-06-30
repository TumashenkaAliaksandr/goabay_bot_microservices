from site_app.models import SocialNetwork


def social_networks(request):
    socials = SocialNetwork.objects.all()
    return {'social_networks': socials}
