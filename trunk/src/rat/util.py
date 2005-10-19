__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"
__copyright__ = "Copyright 2005, Tiago Cogumbreiro"

import gtk
import gobject

class ListSpec:
    """
    A spec is used to create `gtk.ListStore`s and to help 
    This class is used to help the manipulation of `gtk.ListStore`s.
    Here's an example on how to create one::

        my_spec = ListSpec (
            ("STATE", gobject.TYPE_INT),
            ("FILENAME", gobject.TYPE_STRING),
        )
    
    To create a ListStore, just do the following::
    
        store = my_spec.create_list_store ()
    
    To add data to a store you can access it directly::
    
        store.append ((1, "fooo"))
    
    Or by creating a dict object and converting it::
        
        row = {
            my_spec.STATE: 2,
            my_spec.FILENAME: "bar"
        }
        store.append (my_spec.to_tree_row (row))
        
    To access a column on a given row::
        for row in store:
            print "State:", row[my_spec.STATE]
            print "Filename:", row[my_spec.FILENAME]
    
    So here are it's features:
     * helps you centralize the specs of a given ListStore
     * makes your code more readable and less error-prone thanks to the
       created constants
    """
    def __init__ (self, *columns):
        names = []
        gtypes = []
        
        for (index, (name, gtype)) in enumerate (columns):
            assert name != "create_list_store" and name != "to_tree_row"
            
            setattr (self, name, index)
            gtypes.append (gtype)
            
        self.__gtypes = tuple (gtypes)
        
    def create_list_store (self):
        """Creates a new `gtk.ListStore`"""
        return gtk.ListStore (*self.__gtypes)
    
    def to_tree_row (self, mapping):
        """
        Converts a `dict` like object to a list suitable for adding to a 
        `gtk.ListStore`.
        """
        keys = mapping.keys ()
        keys.sort()
        return [mapping[key] for key in keys]

class SimpleListWrapper:
    def __init__ (self, store):
        self.store = store
        
    def __getitem__ (self, index):
        return self.store[index][0]
        
    def append (self, item):
        self.store.append ([item])

class SimpleList (gtk.TreeView):
    def __init__ (self, column_title, editable = True):
        gtk.TreeView.__init__(self)
        store = gtk.ListStore(str)
        self.set_model (store)
        r = gtk.CellRendererText()
        if editable:
            r.set_property ('editable', True)
            r.connect ('edited', self.__on_text_edited)
            
        if not column_title:
            self.set_headers_visible (False)
            column_title = ""
        col = gtk.TreeViewColumn(column_title, r, text = 0)
        self.append_column (col)
        self.wrapper = SimpleListWrapper (store)
        
    def get_simple_store(self):
        return self.wrapper
    
    def __on_text_edited (self, cell, path, new_text, user_data = None):
        self.get_model()[path][0] = new_text

gobject.type_register (SimpleList)

def iterate_all_children (widget):
        
    get_children = getattr (widget, "get_children", None)

    if get_children is None:
        return
    
    for child in get_children ():
        yield child

    get_submenu = getattr (widget, "get_submenu", None)
    
    if get_submenu is None:
        return
    
    sub_menu = get_submenu ()
    
    if sub_menu is not None:
        yield sub_menu


def print_widget_tree (widget, depth = 0):

    for child in iterate_all_children (widget):
        print ("  " * depth) + child.get_name ()
        print_widget_tree (child, depth + 1)

def find_widget_up (widget, name):
    """Finds a widget by name upwards the tree, by searching self and its
    parents"""
    
    assert widget is not None
    
    if widget.get_name () == name:
        return widget
    
    parent = widget.get_parent ()
    if parent is not None:
        return find_widget (parent, name)
    
    return None

def find_widget (widget, name):
    """Finds the widget by name downwards the tree, by searching self and its
    children."""
    
    assert widget is not None
    
    if widget.get_name () == name:
        return widget
        
    get_children = getattr (widget, "get_children", None)

    if get_children is None:
        return None
    
    for child in get_children ():
        w = find_widget (child, name)
        if w is not None:
            return w
    
    get_submenu = getattr (widget, "get_submenu", None)
    
    if get_submenu is None:
        return None
    
    sub_menu = get_submenu ()
    
    if sub_menu is not None:
        return find_widget (sub_menu, name)
    
    return None

def get_root_parent (widget):
    assert widget is not None
    p = widget.get_parent ()
    if not p:
        return widget
    return get_root_parent (p)

import traceback
def traceback_main_loop ():
    idle_add = gobject.idle_add
    
    def tb_idle_add (callback, *args, **kwargs):
        def wrapper (*args, **kwargs):
            try:
                return callback (*args, **kwargs)
            except:
                traceback.print_exc ()
        
        return idle_add (wrapper, *args, **kwargs)
    gobject.idle_add = tb_idle_add
    gobject.idle_add.idle_add = idle_add
    
    timeout_add = gobject.timeout_add
    
    def tb_timeout_add (interval, callback, *args, **kwargs):
        def wrapper (*args, **kwargs):
            try:
                return callback (*args, **kwargs)
            except:
                traceback.print_exc ()
        
        return timeout_add (interval, wrapper, *args, **kwargs)
        
    gobject.timeout_add = tb_timeout_add
    gobject.timeout_add.timeout_add = timeout_add

def untraceback_main_loop ():
    if hasattr (gobject.idle_add, "idle_add"):
        gobject.idle_add = gobject.idle_add.idle_add
        
    if hasattr (gobject.timeout_add, "timeout_add"):
        gobject.timeout_add = gobject.timeout_add.timeout_add
