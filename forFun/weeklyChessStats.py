#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime, timedelta

DEBUG = False

def debug_print(print_string):
   if DEBUG:
      print(print_string)

# Function to execute a curl command and get the response
def execute_curl_command(url, params=None):
   cmd = ["curl", "-G", url]
   if params:
      for key, value in params.items():
         cmd.extend(["--data-urlencode", "{}={}".format(key, value)])

   result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
   if result.returncode == 0:
      return json.loads(result.stdout)
   else:
      print("Error executing curl command: {}".format(result.stderr))
      return None

# Function to fetch the games for a player for a specific month
def fetch_player_daily_games(username, month, year):
   url = f"https://api.chess.com/pub/player/{username}/games/{year}/{month:02d}"
   debug_print("-" * 70)
   debug_print(url)
   debug_print("-" * 70)
   response = execute_curl_command(url)

   if response and 'games' in response:
      daily_games = [game for game in response['games'] if game['time_class'] == 'daily']
      return daily_games
   return []

# Define a function to calculate win percentage
def calculate_win_percentage(wins, draws, total_games):
   if total_games == 0:
      return 0
   return ((wins + 0.5 * draws) / total_games) * 100

def append_games_in_week_range(username, start_of_week, end_of_week, week_games):
   debug_print("start of week " + start_of_week.strftime("%m/%d/%Y %H:%M %p"))
   debug_print("end of week " + end_of_week.strftime("%m/%d/%Y %H:%M %p"))
   month_year_array = [ [start_of_week.month, start_of_week.year] ]
   # We could have two months/years to fetch from, depending on the dates
   # E.g. Start of week is December 26th 2024
   #      End of week is Jan 2nd 2025
   if (start_of_week.month != end_of_week.month) or (start_of_week.year != end_of_week.year):
      month_year_array.append([end_of_week.month, end_of_week.year])

   for month_year in month_year_array:
      # Fetch games using CURL
      daily_games = fetch_player_daily_games(username, month_year[0], month_year[1])
      for game in daily_games:
         game_date = datetime.fromtimestamp(game['end_time'])
         debug_print(game_date)
         if start_of_week <= game_date <= end_of_week:
            debug_print("appending to this week")
            week_games.append(game)
   return

# Define a function to process the weekly stats
def process_stats_for_users(usernames, today):
   results = []

   # Figure out this week's range
   start_of_this_week = today - timedelta(weeks=1)
   end_of_this_week = today
   # Figure out last week's range
   start_of_last_week = today - timedelta(weeks=2)
   end_of_last_week = start_of_this_week

   for username in usernames:
      current_week_games = []
      append_games_in_week_range(username, start_of_this_week, end_of_this_week, current_week_games)
      last_week_games = []
      append_games_in_week_range(username, start_of_last_week, end_of_last_week, last_week_games)

      current_week_wins = 0
      current_week_draws = 0
      current_week_losses = 0
      current_week_total = len(current_week_games)
      for game in current_week_games:
         # Determine the color of the user
         if game['white']['username'] == username:
            color = 'white'
         else:
            color = 'black'

         # Get win/loss/draw
         if (game[color]['result'] == 'win'):
            current_week_wins += 1
         elif (game[color]['result'] in ['checkmated', 'timeout', 'resigned', 'lose']):
            current_week_losses += 1
         elif (game[color]['result'] in ['agreed', 'repetition', 'stalemate']):
            current_week_draws += 1

      last_week_wins = 0
      last_week_losses = 0
      last_week_draws = 0
      last_week_total = len(last_week_games)
      for game in last_week_games:
         # Determine the color of the user
         if game['white']['username'] == username:
            color = 'white'
         else:
            color = 'black'
         # Get win/loss/draw
         if (game[color]['result'] == 'win'):
            last_week_wins += 1
         elif (game[color]['result'] in ['checkmated', 'timeout', 'resigned', 'lose']):
            last_week_losses += 1
         elif (game[color]['result'] in ['agreed', 'repetition', 'stalemate']):
            last_week_draws += 1

      current_week_win_percentage = calculate_win_percentage(current_week_wins, current_week_draws, current_week_total)
      last_week_win_percentage = calculate_win_percentage(last_week_wins, last_week_draws, last_week_total)
      win_percentage_difference = current_week_win_percentage - last_week_win_percentage

      results.append({
         "username": username,
         "current_week_wins": current_week_wins,
         "current_week_losses": current_week_losses,
         "current_week_draws": current_week_draws,
         "current_week_win_percentage": current_week_win_percentage,
         "win_percentage_difference": win_percentage_difference,
      })

   return results

# List of users to report
usernames = ["chiraag926", "philthybhakta", "swenkyorc69", "jamieselects", "mifflinj"]

# Adjust today's date by 12 hours because Chess.com updates their stats every 12 hours
adjust_today = datetime.today() - timedelta(hours=12)
stats = process_stats_for_users(usernames, adjust_today)
stats.sort(key=lambda x: x['current_week_win_percentage'], reverse=True)

print("-" * 70)
print("Weekly Rankings for Daily chess as of " + adjust_today.strftime("%m/%d/%Y %H:%M %p"))
print("-" * 70)

# Print the results
for stat in stats:
   print("User: {} - {:.2f}% ({:.2f}%)".format(stat['username'], stat['current_week_win_percentage'], stat['win_percentage_difference']))
   print("Current Week Wins: {}".format(stat['current_week_wins']))
   print("Current Week Losses: {}".format(stat['current_week_losses']))
   print("Current Week Draws: {}".format(stat['current_week_draws']))
   print("-" * 70)
