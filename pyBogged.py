#!/usr/bin/env python
"""pybogged: A word game implemented with pyGTK"""
__version__ = "1.0"
__author__ = "John Gilmore"
__copyright__ = "(C) 2010 John Gilmore. GNU GPL v3 or later."
__contributors__ = []

#These are in the pytho9n standard library
import ConfigParser
import random
import pipes
import os
import os.path
import time

#These are all part of pyGTK
import pygtk
pygtk.require('2.0')
import gtk
import pango
import gobject


class bogged:
	"""Basic bogged rules engine & dice tracker"""
	def __init__(self,chromosome=None):
		"""Set dice set description,etc"""
		random.seed()
		self.maxwords=0
		self.words  = []
		self.width  = 4
		self.height = 4
		self.grid   = [["A","B","C","D"],["E","F","G","H"],["I","J","K","L"],["M","N","O","P"]]
		self.used   = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
		# Original boggle chromosome:
		chromosome  = "HNWEEVLZNHNRLIXERDNEAGAEPOSCAHREYLVDCMTUIOSUNEEIFFPKASOOABBJHETRVWWATTOOTSYDITSEOSITHIMNUQTTYLER"
		if not chromosome:
			#213 generations optimized chromosome
			#Score = 78.3 words on average.
			#chromosome = "OTZEEAYBYSBPPXMEEOKRARSDARECAPUJSRWSLNITVANOSDAAKYASNSREWBBOTYLWWEFWSQSAEGHNTAMLLNEDNAUTOPEUTESU"
			#This one was evolved with lighter "missing a letter" penaties, and heavier "to many of one char"
			#and "to many only one of X" penalties. Also higher weight for long words.
			#chromosome = "SARDOSTXMVZYGPLNLQSRTOBCOGLOANHJLNOTLNRSRETOSLAIEMRQERGEWAAOEKKPATFWUBUDTSHESEILETRRSEPRYQWSLEEU"
			# Generation=337
			#chromosome = "ATZRWRTALYBVUOXSOISERRELIOTDSNLDBEITRSSETYPEATDILGSEEGRUEANLNLIEBTFWSTOHTSHDLEJPATVASERAMQAIWSOA"
			#Generation=368, added penalty for really small number of words.
			#chromosome = "ABTEWLTIEEVAURXIRSTAREELOVZSSNEOQEEDTSBERTPLOODIGLSSESYUATHMNRAAIRTWODOSLKHDLLJATTCGSRLFMNAPASAY"
			#Generation=377, decided to use computer for something else, I'll stop here most likely.
			chromosome = "AOTEWLTIOETAURRISSVAXEELDDZSRNEEQPDDSSWARTALOOEITLSESZYUETHMNRAGIRTLBVOSLKHOLLJAATCGSTLFMNAPRSEY"
			chromosome = "ABFSZTTEEQEHKWTNUJSCRAFTISASICRDGRTSAAEVIAOGTRSREAZDRVTISACEXESPEEYROEEIDFATEMBLSEEESTQELSLISIPI"
			#chromosome = "AEEPFERSSITPLEEIQEBESRFTBOISUTTDVQTCZRADIDENESIATTLTREVEUSSADAHSWKRRSSAAELIXRRZGIRIGCCOETEMETJYR"
			#Generation = 166, starting from zero with an all-new fitness algo.
			chromosome = "SJPONNSBANDEEAROUNHESZDTEDEKMSTTYEODSLTALUALEGLLHMQSBMRPFLNLSTAPSVEDWTTAASICEXOZGADSRLEPOHEICPEH"
			#ABCDEFGHIJKLMNOPQRSTUVWXYZ
			#8226B1242118355513A7212112
			chromosome = "LLRONWSBRNKDPAXTUNHSZSHNETCDZSTEYEMESFTAHDVLMDJLAMSTOPELTDALSBDPSSTAEGPEAEICNSOAGEQLALEROUEIWPOH"
			#Generation 350 of a new algorythm that punishes for lots of really common words, and punishes for 
			#more than 200 words in the max words of 30 game.
			#least32 greatest152 penalties0 words-456 average78.0 score68.0
			#ABCDEFGHIJKLMNOPQRSTUVWXYZ
			#A3236133416267A22463113223 
			chromosome = "RSQJADAENAOAAKYSNBDOMOCNNOQMMXZSOZZKAAOUIHKNOPGKOBTSTYHCMNSEKHGIOERMEISAWGNWOVARBREXKWTDLAMFILEP"
			#Lest, Greatest, Penalties, Words, Average, Score
			#27 204 0 712 95.0 134.0
			#ABCDEFGHIJKLMNOPQRSTUVWXYZ
			#5252A512813353952482323111 
			chromosome = "FIFHOSGPIOOCNMIPAWLMOAENLSKBRRJBECAFMIKEVEMCARXEITFLCFIQIVWCYOEUEORUUOOSQSIEDAPKSNDWESPMSTPZEHSO"
			chromosome = "OSFIEELUCDKARHPGCFSNXRWNCRGIAEYSROIEBDEIADYWTQCKSSVSIGAEAOWBOTABERPSLEJMUUGZIETMAVLCTVESPKFZOOWD"


		self.dice=[]
		for index in range( self.width * self.height):
			self.dice.append(chromosome[index*6:(index+1)*6])

	def newgame(self):
		"""Start a new game"""
		#Randomly generate array of letters.
		#make a temporary local copy of self.dice
		dice = []
		for i in self.dice:
			dice.append(i)
		for x in range(self.width):
			for y in range(self.height):
				index = random.randrange(len(dice))
				die = dice.pop(index)
				self.grid[x][y] = random.choice(die)
		#Zero "possible two letters" array
		self.possible2letters={}
		#for each letter in grid, set it+neighbor to"true"
		for x in range(self.width):
			for y in range(self.height):
				b = self.grid[x][y]
				if b == "Q":
					b = "U"
					self.possible2letters["QU"]=1
				for i in [-1,0,1]:
					for j in [-1,0,1]:
						if i == 0 and j == 0:
							continue
						#if out of range go to the next loop cycle.
						if x+i < 0 or x+i > self.width-1 or y+j < 0 or y+j > self.height-1:
							continue
						a = self.grid[x+i][y+j]
						self.possible2letters[b+a] = 1
		#Add each unique letter to a string
		letters=""
		for x in range(self.width):
			for y in range(self.height):
				if not letters.count(self.grid[x][y]):
					letters = letters + self.grid[x][y]
		if "Q" in letters and not "U" in letters:
			letters = letters + "U"
		#pipe from "grep" to search the dictionaries for words of three or more letters
		#which have only those letters in them.
		#"zcat -f $files | grep ^\[$letters\]\[$letters\]\[$letters\]\[$letters\]*$"
			#this creates a list of words which consist of only the letters on the grid.
		if os.name=='posix':
			grep=pipes.Template()
			grep.append("zcat --stdout -f $IN", "f-")
			grep.append("grep -E '^[" + letters.swapcase() + "]{3,}$' -", "--")
			dictionary = grep.open("/usr/share/dict/words","r")
		else:
			#On non-POSIX systems, look for "words" in the current directory,
			#and just open it. It'll be a lot slower without grep winnowing out
			#the good stuff, but it'll still work.
			dictionary = open("words","r")
			print("Get a real OS!")
		#Clear wordlist
		self.words=[]
		#Read from the above pipe, and for each word, call checkword and append to words list.
		for word in dictionary:
			word=word.strip()
			#print "checking:" + word
			if self.checkword(word.swapcase()):
				self.words.append(word)
				#print "found:" + word
		self.maxwords=len(self.words)


	def pgrid(self):
		"""prints the grid nicely for command-line debugging"""
		print '/----\\'
		for x in range(self.width):
			a= '|'
			for y in range(self.height):
				if self.used[x][y]:
					a=a+ self.grid[x][y].swapcase()
				else:
					a=a+ self.grid[x][y]
			print a+'|'
		print '\\----/'

	def checkword(self,word):
		"""returns 1 if the given word can actually be legally made on the grid.
			Note that this is called only at the start of a game as part of the
			process of filling the self.words variable. Forever after, self.words
			is used."""
		#reject non-strings and zero length words
		if type(word) != type("t"):
			#print "rejected, not a string"
			return 0
		if not len(word):
			#print "rejected, zero length"
			return 0
		#check that each letter combination exists in possible2letters
		for x in range(len(word)-1):
			if word[x:x+2] not in self.possible2letters:
				#print "rejected, not in 2 letters:" + word[x:x+2]
				return 0
		#for each grid, if it matches the first character:
		for x in range(self.width):
			for y in range(self.height):
				if self.grid[x][y] == word[0]:
					#call checkword2 on the current grid.
					if self.checkword2(word, 0, x, y):
						return 1
		return 0

	def checkword2(self,word, index, x, y):
		"""A recursive function used by checkword"""
		#mark the letter as used
		self.used[x][y]=1
		#print "x=" + str(x) + " y=" +  str(y)
		#self.pgrid()
		#Special handling for the implicit "U" after each "Q"
		if word[index] == "Q" and index+1 < len(word):
			if word[index+1] == "U":
				index += 1
		#return true if at end of word
		if len(word)-1 == index:
			#mark the current letter as unused
			self.used[x][y]=0
			return 1
		#if any neighbor matches the next letter:
		for i in [-1,0,1]:
			for j in [-1,0,1]:
				if i == 0 and j == 0:
					continue
				#if out of range go to the next loop cycle.
				if x+i < 0 or x+i > self.width-1 or y+j < 0 or y+j > self.height-1:
					continue
				a = self.grid[x+i][y+j]
				if self.used[x+i][y+j]:
					# If this letter is already used, it doesn't count
					continue
				if a == word[index+1]:
					#Match found, look for next letter at index+1 on that grid
					if self.checkword2(word,index+1,x+i,y+j):
						#return true if that checkword2 call returned true.
						#mark the that letter as unused
						self.used[x][y]=0
						return 1
		#mark the that letter as unused
		#return False
		self.used[x][y]=0
		return 0

class textMessage:
	"""Display a bunch of passed-in text, nicely word wrapped"""

	def __init__(self,text,title=None,subtitle=None):
		"""Create window"""
		# create a new window
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		#window.set_size_request(200, 100)
		if title is not None:
			window.set_title(title)
		window.set_default_size(500, -1)
		window.set_position(gtk.WIN_POS_CENTER)
		window.connect("delete_event", self.done)

		vbox = gtk.VBox(False, 0)
		window.add(vbox)

		frame = gtk.Frame(subtitle)
		vbox.pack_start(frame, True, True, 5)

		view=gtk.TextView()
		view.set_editable(False)
		view.set_wrap_mode(gtk.WRAP_WORD)
		frame.add(view)
		buf=view.get_buffer()
		buf.set_text(text)

		hbox = gtk.HBox(False, 5)
		vbox.pack_start(hbox,False)

		vbox = gtk.VBox(False, 0)
		hbox.pack_start(vbox,True)

		button = gtk.Button(stock=gtk.STOCK_OK)
		button.connect("clicked", self.ok)
		hbox.pack_start(button, False)
		button.set_flags(gtk.CAN_DEFAULT)
		button.grab_default()

		vbox = gtk.VBox(False, 0)
		hbox.pack_start(vbox,True)

		window.show_all()
		self.window=window


	def ok(self, widget):
		"""Close the window and go away"""
		self.done(widget, None)

	def done(self, widget, entry):
		self.window.hide()
		return True

class gtkbogged:
	def startgame(self, widget):
		"""Start a new game"""
		if len(self.words):
			#Played a game, so record it.
			self.save()
		self.minutes=3
		self.seconds=0
		self.words  = []
		self.ingame = True
		self.saved  = False
		self.gaveup = False
		self.entry.set_text("")
		self.bogged.newgame()
		for x in range(self.bogged.width):
			for y in range(self.bogged.height):
				if self.bogged.grid[x][y] == "Q":
					self.grid[x][y].set_label("Qu")
				else:
					self.grid[x][y].set_label(self.bogged.grid[x][y])
		self.maxscore = 0
		for word in self.bogged.words:
			self.maxscore += len(word) - 2
		self.updatetext()
		self.ingame_changed()

	def updatetext(self):
		"""Update the display of found words in our textbox"""
		buf=self.text.get_buffer()
		if self.gaveup:
			buf.set_text("")
			for word in self.bogged.words:
				sob, eob = buf.get_bounds()
				if word in self.words:
					buf.insert(eob,word+"\t")
				else:
					buf.insert_with_tags_by_name(eob, word+"\t", "missed")
		else:
			buf.set_text("\t".join(self.words))
		self.updatelabel()

	def updatelabel(self):
		"""Update the label with averages, etc. Note this is the only place that the "Score" and "Words" options are used"""
		#Now update the label across the top too.
		average=0
		label = ""
		self.score = 0
		for word in self.words:
			self.score += len(word) - 2
		if self.totalgames != 0:
			if self.options_list["Score"].get_active():
				average = self.totalscore/self.totalgames
			else:
				average = self.totalwords/self.totalgames
		#Show timer only if timer is active
		if self.options_list["Timer"].get_active():
			label += "Time left: " + repr(self.minutes) + ":" + repr(self.seconds).zfill(2) + "\n"
		#Guests don't get shown (or update) the average score
		if not self.options_list["Guest"].get_active():
			if self.totalgames != 0:
				if self.options_list["Score"].get_active():
					average = self.totalscore/self.totalgames
					label += "Average Score: " + repr(average) + "\n"
				else:
					average = self.totalwords/self.totalgames
					label += "Average words: " + repr(average) + "\n"
		#Wording and scoring methods
		if self.options_list["Score"].get_active():
			score = self.score
			label += " Score: " + str(score)
			maxscore = self.maxscore
		else:
			score = len(self.words)
			maxscore = len(self.bogged.words)
			label += " Found " + repr(len(self.words)) + " words"
		#Show max score or maxwords
		if self.options_list["Words"].get_active():
			label += " from a maximum of " + repr(maxscore) + " (" 
			if maxscore:
				label += repr( (score*100)/maxscore)
			else:
				label += "0"
			label += "%)"
		self.label.set_text(label)

	def giveup(self, widget):
		"""give up, show the words the computer found"""
		self.gaveup=True
		self.ingame=False
		self.updatetext()
		self.ingame_changed()
		self.save()

	def ingame_changed(self):
		"""When a game is started or ends, handle timer initialization, disable/enable buttons and checkboxes, etc."""
		for widget in self.disable_list:
			widget.set_sensitive(self.ingame)
		for widget in self.options_list.itervalues():
			widget.set_sensitive(not self.ingame)
		#Now, make either "start game" or "add word" the default
		if self.ingame:
			self.entry.grab_focus()
			if self.timercheckbox.get_active():
				if self.timerid == None:
					self.timerid = gobject.timeout_add(1000,self.timer)
			else:
				if self.timerid is not None:
					gobject.source_remove(self.timerid)
				self.timerid = None
		else:
			self.startgamebutton.grab_focus()
			if self.timerid is not None:
				gobject.source_remove(self.timerid)
			self.timerid=None

	def gridbutton(self, widget):
		"""grid buttons, add the grid's text to the entry"""
		self.entry.set_text(self.entry.get_text() + widget.get_label().swapcase())
		self.checkentry(self.entry)

	def checkentry(self, widget):
		"""Disallow entry of non-creatable words"""
		word = widget.get_text()
		while not self.bogged.checkword(word.swapcase()) and len(word):
			word=word[:-1]
		if word != widget.get_text():
			widget.set_text(word)

	def addword(self, widget):
		"""Add the word to the wordlist, update display of the wordlist"""
		word=self.entry.get_text()
		if word in self.bogged.words and word not in self.words:
			self.words.append(word)
			self.updatetext()
		self.entry.set_text("")

	def clear(self, widget):
		"""Clear the word entry box"""
		self.entry.set_text("")

	def help(self, widget):
		"""Display a brief help window"""
		textMessage("""Game Play:
	Objective: Find lots of words. You'll never find ALL of them, but you can try! 
	Rules: Start you word with any letter cube, move to any adjacent cube, and then to any cube adjacent to that one. Repeat, adding letters as you go, until your word is complete. You may not visit any one block more than once in each word. Diagonal, horizontally up, down, left, or right, are all legal. Words must be at least three letters long, and must be found in the dictionary. Plurals and alternate spellings count as a seperate word.

Options:
	Alternate Scoring: You may simply count words, or you may count points. Each word is worth it's length, minus two. So three letter words are worth 1 point, four letter words worth 2, etc.
	Guest: Playing the game with a shoulder surfer? Want to let him play but don't want to mess up your average? Click "Guest" and any games played don't count towards your average, and aren't included in the log file.
	Timer: You have three minutes to find all the words you can. After three minutes, the game will be automatically terminated. 
	Found words: As part of validating your input, the computer starts each game by groveling through the dictionary, finding all possible words. If you just don't want to know, click this and that information won't be displayed, leaving you with nothing but yourself to compare against.""","Help","Introduction to pyBogged")

	def about(self, widget):
		"""Display a brief about window"""
		textMessage("""ByBogged was written by John Gilmore between 5/17/2010 and 5/24/2010. The inspiration for the word-finding algorythm is borrowed from bogged, written in tcl/tk by Todd David Rudick. I rewrote it in python, creating a GTK user interface, Qu as one tile, guest mode, game logging for later graphing and so forth.
	I borrowed the genetic algorythm for dice generation from some python recipes site somewhere, and added a class at the bottom to apply it to the dice set. The hard part there was coming up with a good criteria for a good set of dice. Feel free to come up with different criteria for what is good, and evolve your own set of dice.""","About","About pyBogged V1.0")

	def exit(self, widget):
		"""Display a confirmation dialogue, and quit. 
		On second thought, just quit!"""
		self.save()
		gtk.main_quit()

	def close(self, widget, entry):
		"""Just call exit"""
		self.exit(widget)

	def save(self):
		"""Log the result of a particular game. Saves the options and averages"""
		if self.saved or self.options_list["Guest"].get_active():
			return
		self.saved=True
		self.totalgames += 1
		self.totalscore += self.score
		self.totalpossiblescore += self.maxscore
		self.totalwords += len(self.words)
		self.totalpossiblewords += len(self.bogged.words)

		config = ConfigParser.SafeConfigParser()
		config.add_section('pyBogged')
		config.add_section('RunningTotals')
		config.set('pyBogged','Timer',repr(self.options_list["Timer"].get_active()))
		config.set('pyBogged','Score',repr(self.options_list["Score"].get_active()))
		config.set('pyBogged','Words',repr(self.options_list["Words"].get_active()))
		config.set('pyBogged','Misses',repr(self.options_list["Misses"].get_active()))
		config.set('pyBogged','Repeats',repr(self.options_list["Repeats"].get_active()))
		config.set('RunningTotals','games',repr(self.totalgames))
		config.set('RunningTotals','score',repr(self.totalscore))
		config.set('RunningTotals','possiblescore',repr(self.totalpossiblescore))
		config.set('RunningTotals','words',repr(self.totalwords))
		config.set('RunningTotals','possiblewords',repr(self.totalpossiblewords))

		try:
			configfile = open(os.path.expanduser('~/.pyBogged/pyBogged.cfg'), 'w+')
		except IOError:
			os.mkdir(os.path.expanduser("~/.pyBogged"))
			configfile = open(os.path.expanduser('~/.pyBogged/pyBogged.cfg'), 'w+')
		config.write(configfile)
		configfile.close()

		#Open log file, and append summary of this game. Use CSV for easy import to spreadsheet
		summary=""
		#correctly-sorting timestamp
		summary+=time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
		summary+=',"'
		summary+=repr(self.options_list["Timer"].get_active())
		#The saved grid
		summary+='","'
		summary+="".join(self.bogged.grid[0])
		summary+="".join(self.bogged.grid[1])
		summary+="".join(self.bogged.grid[2])
		summary+="".join(self.bogged.grid[3])
		summary+='",'
		summary+=repr(self.score)
		summary+=','
		summary+=repr(len(self.words))
		summary+=','
		summary+=repr(self.maxscore)
		summary+=','
		summary+=repr(len(self.bogged.words))
		summary+=',"'
		summary+='","'.join(self.words)
		summary+="\"\n"

		logfile = open(os.path.expanduser('~/.pyBogged/pyBogged_log.csv'),'a+')
		logfile.write(summary)
		logfile.close()

	def load(self):
		"""Load options and averages from previous run of pyBogged"""
		config = ConfigParser.SafeConfigParser()
		config.read(os.path.expanduser('~/.pyBogged/pyBogged.cfg'))

		try:
			self.options_list["Timer"].set_active(config.getboolean('pyBogged', 'Timer'))
			self.options_list["Score"].set_active(config.getboolean('pyBogged', 'Score'))
			self.options_list["Words"].set_active(config.getboolean('pyBogged', 'Words'))
			self.options_list["Repeats"].set_active(config.getboolean('pyBogged', 'Repeats'))
			self.options_list["Misses"].set_active(config.getboolean('pyBogged', 'Misses'))
			self.totalgames = config.getint('RunningTotals', 'games')
			self.totalscore = config.getint('RunningTotals', 'score')
			self.totalpossiblescore = config.getint('RunningTotals', 'possiblescore')
			self.totalwords = config.getint('RunningTotals', 'words')
			self.totalpossiblewords = config.getint('RunningTotals', 'possiblewords')
		except ConfigParser.NoSectionError:
			self.options_list["Timer"].set_active(False)
			self.options_list["Score"].set_active(False)
			self.options_list["Words"].set_active(True)
			self.totalgames = 0
			self.totalscore = 0
			self.totalpossiblescore = 0
			self.totalwords = 0
			self.totalpossiblewords = 0

	def timer(self):
		"""Only called if the timer option is set, counts down to zero and calls the "give up" function"""
		if self.timerid is None:
			return
		self.seconds -= 1
		if self.seconds < 0:
			if self.minutes > 0:
				self.seconds += 60
				self.minutes -= 1
			else:
				self.giveup(None)
				return False
		self.updatelabel()
		return True

	def __init__(self):
		"""Basic variables set. Also GTK window created. GTK window creation is insane!"""
		self.bogged   = bogged()
		self.gaveup   = False
		self.ingame   = False
		self.saved    = True
		self.words    = []
		self.timerid  = None
		self.seconds  = 0
		self.minutes  = 0
		self.maxscore = 0
		self.disable_list = []
		self.options_list = {}


		# create a new window
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)

		window.set_title("PyBogged")
		#window.set_size_request(400, 100)
		window.set_position(gtk.WIN_POS_CENTER)
		window.connect("delete_event", self.close)

		vbox = gtk.VBox(False, 0)
		vbox.set_border_width(5)
		window.add(vbox)
		vbox.show()

		hbox = gtk.HBox(False, 0)
		hbox.set_border_width(5)
		vbox.pack_start(hbox,True,True)
		hbox.show()

		vbox2 = gtk.VBox(False, 3)
		hbox.pack_start(vbox2,False)
		vbox2.show()

		frame = gtk.Frame("Letter Cubes")
		vbox2.pack_start(frame ,False)
		frame.show()

		vbox3 = gtk.VBox(False, 3)
		frame.add(vbox3)
		vbox3.show()

		self.grid=[]
		for x in range(self.bogged.width):
			rowbox= gtk.HBox(True, 5)
			vbox3.add(rowbox)
			rowbox.show()
			self.grid.append([])
			for y in range(self.bogged.height):
				button = gtk.Button(self.bogged.grid[x][y])
				button.connect("clicked", self.gridbutton)
				rowbox.pack_start(button, True, True, 0)
				button.show()
				self.grid[x].append(button)
				self.disable_list.append(button)

		label=gtk.Label("Word")
		vbox2.pack_start(label,False)
		label.show()

		entry = gtk.Entry()
		entry.set_max_length(50)
		entry.set_text("")
		entry.select_region(0, len(entry.get_text()))
		entry.connect("activate", self.addword)
		entry.connect("changed", self.checkentry)
		entry.set_tooltip_text("Type your word here. You'll not be able to type things in that can't be found in the grid above. And only dictionary words can actually be added to the list. You can also click the letters above to add them, one by one, to this box")
		vbox2.pack_start(entry, False, True, 0)
		entry.show()
		self.entry=entry
		self.disable_list.append(entry)

		hbox2 = gtk.HBox(False, 5)
		vbox2.pack_start(hbox2,False)
		hbox2.show()

		button = gtk.Button("_Add word to list")
		button.connect("clicked", self.addword)
		hbox2.pack_start(button, False, True, 0)
		button.set_tooltip_text("Click to (try to) add the word to the list. Or just press \"enter\"")
		button.show()
		self.disable_list.append(button)
		self.addwordbutton=button

		button = gtk.Button("Clear")
		button.connect("clicked", self.clear)
		button.set_tooltip_text("Click to clear the \"Word\" box.")
		hbox2.pack_start(button, False, True, 0)
		button.show()

		hbox2 = gtk.HBox(False,0)
		vbox2.pack_start(hbox2,False,True,0)
		hbox2.show()

		check=gtk.CheckButton("Timer")
		hbox2.pack_start(check,False)
		check.set_active(True)
		check.show()
		check.set_tooltip_text("Check this box for a timed game. Timer is for 3 minutes.")
		self.options_list["Timer"]=check

		self.timercheckbox=check

		check=gtk.CheckButton("Found Words")
		hbox2.pack_start(check,False)
		check.set_active(True)
		check.show()
		check.set_tooltip_text("Check this box to show the number of dictionary words that can be found (max) in this game. It will also display a percentage, showing how many of those words you've found so far.")
		self.options_list["Words"]=check

		hbox2 = gtk.HBox(False,0)
		vbox2.pack_start(hbox2,False,True,0)
		hbox2.show()

		check=gtk.CheckButton("Guest")
		hbox2.pack_start(check,False)
		check.set_active(False)
		check.show()
		check.set_tooltip_text("The game keeps statistics - what your average percentage of found words is, for example. If this box is checked, then this game won't count towards you totals, and in fact won't be recorded at all.")
		self.options_list["Guest"]=check

		check=gtk.CheckButton("Alt. Scoring")
		hbox2.pack_start(check,False)
		check.set_active(False)
		check.show()
		check.set_tooltip_text("Check this box to count \"score\" instead of simply counting workds. Each word is worth it's length, minus two. So three letter words are worth 1 point, four letter words worth 2, etc. Misses are repeated words may optionally be deducted from your score.")
		self.options_list["Score"]=check

		hbox2 = gtk.HBox(False,0)
		vbox2.pack_start(hbox2,False,True,0)
		hbox2.show()

		check=gtk.CheckButton("Misses")
		hbox2.pack_start(check,False)
		check.set_active(False)
		check.show()
		check.set_tooltip_text("If alt. Scoring is checked, and this box is checked, a point will be deducted from your score for each \"word\" you enter that isn't in the dictionary.")
		self.options_list["Misses"]=check

		check=gtk.CheckButton("Repeats")
		hbox2.pack_start(check,False)
		check.set_active(False)
		check.show()
		check.set_tooltip_text("If alt. Scoring is checked, and this box is checked, a point will be deducted from you score for each word you enter that is already in the list")
		self.options_list["Repeats"]=check


		hbox2 = gtk.HBox(False,0)
		vbox2.pack_start(hbox2,True,True,0)
		hbox2.show()

		vbox2 = gtk.VBox(False, 5)
		vbox2.set_border_width(5)
		hbox.pack_start(vbox2)
		vbox2.show()

		label=gtk.Label("Average Score: 0%\nFound 0 words from a maximum of 0 (0%)")
		vbox2.pack_start(label,False)
		label.show()

		self.label=label

		text=gtk.TextView()
		text.set_editable(False)
		text.set_wrap_mode(gtk.WRAP_WORD)
		text.set_tooltip_text("This lists all the words you've found in this game, in alphabetical order. After you give up, you'll be shown all the words you could have found but didn't as well. They're the ones in red.")
		vbox2.pack_start(text)
		text.show()

		tabstops=pango.TabArray(20,False)
		for index in range(20):
			tabstops.set_tab(index,pango.TAB_LEFT,index*pango.SCALE*60)
		text.set_tabs(tabstops)


		missed_tag = gtk.TextTag("missed")
		missed_tag.set_property("foreground", "red")
		text.get_buffer().get_tag_table().add(missed_tag)

		self.text=text

		hbox = gtk.HBox(False,10)
		vbox.pack_start(hbox,False)
		hbox.show()

		button = gtk.Button("_Start Game")
		button.connect("clicked", self.startgame)
		hbox.pack_start(button, True, True, 0)
		button.set_tooltip_text("Start a new game. Options cannot be changed once the game is started, so make sure they're right.")
		button.show()
		self.startgamebutton=button

		button = gtk.Button("_Give Up")
		button.connect("clicked", self.giveup)
		hbox.pack_start(button, True, True, 0)
		button.set_tooltip_text("Had enough? Give up! Then we'll show you all the words you missed!")
		button.show()
		self.disable_list.append(button)

		button = gtk.Button("_Help")
		button.connect("clicked", self.help)
		hbox.pack_start(button, True, True, 0)
		button.show()

		button = gtk.Button("A_bout")
		button.connect("clicked", self.about)
		hbox.pack_start(button, True, True, 0)
		button.show()

		button = gtk.Button("E_xit")
		button.connect("clicked", self.exit)
		hbox.pack_start(button, True, True, 0)
		button.show()


		self.load()
		self.ingame_changed()
		self.updatelabel()

		window.show()

def main():
	gtk.main()
	return 0

if __name__ == "__main__":
	gtkbogged()
	main()
