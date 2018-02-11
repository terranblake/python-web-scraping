from splinter import Browser
import pandas as pd
import time
import pickle
import os


def rebuild_link(parts):
    return '/'.join(parts)


def retrieve_nfl_stats_links(reload):
    if(reload):
        links = {}

        browser.visit('http://www.espn.com/nfl/teams')
        base_url = ''

        for col in range(1, 9):
            for row in range(1, 5):
                link = browser.find_by_xpath('//*[@id="content"]/div[3]/div[1]/div/div[{}]/div/div[2]/ul/li[{}]/div/span/a[1]'.format(col, row))['href']
                team = link.split('/')[-1:][0]
                city = team.split('-')[:1][0]
                mascot = team.split('-')[-2:][0]
                abbrev = link.split('/')[-2:][0]
                
                if base_url is '':
                    base_url = link[0:41]
                    links['base'] = base_url
                    print(base_url)

                links[abbrev] = team
                print(team)

        pickle.dump( links, open( "espn/NFL/team_links.p", "wb" ) )
        return links
    else:
        return pickle.load( open( "espn/NFL/team_links.p", "rb" ) )


def retrieve_nfl_teams_stats(links, reload=False):
    base_url = links.pop('base')
    teams = {}

    if reload is False:
        for abbrev in links:
            teams[links[abbrev]] = pickle.load( open( "espn/NFL/teams/{}/_BASIC_STATS.p".format(links[abbrev]), "rb" ) )
    else:
        for abbrev in links:
            if not os.path.exists("espn/NFL/teams/{}/".format(links[abbrev])):
                os.makedirs("espn/NFL/teams/{}/".format(links[abbrev]))

            roster_url = base_url.replace('stats', 'roster')
            results = pd.read_html('/'.join([roster_url, abbrev, links[abbrev]]))[0]
            results = results.rename(index=str, columns={0: 'Number', 1: 'Name', 2: 'Position', 3: 'Age', 4: 'Height', 5: 'Weight', 6: 'Experience', 7: 'College'})
            results = results.iloc[2:].reset_index(drop=True)
            results = results[results['Number'].map(len) <= 2]
            results = results[results['Name'].map(len) >= 6]

            pickle.dump( results, open( "espn/NFL/teams/{}/_BASIC_STATS.p".format(links[abbrev]), "wb" ) )
            teams[links[abbrev]] = results

    teams['base'] = base_url
    return teams


def retrieve_nfl_players_links(links, reload=False):
    player_links_by_team = {}

    if reload:
        base_url = links.pop('base')
        x = 3

        for i, val in links.items():
            link = rebuild_link([base_url.replace('stats', 'roster'), i, val])

            browser.visit(link)

            team = pickle.load( open( "espn/NFL/teams/{}/_BASIC_STATS.p".format(val), "rb" ) )
            player_links = {}

            for player in team['Name']: 
                player_links[player] = browser.find_by_text(player)['href']

            player_links_by_team['val'] = pickle.dump( player_links, open( "espn/NFL/teams/{}/_PLAYER_LINKS.p".format(val), "wb" ) )
            x=3
    else:
        links.pop('base')
        for i, val in links.items():
            player_links_by_team[val] = pickle.load( open( "espn/NFL/teams/{}/_PLAYER_LINKS.p".format(val), "rb" ) )

    return player_links_by_team
        

browser = Browser('chrome')

team_links = retrieve_nfl_stats_links(reload=False)
nfl_team_data = retrieve_nfl_teams_stats(team_links, False)

team_links['base'] = nfl_team_data.pop('base')

players_links = retrieve_nfl_players_links(team_links, False)

for team, players in players_links.items():
    print(team)
    for player, link in players.items():
        print(team, '\t', player)

# Dictionary Structure

# Key, Value

#   Team, {Players, Links}
#       Player, Link