from . import add_submision
from . import all_submission
from . import assign
from . import change_cover
from . import change_submission_data
from . import delete_comment
from . import delete_picture
from . import delete_submission
from . import download
from . import error_handlers
from . import full_map
from . import index
from . import kutyi
from . import login
from . import single_submission
from . import statistics
from . import user
from . import user_data_info
from . import szimat


def setup(app):
    add_submision.setup(app)
    all_submission.setup(app)
    assign.setup(app)
    change_cover.setup(app)
    change_submission_data.setup(app)
    delete_comment.setup(app)
    delete_picture.setup(app)
    delete_submission.setup(app)
    download.setup(app)
    error_handlers.setup(app)
    full_map.setup(app)
    index.setup(app)
    kutyi.setup(app)
    login.setup(app)
    single_submission.setup(app)
    statistics.setup(app)
    user.setup(app)
    user_data_info.setup(app)
    szimat.setup(app)
