## TODO: maybe rewrite these with pandas built-in rolling calcs
## straight from BP's Jupyter notebook


def format_crash_data(data, col, target):
    """ formats crash data for train/test gets previous week count, previous month count, previous quarter count, 
    avg per week 

    Args:
        data: dataframe of crash data
        col: column name / index for week column? 
        target: week to predict (make into binary target) must be >4 months in

    """
    assert target > 16
    pre_week = target - 1
    pre_month = range(pre_week - 4, target)
    pre_quarter = range(pre_month[0] - 12, target)
    all_prior_weeks = range(1, target)

    # week interval for each segment
    # full range = pre_quarter : target
    sliced = data.loc[(slice(None), slice(1, target)), :]
    week_data = sliced[col].unstack(1)
    week_data.reset_index(level=1, inplace=True)

    # aggregate
    week_data['pre_month'] = week_data[pre_month].sum(axis=1)
    week_data['pre_quarter'] = week_data[pre_quarter].sum(axis=1)
    week_data['pre_week'] = week_data[pre_week]
    # avg as of target week
    week_data['avg_week'] = week_data[all_prior_weeks].apply(
        lambda x: x.sum() / len(all_prior_weeks), axis=1
    )

    # binarize target
    week_data['target'] = (week_data[target] > 0).astype(int)

    return (week_data[['segment_id', 'target', 'pre_week',
                       'pre_month', 'pre_quarter', 'avg_week']])