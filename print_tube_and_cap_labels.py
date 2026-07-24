import socket

def print_to_zebra(printer_host, printer_port, zpl_data):
    """Sends ZPL code to a networked Zebra printer via raw socket."""
    try:
        # Create a network socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the printer
        print(f"Connecting to {printer_host}:{printer_port}...")
        s.connect((printer_host, printer_port))

        # Send the ZPL command (must be encoded as bytes)
        s.send(zpl_data.encode('utf-8'))

        # Close the connection
        s.close()
        print("Label sent successfully!")

    except Exception as e:
        print(f"Failed to print. Error: {e}")

# --- Configuration ---

# Use your printer's hostname or its actual IP address
PRINTER_HOST = "biie-label11"
PRINTER_PORT = 9100

# Printer resolution in dots-per-inch (203 for most Zebra desktop printers
# like the ZD420/ZD421, 300 for higher-res models). Check the printer's
# config label if unsure.
DPI = 203

def inch(value):
    """Convert inches to printer dots."""
    return round(value * DPI)

# --- Label geometry ---
# This label stock has a rectangular body label followed by a round cap
# label on the same row (see photo). Both are printed in a single ^XA..^XZ
# job since they share the same physical row. Measure your actual label
# sheet with a ruler and adjust these if the printout doesn't line up.

RECT_X = inch(0.25)          # left margin to the rectangle label
RECT_Y = inch(0.25)          # top margin to the rectangle label
LINE_HEIGHT = inch(0.16)     # vertical spacing between the 3 stacked lines on the rectangle
MAIN_FONT_SIZE = 20          # font height/width (dots) for each of the 3 rectangle lines

CIRCLE_DIAMETER = inch(0.4)  # diameter of the round cap label, used as the text-centering width below
CIRCLE_FONT_SIZE = 18        # font height/width (dots) for the cap's index text

# The circle position is NOT derived from the rectangle geometry above -
# on this label stock the die-cut spacing doesn't line up with that math,
# which is what caused the cap text to print left-of-center. Tune CIRCLE_X
# (right/left) and CIRCLE_Y (down/up) directly: print a test label, see
# which way the text is off, nudge by ~10-15 dots (~0.05-0.07in), reprint.
CIRCLE_X = inch(1.75)
CIRCLE_Y = inch(0.32)

# --- Label content ---
# Same 3-line rectangle layout as print_table_labels.py:
# line 1 = index, line 2 = sample name, line 3 = concentration.
# The cap label prints the index, centered in the circle.

INDEX_TEXT = "1234"            # line 1 on the rectangle, also printed on the cap
NAME_TEXT = "Sample name"      # line 2 on the rectangle
CONC_TEXT = "10 mg/mL"         # line 3 on the rectangle
QUANTITY = 1                   # number of rows (main + cap pairs) to print

# --- The Label Design (ZPL Code) ---
# ^XA starts the label, ^XZ ends the label.
# ^FO sets the X/Y coordinates. ^A0N sets the font. ^FD is the text data.
# ^FB wraps/justifies text within a field block, used here to center the
# cap text inside the small circle.
# ^PQ sets the number of labels (rows) to print, eg. 10
ZPL_CODE = f"""
^XA
^FO{RECT_X},{RECT_Y}^A0N,{MAIN_FONT_SIZE},{MAIN_FONT_SIZE}^FD{INDEX_TEXT}^FS
^FO{RECT_X},{RECT_Y + LINE_HEIGHT}^A0N,{MAIN_FONT_SIZE},{MAIN_FONT_SIZE}^FD{NAME_TEXT}^FS
^FO{RECT_X},{RECT_Y + 2 * LINE_HEIGHT}^A0N,{MAIN_FONT_SIZE},{MAIN_FONT_SIZE}^FD{CONC_TEXT}^FS
^FO{CIRCLE_X},{CIRCLE_Y}^A0N,{CIRCLE_FONT_SIZE},{CIRCLE_FONT_SIZE}^FB{CIRCLE_DIAMETER},1,0,C,0^FD{INDEX_TEXT}^FS
^PQ{QUANTITY}
^XZ
"""

# Run the function
print_to_zebra(PRINTER_HOST, PRINTER_PORT, ZPL_CODE)
