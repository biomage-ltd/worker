import json
import numpy as np
import json
import requests
from config import get_config
from result import Result


config = get_config()


class GeneExpression:
    def __init__(self, msg, adata):
        self.adata = adata
        self.task_def = msg["body"]

    def _format_result(self, result):
        # JSONify result.
        result = json.dumps(result)

        # Return a list of formatted results.
        return [Result(result)]

    def compute(self):
        # the genes to get expression data for
        genes = self.task_def["genes"]

        # whether to perform feature scaling (defaults to True)
        scale = self.task_def.get("scale", True)

        if scale:
            correct_adata = self.adata.copy()
        else:
            correct_adata = self.adata.raw.to_adata()
            correct_adata = correct_adata.copy()
            correct_adata.X = correct_adata.X.toarray()

        r = requests.post(
            f"{config.R_WORKER_URL}/v0/getExpression",
            headers={"content-type": "application/json"},
            data=json.dumps({}),
        )

        result = r.json()
        print(result)
        # create a proper ordering of cells by increasing IDs
        obs_copy = correct_adata.obs.copy()
        obs_copy.sort_values(by=["cell_ids"], inplace=True)
        obs_copy = obs_copy.dropna()
        cell_list = obs_copy.index.tolist()

        # try to find all genes in the list
        correct_adata.var["genes_to_compute"] = correct_adata.var.index.isin(genes)
        for i in range(0, len(correct_adata.var["gene_names"])):
            print(correct_adata.var["gene_names"][i] == result[i])
        print(len(correct_adata.var["gene_names"]))
        print(len(result))
        # this orders and filters the matrix correctly for both cells and genes
        correct_adata = correct_adata[
            cell_list,
            correct_adata.var["genes_to_compute"],
        ]

        result = {}

        for gene in correct_adata.var.index:
            view = correct_adata[:, correct_adata.var.index == gene]

            expression = view.X.flatten().tolist()
            minimum = float(np.amin(view.X))
            maximum = float(np.amax(view.X))
            mean = float(np.mean(view.X))
            stdev = float(np.std(view.X))

            result[gene] = {
                "min": minimum,
                "max": maximum,
                "mean": mean,
                "stdev": stdev,
                "expression": expression,
            }

        return self._format_result(result)
