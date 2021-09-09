#! /usr/bin/python3
import random

def main():
   total = int(input("Enter the number of team owners: "))

   owners = []
   for x in range(total):
      ownerName = input("Enter owner number " + str(x+1) + ": ")
      owners.append(ownerName)

   listOfCharacters = [
      "Mario", "Donkey Kong", "Link", "Samus", "Dark Samus", "Yoshi", "Kirby", "Fox", "Pikachu", "Luigi", "Ness", "Captain Falcon",
      "Jigglypuff", "Peach", "Daisy", "Bowser", "Ice Climbers", "Sheik", "Zelda", "Dr. Mario", "Pichu", "Falco", "Marth", "Lucina",
      "Young Link", "Ganondorf", "Mewtwo", "Roy", "Chrom", "Mr. Game & Watch", "Meta Knight", "Pit", "Dark Pit", "Zero Suit Samus",
      "Wario", "Snake", "Ike", "Pokemon Trainer", "Diddy Kong", "Lucas", "Sonic", "King Dedede", "Olimar", "Lucario", "R.O.B.",
      "Toon Link", "Wolf", "Villager", "Mega Man", "Wii Fit Trainer", "Rosalina & Luma", "Little Mac", "Greninja", "Mii Fighter",
      "Palutena", "Pac-Man", "Robin", "Shulk", "Bowser Jr.", "Duck Hunt", "Ryu", "Ken", "Cloud", "Corrin", "Bayonetta", "Inkling",
      "Ridley", "Simon Belmont", "Richter", "King K. Rool", "Isabelle", "Incineroar", "Piranha Plant", "Joker", "Hero", "Banjo & Kazooie",
      "Terry", "Bylet", "Min Min", "Steve/Alex", "Sephiroth", "Pyra/Mythra", "Kazuya"]

   random.shuffle(listOfCharacters)

   # For spacing
   print()
   print()
   for owner in owners:
      print(owner+ ": " + listOfCharacters.pop())

if __name__ == "__main__":
   main()
