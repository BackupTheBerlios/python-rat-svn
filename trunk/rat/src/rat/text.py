"""
This module contains to, very usefull utility functions, one for grabbing
the text selected on a certain `gtk.TreeBuffer`, the other creates an iterator
for manipulating searches to a `gtk.TreeBuffer`.
"""
__license__ = "MIT <http://www.opensource.org/licenses/mit-license.php>"
__author__ = "Tiago Cogumbreiro <cogumbreiro@users.sf.net>"
__copyright__ = "Copyright 2005, Tiago Cogumbreiro"

def get_buffer_selection (buffer):
    """Returns the selected text, when nothing is selected it returns the empty
    string."""
    bounds = buffer.get_selection_bounds()
    if bounds == ():
        return ""
    else:
        return buffer.get_slice(*bounds)

def search_iterator (text_buffer, search_text, find_forward = True, start_in_cursor = True):
    """
    This function implements an iterator for searching a gtk.TextBuffer for
    a certain string.
    
    It supports forward and backwards search.
    
    It also supports finding from the start or from where the cursor is located.
    """

    if start_in_cursor:
        bounds = text_buffer.get_selection_bounds ()
        if len (bounds) == 0:
            text_iter = text_buffer.get_iter_at_mark(text_buffer.get_insert())
        else:
            text_iter = find_forward and bounds[1] or bounds[0]
    else:
        if find_forward:
            text_iter = text_buffer.get_start_iter()
        else:
            text_iter = text_buffer.get_end_iter()
    
    first_iter = None
    bounds = 1
    while bounds is not None:
        if find_forward:
            search = text_iter.forward_search
            
        else:
            search = text_iter.backward_search
            
        bounds = search (search_text, gtk.TEXT_SEARCH_TEXT_ONLY, limit = None)
        
        if bounds is None:
            break
            
        yield bounds
        
        if find_forward:
            text_iter = bounds[1]
        else:
            text_iter = bounds[0]