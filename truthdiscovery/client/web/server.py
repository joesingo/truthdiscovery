from io import BytesIO, StringIO
import json

from flask import Flask, render_template, request, jsonify

from truthdiscovery.algorithm import BaseIterativeAlgorithm
from truthdiscovery.client.base import BaseClient
from truthdiscovery.exceptions import ConvergenceError
from truthdiscovery.input import MatrixDataset
from truthdiscovery.output import Result, ResultDiff
from truthdiscovery.graphs import (
    JsonAnimator,
    JsonBackend,
    MatrixDatasetGraphRenderer,
    ResultsGradientColourScheme
)
from truthdiscovery.utils import DistanceMeasures


class route:
    """
    Class to be used a decorator instead of ``app.route`` which allows methods
    to be decorated.

    ``app.route`` cannot be used for methods since it sees an *unbound*
    function, whereas we wish for it to register as a method bound to a
    particular instance of the class.

    As such we keep a record of the parameters passed to the decorator and the
    method names, and defer actually adding the routes in flask until an
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

    def get_graph_renderer(self, colours=None):
        """
        :param colours: (optional) :any:`GraphColourScheme` (or sub-class)
                        instance
        :return: a :any:`GraphRenderer` instance for graphs and animations
        """
        return MatrixDatasetGraphRenderer(
            width=800, height=600, zero_indexed=False, colours=colours,
            font_size=20, backend=JsonBackend()
        )

    @route("/")
    def home_page(self):
        # Map algorithm labels to display name
        labels = {label: cls.__name__
                  for label, cls in self.ALG_LABEL_MAPPING.items()}
        # Data that the JS client needs to construct forms etc
        static_data = {
            "algorithm_labels": labels,
            "distance_measures": [m.value for m in DistanceMeasures]
        }
        return render_template("index.html", data_json=json.dumps(static_data))

    @route("/run/", methods=["GET"])
    def run(self):
        """
        Run an algorithm on a user-supplied dataset. Required HTTP parameters:
        * 'algorithm'
        * 'matrix'

        Optional parameters:
        * 'parameters'
        * 'previous_results'
        * 'get_graph'
        * 'get_animation'.

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

        try:
            results = alg.run(dataset)
        except ConvergenceError as ex:
            return jsonify(ok=False, error=str(ex)), 500

        output = self.get_output_obj(results)

        # Construct a graph and/or animation if requested
        imagery = {}
        if "get_graph" in request.args:
            cs = ResultsGradientColourScheme(results)
            renderer = self.get_graph_renderer(colours=cs)
            json_buffer = StringIO()
            renderer.render(dataset, json_buffer)
            imagery["graph"] = json_buffer.getvalue()

        if "get_animation" in request.args:
            if not isinstance(alg, BaseIterativeAlgorithm):
                err_msg = (
                    "animation not supported for non-iterative algorithm '{}'"
                    .format(alg_label)
                )
                return jsonify(ok=False, error=err_msg), 400
            animator = JsonAnimator(renderer=self.get_graph_renderer())
            json_buffer = StringIO()
            animator.animate(json_buffer, alg, dataset, show_progress=False)
            imagery["animation"] = json_buffer.getvalue()

        if imagery:
            output["imagery"] = imagery

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


def run_debug_server():  # pragma: no cover
    app = get_flask_app()
    app.run(host="0.0.0.0", debug=True)


if __name__ == "__main__":  # pragma: no cover
    run_debug_server()
