#!/usr/bin/env python3
import re
import os
import Reports
import sys
import copy
import gzip

def FileNameToDate(Path):
	#Example: 2022-06-14-1.log.gz
	#First Get the Base Name
	Name = os.path.basename(Path) #Get Rid of Path
	Name = Name.split('.')[0] #Get Rid of Extensions
	SplitName = Name.split('-')
	
	Year = int(SplitName[0])
	Month = int(SplitName[1])
	Day = int(SplitName[2])
	
	return {'Year':Year,'Month':Month,'Day':Day}
	
def LogLineToExactTime(Line,Date):
	#Example: [21:21:22] [ServerMain/INFO]: Building unoptimized datafixer
	#Get Timestamp alone
	RawStamp = Line.split(' ')[0]
	#Remove Brackets
	RawStamp = RawStamp.strip('[]')
	
	#Extract
	SplitStamp = RawStamp.split(':')
	
	Hour = int(SplitStamp[0])
	Minute = int(SplitStamp[1])
	Second = int(SplitStamp[2])
	
	#Quantify whole stamp
	OutStamp = 0
	OutStamp += Second * (10**0)
	OutStamp += Minute * (10**2)
	OutStamp += Hour * (10**4)
	OutStamp += Date['Day'] * (10**6)
	OutStamp += Date['Month'] * (10**8)
	OutStamp += Date['Year'] * (10**10)
	
	return OutStamp
	

DeathMessages = [
        r'\S* was shot by',
        r'\S* was pummeled by',
        r'\S* was pricked to death',
        r'\S* walked into a cactus',
        r'\S* drowned',
        r'\S* experienced kinetic energy',
        r'\S* blew up',
        r'\S* was blown up by',
        r'\S* was killed by',
        r'\S* hit the ground too hard',
        r'\S* fell from a high place',
        r'\S* fell off a ladder',
        r'\S* fell off some vines',
        r'\S* fell off some weeping vines',
        r'\S* fell off some twisting vines',
        r'\S* fell off scaffolding',
        r'\S* fell while climbing',
        r'\S* was squashed by',
        r'\S* went up in flames',
        r'\S* walked into fire',
        r'\S* burned to death',
        r'\S* was burnt to a crisp',
        r'\S* went off with a bang',
        r'\S* tried to swim in lava',
        r'\S* was struck by lightning',
        r'\S* discovered the floor was lava',
        r'\S* walked into danger zone',
        r'\S* was slain by',
        r'\S* was fireballed by',
        r'\S* was stung to death',
        r'\S* was shot by a skull from',
        r'\S* starved to death',
        r'\S* suffocated in a wall',
        r'\S* was squished too much',
        r'\S* was squashed by',
        r'\S* was poked to death',
        r'\S* was killed trying to hurt',
        r'\S* was impaled by',
        r'\S* fell out of the world',
        r'\S* didn\'t want to live in the same world as',
        r'\S* withered away'
        ]
	
	
class statcounter:
	def __init__(self):
		self.PlayerConnected = {}
		self.PlayerDeaths = {}
		self.PlayerUUIDs = {}
		
		self.ConnectedByHour = {}
		self.ServerStruggleByHour = {}
		
	#This Cleans Up if the file ends abruptly
	def nextFileTrigger(self):
		for key in self.PlayerConnected:
			self.PlayerConnected[key] = False
		
	def injest(self,Line,Date):
		LineTime = LogLineToExactTime(Line,Date)
		#print("Injest",LineTime)
		
		#Line Example/: [21:40:49] [User Authenticator #5/INFO]: UUID of player JessieFree is 94cd9501-03af-4933-8595-f7fe070540cb
		
		#Player Stats
		
		#Record UUIDs
		if re.search(r"UUID of player \S* is \S*",Line) != None:
			Clean = re.findall(r"UUID of player \S* is \S*",Line)[0]
			CleanSP = Clean.split(' ')
			
			PlayerName = CleanSP[3]
			PlayerUUID = CleanSP[5]
			
			print("Player",PlayerName,"Has UUID",PlayerUUID)
			self.PlayerUUIDs[PlayerName] = PlayerUUID
			
		#Record Player Joins
		if re.search(r"\S* joined the game",Line) != None:
			Clean = re.findall(r"\S* joined the game",Line)[0]
			CleanSP = Clean.split(' ')
			
			PlayerName = CleanSP[0]
			print("Player",PlayerName,"Joined")
			
			#This is an Important Function as it creates all the information for the player data
			if PlayerName not in self.PlayerConnected:
				self.PlayerConnected[PlayerName] = True
				self.PlayerDeaths[PlayerName] = 0
			else:
				self.PlayerConnected[PlayerName] = True
			
		#Record Player Leaves	
		if re.search(r"\S* left the game",Line) != None:
			Clean = re.findall(r"\S* left the game",Line)[0]
			CleanSP = Clean.split(' ')
			
			PlayerName = CleanSP[0]
			print("Player",PlayerName,"Left")
			
			if PlayerName in self.PlayerConnected:
				self.PlayerConnected[PlayerName] = False
				
		#Record Deaths
		for criteria in DeathMessages:
			if re.search(criteria,Line) != None:
				#Get Player Name
				Clean = re.findall(criteria,Line)[0]
				CleanSP = Clean.split(' ')
			
				PlayerName = CleanSP[0]
				print("Player",PlayerName,"Died")
			
				if PlayerName in self.PlayerConnected:
					self.PlayerDeaths[PlayerName] += 1
		

			
		#Finally, we Tick the Player Connected Counter
		#Lossy Division removes seconds and minutes from timestamp
		TimeAtHour = (LineTime // (10**4))
		if TimeAtHour not in self.ConnectedByHour:
			self.ConnectedByHour[TimeAtHour] = set()
		
		for player in self.PlayerConnected:
			if (player not in self.ConnectedByHour[TimeAtHour]) and (self.PlayerConnected[player] == True):
				self.ConnectedByHour[TimeAtHour].add(player)
			

		#Server Stats
		
		#Record Long Tick Messages
		if re.search(r"Can\'t keep up\! Is the server overloaded\? ",Line) != None:
			if TimeAtHour not in self.ServerStruggleByHour:
				self.ServerStruggleByHour[TimeAtHour] = 1
				
			else:
				self.ServerStruggleByHour[TimeAtHour] += 1
		
			
			

		
	def genreport(self,Dest):
		#print(self.PlayerDeaths,self.PlayerUUIDs,self.ConnectedByHour,self.ServerStruggleByHour)
		Reports.fullReport(Dest,self.PlayerDeaths,self.PlayerUUIDs,self.ConnectedByHour,self.ServerStruggleByHour)
			
		
	

def main(LogDir,OutDir):
	#Get the List of Gz Files
	Allfiles = os.listdir(LogDir)
	LogFiles = []
	for i in Allfiles:
		if '.gz' in i:
			LogFiles.append(LogDir + '/' + i)
	del Allfiles
	
	
	stats = statcounter()
	
	#For Each of the files, open them
	for fpath in LogFiles:
		print("Loading",fpath)
		
		file = gzip.open(fpath,"rb")
		Date = FileNameToDate(fpath)
		while True:
			Line = file.readline().decode("utf-8")
			if Line == '':
				break
			else:
				if re.match(r"\A\[[0-9]{2}:[0-9]{2}:[0-9]{2}\]",Line) != None:
					stats.injest(Line,Date)
					
		stats.nextFileTrigger()
		
		file.close()
		
	stats.genreport(OutDir)
	print("Done")
	
	
	
	
	
	
	
if __name__ == '__main__':
	if len(sys.argv) == 1:
		print("Error, Usage:")
		print(sys.argv[0],"<Log Dir>","<Destination Dir>")
		print("Eg:",sys.argv[0],"Myserver/logs/","reports/")
	else:
		main(sys.argv[1],sys.argv[2])
