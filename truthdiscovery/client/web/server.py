import base64
from io import BytesIO
import json

from flask import Flask, render_template, request, jsonify

from truthdiscovery.client.base import BaseClient
from truthdiscovery.input import MatrixDataset
from truthdiscovery.output import Result, ResultDiff
from truthdiscovery.graphs import (
    MatrixDatasetGraphRenderer, ResultsGradientColourScheme
)


class route:
    """
    Class to be used a decorator instead of ``app.route`` which allows methods
    to be decorated.

    ``app.route`` cannot be used for methods since it sees an *unbound*
    function, whereas we wish for it to register as a method bound to a
    particular instance of the class.

    As such we keep a record of the parameters passed to the decorator and the
    method names, and delay actually adding the routes in flask until an
    instance has been created and passed to ``add_routes``
    """
    # Note: this list is shared amongst all ``route`` instances
    routes = []

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, func):
        route.routes.append((self.args, self.kwargs, func.__name__))
        return func

    @classmethod
    def add_routes(cls, flask_app, class_instance):
        for args, kwargs, func_name in route.routes:
            try:
                meth = getattr(class_instance, func_name)
            except AttributeError:
                continue
            flask_app.add_url_rule(
                *args,
                view_func=meth,
                **kwargs
            )


class WebClient(BaseClient):
    def get_param_dict(self, params_str):
        """
        Parse a multi-line string of parameters to a dictionary where keys are
        parameter names, and values are parameter values as their proper Python
        types
        """
        params = {}
        if params_str is not None:
            for line in params_str.split("\n"):
                key, value = self.algorithm_parameter(line)
                params[key] = value
        return params

    def get_results_object(self, res_str):
        """
        Construct a :any:`Result` object from a JSON string
        :raises ValueError: if string is not valid JSON or does not contain the
                            fields required to construct a :any:`Result` object
        """
        try:
            obj = json.loads(res_str)
        except json.decoder.JSONDecodeError as ex:
            raise ValueError("invalid JSON: {}".format(ex))

        try:
            return Result(
                trust=obj["trust"],
                belief=obj["belief"],
                time_taken=obj["time"],
                iterations=obj["iterations"]
            )
        except KeyError as ex:
            raise ValueError("required field {} missing".format(ex))

    @route("/")
    def home_page(self):
        # Map algorithm labels to display name
        labels = {label: cls.__name__
                  for label, cls in self.ALG_LABEL_MAPPING.items()}
        return render_template(
            "index.html",
            data_json=json.dumps({"algorithm_labels": labels})
        )

    @route("/run/", methods=["GET"])
    def run(self):
        """
        Run an algorithm on a user-supplied dataset. Required HTTP parameters
        are 'algorithm' and 'matrix'; optional parameters are 'parameters',
        'previous_results' and 'get_graph'.

        Responses are JSON objects of the form
        ``{"ok": True, "data": ...}``
        or
        ``{"ok": False, "error": ...}``
        """
        alg_label = request.args.get("algorithm")
        matrix_csv = request.args.get("matrix")

        if alg_label is None or matrix_csv is None:
            err_msg = "'algorithm' and 'matrix' parameters are required"
            return jsonify(ok=False, error=err_msg), 400

        matrix_csv = matrix_csv.replace("_", "")
        params_str = request.args.get("parameters")
        try:
            alg_cls = self.algorithm_cls(alg_label)
            params = self.get_param_dict(params_str)
            alg = self.get_algorithm_object(alg_cls, params)
            dataset = MatrixDataset.from_csv(BytesIO(matrix_csv.encode()))
        except ValueError as ex:
            return jsonify(ok=False, error=str(ex)), 400

        results = alg.run(dataset)
        output = self.get_output_obj(results)

        # Construct a graph of dataset if requested
        if "get_graph" in request.args:
            colour_scheme = ResultsGradientColourScheme(results)
            renderer = MatrixDatasetGraphRenderer(
                dataset, width=800, height=600, colours=colour_scheme,
                zero_indexed=False
            )
            img_buffer = BytesIO()
            renderer.draw(img_buffer)
            img_buffer.seek(0)
            output["graph"] = base64.b64encode(img_buffer.read()).decode()

        # Include diff between previous results if available
        prev_results = request.args.get("previous_results")
        if prev_results is not None:
            try:
                obj = self.get_results_object(prev_results)
            except ValueError as ex:
                err_msg = "'previous_results' is invalid: {}".format(ex)
                return jsonify(ok=False, error=err_msg), 400

            # Previous results have been converted to JSON, which may have
            # changed numeric keys to strings: to ensure results can be
            # compared, convert the current results to and from JSON
            current_results = self.get_results_object(json.dumps(output))
            diff = ResultDiff(obj, current_results)
            output["diff"] = {
                "trust": diff.trust,
                "belief": diff.belief,
                "time_taken": diff.time_taken,
                "iterations": diff.iterations
            }

        return jsonify({"ok": True, "data": output})


def get_flask_app():
    client = WebClient()
    app = Flask(__name__)
    route.add_routes(app, client)
    return app


app = get_flask_app()


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", debug=True)
