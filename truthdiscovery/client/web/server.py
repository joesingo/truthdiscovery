from io import BytesIO
import json

from flask import Flask, render_template, request, abort, Response

from truthdiscovery.client.base import BaseClient
from truthdiscovery.input import MatrixDataset


class WebClient(BaseClient):
    def get_algorithm_object(self, label, params_str):
        """
        :raises ValueError: if label or parameters are invalid
        """
        cls = self.algorithm_cls(label)
        params = {}
        if params_str is not None:
            for line in params_str.split("\n"):
                key, value = self.algorithm_parameter(line)
                params[key] = value

        try:
            return cls(**params)
        except TypeError:
            raise ValueError


app = Flask(__name__)
client = WebClient()


@app.route("/")
def home_page():
    # Map algorithm labels to display name
    labels = {
        label: cls.__name__ for label, cls in client.ALG_LABEL_MAPPING.items()
    }
    return render_template(
        "index.html",
        data_json=json.dumps({"algorithm_labels": labels})
    )


@app.route("/run/", methods=["GET"])
def run():
    try:
        alg_label = request.args["algorithm"]
        matrix_csv = request.args["matrix"]
    except KeyError:
        return abort(400)

    matrix_csv = matrix_csv.replace("_", "")

    params = request.args.get("parameters")
    alg = client.get_algorithm_object(alg_label, params)
    dataset = MatrixDataset.from_csv(BytesIO(matrix_csv.encode()))
    results = alg.run(dataset)
    output = client.get_output_obj(results)
    return Response(json.dumps(output), mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True)
