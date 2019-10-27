from bottle import route, get, template
from cgi import escape
from Sand import drawers
from sandable import sandableFactory

overview = escape("""
Movies are specified in an XML file that expresses the various keyframes that should be drawn.
Drawings (Things) with parameters (Params) are used within the keyframes (Frame) to control
what is drawn and when.  Interpolation is automatically done between keyframes.

<Movie Name="name" FPS="5">                 # Name is required, FPS (Frames Per Second) is optional.
  <Eraser>                                  # Eraser drawn before each frame (optional).
    <Thing Type="type">                     # One or more Things can be used to "erase" the table.
      ...
    </Thing>
  </Eraser>
  <Frame Steps="0" Repeat="1">              # Steps is the number of interpolated frames
    <Thing Type="type" Name="name">         #   until this keyframe is drawn.
      <Param Name="name-1" value="value">   # Repeat is the number of times this frame is drawn.
      ...                                   # A Frame contains one or more Things
      <Param Name="name-N" value="value">   # A Thing contains zero or more Params
    </Thing>                                # Params are Name, Value properties of the Type of Thing
    <Thing Type="type" Random="1">          # If a Thing has an optional Name, its parameters are
      ...                                   #   interpolated between Frames - otherwise the resulting
    </Thing>                                #   polylines are interpolated between Frames.
  </Frame>                                  # Parameters will be randomized if Thing has Random set
</Movie>

The tables below list the Types of Things and the first column indicates the Name for Params.
The other columns briefly describe the fields and their units.""", quote=True)


@route('/help')
@get('/help')
def helpPage():
    return [template('help-page', overview=overview, sandables=drawers, sandableFactory=sandableFactory)]
