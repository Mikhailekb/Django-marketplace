from imagekit import ImageSpec, register
from imagekit.processors import ResizeToFit


class Thumbnail200x200(ImageSpec):
    processors = [ResizeToFit(200, 200)]
    format = 'PNG'
    options = {'quality': 80}


class Thumbnail500x500(ImageSpec):
    processors = [ResizeToFit(500, 500)]
    format = 'PNG'
    options = {'quality': 80}


class Thumbnail800x800(ImageSpec):
    processors = [ResizeToFit(800, 800)]
    format = 'PNG'
    options = {'quality': 80}


register.generator('app_shops:thumbnail_200x200', Thumbnail200x200)
register.generator('app_shops:thumbnail_500x500', Thumbnail500x500)
register.generator('app_shops:thumbnail_800x800', Thumbnail800x800)
