# import flask
# import runner
# from waitress import serve
#
# mng = flask.Flask(__name__)
#
#
# @mng.route("/health")
# def get_health():
#     if runner.is_all_running():
#         return "Up"
#     return flask.Response("Down", 503)
#
#
# def run():
#     serve(mng, host="0.0.0.0", port=8082)
