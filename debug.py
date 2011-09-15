import sys
import traceback
import inspect
from pycurlbrowser.browser import Browser

def debug_exceptions(type, value, tb):
    base_name = "debug"

    # stick a trace in a file
    with open(base_name + '.trace', 'w') as tracefile:
        tracefile.write(str(inspect.getargvalues(tb.tb_frame)))
        tracefile.write("\n\n")
        traceback.print_tb(tb, file=tracefile)

    # find a browser object and save the current page
    # TODO: as this is saving the first one it comes across, that might well be the wrong one...
    for frame, _, _, _, _, _ in inspect.getinnerframes(tb):
        for v in inspect.getargvalues(frame).locals.values():
            if isinstance(v, Browser):
                v.save(base_name + '.html')
                break

    # then call the default handler
    sys.__excepthook__(type, value, tb)
