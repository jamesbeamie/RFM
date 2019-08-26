import json

from rest_framework.renderers import JSONRenderer


class BumpJSONRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):

        # Finally, we can render our data under the "user" namespace.
        return json.dumps({
            'bump': data
        })
