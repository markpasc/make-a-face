from __future__ import with_statement

import typepad
from typepadapp.backends import TypePadBackend


class ALaCarteBackend(TypePadBackend):

    def get_user(self, user_id):
        with typepad.client.batch_request():
            return super(ALaCarteBackend, self).get_user(user_id)
