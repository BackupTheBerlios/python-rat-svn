"""
GConf Widget Persistency is a module for maintaining persistency between your
existing widgets and the GConf keys. Not only it forces the schema you've
defined for the key but also preserves the widget state, for example making it
insensitive when the GConf key is insensitive.

It also implements a representation of a gconf key (GConfValue) that handles
the repetitive hassles of a maintaining its integrity. 
"""
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"
__copyright__ = "Copyright 2005, Tiago Cogumbreiro"

import gconf
import gobject

class Spec:
    """
    The spec is an adapter between a GConfValue and a Python value,
    simplifying the conversion and the integrity.
    
    You should use L{Spec.STRING}, L{Spec.FLOAT}, L{Spec.INT} and L{Spec.BOOL}
    instead.
    """
    def __init__ (self, name, gconf_type, py_type, default):
        self.gconf_type = gconf_type
        self.py_type = py_type
        self.default = default
        self.name = name

Spec.STRING = Spec ("string", gconf.VALUE_STRING, str, '')
Spec.FLOAT = Spec ("float", gconf.VALUE_FLOAT, float, 0.0)
Spec.INT = Spec ("int", gconf.VALUE_INT, int, 0)
Spec.BOOL = Spec ("bool", gconf.VALUE_BOOL, bool, True)
   
def data_file_chooser (button, key, use_directory = False, use_uri = True, default = None, client = None):
    """
    
    Associates a L{gwp.Data} to a gtk.FileChooserButton. This is an utility function
    that wrapps around L{gwp.Data}.

    @param button: the file chooser button
    @param key: the gconf key
    @param use_directory: boolean variable setting if it's we're using files or directories.
    @param use_uri: boolean variable setting if we're using URI's or normal filenames.
    @param default: the default value that L{gwp.GConfValue} falls back to.
    @param client: The GConfClient
    @type button: U{gtk.FileChooserButton <http://pygtk.org/pygtk2reference/class-gtkfilechooserbutton.html>}
    
    @rtype: L{gwp.Data}.
    """
    if not use_directory and not use_uri:
        getter = button.get_filename
        setter = button.set_filename
    elif not use_directory and use_uri:
        getter = button.get_uri
        setter = button.set_uri
    elif use_directory and not use_uri:
        getter = button.get_current_folder
        setter = button.set_current_folder
    elif use_directory and use_uri:
        getter = button.get_current_folder_uri
        setter = button.set_current_folder_uri
    
    return Data (button, getter, setter, "selection-changed", GConfValue (key, Spec.STRING, default = default, client = client), is_lazy = True)

def data_entry (entry, key, data_spec = Spec.STRING, default = None, client = None):
    """
    Associates to a U{gtk.Entry <http://pygtk.org/pygtk2reference/class-gtkentry.html>}
    """
    return Data (entry, entry.get_text, entry.set_text, "changed", GConfValue (key, data_spec, default, client))

def data_spin_button (spinbutton, key, use_int = True, default = None, client = None):
    """
    Associates to a U{gtk.SpinButton <http://pygtk.org/pygtk2reference/class-gtkspinbutton.html>}
    @param use_int: when set to False it uses floats instead.
    """
    
    if use_int:
        return Data (spinbutton, spinbutton.get_value_as_int, spinbutton.set_value, "value-changed", GConfValue (key, Spec.INT, default, client))
    else:
        return Data (spinbutton, spinbutton.get_value, spinbutton.set_value, "value-changed", GConfValue (key, Spec.FLOAT, default, client))

def data_toggle_button (toggle, key, default = None, client = None):
    """
    This is to be used with a U{gtk.ToggleButton <http://pygtk.org/pygtk2reference/class-gtktogglebutton.html>}
    """
    return Data (toggle, toggle.get_active, toggle.set_active, "toggled", GConfValue (key, Spec.BOOL, default, client))

class GConfValue (object):
    """
    The GConfValue represents the GConf key's data. You define a certain schema
    (or type of data) and GConfValue keeps track of its integrity. It adds the
    possibility to define a default value to be used when the key is inexistent
    or contains an invalid data type. You can also define callbacks that notify
    you when the key is altered.
    
    Taken from U{GAW Introduction <http://s1x.homelinux.net/documents/gaw_intro>}::

        import gwp, gconf, gtk
        gconf.client_get_default ().add_dir ("/apps/gwp", gconf.CLIENT_PRELOAD_NONE)

        key_str = gwp.GConfValue (
          key = "/apps/gwp/key_str",
          data_spec = gwp.Spec.STRING
        )

        def on_changed (*args):
          global key_str
          print key_str.key, "=", key_str.data
          gtk.main_quit ()
          
        tmp.set_callback (on_changed)
        tmp.data = "Hello world"

        gtk.main ()
    """
    def __init__ (self, key, data_spec, client = None, **kwargs):
        if not client:
            client = gconf.client_get_default ()

        self.client = client
    
        self.key = key
        
        self.data_spec = data_spec
        
        # init the source id
        self._notify_id = None
        
        if "default" in kwargs:
            self.default = kwargs["default"]

    ############
    # data_spec
    def get_data_spec (self):
        return self._data_spec

    def set_data_spec (self, data_spec):
        self._data_spec = data_spec
        self._setter = getattr (self.client, "set_" + data_spec.name)
        self._getter = getattr (self.client, "get_" + self.data_spec.name)
    
    data_spec = property (get_data_spec, set_data_spec)
    
    #######
    # data
    def get_data (self):
        try:
            val = self._getter (self.key)
        except gobject.GError:
            return self.default
            
        if val is None:
            return self.default
        return val
    
    def set_data (self, value):
        val = self.get_data ()
        if val != value:
            self._setter (self.key, value)
    
    data = property (get_data, set_data)
    

    ##########
    # default
    def get_default (self):
        return getattr (self, "_default", self.data_spec.default)

    def set_default (self, default):
        self._default = default

    def unset_default (self):
        del self._default

    default = property (get_default, set_default, unset_default)
    
    ################
    # Other methods
    def set_callback (self, on_changed):
        assert callable (on_changed)
        
        if self._notify_id is not None:
            self.client_notify_remove (self._notify_id)
            self._notify_id = None
        
        if on_changed is not None:
            self._notify_id = self.client.notify_add (
                self.key,
                on_changed
            )
    
    def __del__ (self):
        self.set_callback (None)
    
    def reset_default (self):
        """
        Resets the default value to the one present in the Spec
        """
        if hasattr (self, "_default"):
            del self.default


class RadioButtonData:
    """
    A radio_group is a dictionary that associates a gconf boolean key
    with a radio button::
    
        data = RadioButtonData (
            {
                'cheese': cheese_btn,
                'ham': ham_btn,
                'fish': fish_btn
            },
        )
        data.selected_by_default = 'ham'
    
        selected_value = data.data
        data.data = 'fish'
    """
    
    selected_by_default = None
    
    def __init__ (self, widgets, key, client = None):
        self.widgets = widgets
        self.keys = {}
        self.gconf_value = GConfValue (key, Spec.STRING, client)
        self.gconf_value.set_callback (self._on_gconf_changed)
        
        notify_widget = False
        for key, widget in widgets.iteritems ():
            if not notify_widget:
                widget.connect ("toggled", self._on_widget_changed)
                notify_widget = True
            widget.connect ("destroy", self._on_destroy)

            self.keys[widget] = key
            
        self.sync_widget ()
        
    def _on_destroy (self, widget):
        key = self.keys[widget]
        del self.widgets[key]
        # Set the widget to none so that the key still exists
        self.keys[widget] = None
        
    def _get_active (self):
        for radio in self.keys:
            if radio is not None and radio.get_active ():
                return radio
        return None
    
    def _on_widget_changed (self, radio_button):
        # Update gconf entries
        self.sync_gconf ()
        
    def _on_gconf_changed (self, client, conn_id, entry, user_data = None):
        
        data_spec = self.gconf_value.data_spec

        for widget in self.keys:
            widget.set_sensitive (client.key_is_writable (self.gconf_value.key))
            
        if entry.value is None or entry.value.type != data_spec.gconf_type:
            self.sync_gconf ()

        else:
            self.sync_widget ()
            
    def sync_widget (self):
        key = self.gconf_value.data
        
        if key in self.widgets:
            # value is in radio group
            self.widgets[key].set_active (True)
        
        else:
            # When there is a default value, set it
            if self.selected_by_default is not None:
                self.data = self.selected_by_default
            
            # Otherwise deselect all entries
            active = self._get_active ()
            if active is not None:
                # Unset the active radio button
                active.set_active (False)
        self.sync_gconf ()
    
    def sync_gconf (self):
        active = self._get_active ()
        if active is not None:
            self.gconf_value.data = self.keys[active]
        else:
            self.gconf_value.reset_default ()
        
    def set_data (self, value):
        self.sync_gconf ()
        self.gconf_value = value
        
    def get_data (self):
        self.sync_gconf ()
        return self.gconf_value.data
    
    data = property (get_data, set_data)

class OutOfSyncError (StandardError): pass

class Data (object):
    """
    This utility class acts as a synchronizer between a widget and gconf entry.
    This data is considered to have problematic backends, since widgets can be
    destroyed and gconf can have integrity problems (for example permissions or
    schema change).
    
    To use the gwp.Data object you just need to specify it's associated type
    (the schema) and optionally a default value.
    
    Here's a simple example on how to use it (taken from U{GAW Introduction <http://s1x.homelinux.net/documents/gaw_intro>},
    this was this module's former name)::
    
        import gaw
        import gtk
        import gconf
        # Monitor the key, so gaw can listen for gconf events
        gconf.client_get_default ().add_dir ("/apps/gaw", gconf.CLIENT_PRELOAD_NONE)
  
        win = gtk.Window (gtk.WINDOW_TOPLEVEL)
        entry = gtk.Entry ()
        entry.show ()
        # bind the key with the widget
        gconf_data = gaw.data_entry (entry, "/apps/gaw/str_key")
        win.add (entry)
        win.show ()
        gtk.main ()            
    """
    
    def __init__ (self, widget, widget_getter, widget_setter, changed_signal, gconf_value, is_lazy = False):
        """
        @param widget: This is the widget this is observing.
        @type widget: gtk.Widget
        
        @param widget_getter: The function that gets the widget's data
        
        @param widget_setter: The function that sets the widget's data
        
        @param changed_signal: The name of the signal this observer should be
        connecting too.
        
        @param gconf_value: The value stored in GConf
        
        @type gconf_value: gwp.GConfValue
        """
        self.widget = widget
        self._widget_setter = widget_setter
        self._widget_getter = widget_getter
        self.gconf_value = gconf_value
        self.is_lazy = is_lazy
        
        gconf_value.set_callback (self._on_gconf_changed)

        widget.connect (changed_signal, self._on_widget_changed)
        widget.connect ("destroy", self._on_destroy)

        if self.widget is not None:
            self.sync_widget ()
    
    def get_data (self, sync_gconf = True):
        if sync_gconf:
            self.sync_gconf ()
            
        return self.gconf_value.data
    
    def set_data (self, data):
        assert isinstance (data, self.gconf_value.data_spec.py_type)
        try:
            self.gconf_value.data = data
        except gobject.GError:
            # when something goes wrong there's nothing we can do about it
            pass

    data = property (get_data, set_data, None, "The data contained in this component.")

    def _on_destroy (self, widget):
        self._widget = None
        
    def _on_widget_changed (self, *args):
        if self.widget is None:
            return
        # Widget has changed its value, we need to update the GConfValue
        self.sync_gconf (from_widget = True)
            
    def _on_gconf_changed (self, client, conn_id, entry, user_data = None):
        # Something was updated on gconf
        if self.widget is None:
            return
        
        data_spec = self.gconf_value.data_spec
        
        self.widget.set_sensitive (client.key_is_writable (self.gconf_value.key))
        if entry.value is not None and entry.value.type == data_spec.gconf_type:
            converter = getattr (entry.value, 'get_' + data_spec.name)
            self._widget_setter (converter ())
            
        else:
            self._widget_setter (self.gconf_value.default)
            
        # Because widgets can validate data, sync the gconf entry again
        self.sync_gconf(from_gconf = True)
    
    def sync_widget (self):
        """
        Synchronizes the widget in favour of the gconf key. You must check if
        there is a valid widget before calling this method.
        """
        assert self.widget, "Checking if there's a valid widget is a prerequisite."

        # Set the data from the gconf_value
        val = self.gconf_value.data

        if val is not None:
            self._widget_setter (val)
        
        if self.is_lazy:
            gobject.idle_add (self._check_sync, val)
        else:
            self._check_sync (val)
    
    def _check_sync (self, value):
        # Because some widgets change the value, update it to gconf again
        new_val = self._widget_getter ()
        if new_val is None:
            raise OutOfSyncError ("Widget getter returned 'None' after a value was set.")
        
        # The value was changed by the widget, we updated it back to GConfValue
        if value != new_val:
            self.sync_gconf ()
    
    def sync_gconf (self, from_widget = False, from_gconf = False):
        """
        Synchronizes the gconf key in favour of the widget. You must check if
        there is a valid widget before calling this method.
        """
        assert self.widget, "Checking if there's a valid widget is a prerequisite."
        # First we 
        val = self._widget_getter ()
        if val is None:
            return
            #val = self.gconf_value.default

        try:
            self.gconf_value.data = val
        except gobject.GError:
            raise OutOfSyncError

            new_val = self.gconf_value.data
            if val != new_val:
                raise OutOfSyncError
            
            
