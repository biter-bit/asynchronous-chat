class ServerCheckPort:
    """
    Класс дескриптор порта. Запрещает установку значения меньше 0 и удаление атрибута
    """
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, '_name_port', 7777)

    def __set__(self, instance, value):
        if int(value) < 0:
            raise Exception('The port value is less then 0')
        setattr(instance, '_name_port', value)

    def __delete__(self, instance):
        raise AttributeError("Невозможно удалить атрибут")