import bge
import blf

FONT_SIZE = 40
SMART_WRAP = True
MARGIN = 0.1

globals = {
    "SCROLLBACK": "",
    "FONT": "spirit",
    "PERSPECTIVE": None,
    "NARRATOR": None,
    }

# ------------------------------------------------------------------------------
# Drawing


FONTS = {
    "stone": "//fonts/Caesar_Dressing/CaesarDressing-Regular.ttf",
    "heavywood": "//fonts/Freckle_Face/FreckleFace-Regular.ttf",
    "lightwood": "//fonts/Rum_Raisin/RumRaisin-Regular.ttf",
    "water": "//fonts/Indie_Flower/IndieFlower.ttf",
    "spirit": "//fonts/Mystery_Quest/MysteryQuest-Regular.ttf",
    "metal": "//fonts/Russo_One/RussoOne-Regular.ttf",
    }

font_ids = {}


def get_font(name):
    if name in font_ids:
        return font_ids[name]
    try:
        font_path = bge.logic.expandPath(FONTS[name])
    except KeyError:
        print('Warning: unknown font %s' % name)
        font_ids[name] = 0
    else:
        font_ids[name] = blf.load(font_path)
    return font_ids[name]


def draw_text(text):
    """
    Draws all text
    """
    def draw_block(text):
        pass

    font_id = get_font(globals['FONT'])

    import bgl
    from bge import render, logic

    """write on screen"""
    width = render.getWindowWidth()
    height = render.getWindowHeight()

    # OpenGL setup
    bgl.glMatrixMode(bgl.GL_PROJECTION)
    bgl.glLoadIdentity()
    bgl.gluOrtho2D(0, width, 0, height)
    bgl.glMatrixMode(bgl.GL_MODELVIEW)
    bgl.glLoadIdentity()
    bgl.glColor3f(1, 1, 1)

    # BLF drawing routine
    dim = min(width, height)
    x, y = (dim * MARGIN), (dim * (1.0 - MARGIN))
    blf.size(font_id, FONT_SIZE, 72)

    if not SMART_WRAP:
        blf.position(font_id, x, y, 0.0)
        blf.draw(font_id, text)
    else:
        text_lines = text.split("\n")
        for text_line in text_lines:
            text_split = []
            text_remainder = text_line.split()
            while text_remainder:
                text_test = ""
                while text_remainder and blf.dimensions(font_id, text_test)[0] < width - (MARGIN * 2 * dim):
                    text_split.append(text_remainder.pop(0))
                    text_test = " ".join(text_split)
                if text_remainder and len(text_split) > 1:
                    text_remainder.insert(0, text_split.pop())
                    text_test = " ".join(text_split)
                blf.position(font_id, x, y, 0.0)
                blf.draw(font_id, text_test)
                text_split.clear()
                y -= FONT_SIZE * 1.5
            # \n
            y -= FONT_SIZE * 2


def draw_cb():
    """Run on redraw"""
    text = draw_text_calc()  # could cache

    draw_text(text)


def draw_init(cont):
    """Only run once to setup callback"""

    import bge
    globals["own"] = cont.owner

    import bge
    scene = bge.logic.getCurrentScene()
    scene.post_draw.append(draw_cb)


def draw_text_calc():
    """Collects all info and creates the text to draw"""

    own = globals["own"]
    text = own["Text"]

    return globals["SCROLLBACK"] + "\n> " + text


# ------------------------------------------------------------------------------
# Execution


def exec_init(cont):
    import tba
    import tba.action
    import tba.waypoints
    sce = bge.logic.getCurrentScene()


    # this could be moved  to action.py
    ob = sce.objects["_WAYPOINTS"]
    globals["WAYPOINTS"] = tba.waypoints.parse_nodegraph(ob)
    ob.endObject()


    globals["NARRATOR"] = tba.render.Narrator()
    globals["PERSPECTIVE"] = tba.render.Perspective(sce.active_camera)

    # autoexec
    from .parse import parse_command
    n = globals["NARRATOR"]
    p = globals["PERSPECTIVE"]
    globals["SCROLLBACK"] += "\n" + parse_command(n, p, "embody statue")


def exec(cont):

    if not cont.sensors[0].positive:
        return

    # until we have bigger
    globals["SCROLLBACK"] = ""

    own = globals["own"]
    text_command = own["Text"]
    own["Text"] = ""
    if not text_command:
        return
    # TODO

    import tba.render
    sce = bge.logic.getCurrentScene()

    if 0:
        n = tba.render.Narrator()
        p = tba.render.Perspective(sce.active_camera)
    else:
        n = globals["NARRATOR"]
        p = globals["PERSPECTIVE"]


    from .parse import parse_command

    text_ls = []
    text_ls.append("> " + text_command)
    text_ls.append(parse_command(n, p, text_command))

    p = globals["PERSPECTIVE"]
    text_ls.append(" ".join(n.describe_scene(p)))

    p.prettyprint()


    globals["SCROLLBACK"] += "\n".join(text_ls)

    #print(text)


def update_filter(c):
    sce = bge.logic.getCurrentScene()
    o = c.owner
    o.worldPosition = sce.active_camera.worldPosition
    o.worldOrientation = sce.active_camera.worldOrientation
