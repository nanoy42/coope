from django_tex.environment import environment

def latex_safe(value):
    return str(value).replace('_', '\_').replace('$', '\$').replace('&', '\&').replace('#', '\#').replace('{', '\{').replace('}','\}')


def my_environment(**options):
    env = environment(**options)
    env.filters.update({
        'latex_safe': latex_safe
    })
    return env