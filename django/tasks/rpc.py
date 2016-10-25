from xmlrpc.server import SimpleXMLRPCServer


def prepare_input_command(src, state):
    scope = {"state_in": state, "state_out": None}
    exec(src, scope, scope)
    return {"command": scope["command"], "state": scope["state_out"]}


def parse_output(src, state, stdout, stderr, status_code):
    scope = {"state_in": state, "stdout": stdout, "stderr": stderr, "status_code": status_code, "state_out": None}
    exec(src, scope, scope)
    return {"state": scope["state_out"],
            "grade": scope["grade"],
            "output_msg": scope["output_msg"],
            "exec_next_step": scope["exec_next_step"]}


if __name__ == "__main__":
    server = SimpleXMLRPCServer(("localhost", 8000))
    server.register_function(prepare_input_command, 'prepare_input_command')
    server.register_function(parse_output, 'parse_output')
    server.serve_forever()
