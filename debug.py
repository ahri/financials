import sys
import traceback
import inspect
from pprint import pprint
from pycurlbrowser.browser import Browser

def debug_exceptions(type, value, tb):
    base_name = "dump"

    # find a browser object in the stack
    frames = inspect.getinnerframes(tb)
    frames.reverse() # reversed because we want the innermost first
    browser = None
    for frame, _, _, _, _, _ in frames:
        for v in inspect.getargvalues(frame).locals.values():
            if isinstance(v, Browser):
                browser = v
                break

    localest = frames[0][0]

    # stick a trace in a file
    with open(base_name + '.trace', 'w') as tracefile:
        tracefile.write("Locals:\n")
        pprint(localest.f_locals, tracefile)
        tracefile.write("\n")
        if browser is not None:
            tracefile.write("URL: %s\n" % browser.url)
            tracefile.write("\n")
        traceback.print_tb(tb, file=tracefile)

    if browser is not None:
        browser.save(base_name + '.html')

    # then call the default handler
    sys.__excepthook__(type, value, tb)
