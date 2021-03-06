import bge

def _strip(text_split):
    return [
        w for w in text_split
        if w not in {"in", "at", "an", "the", "is", "to", "am"}]


def parse_node(p, text):
    """ Given some text, return an object. """
    scene = bge.logic.getCurrentScene()
    node = p.get_node_fuzzy(text)
    return node


def _parse_command__verb_object(n, p, text, fn):
    """ General action on object """
    text_split = text.lower().split()
    text_split = _strip(text_split[1:])
    text_remainder = " ".join(text_split)
    try:
        node_subject = p.get_node_fuzzy(" ".join(text_split))
    except KeyError as e:
        return e.args[0]
    return fn(n, p, node_subject)


def parse_command(n, p, text):
    """ Parse input, call action (or inspect), and return output """

    # relates to action at the moment
    from . import action

    text_split = text.lower().split()

    # basic action/objects
    if text_split[0] in {"l", "x", "ls", "look", "inspect", "check", "investigate", "who"}:
        if len(text_split) > 1:
            return _parse_command__verb_object(n, p, text, action.inspect_node)
        else:
            #action.describe()
            # Can just return, because UI always renders location description.
            return ""
    if text_split[0] in {"w", "where", "locate"}:
        if len(text_split) > 1:
            return _parse_command__verb_object(n, p, text, action.whereis_node)
        else:
            action.whereis_node(n, p, p.root)
    if text_split[0] in {"e", "embody", "become", "possess", "cd"}:
        return _parse_command__verb_object(n, p, text, action.embody_node)
    if text_split[0] in {"t", "eat", "chew", "gobble"}:
        return _parse_command__verb_object(n, p, text, action.eat_node)
    if text_split[0] in {"take", "get", "grab"}:
        return _parse_command__verb_object(n, p, text, action.take_node)
    if text_split[0] in {"drop"}:
        return action.drop_any(n, p)
    if text_split[0] in {"g", "move", "go", "mv"}:
        return _parse_command__verb_object(n, p, text, action.move_to)

    if text_split[0] in {"q", "quit", "exit"}:
        bge.logic.endGame()
        return ""

    return "Not sure what you mean"

