import extract_intersections
import tag_segments
import join_segments_crash_concern
import make_canon_dataset


if __name__ == '__main__':
    # TODO: Decide on some sort of analysis pipeline framework or tool: Makefiles? Luigi/Airflow? Drain?
    extract_intersections.main("data/raw/ma_cob_spatially_joined_streets.shp", out_pickle = "data/interim/inters.pkl", out = "data/interim/inters.shp")
    tag_segments.main()
    join_segments_crash_concern.main()
    make_canon_dataset.main()