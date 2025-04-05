import ast
import code_diff as cd


def parse_code(code: str):
    """
    Parse the given Python code into an AST.
    """
    return ast.parse(code)


def unparse_code(node: ast.AST):
    """
    Unparse the AST back to Python code.
    """
    return ast.unparse(node)


def compare_ast_nodes(node1, node2):
    """
    Compare two AST nodes and return differences as a list of explanations.
    Also, generate the new versions of the code (both original and modified).
    """
    diffs = []
    modified_code1 = ""
    modified_code2 = ""

    if type(node1) != type(node2):
        diffs.append(f"Different node types: {type(node1)} vs {type(node2)}")
        modified_code1 += unparse_code(node1)  # TODO: I think these are needed here
        modified_code2 += unparse_code(node2)
        return diffs, modified_code1, modified_code2

    # If the nodes are of the same type, compare their fields.
    if isinstance(node1, ast.AST):
        for field in node1._fields:
            value1 = getattr(node1, field, None)
            value2 = getattr(node2, field, None)

            # If the value is a list, compare each item in the list
            if isinstance(value1, list):
                if len(value1) != len(value2):
                    diffs.append(f"Different number of items in list '{field}': {len(value1)} vs {len(value2)}")
                # TODO: move this for into an else clause?
                for i, (v1, v2) in enumerate(zip(value1, value2)):
                    sub_diffs, sub_code1, sub_code2 = compare_ast_nodes(v1, v2)
                    diffs.extend(sub_diffs)
                    modified_code1 += sub_code1
                    modified_code2 += sub_code2
            else:
                if value1 != value2:  # TODO: this is wrong
                    diffs.append(f"Different values in field '{field}': '{value1}' vs '{value2}'")
                    modified_code1 += unparse_code(node1)
                    modified_code2 += unparse_code(node2)
    return diffs, modified_code1, modified_code2


def find_differences(code1, code2):
    """
    Find and return the differences between two Python code snippets and also generate modified code.
    """
    # Parse the code snippets into ASTs
    # tree1 = parse_code(code1)
    # tree2 = parse_code(code2)
    #
    # # Compare the two ASTs
    # differences, modified_code1, modified_code2 = compare_ast_nodes(tree1, tree2)
    #
    # if differences:
    #     return "\n".join(differences), modified_code1, modified_code2
    # else:
    #     return "No differences found.", code1, code2
    return cd.difference(code1, code2, lang='python')  # TODO: language as global var
