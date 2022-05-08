"""
restful api 抽象方法
"""
from collections import OrderedDict


class CommonPagi:

    def get_paginated_data(self, queryset, view):
        qs = queryset
        default_paginated = False
        if not view.request.query_params.get('limit') or not view.request.query_params.get('offset'):
            default_paginated = True
        else:
            qs = view.paginate_queryset(qs)
        objs_serializer = view.get_serializer(qs, many=True)

        if default_paginated:
            return OrderedDict([
                ('count', len(objs_serializer.data[:5])),
                ('next', view.request.build_absolute_uri() + '?limit=5&offset=5'),
                ('previous', ""),
                ('results', objs_serializer.data[:5])
            ])

        return OrderedDict([
            ('count', view.paginator.count),
            ('next', view.paginator.get_next_link()),
            ('previous', view.paginator.get_previous_link()),
            ('results', objs_serializer.data)
        ])
