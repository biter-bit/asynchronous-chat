import dis


class ClientVerifier(type):
    """ Метакласс для клиента. Запрещает создание сокета и использование методов listen и accept """

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
    """
    Метакласс для пользователя. Запрещает использовать метод connect
    """
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
