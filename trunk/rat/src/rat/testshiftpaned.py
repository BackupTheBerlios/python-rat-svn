import unittest
import gtk

from shiftpaned import ShiftPaned, SHOW_BOTH, SHOW_LEFT, SHOW_RIGHT

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
    unittest.main()


