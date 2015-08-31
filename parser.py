import re

def main(latex_string):
    targetted_commands = [
        'newbool',
        'providebool',
        'boolfalse',
        'booltrue',
        'setbool',
        'ifbool',
        'notbool',
        'newtoggle',
        'providetoggle',
        'toggletrue',
        'togglefalse',
        'settoggle',
        'iftoggle',
        'nottoggle'
    ]
    commands_re = re.compile(r'\\(%s)' % '|'.join(targetted_commands))
    output = ''
    string_position = 0
    context = dict()

    for command in commands_re.finditer(latex_string):
        command_name = command.group(1)
        command_start = command.start()
        command_end = command.end()
        optional, required, raw_text_length = get_parameters(latex_string[command_end:])
        output += latex_string[string_position:command_start]
        string_position = command_start
        output += replace_command(command_name, optional, required, context)
        string_position = command_end + raw_text_length
    print output

def replace_command(command, optional, required, context):
    if command in ['newbool', 'providebool', 'newtoggle', 'providetoggle']:
        return ''
    if command in ['booltrue', 'toggletrue']:
        context[required[0]] = True
        return ''
    elif command in ['boolfalse', 'togglefalse']:
        context[required[0]] = False
        return ''
    elif command in ['setbool', 'settoggle']:
        options = {'true' : True, 'false' : False}
        context[required[0]] = options[required[1]]
        return ''
    elif command in ['ifbool', 'iftoggle']:
        if context[required[0]]:
            return required[1]
        else:
            return required[2]
    elif command in ['notbool', 'nottoggle']:
        if not context[required[0]]:
            return required[1]
        else:
            return required[2]

def get_parameters(latex_string):
    state = 'find_parameter'
    scope_count = 0
    scope_characters = None
    parameter_type = None
    character_count = 0
    trailing_character_count = 0
    required_parameters = list()
    optional_parameters = list()
    parameter_characters = list()
    escaped = False
    in_comment = False

    for character in latex_string:
        character_count += 1
        if character == '%':
            in_comment = True
        elif in_comment:
            if character == '\n':
                in_comment = False
                continue
        elif state == 'find_parameter':
            if character == '{':
                parameter_type = 'required'
                scope_characters = ('{', '}')
                scope_count += 1
                trailing_character_count = 0
                state = 'read_parameter'
            elif character == '[':
                parameter_type = 'optional'
                scope_characters = ('[', ']')
                scope_count += 1
                trailing_character_count = 0
                state = 'read_parameter'              
            elif character in [' ', '\t', '\n', '\r', '\f', '\v']:
                trailing_character_count += 1
            else:
                character_count -= (trailing_character_count + 1)
                break
        elif state == 'read_parameter':
            scope_start_char, scope_end_char = scope_characters
            if not escaped and character == scope_start_char:
                scope_count += 1
                parameter_characters.append(character)
            elif not escaped and character == scope_end_char:
                scope_count -= 1
                if scope_count == 0:
                    if parameter_type == 'required':
                        required_parameters.append(''.join(parameter_characters))
                        parameter_characters = list()
                        state = 'find_parameter'
                    elif parameter_type == 'optional':
                        optional_parameters.append(''.join(parameter_characters))
                        parameter_characters = list()
                        state = 'find_parameter'
                else:
                    parameter_characters.append(character)
            else:
                parameter_characters.append(character)
                if character == '\\':
                    escaped = True
                else:
                    escaped = False

    return optional_parameters, required_parameters, character_count

if __name__ == '__main__':
    with open('example.tex') as example_file:
        main(example_file.read())