def expand_to_include_full_function(a, diff_a, first_diff_index, last_diff_index):
    if (first_diff_index > 0 and
            (a[first_diff_index - 1] == '.' or a[first_diff_index - 1].isalnum() or a[first_diff_index - 1] == '_')):
        first_diff_index -= 1
        while (first_diff_index > 0
               and (a[first_diff_index] == '.' or a[first_diff_index].isalnum() or a[first_diff_index] == '_')):
            first_diff_index -= 1
        diff_a = a[first_diff_index:last_diff_index]

    if a[first_diff_index] == '.' and first_diff_index > 0:
        while (first_diff_index > 0
               and (a[first_diff_index] == '.' or a[first_diff_index].isalnum() or a[first_diff_index] == '_')):
            first_diff_index -= 1
        diff_a = a[first_diff_index:last_diff_index]

    if a[last_diff_index] == '(':
        diff_a += a[last_diff_index]
        last_diff_index += 1

    counter = 0
    for i in range(first_diff_index, last_diff_index):
        if a[i] == '(':
            counter += 1
        if a[i] == ')':
            counter -= 1
            if counter < 0:
                j = i - 1  # changed
                while counter < 0 <= j:
                    if a[j] == '(':
                        counter += 1
                    if a[j] == ')':
                        counter -= 1
                    j -= 1
                diff_a = a[j:last_diff_index]
                first_diff_index = j
    if counter > 0:
        j = last_diff_index
        while counter > 0 and j < len(a):
            if a[j] == '(':
                counter += 1
            if a[j] == ')':
                counter -= 1
            j += 1
        diff_a = diff_a + a[last_diff_index:j]
        last_diff_index = j
    i = first_diff_index - 1
    is_assignment = False
    while i >= 0:
        match a[i]:
            case ' ':
                pass
            case '=':
                is_assignment = True
            case _:
                if not is_assignment:
                    return diff_a, first_diff_index, last_diff_index
                break
        i -= 1
    is_name_found = False
    while i >= 0:
        match a[i]:
            case ' ' | '\n':
                if is_name_found:
                    diff_a = a[i:first_diff_index] + diff_a
                    first_diff_index = i
                    break
            case '-' | '+' | '*' | '/' | '%' | '&' | '|' | '^' | '>' | '<' | ':':  # assignment operators
                pass
            case _:
                is_name_found = True
        i -= 1

    return diff_a, first_diff_index, last_diff_index


def trim_unnecessary_indentations(diff_a):
    if not (diff_a[0] == ' ' or diff_a[0] == '\t'):
        return diff_a.strip()
    i = 0
    for j in range(len(diff_a)):
        if not (diff_a[j] == ' ' or diff_a[j] == '\t'):
            break
        i += 1
    start_indentation = diff_a[:i]
    diff_a = diff_a.replace(f"\n{start_indentation}", "\n")
    return diff_a.strip()


def include_full_rows(a, diff_a, first_diff_index, last_diff_index):
    original_first_index = first_diff_index
    while first_diff_index > 0 and a[first_diff_index - 1] != '\n':
        first_diff_index -= 1
    diff_a = a[first_diff_index:original_first_index] + diff_a

    # original_last_index = last_diff_index
    # while last_diff_index < len(a) and a[last_diff_index] != '\n':
    #     last_diff_index += 1
    # diff_a = diff_a + a[original_last_index:last_diff_index]
    return diff_a, first_diff_index, last_diff_index
