import re


def add_numbers(filename):
    lines = open(filename, 'r').readlines()

    num = 0
    for line in lines:
        matched = re.match(r'(?:===>|) *(\d+)\.[a-zA-Z_]*', line)
        if matched:
            current_num = int(matched.groups()[0])
            if current_num >= 10000:
                current_num -= 10000
            num = max(num, current_num)

    matches = set()
    for line in lines:
        matched = re.match(r'(?:===>|) *(?!\d+\.)([a-zA-Z_]*)', line)
        if matched:
            value = matched.groups()[0]
            if value != '':
                matches |= {value}

    matches = sorted(list(matches))

    text = open(filename, 'r').read()
    for value in matches:
        num += 1
        if re.match(r'^[a-z]', value):
            output = num + 10000
        else:
            output = num
        replaced = str(output) + '.' + value
        text = re.sub(r'\b' + value + r'\b', replaced, text)
    return text
