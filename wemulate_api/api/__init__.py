from flask_restx import Api
from wemulate_api.api.v1 import api as v1

api = Api(
    title="WEmulate API",
    description="Simple REST API to use the WEmulate module",
    doc="/api/doc",
)

api.add_namespace(v1, path="/api/v1")
