# -*- coding: UTF-8 -*-


def clean(value):
    import re
    sanitized =re.sub(r'[^A-Za-z0-9_. ñÑáéíóúÁÉÍÓÚ$€]+|^\.|\.$|^ | $|^$', '', value)
    print value
    print sanitized
    print "---------------------------------"
    return sanitized


clean("prueba")
clean("prueba' OR username='admin")
clean("prueba\" OR username=\"admin")
clean("prueba' OR username='admin; --")
clean("1234567890 abzdefghijklmnñopqrstuvwxyz")
clean("áéíóú")
clean("ÁÉÍÓÚ")
clean("pass_with$and)(")
