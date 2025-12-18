def percentage_calculation(stats):
    """
    Calculates percentage stats (%FG, %FT, %3PM) based on counting stats.
    Modifies the stats dictionary in-place.
    """
    try:
        # Floor Division : Gives only Fractional Part as Answer

        if stats is not None and 'FGA' in stats.keys():
            # Avoid division by zero
            if stats['FGA'] > 0:
                stats['%FG'] = stats['FGM'] / stats['FGA']
            else:
                stats['%FG'] = 0.0
                
        if stats is not None and 'FTA' in stats.keys():
            if stats['FTA'] > 0:
                stats['%FT'] = stats['FTM'] / stats['FTA']
            else:
                stats['%FT'] = 0.0
                
        if stats is not None and '3PA' in stats.keys():
            if stats['3PA'] > 0:
                stats['%3PM'] = stats['3PM'] / stats['3PA']
            else:
                stats['%3PM'] = 0.0

    except ZeroDivisionError:
        print("Sorry ! You are dividing by zero ")
