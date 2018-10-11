import cheby.parser as parser
import cheby.tree as tree
import cheby.layout as layout
import copy

def expand_x_hdl_field(f, n, dct):
    # Default values
    f.hdl_type = 'wire' if f._parent.access == 'ro' else 'reg'
    f.hdl_write_strobe = False
    f.hdl_read_strobe = False

    for k, v in dct.items():
        if k == 'type':
            f.hdl_type = parser.read_text(n, k, v)
        elif k == 'write-strobe':
            f.hdl_write_strobe = parser.read_bool(n, k, v)
        elif k == 'read-strobe':
            f.hdl_read_strobe = parser.read_bool(n, k, v)
        else:
            parser.error("unhandled '{}' in x-hdl of {}".format(
                  k, n.get_path()))

def expand_x_hdl(n):
    "Decode x-hdl extensions"
    x_hdl = getattr(n, 'x_hdl', {})
    if isinstance(n, tree.Field):
        expand_x_hdl_field(n, n, x_hdl)
    elif isinstance(n, tree.Reg):
        if not n.has_fields():
            expand_x_hdl_field(n.children[0], n, x_hdl)

    # Visit children
    if isinstance(n, tree.Submap):
        if n.filename is not None:
            expand_hdl(n.c_submap)
        return
    if isinstance(n, tree.CompositeNode):
        for el in n.children:
            expand_x_hdl(el)
    elif isinstance(n, tree.Reg):
        for f in n.children:
            expand_x_hdl(f)
    elif isinstance(n, tree.FieldBase):
        pass
    else:
        raise AssertionError(n)

def tree_copy(n, new_parent):
    if isinstance(n, tree.Reg):
        res = copy.copy(n)
        res._parent = new_parent
        res.children = [tree_copy(f, res) for f in n.children]
        return res
    elif isinstance(n, tree.FieldBase):
        res = copy.copy(n)
        res._parent = new_parent
        return res
    else:
        raise AssertionError(n)


def unroll_array(n):
    # Transmute the array to a block with children
    res = tree.Block(n._parent)
    res.name = n.name
    res.align = False
    res.c_address = n.c_address
    res.c_sel_bits = n.c_sel_bits
    res.c_blk_bits = n.c_blk_bits
    res.c_size = n.c_size
    assert len(n.children) == 1
    el = n.children[0]
    for i in range(n.repeat):
        c = tree_copy(el, res)
        c.name = "{}{:x}".format(el.name, i)
        c.c_address = i * n.c_elsize
        res.children.append(c)
    layout.build_sorted_children(res)
    return res


def unroll_arrays(n):
    if isinstance(n, tree.Reg):
        # Nothing to do.
        return n
    if isinstance(n, tree.Array) and n.align == False:
        # Unroll
        return unroll_array(n)
    if isinstance(n, tree.CompositeNode):
        nl = [unroll_arrays(el) for el in n.children]
        n.children = nl
        layout.build_sorted_children(n)
        return n
    raise AssertionError


def expand_hdl(root):
    expand_x_hdl(root)
    unroll_arrays(root)
    layout.set_abs_address(root, 0)
