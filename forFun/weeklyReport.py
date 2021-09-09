#! /usr/bin/python3

#import libraries used below
import http.client
import json

def fetchWeeklyReport(gamerTag, platform):
   weeklyReport = {}
   # Connect to the API
   conn = http.client.HTTPSConnection("call-of-duty-modern-warfare.p.rapidapi.com")
   headers = {
      'x-rapidapi-host': "call-of-duty-modern-warfare.p.rapidapi.com",
      'x-rapidapi-key': "9bcafd893fmshe89314b7c7dce90p13b521jsnc68c4447ad18"
      }
   conn.request("GET", "https://call-of-duty-modern-warfare.p.rapidapi.com/weekly-stats/" + gamerTag + "/" +platform, headers=headers)
   res = conn.getresponse()
   data = res.read()
   json_dictionary = json.loads(data.decode("utf-8"))
   if "wz" in json_dictionary:
      if "mode" in json_dictionary["wz"]:
         for mode in json_dictionary["wz"]["mode"].keys():
            modeReport = {}

            modeReport["KD"] = format(json_dictionary["wz"]["mode"][mode]["properties"]["kdRatio"], ".2f")
            modeReport["Matches Played"] = json_dictionary["wz"]["mode"][mode]["properties"]["matchesPlayed"]

            # some modes do not have a Gulag, such as Power Grab or Plunder
            if "gulagKills" in json_dictionary["wz"]["mode"][mode]["properties"]:
               gulagKills = int(json_dictionary["wz"]["mode"][mode]["properties"]["gulagKills"])
               gulagDeaths = int(json_dictionary["wz"]["mode"][mode]["properties"]["gulagDeaths"])
               if gulagKills + gulagDeaths > 0:
                  gulagWinPerecentage = 100 *(gulagKills / (gulagKills + gulagDeaths))
                  modeReport["Gulag Win Percentage"] = str(format(gulagWinPerecentage, ".2f")) + " %"
               else:
                  modeReport["Gulag Win Percentage"] = "N/A"
            else:
               modeReport["Gulag Win Percentage"] = "N/A"
            weeklyReport[mode] = modeReport

   for modeReport in weeklyReport.keys():
      print("////////////////////////////////")
      print(modeReport)
      print("////////////////////////////////")
      for modeReportKey in weeklyReport[modeReport].keys():
         print(modeReportKey, ' : ', weeklyReport[modeReport][modeReportKey])
      print()


def main():
   # fetch stats from the last 7 days and display it
   fetchWeeklyReport("chiraag926", "psn")
   return

if __name__ == "__main__":
   main()
