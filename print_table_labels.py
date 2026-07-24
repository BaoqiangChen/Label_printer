import socket
import sys

try:
    import openpyxl
except ImportError:
    sys.exit("Missing dependency. Install it with: pip3 install openpyxl")

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
        print("Label(s) sent successfully!")

    except Exception as e:
        print(f"Failed to print. Error: {e}")

# --- Configuration ---

# Use your printer's hostname or its actual IP address
PRINTER_HOST = "biie-label11"
PRINTER_PORT = 9100

# Path to the Excel table. First row is the header (Index, Sample name,
# Concentration, Unit); every row after that is one tube (one main + cap label pair).
EXCEL_PATH = sys.argv[1] if len(sys.argv) > 1 else "./print_table.xlsx"

# Printer resolution in dots-per-inch (203 for most Zebra desktop printers
# like the ZD420/ZD421, 300 for higher-res models). Check the printer's
# config label if unsure.
DPI = 203

def inch(value):
    """Convert inches to printer dots."""
    return round(value * DPI)

# --- Label geometry ---
# Calibrated against the physical label sheet (rectangle body label +
# round cap label on the same row). Re-tune if you switch to different
# label stock.

RECT_X = inch(0.25)          # left margin to the rectangle label
RECT_Y = inch(0.25)          # top margin to the rectangle label
LINE_HEIGHT = inch(0.16)     # vertical spacing between the 3 stacked lines on the rectangle
MAIN_FONT_SIZE = 20          # font height/width (dots) for each of the 3 rectangle lines

CIRCLE_DIAMETER = inch(0.4)  # diameter of the round cap label, used as the text-centering width below
CIRCLE_X = inch(1.75)        # tuned directly against test prints, not derived from RECT_* geometry
CIRCLE_Y = inch(0.32)
CIRCLE_FONT_SIZE = 18        # font height/width (dots) for the cap's index text

QUANTITY_PER_ROW = 1         # how many copies of each row's label pair to print

# --- Read the table ---

wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
ws = wb.active

rows = list(ws.iter_rows(values_only=True))
header = [str(h).strip().lower() if h is not None else "" for h in rows[0]]

def col(name):
    return header.index(name)

idx_col = col("index")
name_col = col("sample name")
conc_col = col("concentration")
unit_col = col("unit")

def format_value(value):
    """Render numbers without a pointless trailing .0 (openpyxl reads them as float)."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)

samples = []
for row in rows[1:]:
    if row[idx_col] is None:
        continue
    samples.append({
        "index": str(row[idx_col]),
        "name": str(row[name_col]),
        "concentration": f"{format_value(row[conc_col])} {row[unit_col]}",
    })

print(f"Loaded {len(samples)} samples from {EXCEL_PATH}")

# --- Build the ZPL Code ---
# ^XA starts the label, ^XZ ends it. Each sample gets its own ^XA..^XZ job
# (one rectangle + one circle, printed together as they share a physical row).
# ^FO sets the X/Y coordinates. ^A0N sets the font. ^FD is the text data.
# ^FB centers the cap text inside the small circle.
# ^PQ sets how many copies of that label to print.

labels = []
for s in samples:
    label = f"""
^XA
^FO{RECT_X},{RECT_Y}^A0N,{MAIN_FONT_SIZE},{MAIN_FONT_SIZE}^FD{s['index']}^FS
^FO{RECT_X},{RECT_Y + LINE_HEIGHT}^A0N,{MAIN_FONT_SIZE},{MAIN_FONT_SIZE}^FD{s['name']}^FS
^FO{RECT_X},{RECT_Y + 2 * LINE_HEIGHT}^A0N,{MAIN_FONT_SIZE},{MAIN_FONT_SIZE}^FD{s['concentration']}^FS
^FO{CIRCLE_X},{CIRCLE_Y}^A0N,{CIRCLE_FONT_SIZE},{CIRCLE_FONT_SIZE}^FB{CIRCLE_DIAMETER},1,0,C,0^FD{s['index']}^FS
^PQ{QUANTITY_PER_ROW}
^XZ
"""
    labels.append(label)

ZPL_CODE = "".join(labels)

# Run the function
print_to_zebra(PRINTER_HOST, PRINTER_PORT, ZPL_CODE)
