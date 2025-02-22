#!/usr/bin/env python3
import subprocess
import json
from datetime import datetime, timedelta

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

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

def fetch_player_daily_games_of_month(username, month, year):
    url = f"https://api.chess.com/pub/player/{username}/games/{year}/{month:02d}"
    response = execute_curl_command(url)
    return [game for game in response.get('games', []) if game['time_class'] == 'daily']

def fetch_player_daily_stats(username):
    url = f"https://api.chess.com/pub/player/{username}/stats"
    response = execute_curl_command(url)
    daily_rating = 0
    daily_wins = 0
    daily_draws = 0
    daily_losses = 0

    if 'chess_daily' in response:
        if 'last' in response['chess_daily']:
            if 'rating' in response['chess_daily']['last']:
                daily_rating = response['chess_daily']['last']['rating']
        if 'record' in response['chess_daily']:
            if 'win' in response['chess_daily']['record']:
                daily_wins = response['chess_daily']['record']['win']
            if 'draws' in response['chess_daily']['record']:
                daily_draws = response['chess_daily']['record']['draws']
            if 'loss' in response['chess_daily']['record']:
                daily_losses = response['chess_daily']['record']['loss']

    return daily_rating, daily_wins, daily_draws, daily_losses

def calculate_win_percentage(wins, draws, total_games):
    return ((wins + 0.5 * draws) / total_games) * 100 if total_games else 0

def append_games_in_week_range(username, start_of_week, end_of_week, week_games):
    months_years = {(start_of_week.month, start_of_week.year), (end_of_week.month, end_of_week.year)}
    for month, year in months_years:
        for game in fetch_player_daily_games_of_month(username, month, year):
            game_date = datetime.fromtimestamp(game['end_time'])
            if start_of_week <= game_date <= end_of_week:
                week_games.append(game)

def process_stats_for_users(usernames, today):
    results = {}
    start_of_this_week, end_of_this_week = today - timedelta(weeks=1), today
    start_of_last_week, end_of_last_week = today - timedelta(weeks=2), start_of_this_week
    
    for username in usernames:
        print("Fetching stats for " + username + "...")

        # Fetch overall daily rating and record
        overall_rating, overall_wins, overall_draws, overall_losses = fetch_player_daily_stats(username)
        overall_win_percentage = calculate_win_percentage(overall_wins, overall_draws, (overall_wins + overall_draws + overall_losses))

        current_week_games, last_week_games = [], []
        append_games_in_week_range(username, start_of_this_week, end_of_this_week, current_week_games)
        append_games_in_week_range(username, start_of_last_week, end_of_last_week, last_week_games)
        
        def count_results(games, opponent=None):
            wins, draws, losses = 0, 0, 0
            for game in games:
                if game['white']['username'] == username:
                    color = 'white'
                    opponent_color = 'black'
                else:
                    color = 'black'
                    opponent_color = 'white'

                if opponent is None:
                    result = game[color]['result']
                elif game[opponent_color]['username'] == opponent:
                    result = game[color]['result']
                else:
                    continue

                if result == 'win': wins += 1
                elif result in ['checkmated', 'timeout', 'resigned', 'lose']: losses += 1
                elif result in ['agreed', 'repetition', 'stalemate']: draws += 1
            return wins, draws, losses
        
        curr_wins, curr_draws, curr_losses = count_results(current_week_games)
        last_wins, last_draws, last_losses = count_results(last_week_games)
        
        curr_win_percentage = calculate_win_percentage(curr_wins, curr_draws, len(current_week_games))
        last_win_percentage = calculate_win_percentage(last_wins, last_draws, len(last_week_games))

        opponent_win_percentage = {}
        # Calculate the weekly win percentage of the current user against all other users
        for opponent in usernames:
                if username == opponent:
                    continue
                opponent_curr_wins, opponent_curr_draws, opponent_curr_losses = count_results(current_week_games, opponent)
                opponent_win_percentage[opponent] = calculate_win_percentage(opponent_curr_wins, opponent_curr_draws, len(current_week_games))

        results[username] = {
            "overall_rating": overall_rating,
            "overall_win_percentage": overall_win_percentage,
            "wins": curr_wins,
            "losses": curr_losses,
            "draws": curr_draws,
            "win_percentage": curr_win_percentage,
            "win_percentage_diff": curr_win_percentage - last_win_percentage,
            "opponent_win_percentage": opponent_win_percentage
        }
    return results


def generate_html_report(today, stats, filename="DailyChessPowerRankings.html"):
    # Convert stats dictionary into a sorted list
    sorted_stats = sorted(stats.items(), key=lambda x: (-x[1]['win_percentage'], -(x[1]['wins'] + x[1]['losses'] + x[1]['draws'])))

    html_content = f"""
    <html>
    <head>
        <title>Daily Chess Power Rankings</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #F5DEB3; /* Light Beige */
                color: #000000; /* Black text */
            }}
            h2 {{
                color: #DAA520; /* Gold */
            }}
            h3 {{
                color: #6F4E37; /* Dark Brown */
            }}
            h4 {{
                color: #8B4513; /* Saddle Brown */
            }}
            table {{
                width: 50%; /* Shortened width */
                border-collapse: collapse;
                margin: 20px 0;
                background: #ffffff; /* White */
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
            }}
            th, td {{
                border: 1px solid #6F4E37; /* Dark Brown Borders */
                padding: 8px; /* Reduced padding for compactness */
                text-align: left; /* Left-align all text */
                word-wrap: break-word;
                white-space: normal;
            }}
            th {{
                background-color: #DAA520; /* Gold Header */
                color: white;
            }}
            tr:nth-child(even) {{
                background-color: #D2B48C; /* Tan for alternating rows */
            }}
            tr:nth-child(odd) {{
                background-color: #F5DEB3; /* Beige */
            }}
            tr:hover {{
                background-color: #FFD700; /* Light Gold hover effect */
                transition: 0.3s;
            }}
            p {{
                font-weight: bold;
                color: #8B0000; /* Dark Red */
            }}
            .formula {{
                font-size: 14px;
                font-style: italic;
                color: #333;
                margin-top: -10px;
            }}
        </style>
    </head>
    <body>
        <h2>Daily Chess Power Rankings</h2>
        <p><strong>NOTE:</strong>Power Rankings are based off Win % of this week. The stats collected from {today} and are for Daily games only.</p>
        <p class="formula">Win % = [(Wins + (0.5 * Draws)) / Total Games] * 100</p>
    """

    for rank, (username, stat) in enumerate(sorted_stats, start=1):
        def strip_trailing_zeros(value):
            return int(value) if value == int(value) else round(value, 2)

        overall_win_percentage = strip_trailing_zeros(stat['overall_win_percentage'])
        win_percentage = strip_trailing_zeros(stat['win_percentage'])
        win_percentage_diff = strip_trailing_zeros(stat['win_percentage_diff'])

        html_content += f"""
        <h3>#{rank} {username}</h3>
        <table>
            <tr>
                <th>Win % (Change)</th><th>Wins</th><th>Losses</th><th>Draws</th><th>Total Games</th><th>Overall Win %</th><th>Overall Rating</th>
            </tr>
            <tr>
                <td>{win_percentage}% ({win_percentage_diff:+}%)</td>
                <td>{stat['wins']}</td>
                <td>{stat['losses']}</td>
                <td>{stat['draws']}</td>
                <td>{stat['wins'] + stat['losses'] + stat['draws']}</td>
                <td>{overall_win_percentage}%</td>
                <td>{stat['overall_rating']}</td>
            </tr>
        </table>
        """

        # Table for win percentage against each opponent
        html_content += """
        <h4>Win Percentage Against Each Opponent</h4>
        <table>
            <tr>
                <th>Opponent</th><th>Win %</th>
            </tr>
        """
        for opponent, win_percent in stat['opponent_win_percentage'].items():
            html_content += f"""
            <tr>
                <td>{opponent}</td>
                <td>{strip_trailing_zeros(win_percent)}%</td>
            </tr>
            """
        html_content += "</table>"

    html_content += """
    </body>
    </html>"""

    with open(filename, "w") as file:
        file.write(html_content)
    print(f"HTML report generated: {filename}")

def send_email(receiver_emails, filename="ChessPowerRankings.html"):
    # Email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    sender_email = "cajhtov69@gmail.com"
    password = "vepspiahxnkencjj"  # Use an app password if you have 2FA enabled

    # Create the email
    subject = "Daily Chess Power Rankings"
    body = "Hello, please find the attached HTML file."

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_emails)
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    # Attach an HTML file
    try:
        with open(filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        
        # Encode to base64
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={filename}",
        )
        
        message.attach(part)

        # Send the email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_emails, message.as_string())
        
        print("Email with HTML attachment sent successfully!")

    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    usernames = ["philthybhakta", "chiraag926", "mifflinj", "swenkyorc69", "jamieselects"]
    # email_list = ["chiragamin@hotmail.com", "j.hosea92@gmail.com", "jamesgbarnes13@gmail.com"]
    adjust_today = datetime.today() - timedelta(hours=12)
    stats = process_stats_for_users(usernames, adjust_today)
    generate_html_report(adjust_today.strftime("%m/%d/%Y %H:%M %p"), stats)
    # send_email(email_list)
