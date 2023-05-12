import dis


class ClientVerifier(type):
    def __init__(cls, clsname, base, attrs):
        for k, v in attrs.items():
            try:
                bytecode = dis.Bytecode(v)
            except TypeError:
                pass
            else:
                for instruction in bytecode:
                    if instruction.opname in ('CALL_METHOD', 'LOAD_METHOD') and instruction.argrepr in (
                            'listen', 'accept'):
                        raise Exception('Method cannot use listen or accept')
                    if instruction.opname == 'LOAD_GLOBAL' and instruction.argval == 'socket':
                        raise Exception('Cannot create sockets in the ClientSender')
        super().__init__(clsname, base, attrs)


class ServerVerifier(type):
    def __init__(cls, clsname, base, attrs):
        for k, v in attrs.items():
            try:
                bytecode = dis.Bytecode(v)
            except TypeError:
                pass
            else:
                for instruction in bytecode:
                    if instruction.opname in ('CALL_METHOD', 'LOAD_METHOD') and instruction.argrepr == 'connect':
                        raise Exception('Method cannot use connect')
        super().__init__(clsname, base, attrs)
