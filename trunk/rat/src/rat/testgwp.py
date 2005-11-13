__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"
__copyright__ = "Copyright 2005, Tiago Cogumbreiro"

import unittest
import gwp
import gconf
import gtk

GCONF_KEY = "/apps/gwp/key_str"

class TestGConfValue (unittest.TestCase):
    def setUp(self):
        self.gconf = gconf.client_get_default ().add_dir ("/apps/gwp", gconf.CLIENT_PRELOAD_NONE)
        self.value = gwp.GConfValue (
          key = GCONF_KEY,
          data_spec = gwp.Spec.STRING
        )
        
    def test_set_default(self):
        self.assertEqual(self.value.data_spec, gwp.Spec.STRING)
        self.assertEqual(self.value.default, self.value.data_spec.default)
        self.value.default = "default"
        self.assertEqual(self.value.default, "default")
        self.value.unset_data()
        self.assertEqual(self.value.client.get_string(self.value.key), self.value.default)
        self.assertEqual(self.value.data, self.value.default)
    
    def test_set_data(self):
        self.value.unset_data()

        self.value.data = "foo"
        self.assertEqual(self.value.client.get_string(self.value.key), "foo")
        self.assertEqual(self.value.data, "foo")
    
    def callback1(self, *args):
        self.assertTrue(self.value.data, "bar")
        self.foo = True
        gtk.main_quit()
    
    def test_set_callback(self):
        self.value.unset_data()
        self.foo = False
        self.value.set_callback(self.callback1)
        self.value.data = "bar"
        gtk.main()
        self.assertTrue(self.foo)
    
    def test_default(self):
        self.assertEqual(self.value.default, "")
        self.value.default = "var"
        self.assertEqual(self.value.default, "var")
        self.value.reset_default()
        self.assertEqual(self.value.default, "")


class TestData(unittest.TestCase):
    def setUp(self):
        self.entry = gtk.Entry()
        self.entry.set_text("foo")
        self.value = gwp.data_entry(self.entry, GCONF_KEY)
        
    def test_unset_data(self):
        # First we make sure the integrity exists upon start
        self.assertEqual(self.entry.get_text(), self.value.data)
        self.assertEqual(self.value.gconf_value.data, self.value.data)
        
        # Now we reset the data, and check if it actually changed
        del self.value.data
        self.assertEqual(self.value.gconf_value.default, "")
        self.assertEqual(self.value.gconf_value.data, "")
        self.assertEqual(self.entry.get_text(), "")
        self.assertEqual(self.value.data, "")

        
    def test_widget_to_gconf(self):
        """From widget to gconf entry"""
        
        self.entry.set_text("bar")
        self.assertEqual(self.value.data, "bar")

    def test_gconf_to_widget(self):
        """From gconf to widget"""
        self.value.data = "foo"
        self.assertEqual(self.entry.get_text(), "foo")
    
    
    def test_destroy_widget(self):
        pass
    
    def test_widget_signal(self):
        pass
    
    def test_gconf_signal(self):
        pass
    
    def test_gconf_disabled(self):
        pass
    
    def test_sync_widget(self):
        pass
    
    def test_sync_gconf(self):
        pass

class TestRadioButtonData:
    def test_unset_data(self):
        pass
    
    def test_set_data(self):
        pass
    
    def test_destroy_widget(self):
        pass
    
    def test_widget_signal(self):
        pass
    
    def test_gconf_signal(self):
        pass
    
    def test_gconf_disabled(self):
        pass
    
    def test_sync_widget(self):
        pass
    
    def test_sync_gconf(self):
        pass
    
def main():
    unittest.main()

if __name__ == '__main__':
    main()