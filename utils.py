def ordinal(number):
    number_string = str(number)
    if number_string.endswith('11'):
        return number_string + 'th'
    if number_string.endswith('12'):
        return number_string + 'th'
    if number_string.endswith('13'):
        return number_string + 'th'
    if number_string.endswith('1'):
        return number_string + 'st'
    if number_string.endswith('2'):
        return number_string + 'nd'
    if number_string.endswith('3'):
        return number_string + 'rd'
    return number_string + 'th'

def s_if_not_1(value):
    return 's' if value != 1 else ''
