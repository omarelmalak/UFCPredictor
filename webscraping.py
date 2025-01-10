import time
import requests
from bs4 import BeautifulSoup
import pandas as pd


def get_fighter_urls(curr_standings_url: str) -> list[str]:
    data = requests.get(curr_standings_url)
    soup = BeautifulSoup(data.text, features="html.parser")

    fighters_table = soup.select('table.b-statistics__table')[0]
    fighter_links = fighters_table.find_all('a')

    # CREATE SET OF LINKS => AVOID DUPLICATES
    fighter_links_hrefs_list = []
    for link in fighter_links:
        fighter_links_hrefs_list.append(link.get("href"))

    fighter_urls = []
    for link in fighter_links_hrefs_list:
        if link and '/fighter-details/' in link and link not in fighter_urls:
            fighter_urls.append(link)

    return fighter_urls


def get_fight_urls(fighter_url: str) -> tuple[list[str], str]:
    curr_fighter_data = requests.get(fighter_url)
    soup = BeautifulSoup(curr_fighter_data.text, features="html.parser")

    fighter_name = soup.select('span.b-content__title-highlight')[0].text.split()

    fighter_name = " ".join(fighter_name)

    fight_links = soup.find_all('a')

    # CREATE SET OF LINKS => AVOID DUPLICATES
    fight_links_hrefs_list = []
    for link in fight_links:
        fight_links_hrefs_list.append(link.get("href"))

    fight_urls = []
    for link in fight_links_hrefs_list:
        if link and '/fight-details/' in link and link not in fight_urls:
            fight_urls.append(link)

    return fight_urls, fighter_name


def get_cleaned_fight_totals_df(fight_totals: pd.DataFrame, win: bool, submission: bool, fighter_name: str) -> pd.DataFrame:
    kd = None
    sig_str_attempted = None
    sig_str_landed = None
    sig_str_percentage = None
    total_str_attempted = None
    total_str_landed = None
    total_str_percentage = None
    td_attempted = None
    td_landed = None
    td_percentage = None
    sub_attempted = None
    sub_successful = None
    sub_percentage = None
    ctrl_time_sec = None

    opp_fighter = None

    opp_kd = None
    opp_sig_str_attempted = None
    opp_sig_str_landed = None
    opp_sig_str_percentage = None
    opp_total_str_attempted = None
    opp_total_str_landed = None
    opp_total_str_percentage = None
    opp_td_attempted = None
    opp_td_landed = None
    opp_td_percentage = None
    opp_sub_attempted = None
    opp_sub_successful = None
    opp_sub_percentage = None
    opp_ctrl_time_sec = None

    first = True

    for column, value in fight_totals.items():
        cell = value[0].split(" ")
        # print(cell)
        if column == "Fighter":
            fighter_name = fighter_name.split()

            for i in range(len(fighter_name)):
                if cell[i] != fighter_name[i]:
                    first = False

            opp_fighter_lst = []
            if first:
                for i in range(len(fighter_name), len(cell)):
                    opp_fighter_lst.append(cell[i])
            else:
                for i in range(len(cell) - len(fighter_name)):
                    opp_fighter_lst.append(cell[i])

            opp_fighter = " ".join(opp_fighter_lst)

            """
            opp_name_length = len(cell) - len(fighter_name)
            
            if len(fighter_name) == 2 and opp_name_length == 2:
                if cell[2] == fighter_name[0] and cell[3] == fighter_name[1]:
                    first = False
            elif len(fighter_name) == 1 and opp_name_length == 2:
                # i.e. Aoriqileng vs. any of his opponents
                if cell[2] == fighter_name[0]:
                    first = False
            elif len(fighter_name) == 2 and opp_name_length == 1:
                if cell[1] == fighter_name[0] and cell[2] == fighter_name[1]:
                    first = False
            elif len(fighter_name) == 1 and opp_name_length == 1:
                if cell[1] == fighter_name[0]:
                    first = False
            """

        elif column == "KD":
            kd = int(cell[0])

            opp_kd = int(cell[2])

            if not first:
                kd, opp_kd = opp_kd, kd
        elif column == "Sig. str.":
            sig_str_landed = int(cell[0])
            sig_str_attempted = int(cell[2])

            opp_sig_str_landed = int(cell[4])
            opp_sig_str_attempted = int(cell[6])

            if not first:
                sig_str_landed, opp_sig_str_landed = opp_sig_str_landed, sig_str_landed
                sig_str_attempted, opp_sig_str_attempted = opp_sig_str_attempted, sig_str_attempted
        elif column == "Sig. str. %":
            try:
                sig_str_percentage = float(int(cell[0][:cell[0].index('%')]) / 100)
            except ValueError:
                sig_str_percentage = 'N/A'

            try:
                opp_sig_str_percentage = float(int(cell[2][:cell[2].index('%')]) / 100)
            except ValueError:
                opp_sig_str_percentage = 'N/A'

            if not first:
                sig_str_percentage, opp_sig_str_percentage = opp_sig_str_percentage, sig_str_percentage
        elif column == "Total str.":
            total_str_landed = int(cell[0])
            total_str_attempted = int(cell[2])

            try:
                total_str_percentage = round(float(total_str_landed / total_str_attempted), 2)
            except ZeroDivisionError:
                # FIGHTER DOESN'T ATTEMPT A STRIKE
                total_str_percentage = 'N/A'

            opp_total_str_landed = int(cell[4])
            opp_total_str_attempted = int(cell[6])

            try:
                opp_total_str_percentage = round(float(opp_total_str_landed / opp_total_str_attempted), 2)
            except ZeroDivisionError:
                # OPPONENT DOESN'T ATTEMPT A STRIKE (i.e. David Abbott vs. John Matua)
                opp_total_str_percentage = 'N/A'

            if not first:
                total_str_landed, opp_total_str_landed = opp_total_str_landed, total_str_landed
                total_str_attempted, opp_total_str_attempted = opp_total_str_attempted, total_str_attempted
                total_str_percentage, opp_total_str_percentage = opp_total_str_percentage, total_str_percentage
        elif column == "Td":
            td_landed = int(cell[0])
            td_attempted = int(cell[2])

            opp_td_landed = int(cell[4])
            opp_td_attempted = int(cell[6])

            if not first:
                td_landed, opp_td_landed = opp_td_landed, td_landed
                td_attempted, opp_td_attempted = opp_td_attempted, td_attempted
        elif column == "Td %":
            if first:
                if td_attempted == 0:
                    td_percentage = 'N/A'
                else:
                    td_percentage = float(int(cell[0][:cell[0].index('%')]) / 100)

                if opp_td_attempted == 0:
                    opp_td_percentage = 'N/A'
                else:
                    opp_td_percentage = float(int(cell[2][:cell[2].index('%')]) / 100)
            else:
                if td_attempted == 0:
                    td_percentage = 'N/A'
                else:
                    td_percentage = float(int(cell[2][:cell[2].index('%')]) / 100)

                if opp_td_attempted == 0:
                    opp_td_percentage = 'N/A'
                else:
                    opp_td_percentage = float(int(cell[0][:cell[0].index('%')]) / 100)
        elif column == "Sub. att":
            sub_attempted = int(cell[0])

            opp_sub_attempted = int(cell[2])

            if not first:
                sub_attempted, opp_sub_attempted = opp_sub_attempted, sub_attempted

            # ADJUST SUCCESSFUL SUBMISSIONS + SUBMISSION PERCENTAGE SUCCESS
            if submission:
                if win:
                    sub_successful = 1
                    try:
                        sub_percentage = 1 / sub_attempted
                    except ZeroDivisionError:
                        sub_percentage = 'N/A'

                    opp_sub_successful = 0

                    if opp_sub_attempted:
                        opp_sub_percentage = 0
                    else:
                        opp_sub_percentage = 'N/A'
                else:
                    opp_sub_successful = 1
                    try:
                        opp_sub_percentage = 1 / opp_sub_attempted
                    except ZeroDivisionError:
                        opp_sub_percentage = 'N/A'

                    sub_successful = 0

                    if sub_attempted:
                        sub_percentage = 0
                    else:
                        sub_percentage = 'N/A'
            else:
                if sub_attempted:
                    sub_percentage = 0
                    sub_successful = 0

                if opp_sub_attempted:
                    opp_sub_percentage = 0
                    opp_sub_successful = 0

                if sub_percentage is None:
                    sub_percentage = 'N/A'

                if sub_successful is None:
                    sub_successful = 0

                if opp_sub_percentage is None:
                    opp_sub_percentage = 'N/A'

                if opp_sub_successful is None:
                    opp_sub_successful = 0

        elif column == "Ctrl":
            # IF FOUGHT IN PRIDE, NO CTRL TIME RECORDED (i.e. Quinton Jackson EARLY CAREER)
            if cell[0].find(':') < 0:
                ctrl_time_sec = 'N/A'
                opp_ctrl_time_sec = 'N/A'
            else:
                ctrl_min_to_sec = 60 * int(cell[0][:cell[0].index(':')])
                ctrl_sec = int(cell[0][(cell[0].index(':') + 1):])
                ctrl_time_sec = ctrl_min_to_sec + ctrl_sec

                opp_ctrl_min_to_sec = 60 * int(cell[2][:cell[2].index(':')])
                opp_ctrl_sec = int(cell[2][(cell[2].index(':') + 1):])
                opp_ctrl_time_sec = opp_ctrl_min_to_sec + opp_ctrl_sec

            if not first:
                ctrl_time_sec, opp_ctrl_time_sec = opp_ctrl_time_sec, ctrl_time_sec
        else:
            print("ERROR: Invalid column.")

    cleaned_fight_data = {
        'Opp. Fighter': [opp_fighter],

        'KD': [kd],
        'Sig. Str. Landed': [sig_str_landed],
        'Sig. Str. Attempted': [sig_str_attempted],
        'Sig. Str. %': [sig_str_percentage],
        'Total Str. Landed': [total_str_landed],
        'Total Str. Attempted': [total_str_attempted],
        'Total Str. %': [total_str_percentage],
        'TD Landed': [td_landed],
        'TD Attempted': [td_attempted],
        'TD %': [td_percentage],
        'Sub. Attempted': [sub_attempted],
        'Sub. Successful': [sub_successful],
        'Sub. %': [sub_percentage],
        'Ctrl Time (Sec)': [ctrl_time_sec],

        'Opp. KD': [opp_kd],
        'Opp. Sig. Str. Landed': [opp_sig_str_landed],
        'Opp. Sig. Str. Attempted': [opp_sig_str_attempted],
        'Opp. Sig. Str. %': [opp_sig_str_percentage],
        'Opp. Total Str. Landed': [opp_total_str_landed],
        'Opp. Total Str. Attempted': [opp_total_str_attempted],
        'Opp. Total Str. %': [opp_total_str_percentage],
        'Opp. TD Landed': [opp_td_landed],
        'Opp. TD Attempted': [opp_td_attempted],
        'Opp. TD %': [opp_td_percentage],
        'Opp. Sub. Attempted': [opp_sub_attempted],
        'Opp. Sub. Successful': [opp_sub_successful],
        'Opp. Sub. %': [opp_sub_percentage],
        'Opp. Ctrl Time (Sec)': [opp_ctrl_time_sec],
    }

    cleaned_fight_totals = pd.DataFrame(cleaned_fight_data)

    return cleaned_fight_totals


if __name__ == "__main__":
    alphabet = ["a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s, t, u, v, w, x, y, z"]

    fighter_dfs = []

    alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m"]
    for letter in alphabet:
        curr_standings_url = "http://www.ufcstats.com/statistics/fighters?char=" + letter + "&page=all"
        fighter_urls = get_fighter_urls(curr_standings_url)

        # Adesanya (AS EXAMPLE)
        # fighter_urls = ['http://www.ufcstats.com/fighter-details/1338e2c7480bdf9e']

        for fighter_url in fighter_urls:
            row = 0

            drop_next = False

            curr_fighter_data = requests.get(fighter_url)

            # GET A FIGHTS DATAFRAME
            fights = pd.read_html(curr_fighter_data.text, match="W/L")[0]

            # DROP GARBAGE ROW, "NEXT" ROW IF THERE IS ONE (DO NOT NEED "NEXT" FIGHT), AND RECALIBRATE INDICES
            fights.drop(0, inplace=True)
            fights.reset_index(drop=True, inplace=True)

            for i in range(len(fights)):
                # CHANGE Event COLUMN TO A PARSABLE Date COLUMN (PANDAS Data DATATYPE)

                event_listed = fights.iloc[i]["Event"].lower().split()
                month_to_read = False
                day_to_read = False

                for elem in event_listed:
                    if elem == "jan.":
                        month = "01"
                        month_to_read = True
                    elif elem == "feb.":
                        month = "02"
                        month_to_read = True
                    elif elem == "mar.":
                        month = "03"
                        month_to_read = True
                    elif elem == "apr.":
                        month = "04"
                        month_to_read = True
                    elif elem == "may.":
                        month = "05"
                        month_to_read = True
                    elif elem == "jun.":
                        month = "06"
                        month_to_read = True
                    elif elem == "jul.":
                        month = "07"
                        month_to_read = True
                    elif elem == "aug.":
                        month = "08"
                        month_to_read = True
                    elif elem == "sep.":
                        month = "09"
                        month_to_read = True
                    elif elem == "oct.":
                        month = "10"
                        month_to_read = True
                    elif elem == "nov.":
                        month = "11"
                        month_to_read = True
                    elif elem == "dec.":
                        month = "12"
                        month_to_read = True
                    elif month_to_read:
                        day = elem[:elem.index(",")]
                        day_to_read = True
                        month_to_read = False
                    elif day_to_read:
                        year = elem

                full_date = f"{year}-{month}-{day}"

                # print(full_date)

                fights.loc[i, "Event"] = full_date

                # CLEAN Method COLUMN TO REMOVE EXTRA SUMMARY INFO FOR Method Code (i.e. "Punch", "Punches", "Kick")
                try:
                    method_listed = fights.iloc[i]["Method"].split()

                    fights.loc[i, "Method"] = method_listed[0]
                except AttributeError:
                    pass

            fights.rename(columns={'Event': 'Date'}, inplace=True)

            # INITIALIZE METHOD CODE COLUMN
            fights["Method Code"] = None

            # IF THEY HAVE NO FIGHTS ON RECORD, SKIP THEM (i.e. Cyborg Abreu)
            if len(fights) == 0:
                print("FIGHTER NOT ELIGIBLE")
                continue

            if fights.iloc[0]["W/L"].lower() == "next":
                fights.drop(0, inplace=True)
                fights.reset_index(drop=True, inplace=True)
                drop_next = True

            fights.drop(columns=["Kd", "Str", "Td", "Sub"], inplace=True)
            fights["Total Fight Time (Sec)"] = 0

            fight_info = get_fight_urls(fighter_url)

            fight_urls = fight_info[0]
            fighter_name = fight_info[1]

            if len(fight_urls) < 5:
                # IF THE FIGHTER HAS LESS THAN 5 FIGHTS ON RECORD, SKIP THEM
                print(f"{fighter_name} HAS NOT ENOUGH FIGHTS")
                continue

            # IF THEY HAVE AN UPCOMING FIGHT, DROP THE PREVIEW URL (i.e. Sean Strickland vs. Paulo Costa)
            if drop_next:
                fight_urls.pop(0)

            fight_stats_dict = {
                'KD': [],
                'Sig. Str. Landed': [],
                'Sig. Str. Attempted': [],
                'Sig. Str. %': [],
                'Total Str. Landed': [],
                'Total Str. Attempted': [],
                'Total Str. %': [],
                'TD Landed': [],
                'TD Attempted': [],
                'TD %': [],
                'Sub. Attempted': [],
                'Sub. Successful': [],
                'Sub. %': [],
                'Ctrl Time (Sec)': [],

                'Opp. KD': [],
                'Opp. Sig. Str. Landed': [],
                'Opp. Sig. Str. Attempted': [],
                'Opp. Sig. Str. %': [],
                'Opp. Total Str. Landed': [],
                'Opp. Total Str. Attempted': [],
                'Opp. Total Str. %': [],
                'Opp. TD Landed': [],
                'Opp. TD Attempted': [],
                'Opp. TD %': [],
                'Opp. Sub. Attempted': [],
                'Opp. Sub. Successful': [],
                'Opp. Sub. %': [],
                'Opp. Ctrl Time (Sec)': [],
            }

            fighter_stats_df = pd.DataFrame(fight_stats_dict)

            for fight_url in fight_urls:

                # COLLECT TOTAL FIGHT TIME
                num_rounds = int(fights.iloc[row]["Round"])

                # ENSURE INTEGER ROUNDS
                fights.loc[row, "Round"] = num_rounds

                min_to_sec = 60 * int(fights.iloc[row]["Time"][:fights.iloc[row]["Time"].index(':')])
                sec = int(fights.iloc[row]["Time"][(fights.iloc[row]["Time"].index(':') + 1):])
                final_round_duration_sec = min_to_sec + sec

                if num_rounds == 1:
                    total_duration_sec = final_round_duration_sec
                else:
                    total_duration_sec = num_rounds * 300 + final_round_duration_sec

                fights.loc[row, "Total Fight Time (Sec)"] = total_duration_sec

                if fights.iloc[row]["W/L"].lower() == "win":
                    win = True
                else:
                    win = False

                if "sub" in fights.iloc[row]["Method"].lower():
                    submission = True
                else:
                    submission = False

                fight_date = fights.iloc[row]["Date"]

                curr_fight = requests.get(fight_url)

                try:
                    fight_totals = pd.read_html(curr_fight.text, match="Rev")[0]
                except ValueError:
                    # IN THE CASE THAT THERE IS NO ROUND-BY-ROUND FIGHT DATA FOR THAT FIGHT
                    # (i.e. Tom Aaron - Strikeforce)
                    break

                # DROP REVERSALS DATA (NOT VERY USEFUL) AND FIGHTER COLUMN (WE KNOW WHICH FIGHTER IT IS)
                fight_totals.drop(columns=["Rev."], inplace=True)

                # SIGNIFICANT STRIKES DISTRIBUTION (NOT BEING USED FOR INITIAL MODEL TRAINING)
                """
                try:
                    sig_strikes_distribution = pd.read_html(curr_fight.text, match="Head")[0]
                except ValueError:
                    # IN THE CASE THAT THERE IS NO ROUND-BY-ROUND FIGHT DATA FOR THAT FIGHT
                    # (i.e. Tom Aaron - Strikeforce)
                    break

                # DROP REDUNDANT DATA
                sig_strikes_distribution.drop(columns=["Sig. str", "Sig. str. %", "Fighter"], inplace=True)
                """

                cleaned_fight_totals = get_cleaned_fight_totals_df(fight_totals, win, submission, fighter_name)
                cleaned_fight_totals["Date"] = fight_date

                fighter_stats_df = pd.concat([fighter_stats_df, cleaned_fight_totals], ignore_index=True)

                row += 1

            if len(fighter_stats_df) == len(fights):
                # WE ONLY WANT TO INCLUDE FIGHTERS WHO HAVE NO MISSING FIGHT DATA, ALL THEIR FIGHTS ARE DOCUMENTED
                # ROUND-BY-ROUND
                fighter_full_df = fights.merge(fighter_stats_df, on="Date")

                # EXCLUDE no-contests AND draws AS RARE AND NOT USEFUL FIGHTS
                fighter_full_df = fighter_full_df.drop(fighter_full_df[fighter_full_df["W/L"] == "nc"].index)
                fighter_full_df = fighter_full_df.drop(fighter_full_df[fighter_full_df["W/L"] == "draw"].index)

                fighter_full_df.drop(columns=["Fighter"], inplace=True)
                fighter_full_df.insert(0, "Fighter", fighter_name)

                fighter_full_df["Date"] = pd.to_datetime(fighter_full_df["Date"])

                fighter_dfs.append(fighter_full_df)

                # QUICK-SLEEP FOR DELAYED TRAFFIC (AVOID BLOCKING)
                time.sleep(1)

                print(f"{fighter_name} ELIGIBLE")
            else:
                print(f"{fighter_name} NOT ELIGIBLE")

            # print(f"{fighter_name} PROCESSED")

        all_fighters_dfs = pd.concat(fighter_dfs, ignore_index=True)

        # ADD Method Code COLUMN VALUES BY PARSING Method COLUMN VALUES AS CATEGORIZED CODES
        # ~~ BONUS PREDICTOR COLUMN ~~
        all_fighters_dfs["Method Code"] = all_fighters_dfs["Method"].astype("category").cat.codes

        # ADD Opp. Fighter Code COLUMN VALUES BY PARSING Opp. Fighter COLUMN VALUES AS CATEGORIZED CODES
        # ~~ BONUS PREDICTOR COLUMN ~~
        all_fighters_dfs["Opp. Fighter Code"] = all_fighters_dfs["Opp. Fighter"].astype("category").cat.codes

        # ADD Target COLUMN VALUES BY PARSING W/L COLUMN VALUES AS CATEGORIZED CODES
        # -- MOST IMPORTANT COLUMN --
        all_fighters_dfs["Target"] = all_fighters_dfs["W/L"].astype("category").cat.codes

        all_fighters_dfs.to_csv(f"{letter}_fighters.csv")