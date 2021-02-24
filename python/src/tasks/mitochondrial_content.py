import json
from config import get_config
from result import Result
import numpy as np
import requests

config = get_config()


class GetMitochondrialContent:
    def __init__(self):
        pass
    
    def _format_result(self, result):
        # JSONify result.
        result = json.dumps(result)

        # Return a list of formatted results.
        return [Result(result)]

    def compute(self):
        # Retrieve the MitochondrialContent of all the cells
        request = {}
        r = requests.post(
            f"{config.R_WORKER_URL}/v0/getMitochondrialContent",
            headers={"content-type": "application/json"},
            data=json.dumps(request),
        )

        # The values are ordered by the default order of the Embedding in the Seurat object
        # The result contains a list with the MT-content values
        result = r.json()
        return self._format_result(result)

