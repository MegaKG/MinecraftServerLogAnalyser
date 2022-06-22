from HTML_PY import *
import matplotlib.pyplot as plt
import io
import base64
import json

def commonPage(*InnerContent):
	return html(
			header(
				h("Server Statistics",Layer=2),
				br()
			),
			body(*InnerContent),
			footer(
				a("Back to Main Page",EXTRA={'href':'index.html'})
			)
		)
			
			


def fullReport(Dest,PlayerDeaths,PlayerUUIDs,ConnectedByHour,ServerErrorByHour):
	def savePage(IN,Path):
			f = open(Path,"w")
			f.write(str(IN))
			f.close()
			
	def exportPlot(p):
			fobj = io.BytesIO()
			p.savefig(fobj,format="png",bbox_inches='tight')
			fobj.seek(0)
			return 'data:image/png;base64,' + base64.b64encode(fobj.read()).decode()
			
	
	#First the Main Page
	savePage(commonPage(
				h("Contents:",Layer=3),

				ul(
					li(a("Connection Statistics",EXTRA={'href':'ConnectionStats.html'})),
					li(a("Player Statistics",EXTRA={'href':'PlayerStats.html'})),
					li(a("Player Information",EXTRA={'href':'PlayerInfo.html'})),
					li(a("Server Statistics",EXTRA={'href':'ServerStats.html'})),
					li(a("Raw Json",EXTRA={'href':'Raw.html'})),
				)

			),Dest + "/index.html")
	print("Generated Main Page")
	
	#Player Information
	tbl = table(tr(th("Username"),th("UUID")),EXTRA={"border":"1"})
	for player in PlayerUUIDs:
		tbl.append(tr(td(player),td(PlayerUUIDs[player])))
	
	savePage(commonPage(
				h("Player UUIDs:",Layer=3),
				tbl
			),Dest + "/PlayerInfo.html")
	print("Generated Player Information Page")
	
	#Player Statistics
	tbl = table(tr(th("Username"),th("Deaths"),th("Total Hours"),th("Average Hours"),th("Max Hours"),th("Min Hours"),th("Sessions")),EXTRA={"border":"1"})
	for player in PlayerDeaths:
		TotalHours = 0
		Sessions = 0
		
		Times = []
		Prev = False
		Count = 0
		for hour in ConnectedByHour:
			if player in ConnectedByHour[hour]:
				TotalHours += 1
				Prev = True
				Count += 1
			else:
				if Prev == True:
					Prev = False
					Times.append(Count)
					Count = 0
					Sessions += 1
		
		MinHours = min(Times)
		MaxHours = max(Times)
		AvgHours = TotalHours / Sessions

		tbl.append(tr(td(player),td(PlayerDeaths[player]),td(TotalHours),td(AvgHours),td(MaxHours),td(MinHours),td(Sessions)))
		
	del Times
	savePage(commonPage(
				h("Player Statistics:",Layer=3),
				tbl
			),Dest + "/PlayerStats.html")
	print("Generated Player Statistics Page")
	
	
	#Connection Statistics:
	d = div()
	d.append(h("Total Connections By Day Operational",Layer=3))
	DaysPlayers = {}
	
	for stamp in sorted(list(ConnectedByHour.keys())):
		DayStamp = stamp // (10**2)
		DaysPlayers[DayStamp] = set()
		
		for player in ConnectedByHour[stamp]:
			if player not in DaysPlayers[DayStamp]:
				DaysPlayers[DayStamp].add(player)
				
	Days = {}
	DayCount = 0
	for stamp in sorted(list(DaysPlayers.keys())):
		Days[str(stamp)] = len(DaysPlayers[stamp])
		DayCount += 1
	del DaysPlayers
	
	plt.figure(figsize=(10,5))
	plt.tight_layout()
	plt.xlabel("Date")
	plt.ylabel("Connections")
	plt.xticks(rotation = 45)
	plt.bar(list(Days.keys()),list(Days.values()))
	d.append(img(exportPlot(plt)))
	
	del Days
	
	
	d.append(h("Average Connections By Hour of Day",Layer=3))
	Hours = {}
	for i in range(0,24):
		Hours[i] = 0
	
	for stamp in sorted(list(ConnectedByHour.keys())):
		Connected = len(ConnectedByHour[stamp])
		DayHour = stamp - ((stamp//(10**2))*(10**2))
		Hours[DayHour] += Connected
		
	for Hour in Hours:
		Hours[Hour] /= DayCount
		
	plt.figure(figsize=(10,5))
	plt.tight_layout()
	plt.xlabel("Hour of Day")
	plt.ylabel("Connections")
	plt.bar(list(Hours.keys()),list(Hours.values()))
	d.append(img(exportPlot(plt)))
	
	del Hours
	
	savePage(commonPage(
				d

			),Dest + "/ConnectionStats.html")
	print("Generated Connection Statistics Page")
		
	
	
	
	#Raw Data
	savePage(commonPage(
				h("Contents:",Layer=3),

				ul(
					li(a("PlayerDeaths.json",EXTRA={'href':'PlayerDeaths.json'})),
					li(a("PlayerUUIDs.json",EXTRA={'href':'PlayerUUIDs.json'})),
					li(a("ConnectedByHour.json",EXTRA={'href':'ConnectedByHour.json'})),
					li(a("ServerErrorByHour.json",EXTRA={'href':'ServerErrorByHour.json'})),
				)

			),Dest + "/Raw.html")
	print("Generated Raw Page")
	
	#The Json Files
	savePage(json.dumps(PlayerDeaths,indent=4),Dest + "/PlayerDeaths.json")
	savePage(json.dumps(PlayerUUIDs,indent=4),Dest + "/PlayerUUIDs.json")
	#Here we need to convert from set to serialise it
	Out = {}
	for i in ConnectedByHour:
		Out[i] = list(ConnectedByHour[i])
	savePage(json.dumps(Out,indent=4),Dest + "/ConnectedByHour.json")
	del Out
	savePage(json.dumps(ServerErrorByHour,indent=4),Dest + "/ServerErrorByHour.json")
	print("Saved Raw Json Files")
	
	#Finally the Server Statistics
	d = div()
	Hours = {}
	for i in range(0,24):
		Hours[i] = 0
	
	for stamp in sorted(list(ServerErrorByHour.keys())):
		SError = ServerErrorByHour[stamp]
		DayHour = stamp - ((stamp//(10**2))*(10**2))
		Hours[DayHour] += SError
		
	for Hour in Hours:
		Hours[Hour] /= DayCount
		
	plt.figure(figsize=(10,5))
	plt.tight_layout()
	plt.xlabel("Hour of Day")
	plt.ylabel("Errors")
	plt.bar(list(Hours.keys()),list(Hours.values()))
	d.append(img(exportPlot(plt)))
	
	del Hours
	
	
	savePage(commonPage(
			h("Server Load Errors:",Layer=3),
			d
			),Dest + "/ServerStats.html")
	print("Generated Server Statistics")
	
	
	
