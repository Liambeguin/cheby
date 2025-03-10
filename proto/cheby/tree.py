"""Classes to represent a Cheby tree.
   This is mostly data oriented:
   - the variables represent user data.  The name of the attribute has
     no prefix.  These variables shouldn't be modified by the program,
     so that the original file can be rewritten (without the comments).
     They musnt' have an 'X_' prefix.
   - Extensions are stored as python data in a 'x_XXX' field, where 'XXX' is
     the name of the extension.
   - Computed values have the 'c_' prefix (layout module).
   - HDL fields have the 'h_' prefix (gen_hdl module). """

BYTE_SIZE = 8


class Node(object):
    """Base class for any Cheby node.
       :var parent: the parent of that node, None for the root.
       """
    _dispatcher = {}    # Class variable for visitor.

    def __init__(self, parent):
        self._parent = parent

    @property
    def parent(self):
        return self._parent

    def visit(self, name, *args, **kwargs):
        return self._dispatcher[name](*args, **kwargs)


class NamedNode(Node):
    """Many Cheby nodes have a name/description/comment.  Create a
       common class for them."""
    _dispatcher = {}

    def __init__(self, parent):
        super(NamedNode, self).__init__(parent)
        self.name = None
        self.description = None
        self.comment = None		# One-line comment for generated code
        self.note = None
        # Computed values
        self.c_address = None
        self.c_size = None
        self.c_align = None

    def get_path(self):
        """Return the full path (from the root) of this node."""
        if self.name is None:
            p = '/??'
        else:
            p = '/' + self.name
        if self._parent is None:
            return p
        else:
            return self._parent.get_path() + p

    def get_root(self):
        if self._parent is None:
            return self
        else:
            return self._parent.get_root()

    def get_ext_node(self, ext):
        "Get the object :name ext: or None if it doesn't exist"
        if not hasattr(self, ext):
            return None
        return getattr(self, ext)

    def get_extension(self, ext, name, default=None):
        x = self.get_ext_node(ext)
        if x is None:
            return default
        return x.get(name, default)


class CompositeNode(NamedNode):
    """Base class for Cheby nodes with children; they are also named.
       :var children: is the list of children."""
    _dispatcher = {}

    def __init__(self, parent):
        super(CompositeNode, self).__init__(parent)
        self.address = None
        self.align = None
        self.size_str = None     # Size (possibly with units)
        self.size_val = None     # Value of size_str.
        self.children = []
        # Computed variables
        self.c_size = None       # Compute by layout (aligned)


class Root(CompositeNode):
    _dispatcher = {}
    NAME = "MemoryMap"

    def __init__(self):
        super(Root, self).__init__(None)
        self.bus = None
        self.word_endian = None
        self.version = None        # Semantic version (as a string)
        self.ident = None          # x-map-info:ident
        self.memmap_version = None # x-map-info:memmap-version
        self.address_spaces = []
        self.x_enums = []
        self.schema_version = {}
        # Computed variables
        self.c_word_size = None       # Word size in bytes
        self.c_addr_word_bits = None  # log2(c_word_size)
        self.c_filename = None        # Filename for the tree.
        self.c_word_endian = None     # word endianness ('any', 'little', 'big')
        self.c_version = None
        self.c_memmap_version = None
        self.c_enums_dict = {}      # Dictionnary from enum name to enum node.
        self.c_address_spaces_map = {}


class Block(CompositeNode):
    _dispatcher = {}
    NAME = "Block"

    def __init__(self, parent):
        super(Block, self).__init__(parent)
        self.origin = None


class Submap(CompositeNode):
    _dispatcher = {}
    NAME = "Submap"

    def __init__(self, parent):
        super(Submap, self).__init__(parent)
        self.filename = None
        self.interface = None
        self.include = None
        self.address_space = None
        # Computed variables
        self.c_submap = None


class Repeat(CompositeNode):
    _dispatcher = {}
    NAME = "Repeat"

    def __init__(self, parent):
        super(Repeat, self).__init__(parent)
        self.count = None


class Memory(CompositeNode):
    _dispatcher = {}
    NAME = "Memory"

    def __init__(self, parent):
        super(Memory, self).__init__(parent)
        self.memsize_val = None
        self.memsize_str = None
        self.interface = None
        self.c_depth = None       # Memory depth (memsize / elsize)


class Reg(NamedNode):
    _dispatcher = {}
    NAME = "Reg"

    def __init__(self, parent):
        super(Reg, self).__init__(parent)
        self.width = None
        self.type = None
        self.access = None      # Mandatory, always defined.
        self.address = None
        self.children = []
        self.preset = None
        self.constant = None
        # Computed (by layout)
        self.c_size = None      # Size in bytes
        self.c_rwidth = None    # Width of the register
        # (can be smaller than the width if data are partially generated or
        # used, like the rmw)
        self.c_iowidth = None   # Width of I/O wires
        self.c_mwidth = None    # Width for the memory map (== self.width)
        self.c_nwords = None    # Number of words for multi-words registers
        self.c_align = None     # Alignment
        self.c_type = None      # Type. None if register with fields.

    def has_fields(self):
        """True if the register has one or more fields defined by the user.
        False when the whole register is standalone"""
        return len(self.children) != 1 \
            or not isinstance(self.children[0], FieldReg)


class FieldBase(NamedNode):
    "Base for Field and FieldReg"
    NAME = "Field"

    def __init__(self, parent):
        super(FieldBase, self).__init__(parent)
        self.hi = None
        self.lo = None
        self.preset = None
        self.type = None
        self.c_type = None


class Field(FieldBase):
    "A field within a register."
    pass


class FieldReg(FieldBase):
    "A pseudo field for a register without fields."
    pass


class EnumVal(NamedNode):
    def __init__(self, parent):
        super(EnumVal, self).__init__(parent)
        self.value = None


class EnumDecl(CompositeNode):
    def __init__(self, parent):
        super(EnumDecl, self).__init__(parent)
        self.width = None       # Width or None
        self.c_width = None     # computed width.
        # children are EnumVal.


class AddressSpace(CompositeNode):
    def __init__(self, parent):
        super(AddressSpace, self).__init__(parent)
        # Children are nodes

class AddressSpaces(CompositeNode):
    def __init__(self, parent):
        super(AddressSpaces, self).__init__(parent)
        # children are AddressSpace


class Visitor(object):
    def visit(self, n, *args, **kwargs):
        return n.visit(self.__class__, self, n, *args, **kwargs)

    @classmethod
    def register(cls, typ):
        def fun(f):
            typ._dispatcher[cls] = f
            return f
        return fun
