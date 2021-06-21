import arcpy

# Set geoprocessing environment
arcpy.env.workspace = arcpy.GetParameterAsText(0)
arcpy.env.overwriteOutput = True

# Input seed point layer
seeds = arcpy.GetParameterAsText(1)

# Input demand point layer
demand = arcpy.GetParameterAsText(2)

# Input number of random seeds to generate
number_of_seeds = arcpy.GetParameterAsText(3)
if not number_of_seeds:
    number_of_seeds = 4

# Enter mean center weight
weight = arcpy.GetParameterAsText(4)

# Enter name for output feature class
output_name = arcpy.GetParameterAsText(5)

# Input threshold distance
threshold = arcpy.GetParameterAsText(6)

# Generate random seeds if no seeds available
if not seeds:
    arcpy.AddMessage("Generating random points...")
    arcpy.CreateRandomPoints_management(arcpy.env.workspace, "Random_points", demand, "", number_of_seeds, "10000 Meters")
    seeds = "Random_points"

# Iteration loop
for a in range(0, 100):
    # Iteration message
    arcpy.AddMessage("Iteration %d..." %(a+1))

    # Create Thiessen Polygons
    arcpy.AddMessage("Generating Thiessen polygons...")
    arcpy.CreateThiessenPolygons_analysis(seeds, "Thiessen_polygons" + "_0" + "%d" % (a + 1), "All fields")

    # Spatial join between Thiessen Polygons and demand points
    Thiessen = "Thiessen_polygons" + "_0" + "%d" % (a + 1)
    arcpy.AddMessage("Joining demand points and Thiessen polygons...")
    arcpy.SpatialJoin_analysis(demand, Thiessen, "Points_to_Thiessen" + "_0" + "%d" % (a + 1), "JOIN_ONE_TO_ONE", "KEEP_ALL")

    # Weighted mean center within polygons
    arcpy.AddMessage("Calculating mean centers weighted by %s..." % weight)
    PointThiessen = "Points_to_Thiessen" + "_0" + "%d" % (a + 1)
    arcpy.MeanCenter_stats(PointThiessen, output_name + "_0" + "%d" % (a + 1), weight, "Input_FID", "Input_FID")

    # Near tool
    output = output_name + "_0" + "%d" % (a + 1)
    field = "NEAR_DIST"
    arcpy.AddMessage("Calculating point movement distance...")
    arcpy.Near_analysis(output, seeds, "", "", "", "PLANAR")

    # Apply threshold distance before next iteration occurs
    all_distances = []
    cursor = arcpy.da.SearchCursor(output, [field])
    for row in cursor:
        all_distances.append(row[0])

    average = sum(all_distances) / len(all_distances)
    if average < int(threshold):
        break

    # Redefine seeds before next iteration
    seeds = output_name + "_0" + "%d" % (a + 1)

# Final message when operation is finished
arcpy.AddMessage("Successfully allocated facilities.")