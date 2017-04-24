import extract_intersections
import create_segments
import join_segments_crash_concern
import make_canon_dataset


# TODO: Decide on some sort of analysis pipeline framework or tool: Makefiles? Luigi/Airflow? Drain?
extract_intersections.main("data/raw/ma_cob_spatially_joined_streets.shp", out_pickle = "data/interim/inters.pkl", out = "data/interim/inters.shp")
create_segments.main()
join_segments_crash_concern.main()
make_canon_dataset.main()