#! /usr/bin/env python
class Print:
  """
  Utility class for printing structured event data in a human-readable format.
    
  This class provides methods to print individual events or multiple events from
  an Awkward array, handling nested fields and subfields recursively.
  """
  def __init__(self):
    """ Placeholder init """ 
    pass  

  def PrintEvent(self, event, prefix=''):
    """
    Print a single event in human-readable format, including all fields and subfields.
    
    Args:
      event (awkward.Array): Event to print, containing fields and possibly subfields
      prefix (str, optional): Prefix to prepend to field names. Used for nested fields. Defaults to empty string.
                              
    Note:
      Recursively handles nested fields, e.g. field.subfield.value
    """ 
    for field in event.fields: # Loop through array elements in the event
      value = event[field] # Get the value
      full_field = f'{prefix}{field}' # Set full field using prefix provided in function call
      if hasattr(value, 'fields') and value.fields: # Check for subfields 
        self.PrintEvent(value, prefix=f"{full_field}.")  # Recurse into subfields
      else: # If no further subfields, print the full field and value
        print(f'{full_field}: {value}')
    return

  def PrintNEvents(self, array, n_events=1):
    """
    Print the first n events from an array in human-readable format.
        
    Args:
      array_ (awkward.Array): Array of events to print
      n (int, optional): Number of events to print. Defaults to 1.
            
    Note:
      Prints a separator line between events for better readability.
      Events are numbered starting from 1.
            
    Example:
      >>> printer = Print()
      >>> printer.PrintNEvents(events, n_events=2)
            
      ---> Printing 2 event(s)...
            
      -------------------------------------------------------------------------------------
      field1: value
      field2.subfield1: value
      -------------------------------------------------------------------------------------
      
      -------------------------------------------------------------------------------------
      field1: value
      field2.subfield1: value
      -------------------------------------------------------------------------------------
    """
    print(f"\n---> Printing {n_events} event(s)...\n")
    for i, event in enumerate(array, start=1): # Iterate event-by-event 
      print(f'-------------------------------------------------------------------------------------')
      self.PrintEvent(event) # Call self.print_event() 
      print(f'-------------------------------------------------------------------------------------\n')
      if i == n_events: # Return if 'n_events' is reached
        return 
