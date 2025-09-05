# -*- coding: utf-8 -*-
{
    'name': 'Saudi Food & Drug Authority Theme',
    'category': 'Tools',
    'version': '0.1',
    'summary': 'Customization for backend and forntend themes built for Saudi Food & Drug Authority',
    'description': 'Saudi Food & Drug Authority Theme',
    'author': "Expert Co. Ltd.",
    'website': "https://www.exp-sa.com",
    'depends': ['web','odex25_web'],
    'data': [
        'views/assets.xml',
        'views/icons.xml',
        'views/settings.xml',
    ],
    "qweb": [
        'static/src/xml/*'
    ],
    'license': 'LGPL-3',
    'pre_init_hook': 'test_pre_init_hook',
    'post_init_hook': 'test_post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
