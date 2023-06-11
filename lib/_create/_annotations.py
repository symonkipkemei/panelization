

def create_text_note(doc, active_view):
    try:
        with Transaction(doc, __title__) as t:
            t.Start()
            # creating elements

            # method 1 - go into that class you would like to create (revitapi)
            # i.e creating a text note

            position = XYZ(0, 0, 0)
            text = "Hello symon kipkemei"
            text_typeId = FilteredElementCollector(doc).OfClass(TextNoteType).FirstElementId()
            TextNote.Create(doc, active_view.Id, position, text, text_typeId)

            # Transaction guards any changes made to the revit Model
            t.Commit()
    except Exception as e:
        print ("Error", e, "occured")
    # create a wall from a set  of points



def create_room():
    """
    Creates room and a room tag
    """

    # create room, check the room class, if create absent check class in Document class
    with Transaction(doc, __title__) as t:
        t.Start()
        temp = """
        public Room NewRoom(
        	Level level,
        	UV point
        )"""
        level = active_level
        pt = UV(0, 10)
        room = doc.Create.NewRoom(level, pt)


        temp = """
        public RoomTag NewRoomTag(
	    LinkElementId roomId,
	    UV point,
	    ElementId viewId
        )"""

        roomId = LinkElementId(room.Id)
        point = UV(0, 10)
        viewId = active_view.Id


        doc.Create.NewRoomTag(roomId, point, viewId)
        # custom variable
        t.Commit()




