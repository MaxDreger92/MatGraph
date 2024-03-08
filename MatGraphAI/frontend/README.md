# reactGraphAI

Interactive canvas frontend for a PHD project on Research Data Management at Forschungszentrum Jülich.

Hosted at: https://thiloschenkelberg.github.io/reactGraphAI/

Refers to: https://github.com/IEK-13/MatGraphAI

# Try it out

You can try out a prototype using a test account:

Mail: test@test.com <br>
Password: testaccount

Then go to "Search" tab for main functionality

## Controls

### Create nodes

On search canvas, press <b>Right Click</b> to open the radial menu and create nodes.

Hover over menu items to see their node type.

![Radial menu](https://res.cloudinary.com/dseyvzrwt/image/upload/v1703003089/wheel-3_v9suti.png)

### Connect nodes

You can connect nodes, by hovering the border of any node, press and hold the small connector circle and drag it over another node. A connection is made, provided that node types are compatible.

![Connect nodes](https://res.cloudinary.com/dseyvzrwt/image/upload/v1703001995/connector-1_p18xvk.png) &nbsp;&nbsp; ![Connect nodes](https://res.cloudinary.com/dseyvzrwt/image/upload/v1703001995/connector-2_lxh7fx.png)

You may also drag out from the connector circle to empty canvas space. The radial menu will open with all nodes, that are connection-compatible to the starting node. A connection is then automatically created between these two nodes.

![Connect nodes](https://res.cloudinary.com/dseyvzrwt/image/upload/v1703001996/connector-3_hdpygq.png)

### Select and move nodes, pan and zoom on canvas

Select nodes by clicking on them, multi-select with <b>Ctrl</b>, by using a selection rectangle (left-mouse drag from anywhere on canvas) or with key combination <b>Ctrl-A</b> to select all nodes.

Move any selected nodes, by left-mouse dragging on one of the selected nodes.

Pan on the canvas by middle-mouse dragging anywhere on canvas or nodes.

Zoom with mouse-wheel.

### More canvas actions

![Canvas actions](https://res.cloudinary.com/dseyvzrwt/image/upload/v1703001995/tools-1_jm55mc.png)

You can also undo and redo with key combinations:

Undo: <b>Ctrl-Z</b> <br>
Redo: <b>Ctrl-Y</b> or <b>Ctrl-Shift-Z</b>

### Open/Close Json-viewer

Nodes and connections are automatically converted to the appropriate json-format. You can view the json by clicking the double arrowheads at the right side of the canvas.

![Open/Close Json-viewer](https://res.cloudinary.com/dseyvzrwt/image/upload/v1703001995/extended-window-1_h70q8n.png)

### Commit search query

Not implemented at the moment.
