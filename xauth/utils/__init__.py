from rest_framework import status, response as drf_response


def valid_str(string, length: int = 1) -> bool:
    """
    Checks for `string`'s null(not None and length) status

    :param string: str checked for validity
    :param length: minimum length `string` should have
    :return: True if `string` is of `length`
    """
    return string is not None and isinstance(string, str) and len(string) > length - 1


def reset_empty_nullable_to_null(obj, fields):
    """
    Reset '' in named attributes contained in `fields` to None otherwise the provided 
    value is retained
    
    :param obj: object(class instance) containing attributes in `field`
    :param fields: an iterable(list/tuple) of string names of attributes contained in 
    `self`
    :return: list of attribute names that raised AttributeError in the process
    """
    failed = []
    for f in fields:
        try:
            val = getattr(obj, f)
            if valid_str(val) is False:
                setattr(obj, f, None)
        except AttributeError:
            failed.append(f)
    return failed


def get_204_wrapped_response(r: drf_response.Response):
    if not r.data or r.status_code == status.HTTP_204_NO_CONTENT:
        return drf_response.Response(status=status.HTTP_204_NO_CONTENT)
    return get_wrapped_response(r)


def get_wrapped_response(r: drf_response.Response):
    from .response import APIResponse
    from .settings import XENTLY_AUTH
    if XENTLY_AUTH.get('WRAP_DRF_RESPONSE', True):
        _response = APIResponse(payload=r.data, status_code=r.status_code)
        return drf_response.Response(_response.response(), status=_response.status_code)
    else:
        return r
