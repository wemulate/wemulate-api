class ConnectionParser:
    
    def __init__ (self, flaskApi):
        self.parser = flaskApi.parser()
        self.parser.add_argument(
            'connections',
            type=list,
            location='json'
        )


    def parse_arguments(self):
        args = self.parser.parse_args()
        return args['connections']