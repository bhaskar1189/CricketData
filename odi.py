import json
import scrapy
 
class QuotesSpider(scrapy.Spider):
	name = 'odi'
	start_urls=[
		"http://www.espncricinfo.com/ci/engine/series/index.html?season=2017%2F18;view=season",
	]
	def bowlers_details(self,response):
		title=response.meta["title"]
		NoUrl=response.meta["NoUrl"]
		InName=response.meta["InName"]
		Innings=response.meta["Innings"]
		data=json.loads(response.body)
		Inning_one=response.meta["Inning_one"]
		bowlers_urls=response.meta["bowlers_urls"]
		common=response.meta["common"]
		player={
			"Batting_lhb":data["centre"]["bowling"]["batting_lhb"],
			"Batting_rhb":data["centre"]["bowling"]["batting_rhb"],
			"Overall":data["centre"]["bowling"]["overall"],
		}
		common["bowling"].append(player)
		if bowlers_urls:
			link=bowlers_urls.pop()
			yield scrapy.Request(link,callback=self.bowlers_details,meta={'Inning_one':Inning_one,'bowlers_urls':bowlers_urls,'common':common,'Innings':Innings,"InName":InName,'NoUrl':NoUrl,'title':title},dont_filter=True)
		else:
			Inning_one["common"]=common
			Innings[InName].append(Inning_one)
			if(NoUrl):
				yield{
					title:Innings,
				}
	def batsman_details(self,response):
		title=response.meta["title"]
		NoUrl=response.meta["NoUrl"]
		InName=response.meta["InName"]
		Innings=response.meta["Innings"]
		data=json.loads(response.body)
		Inning_one=response.meta["Inning_one"]
		batsman_urls=response.meta["batsman_urls"]
		bowlers_urls=response.meta["bowlers_urls"]
		common=response.meta["common"]
		common["batting"].append(data["centre"]["batting"])
		if batsman_urls:
			link=batsman_urls.pop()
			yield scrapy.Request(link,callback=self.batsman_details,meta={'Inning_one':Inning_one,'batsman_urls':batsman_urls,'bowlers_urls':bowlers_urls,'common':common,'Innings':Innings,"InName":InName,'NoUrl':NoUrl,'title':title},dont_filter=True)
		else:
			link=bowlers_urls.pop()
			yield scrapy.Request(link,callback=self.bowlers_details,meta={'Inning_one':Inning_one,'bowlers_urls':bowlers_urls,'common':common,'Innings':Innings,"InName":InName,'NoUrl':NoUrl,'title':title},dont_filter=True)
	def match_details(self,response):
		Innings=response.meta["Innings"]
		data=json.loads(response.body)
		match={}
		match["batting"]=data["centre"]["batting"]
		match["bowling"]=data["centre"]["bowling"]
		Innings["matchDetails"].append(match)
	def takeCommentaryDetails(self,response):
		Innings=response.meta["Innings"]
		tot_text=response.xpath("//div[@class='commentary-section']//text()").extract()
		commentary=[]
		for text in tot_text:
			text=str(text.encode("utf-8")).decode("unicode-escape").encode("ascii","ignore").replace("'","").replace('"',"").replace("\n","").replace("\t","")
			if text.strip():
				commentary.append(text)
		title=response.meta['title']
		com={title:commentary}
		Innings["commentary"].append(com)
	def commentary(self,response):
		Innings=response.meta["Innings"]
		Innings["commentary"]=[]
		urls=response.xpath("//ul[@class='tabs-block inline-list clearfix']/li/a")
		for link in urls:
			title=str(link.xpath(".//text()").extract()).decode("unicode-escape").encode("ascii","ignore").replace("u'","").replace("']","").replace("[","")
			send_link=link.xpath(".//@href").extract()
			link=str(send_link).decode("unicode-escape").encode("ascii","ignore").replace("u'","").replace("[","").replace("]","").replace("'","")
			send_link="http://www.espncricinfo.com"+link
			yield scrapy.Request(send_link,callback=self.takeCommentaryDetails,meta={'title':title,'Innings':Innings},dont_filter=True)
	def starting_parse(self,response):
		title=response.meta["title"]
		matchid=response.meta["matchid"]
		NoUrl=response.meta["NoUrl"]
		In=response.meta["In"]
		InName=response.meta["InName"]
		Innings=response.meta["Innings"]
		Innings[InName]=[]
		data = json.loads(response.body)
		centre=str(data["centre"])
		if centre !="{}":
			Inning_one={}
			Inning_one['Batting']=data["centre"]["batting"]
			Inning_one['Bowling']=data["centre"]["bowling"]
			Inning_one['Partnership']=data["centre"]["fow"]
			batting=data["centre"]["common"]["batting"]
			bowling=data["centre"]["common"]["bowling"]
			Inning_one["common"]=[]
			common={}
			common["batting"]=[]
			common["bowling"]=[] 
			batsman=[]
			bowlers=[]
			for bat in batting:
				batsman.append("http://www.espncricinfo.com/ci/engine/match/live/centre/"+matchid+".json?batsman="+bat['player_id']+";card=batting;innings="+str(In)+";xhr=1")
			for bowl in bowling:
				bowlers.append("http://www.espncricinfo.com/ci/engine/match/live/centre/"+matchid+".json?bowler="+bowl['player_id']+";card=bowling;innings="+str(In)+";xhr=1")
			link=batsman.pop()
			yield scrapy.Request(link,callback=self.batsman_details,meta={'Inning_one':Inning_one,'batsman_urls':batsman,'bowlers_urls':bowlers,'common':common,'Innings':Innings,"InName":InName,'NoUrl':NoUrl,'title':title},dont_filter=True)
	def start_parse(self,response):
		title=response.meta["title"]
		Innings=response.meta["Innings"]
		matchid=response.meta['matchid']
		data=json.loads(response.body)
		centre=str(data["centre"])
		if centre !="{}":
			innings_list=data["centre"]["common"]["innings_list"]
			innings_count=0
			In_List=[]
			for item in innings_list:
				In_List.append(item["description"])
				innings_count+=1
			i=innings_count
			urls=[]
			while(i is not 0):
				urls.append('http://www.espncricinfo.com/ci/engine/match/live/centre/'+matchid+'.json?innings='+str(i)+';xhr=1')
				i-=1
			Innings['matchDetails']=[]
			i=0
			while(True):
				if(urls):
					link=urls.pop()
					NoUrl=True
					if(urls):
						NoUrl=False
					yield scrapy.Request(link,callback=self.starting_parse,meta={'Innings':Innings,"InName":In_List[i],"In":i+1,'NoUrl':NoUrl,'title':title,'matchid':matchid},dont_filter=True)
					i=i+1
				else:
					match="http://www.espncricinfo.com/ci/engine/match/live/centre/"+matchid+".json?card=match;xhr=1"
					yield scrapy.Request(match,callback=self.match_details,meta={'Innings':Innings,'title':title},dont_filter=True)
					break
	def PlayerVsPlayer(self,response):
		Innings=response.meta["Innings"]
		div=response.xpath("//div[@id='stats-container']/div[@id='playerstats']")
		inningName=response.xpath("//div[@id='playerstats']//h6/text()").extract()
		j=0
		for k in inningName:
			j+=1
		PlayerDetails={}
		i=0
		for i in range(0,j):
			name=inningName[i]
			PlayerDetails[name]=[]
			id="\'team"+str(i+1)+"-1-block\'"
			path=".//div[@id="+id+"]/table[@class='innings-table']"
			players=response.xpath(path)
			for player in players:
				playerName=str(player.xpath(".//caption/text()").extract()).decode("unicode-escape").encode("ascii","ignore").replace("u'","").replace("[","").replace("]'","")
				table=player.xpath(".//tr")
				for tr in table:
					playerDet={}
					keys=['BowlerName','0s','1s','2s','3s','4s','5s','6s','7+']
					td=tr.xpath(".//td/text()")
					dicts={}
					j=0
					appends=[]
					for tds in td:
						take=tds.extract()
						if(j<9):
							dicts[keys[j]]=take
						if(j>=9):
							appends.append(take)
						j=j+1
					if appends:
						if(appends[0]=="bowled" or appends[0]=="stumped" or appends[0]=="lbw" or appends[0]=="caught"):
							dicts['Dismissal']=appends[0]
							dicts['Runs']=appends[1]
							dicts['Balls']=appends[2]
							dicts['SR']=appends[3]
						else:
							dicts['Runs']=appends[0]
							dicts['Balls']=appends[1]
							dicts['SR']=appends[2]
						playerDet[playerName]=dicts
						PlayerDetails[name].append(playerDet)
			i=i+1
		Innings["PlayerVsPlayer"].append(PlayerDetails)
	def First_Link(self, response):
		title=response.xpath("//title/text()").extract()
		title=str(title).rsplit(',',2)[0]
		title=title.replace("u'","").replace("[","").replace("u\\","")
		matchid=response.xpath("//div[@id='matchId']/@data-matchid").extract()
		matchid=str(matchid).decode("unicode-escape").encode("ascii","ignore").replace("u'","").replace("']","").replace("[","")
		Innings={}
		Innings["PlayerVsPlayer"]=[]
		url=(response.url).replace(".html",".json")
		pvp=(response.url)+"?view=pvp"
		com_link=response.urljoin(response.xpath("//div[@class='menuArchive']/span/a/@href")[0].extract())
		yield scrapy.Request(url,callback=self.start_parse,meta={'matchid':matchid,'Innings':Innings,'title':title},dont_filter=True)
		yield scrapy.Request(com_link,callback=self.commentary,meta={'Innings':Innings},dont_filter=True)
		yield scrapy.Request(pvp,callback=self.PlayerVsPlayer,meta={'Innings':Innings},dont_filter=True)
	def get_details(self,response):
		urls=response.meta["urls"]
		extract_links=response.meta['extract_links']
		div=response.xpath("//span[@class='match-no']/a/@href").extract()
		for link in div:
			extract_links.append("http://cricinfo.com"+link)
		if urls:
			link=urls.pop()
			yield scrapy.Request(link,callback=self.get_details,meta={'urls':urls,'extract_links':extract_links},dont_filter=True)
		else:
			i=0
			for link in extract_links:
				i+=1
				yield scrapy.Request(link,callback=self.First_Link,dont_filter=True)
			print "Counting",i
	def parse_links(self,response):
		extract_links=response.meta['extract_links']
		urls=response.meta['urls']
		link_urls=response.meta['link_urls']
		div=response.xpath("//section[@class='series-summary-wrap']")
		i=0
		for links in div:
			link=links.xpath(".//section['series-summary-block collapsed']")
			i+=1
			if i==1:
				continue
			for url in link:
				check=url.xpath(".//div[@class='result-info']/span/text()")
				if check:
					url=url.xpath(".//@data-summary-url").extract()
					if str(url).replace("[]","").strip():
						urls.append("http://cricinfo.com"+str(url).replace("[u'","").replace("']",""))
			break
		if(link_urls):
			link=link_urls.pop()
			yield scrapy.Request(link,callback=self.parse_links,meta={'extract_links':extract_links,'urls':urls,'link_urls':link_urls},dont_filter=True)
		else:
			link=urls.pop()
			yield scrapy.Request(link,callback=self.get_details,meta={'urls':urls,'extract_links':extract_links},dont_filter=True)
	def parse(self,response):
		link_urls=[
			#"http://www.espncricinfo.com/ci/engine/series/index.html?season=2017;view=season",
			#"http://www.espncricinfo.com/ci/engine/series/index.html?season=2016%2F17;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2016;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2015%2F16;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2015;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2014%2F15;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2014;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2013%2F14;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2013;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2012%2F13;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2012;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2011%2F12;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2011;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2010%2F11;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2010;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2009%2F10;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2009;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2008%2F09;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2008;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2007%2F08;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2007;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2006%2F07;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2006;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2005%2F06;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2005;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2004%2F05;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2004;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2003%2F04;view=season",
			"http://www.espncricinfo.com/ci/engine/series/index.html?season=2003;view=season",
		]
		extract_links=[]
		urls=[]
		if(link_urls):
			link=link_urls.pop()
			yield scrapy.Request(link,callback=self.parse_links,meta={'extract_links':extract_links,'urls':urls,'link_urls':link_urls},dont_filter=True)