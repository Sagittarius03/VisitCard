def global_context(request):
    context = {}
    
    scss_dir = 'main/scss/'
    context['scss'] = [
        # "cosmic-bg.scss",
        "base.scss",
    ]
    
    context['scss'] = [scss_dir + file for file in context['scss']]
    
    return context