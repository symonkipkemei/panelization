
def create_curve():
    """creating a new detail line"""
    # create a geometry curve
    temp = """
                public static Line CreateBound(
            	XYZ endpoint1,
            	XYZ endpoint2
                )"""
    endpoint1 = XYZ(0, 1, 0)
    endpoint2 = XYZ(0, 100, 0)

    geometryCurve = Line.CreateBound(endpoint1, endpoint2)

    # create new detail curve

    temp = """
                    public DetailCurve NewDetailCurve(
                	View view,
                	Curve geometryCurve
                    )"""

    view = active_view

    doc.Create.NewDetailCurve(view, geometryCurve)

def create_random_wall():
    """Creates a new rectangular profile wall within the project using the specified wall type, height, and offset."""

    temp = """
    public static Wall Create(
	Document document,
	Curve curve,
	ElementId wallTypeId,
	ElementId levelId,
	double height,
	double offset,
	bool flip,
	bool structural
    )
    """
    endpoint1 = XYZ(0, 1, 0)
    endpoint2 = XYZ(0, 100, 0)
    curve = Line.CreateBound(endpoint1, endpoint2)
    wallTypeId = 9756
    levelId = active_level.Id
    Wall.Create(doc,curve,wallTypeId,levelId,3000,0,True,True)


def create_rectangular_wall():
    """
    Creates a new rectangular profile wall within the project using the default wall style.
    """

    temp = """
    public static Wall Create(
	Document document,
	Curve curve,
	ElementId levelId,
	bool structural
    )"""

    endpoint1 = XYZ(0, 1, 0)
    endpoint2 = XYZ(0, 100, 0)
    curve = Line.CreateBound(endpoint1, endpoint2)
    level_id = active_level.Id

    Wall.Create(doc,curve,level_id,True)


def place_window():
    temp = """
    public FamilyInstance NewFamilyInstance(
	XYZ location,
	FamilySymbol symbol,
	Element host,
	StructuralType structuralType
    )"""
    endpoint1 = XYZ(0, 1, 0)
    endpoint2 = XYZ(0, 100, 0)
    endpoint3 = (endpoint2 + endpoint1) /2


    host_wall = doc.GetElement(ElementId(285382))
    print ("host wall", host_wall)


    window_type = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows)\
        .WhereElementIsElementType().FirstElement()
    window = doc.Create.NewFamilyInstance(endpoint3, window_type, host_wall, StructuralType.NonStructural)



def get_symbol(f_param_value):
    # define parameters
    param_type = ElementId(BuiltInParameter.ALL_MODEL_TYPE_NAME)
    print (param_type)
    param_family = ElementId(BuiltInParameter.ALL_MODEL_FAMILY_NAME)
    print (param_family)

    # Create a rule
    # f_param_value = "TYPE NAME HERE"
    f_param = ParameterValueProvider(param_type)
    evaluator = FilterStringEquals()

    f_rule = FilterStringRule(f_param, evaluator, f_param_value, True)

    #create a filter
    filter_type_name = ElementParameterFilter(f_rule)

    #Get elements
    element_by_type = FilteredElementCollector(doc)\
                        .WherePasses(filter_type_name)\
                        .WhereElementIsNotElementType()\
                        .ToElements()

    return element_by_type