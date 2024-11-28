#! /usr/bin/env python
class Print:
  def __init__(self):
    """  Placeholder init """ 
    pass  

  def PrintEvent(self, event, prefix=''):
    """ Print this event in human readable form """ 
    for field in event.fields: # Loop through array elements in the event
      value = event[field] # Get the value
      full_field = f'{prefix}{field}' # Set full field using prefix provided in function call
      if hasattr(value, 'fields') and value.fields: # Check for subfields 
        self.PrintEvent(value, prefix=f"{full_field}.")  # Recurse into subfields
      else: # If no further subfields, print the full field and value
        print(f'{full_field}: {value}')
    return

  def PrintNEvents(self, array_, n=1):
    """  Print n events human readable form """ 
    print(f"\n---> Printing {n} event(s)...\n")
    for i, event in enumerate(array_, start=1): # Iterate event-by-event 
      print(f'-------------------------------------------------------------------------------------')
      self.PrintEvent(event) # Call self.print_event() 
      print(f'-------------------------------------------------------------------------------------\n')
      if i == n: # Return if 'n' is reached
        return 
