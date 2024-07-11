def get_picks(pick, roster_size, teams):    
    picks = [pick, (2*teams+1)-pick]
    for i in range(2,roster_size):
        picks.append(picks[i-2]+(2*teams))
    return picks

def get_team_from_pick(pick, teams):
    if ((pick-1) // teams + 1) % 2 == 1:
        return (pick-1) % teams + 1
    else:
        return teams - ((pick-1) % teams)

def full_position_constraints(roster_settings):
    # Constraints -- based on league settings
    min_qbs, max_qbs = roster_settings['slots_qb'], 3
    min_rbs, max_rbs = roster_settings['slots_rb']+roster_settings['slots_flex'], 6
    min_wrs, max_wrs = roster_settings['slots_wr']+roster_settings['slots_flex'], 6
    min_tes, max_tes = roster_settings['slots_te'], 2
    starting_qb = roster_settings['slots_qb']
    starting_rb = roster_settings['slots_rb']
    starting_wr = roster_settings['slots_wr']
    starting_te = roster_settings['slots_te']
    try:
        num_flex = roster_settings['slots_flex']
    except:
        num_flex = 0
    try: 
        num_sflex = roster_settings['slots_super_flex']
    except:
        num_sflex = 0
    starting_flex = starting_rb + starting_wr + starting_te + num_flex
    starting_sflex = starting_qb + starting_flex + num_sflex
    starting_dst = roster_settings['slots_def']
    starting_k = roster_settings['slots_k']

    return {'min_qbs': min_qbs, 'max_qbs': max_qbs, 'min_rbs': min_rbs, 'max_rbs': max_rbs, 'min_wrs': min_wrs, 'max_wrs': max_wrs, 'min_tes': min_tes, 'max_tes': max_tes, 'starting_qb': starting_qb, 'starting_rb': starting_rb, 'starting_wr': starting_wr, 'starting_te': starting_te, 'starting_flex': starting_flex, 'num_flex': num_flex, 'starting_sflex': starting_sflex, 'num_sflex': num_sflex, 'starting_k': starting_k, 'starting_dst': starting_dst}

def remaining_position_constraints(drafted_pos, full_team, cur_team):

    qb_low = max(0, full_team["min_qbs"] - drafted_pos[cur_team]['QB'])
    rb_low = max(0, full_team["min_rbs"] - drafted_pos[cur_team]['RB'])
    wr_low = max(0, full_team["min_wrs"] - drafted_pos[cur_team]['WR'])
    te_low = max(0, full_team["min_tes"] - drafted_pos[cur_team]['TE'])

    qb_high = max(0, full_team["max_qbs"] - drafted_pos[cur_team]['QB'])
    rb_high = max(0, full_team["max_rbs"] - drafted_pos[cur_team]['RB'])
    wr_high = max(0, full_team["max_wrs"] - drafted_pos[cur_team]['WR'])
    te_high = max(0, full_team["max_tes"] - drafted_pos[cur_team]['TE'])

    qb_start = max(0, full_team["starting_qb"] - drafted_pos[cur_team]['QB'])
    rb_start = max(0, full_team["starting_rb"] - drafted_pos[cur_team]['RB'])
    wr_start = max(0, full_team["starting_wr"] - drafted_pos[cur_team]['WR'])
    te_start = max(0, full_team["starting_te"] - drafted_pos[cur_team]['TE'])

    extra_rb = max(0, drafted_pos[cur_team]['RB'] - full_team["starting_rb"])
    extra_wr = max(0, drafted_pos[cur_team]['WR'] - full_team["starting_wr"])
    extra_te = max(0, drafted_pos[cur_team]['TE'] - full_team["starting_te"])
    extra_qb = max(0, drafted_pos[cur_team]['QB'] - full_team["starting_qb"])
    extra_flex = extra_rb + extra_wr + extra_te
    #between 0, number of sflex spots - for model contsraint 
    extra_sflex = min(full_team['num_sflex'], max(0, extra_rb + extra_wr + extra_te + extra_qb - full_team["num_flex"]))

    flex_starting = max(0, full_team["starting_flex"] - (min(full_team["starting_rb"], drafted_pos[cur_team]['RB']) + min(full_team["starting_wr"], drafted_pos[cur_team]['WR']) + min(full_team["starting_te"], drafted_pos[cur_team]['TE']) + min(full_team["num_flex"], extra_flex)))
    sflex_starting = max(0, full_team["starting_sflex"] - (min(full_team["starting_qb"], drafted_pos[cur_team]['QB']) + min(full_team["starting_rb"], drafted_pos[cur_team]['RB']) + min(full_team["starting_wr"], drafted_pos[cur_team]['WR']) + min(full_team["starting_te"], drafted_pos[cur_team]['TE']) + min(full_team["num_flex"], extra_flex) + min(full_team["num_sflex"], max(0, extra_flex-full_team["num_flex"])+extra_qb)))
    k_start = max(0, full_team["starting_k"] - drafted_pos[cur_team]['K'])
    dst_start = max(0, full_team["starting_dst"] - drafted_pos[cur_team]['DST'])
    flex_num = flex_starting - (rb_start + wr_start + te_start)
    sflex_num = sflex_starting - (qb_start + rb_start + wr_start + te_start + flex_num)

    #binary extras - for model constraint
    extra_rb = 1*(extra_rb > 0)
    extra_wr = 1*(extra_wr > 0)
    extra_te = 1*(extra_te > 0)
    extra_qb = 1*(extra_qb > 0)

    remaining_settings = {'min_qbs': qb_low, 'max_qbs': qb_high, 'min_rbs': rb_low, 'max_rbs': rb_high, 'min_wrs': wr_low, 'max_wrs': wr_high, 'min_tes': te_low, 'max_tes': te_high, 'starting_qb': qb_start, 'starting_rb': rb_start, 'starting_wr': wr_start, 'starting_te': te_start, 'starting_flex': flex_starting, 'num_flex': flex_num, 'starting_sflex': sflex_starting, 'num_sflex': sflex_num, 'starting_k': k_start, 'starting_dst': dst_start, 'extra_rb': extra_rb, 'extra_wr': extra_wr, 'extra_te': extra_te, 'extra_qb': extra_qb, 'extra_flex': extra_flex, 'extra_sflex': extra_sflex}
    return remaining_settings