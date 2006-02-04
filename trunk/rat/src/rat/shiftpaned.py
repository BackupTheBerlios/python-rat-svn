import gtk
import unittest

(
SHOW_LEFT,
SHOW_RIGHT,
SHOW_BOTH,
) = range(3)

def _remove_all(widget):
    map(widget.remove, widget.get_children())


class ShiftPaned(gtk.VBox):
    _state = SHOW_BOTH
    _left_args = ()
    _left_kwargs = {}
    _right_args = ()
    _right_kwargs = {}
    left_widget = None
    right_widget = None
    
    def has_both_widgets(self):
        return self.right_widget is not None and self.left_widget is not None
    
    def __init__(self, paned_factory=gtk.HPaned):
        self.paned = paned_factory()
        self.paned.show()
        super(ShiftPaned, self).__init__()
    
    def update_children(self):
        if self.has_both_widgets():
            _remove_all(self)
            _remove_all(self.paned)
            if self._state == SHOW_BOTH:
                self.add(self.paned)
                self.paned.pack1(
                    self.left_widget,
                    *self._left_args,
                    **self._left_kwargs
                )
                
                self.paned.pack2(
                    self.right_widget,
                    *self._right_args,
                    **self._right_kwargs
                )
            elif self._state == SHOW_LEFT:
                self.add(self.left_widget)
            elif self._state == SHOW_RIGHT:
                self.add(self.right_widget)
                
        elif len(self.get_children()) >= 1:
            self.remove(self.get_children()[0])
    
    def pack1(self, widget, *args, **kwargs):
        assert widget is not None
        self._left_args = args
        self._left_kwargs = kwargs
        self.left_widget = widget
        self.update_children()
    
    def pack2(self, widget, *args, **kwargs):
        assert widget is not None
        self._right_args = args
        self._right_kwargs = kwargs
        self.right_widget = widget
        self.update_children()
        
    def set_state(self, state):
        if state == self._state:
            return
        self._state = state
        self.update_children()

    def get_state(self):
        return self._state


class TestPaned(unittest.TestCase):
    def setUp(self):
        self.paned = ShiftPaned()

    def assertChild(self, widget):
        # Calls the super, dirty hack to get the real elements
        children = gtk.VBox.get_children(self.paned)
        if widget is None:
            self.assertEquals(0, len(children))
        else:
            self.assertEquals(1, len(children))
            self.assertEquals(children[0], widget)

    def assertState(self, state):
        self.assertEquals(state, self.paned.get_state())
        
    def test_paned(self):
        # It is initially empty
        self.assertChild(None)
        
        # When it contains only one element it remains empty
        lbl1 = gtk.Label("left")
        self.paned.pack1(lbl1)
        self.assertChild(None)
        
        # When it contaisn two elements it cointains the container of the
        # elements of the given type
        lbl2 = gtk.Label("right")
        self.paned.pack2(lbl2)
        
        # It should begin on 'SHOW_BOTH' state
        self.assertChild(self.paned.paned)
        self.assertState(SHOW_BOTH)
        
        # Changing it to SHOW_BOTH does no effect
        self.paned.set_state(SHOW_BOTH)
        self.assertChild(self.paned.paned)
        self.assertEquals(self.paned.paned.get_child1(), self.paned.left_widget)
        self.assertEquals(self.paned.paned.get_child2(), self.paned.right_widget)

        # Their children should be now filled
        self.paned.set_state(SHOW_LEFT)
        self.assertChild(self.paned.left_widget)
        
        # Now show the right
        self.paned.set_state(SHOW_RIGHT)
        self.assertChild(self.paned.right_widget)

if __name__ == '__main__':
    #unittest.main()
    p = ShiftPaned(gtk.VPaned)
    btn1 = gtk.Button("Show right only")
    btn2 = gtk.Button("Show left only")
    p.pack1(btn1)
    p.pack2(btn2)
    def on_click(btn):
        p.set_state(SHOW_RIGHT)
    btn1.connect("clicked", on_click)
    def on_click(btn):
        p.set_state(SHOW_LEFT)
    btn2.connect("clicked", on_click)
    btn1.show()
    btn2.show()
    w = gtk.Window()
    w.add(p)
    w.show_all()
    w.connect("delete-event", gtk.main_quit)
    gtk.main()


