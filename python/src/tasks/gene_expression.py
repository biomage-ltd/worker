import json
import requests
import numpy as np
import backoff
from config import get_config
from result import Result
from aws_xray_sdk.core import xray_recorder

config = get_config()


class GeneExpression:
    def __init__(self, msg):
        self.task_def = msg["body"]

    def _format_result(self, result):
        # JSONify result.
        result = json.dumps(result)
        # Return a list of formatted results.
        return [Result(result)]

    @xray_recorder.capture('GeneExpression.compute')
    @backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_time=30)
    def compute(self):
        # the genes to get expression data for
        genes = self.task_def["genes"]
        # whether to perform feature scaling (defaults to True)
        # In r we currently use the data matrix of the Seurat object.
        # scale = self.task_def.get("scale", True)
        request = {"genes": genes}
        r = requests.post(
            f"{config.R_WORKER_URL}/v0/getExpression",
            headers={"content-type": "application/json"},
            data=json.dumps(request),
        )
        # raise an exception if an HTTPError if one occurred because otherwise r.json() will fail
        r.raise_for_status()
        resultR = r.json()
        result = {}
        if not len(resultR):
            result[genes[0]] ={
                "error": 404,
                "message": "Gene {} not found!".format(genes[0]),
            }
        
        else:       
            for gene in resultR.keys():

                view = resultR[gene]
                # This is not necessary and is also costly, but I leave it commented as a reminder
                # that this object has integer zeros and floating point for n!=0.
                # expression = [float(item) for item in view]
                minimum = float(np.amin(view))
                maximum = float(np.amax(view))
                mean = float(np.mean(view))
                stdev = float(np.std(view))

                result[gene] = {
                    "min": minimum,
                    "max": maximum,
                    "mean": mean,
                    "stdev": stdev,
                    "expression": view,
                }
        return self._format_result(result)
