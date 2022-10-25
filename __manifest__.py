{
    "name": "State Transition",
    "summary": "A module for helping user define their state transition",
    "description": """""",
    "author": "Drake Bui",
    "website": "https://www.drakebui.ml",
    "category": "Services",
    "version": "15.0.1.0",
    "depends": ['hr'],
    "data": [
        #     Security
        'security/ir.model.access.csv',
        #     Data

        #     Views
        'views/state_transition_views.xml',
        'views/state_transition_route_views.xml',
        'views/state_transition_template_views.xml'
        #     Wizard
    ],
    'assets': {
        'web.assets_backend': [
            'state_transition/static/**/*',
        ],
        'web.assets_qweb': [
            'state_transition/static/src/**/*.xml',
        ]
    }
}
