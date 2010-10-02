#!/usr/bin/env python
# genetic.py
#

import random
import pickle		
import pyBogged

MAXIMIZE, MINIMIZE = 11, 22
env=None

class Individual(object):
	alleles = (0,1)
	length = 30
	seperator = ''
	optimization = MINIMIZE

	def __init__(self, chromosome=None):
		self.chromosome = chromosome or self._makechromosome()
		self.score = None  # set during evaluation
	
	def _makechromosome(self):
		"makes a chromosome from randomly selected alleles."
		return [random.choice(self.alleles) for gene in range(self.length)]

	def evaluate(self, optimum=None):
		"this method MUST be overridden to evaluate individual fitness score."
		pass
	
	def crossover(self, other):
		"override this method to use your preferred crossover method."
		return self._twopoint(other)
	
	def mutate(self, gene):
		"override this method to use your preferred mutation method."
		self._pick(gene) 
	
	# sample mutation method
	def _pick(self, gene):
		"chooses a random allele to replace this gene's allele."
		self.chromosome[gene] = random.choice(self.alleles)
	
	# sample crossover method
	def _twopoint(self, other):
		"creates offspring via two-point crossover between mates."
		left, right = self._pickpivots()
		def mate(p0, p1):
				chromosome = p0.chromosome[:]
				chromosome[left:right] = p1.chromosome[left:right]
				child = p0.__class__(chromosome)
				child._repair(p0, p1)
				return child
		return mate(self, other), mate(other, self)

	# some crossover helpers ...
	def _repair(self, parent1, parent2):
		"override this method, if necessary, to fix duplicated genes."
		pass

	def _pickpivots(self):
		left = random.randrange(1, self.length-2)
		right = random.randrange(left, self.length-1)
		return left, right

	#
	# other methods
	#

	def __repr__(self):
		"returns string representation of self"
		return '<%s chromosome="%s" score=%s>' % \
					(self.__class__.__name__,
					self.seperator.join(map(str,self.chromosome)), self.score)

	def __cmp__(self, other):
		if self.optimization == MINIMIZE:
				return cmp(self.score, other.score)
		else: # MAXIMIZE
				return cmp(other.score, self.score)
	
	def copy(self):
		twin = self.__class__(self.chromosome[:])
		twin.score = self.score
		return twin


class Environment(object):
	def __init__(self, kind, population=None, size=100, maxgenerations=100, 
					crossover_rate=0.90, mutation_rate=0.01, optimum=None):
		self.kind = kind
		self.size = size
		self.optimum = optimum
		self.population = population or self._makepopulation()
		for individual in self.population:
				individual.evaluate(self.optimum)
		self.crossover_rate = crossover_rate
		self.mutation_rate = mutation_rate
		self.maxgenerations = maxgenerations
		self.generation = 0
		self.report()

	def _makepopulation(self):
		return [self.kind() for individual in range(self.size)]
	
	def run(self):
		while not self._goal():
				self.step()
	
	def _goal(self):
		return self.generation > self.maxgenerations or \
					self.best.score == self.optimum
	
	def step(self):
		self.population.sort()
		self._crossover()
		self.generation += 1
		self.report()
	
	def _crossover(self):
		next_population = [self.best.copy()]
		while len(next_population) < self.size:
				mate1 = self._select()
				if random.random() < self.crossover_rate:
					mate2 = self._select()
					offspring = mate1.crossover(mate2)
				else:
					offspring = [mate1.copy()]
					if random.random < 0.4:
						offspring.append(make1.copy())
				for individual in offspring:
					self._mutate(individual)
					individual.evaluate(self.optimum)
					next_population.append(individual)
		self.population = next_population[:self.size]

	def _select(self):
		"override this to use your preferred selection method"
		return self._tournament()
	
	def _mutate(self, individual):
		for gene in range(individual.length):
				if random.random() < self.mutation_rate:
					individual.mutate(gene)

	#
	# sample selection method
	#
	def _tournament(self, size=8, choosebest=0.90):
		competitors = [random.choice(self.population) for i in range(size)]
		competitors.sort()
		if random.random() < choosebest:
				return competitors[0]
		else:
				return random.choice(competitors[1:])
	
	def best():
		doc = "individual with best fitness score in population."
		def fget(self):
				return self.population[0]
		return locals()
	best = property(**best())

	def report(self):
		print "="*70
		print "generation: ", self.generation
		print "best:		", self.best


"""
Use this genetic code to generate/evaluate new sets of dice.
The main challange is to write an evaluation function that results in interesting sets.
"""
class setadice(Individual):
	"""A subclass of individual for bogged dice sets"""

	def __init__(self,chromosome=None):
		"""Setup of length, optimization type, making chromosome from string, etc"""
		self.optimization = MAXIMIZE
		self.length=16*6
		self.alleles="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		self.score=0
		if type(chromosome) == type(""):
			self.chromosome=[]
			for chr in chromosome:
				self.chromosome.append(chr)
		else:
			self.chromosome = chromosome or self._makechromosome()
						
	def freqsort(self, die):
				"""Take a list, sort it in order of frequency in letter_freq"""
				sorted=[]
				for letter in letter_freq:
					for a in range(die.count(letter.upper())):
						sorted.append(letter.upper())
				return sorted	
		
	def dicesort(self):
				"""A stable chromosome sort, which doesn't affect the effect of the genes, but re-arranges them into a constant order"""
				#This is done by sorting each die (set of six letters) and then sorting the dice.
				#all sorts are done in order of freq in letter_freq. This is so that more common letters
				#end up at one end of the chromosome. Should make mating more consistent.
				scores=[]
				chromosome=[]
				print "a"+"".join(self.chromosome)
				for i in range(16):
					die=self.chromosome[i*6:(i+1)*6]
					die=self.freqsort(die)
					score=0
					for j in range(6):
						score+=letter_freq.index(die[j].lower())
					scores.append(score)
					chromosome.extend(die)
				print "c"+"".join(chromosome)
				order=scores[:]
				order.sort(reverse=True)
				self.chromosome=chromosome
				chromosome=[]
				while len(order):
					print "d"+"".join(chromosome)
					index=scores.index(order.pop())
					#cludge: set that score to an unattainable value, to prevent it from being selected twice.
					#max score for a dice would b 6 j's, or 6*26
					scores[index]=8*30
					chromosome.extend(self.chromosome[index*6:(index+1)*6])
				print "e"+"".join(chromosome)
				self.chromosome=chromosome

	def addallwords(self,words):
		self.allwords = 0
		for word,count in self.words.iteritems():
			freq = words[word]
			if freq == 1:
				#Unique words are worth 6 points each
				self.allwords += 6 * count
			elif freq < 5:
				#If there's two, their worth 3 points each
				self.allwords += 5 * count
			elif freq < 10:
				#If there's three, two points each
				self.allwords += 4 * count
			elif freq < 18:
				#Less that fifteen? 1 point each
				self.allwords += 2 * count
			else:
				#More than five? minus one point each
				self.allwords -= 2 * count
		self.score = self.lowestscore + self.lowscore + self.average/2 + self.allwords/15 - self.penalties
		max=230
		if self.highscore > max:
			self.score -= (self.highscore - max) * 2
		if self.highestscore > max:
			self.score -= (self.highestscore - max) * 2

	def evaluate(self,optimum=None):
		"""Generates 30 new games, and adds the scores. Also standardizes the chromosomes"""
		# To make things more interesting, penalize for:
		#	more than nine of any letter
		#	more than five letters which have only one
		# Penalize heavily for not having any of a particular letter
					#First, sort the faces on the dice
					#Second, sort the dice by total frequency
		freq=[]
		for index in range(len(self.alleles)):
			count=self.chromosome.count(self.alleles[index])
			chr="0123456789ABCDEFGHIJKLMOP*********"[count]
			freq.append(chr)
		self.freq="".join(freq)


		words={}
		scores=[]
		t=pyBogged.bogged(self.chromosome)
		#Run 30 games
		for i in range(30):
			t.newgame()
			thisscore=0
			for word in t.words:
				thisscore += len(word) - 2
				if not word in words:
					words[word]=1
				else:
					words[word]+=1
			scores.append(thisscore)

		self.penalties=0
		if self.freq.count("1") > 7:
			self.penalties += (self.freq.count("1")-7) * 22
		self.penalties += self.freq.count("0") * 80
		self.penalties += self.freq.count("B") * 6
		self.penalties += self.freq.count("C") * 12
		self.penalties += self.freq.count("D") * 24
		self.penalties += self.freq.count("E") * 48
		self.penalties += self.freq.count("F") * 96
		self.penalties += self.freq.count("G") * 192
		self.penalties += self.freq.count("H") * 192 * 2
		self.penalties += self.freq.count("I") * 192 * 4
		self.penalties += self.freq.count("J") * 192 * 5
		self.penalties += self.freq.count("K") * 192 * 6
		self.penalties += self.freq.count("L") * 192 * 7
		self.penalties += self.freq.count("M") * 192 * 8 

		self.average=sum(scores)/len(scores)
		scores.sort()
		self.lowestscore=scores.pop(0)
		self.lowscore=scores.pop(0)
		self.highestscore=scores.pop()
		self.highscore=scores.pop()
		self.words=words

		self.score = self.lowestscore + self.lowscore + self.average/2 - self.penalties
		return self.score	

	def mutate(self,gene):
		"""most of the time, swap letters around rather than picking new ones"""
		if random.random < 0.15:
			self._pick(gene)
		else:
			gene2=random.randrange(self.length)
			a=self.chromosome[gene]
			self.chromosome[gene]=self.chromosome[gene2]
			self.chromosome[gene2]=a

def save():
	"""pickles the population of dice into the "generations" file for later loading"""
	f=open("generations","w")
	pickle.dump(env,f)
	f.close()

def load():
	"""Loads the pickled population of dice"""
	global env
	try:
		f=open("generations","r")
		env=pickle.load(f)
		f.close()
	except IOError:
		print "="*70
		print "Failed to load previous generations"
		print "Evolution will be started with random chromosomes."
		print "="*70

def report():
	"""Prints the entire population, in a useful format.."""
	print env.population[0].alleles, "Chromosome".ljust(len(env.population[0].chromosome)),"Score"
	for die in env.population:
		dice = []
		for i in range(16):
			dice.append("".join(die.chromosome[i*6:(i+1)*6]))
		chromosome="-".join(dice)
		print die.freq,chromosome,die.lowscore,die.highscore,die.penalties,die.allwords,round(die.average),round(die.score,1)

def step():
	"""This step re-evalutated even the 'Best', preventing a lucky fluke score from dominating for generations"""	
	global env
	if env==None:
		env=Environment(setadice,size=50,mutation_rate=0.03, crossover_rate=0.10)
	env.step()
	#The primary implementation of "Environment" doesn't revaluate the "best" score between generations.
	#Revaluate to prevent a lucky score from dominating for generations.
	env.population[0].evaluate()
	#Count all words in all populations.
	words={}
	for die in env.population:
		for word,count in die.words.iteritems():
			if word in words:
				words[word]+=count
			else:
				words[word]=count
	#Apply global word freq prefs
	for die in env.population:
		die.addallwords(words)
	#Print out word freq info.
	wordfreq={}
	sortedwords=[]
	for word,count in sorted(words.iteritems()):
		if not count in wordfreq:
			wordfreq[count]=1
		else:
			wordfreq[count]+=1
		if count > 70:
			sortedwords.append(word)
	sortedwords.sort()
	print sorted(wordfreq.iteritems())
	env.population.sort()
	report()

def botched_load():
		global env
		env=Environment(setadice,size=50,mutation_rate=0.03, crossover_rate=0.10)
		env.population.append(setadice("ABTLDISTEEEAKWLKUJSZICFTAVROKFSAESTTAAEFIEBGEETLERZARVPGSHCTIOQPNIYRXSNRDQTLLIBFRESCDEMANEGEJASI"))
		env.population.append(setadice("ATTLEISTEAEEKWDLUSSZNYLSAVAEFLSKBCIOBZEPSEAGAKILERRASIPGDHCTIOQPHVFRXZNRDQTNSIJFRASCDLMADEGEBESS"))
		env.population.append(setadice("ABTLDISTEEEAKWLKUJSZICFTAVNOKFSAESTIAAEFAEBGEETLERZTRVPGLHCTIOQPRIYRXSNRDQTESIBFRESCDLMANEGEJASI"))
		env.population.append(setadice("ABTLDISTEEEAKWLKUJSZICFTAVROKFSAESTIAAEFTEBGEETLERZARVPGLRCTIOQPNIYHXZNRDQTESIBFRESCDLMANEGEJASI"))
		env.population.append(setadice("ARTLEISTEEEAKWEDUSSZNSLSEVAEFGSKBGIOLFAYFFFOKETLDRSABVPGLHCTPSQHNIYRXZNRDQTDGIBFRASCDLMANECEJESI"))
		env.population.append(setadice("AUTLSISTEEDAKWMDRRSZNSFTAVAOKFSKSCBODYFYSEDGPETLERBVNAEGLHCSPEQLHIFRXZNRFQNGSIBLEAECETLASEDGJIFI"))
		env.population.append(setadice("ABTLEISTEEEAKWLKUJSIICFTAVROKFSAESTIAAEFTSBGEETLERZARVPGLHCTIONPJIYRXSNRDQTESIBFREDCDLMANEGEQASZ"))
		env.population.append(setadice("ABZLEISTEEEAKWDDUSSZNSBSAVAEFLSKLCHOGFFYFEFGKETLERSARVPGLHCTIOQPNIYRXTNRDQTDSIBFRASCDLMANEGEJESI"))
		env.population.append(setadice("ABTLDISTEEEAKWLKUJSZICFTAVROKFSAESTIAAEFTEBGEETLERZARVPGLHCTIOQPNIYRXSNRDQTESIBFRESCDLMANEGEJASI"))
		env.population.append(setadice("ABTLEISTEEEAKWDLUSSZNSLSAVAEFLSKBCIOTZEPSEAGAKYLERRASIPGDHCTIOQPHVFRXZNRDQTNSIBFRASCDLMADEGEJESI"))
		env.population.append(setadice("ANTLDLSTEEEAKWLKUJSZICFTAVROKFSASSTIAAEFTEBGEPTLERGARVPZIHCTIOQENIYRXSBRDQTEEIBFRESCDLMANEGEJASI"))
		env.population.append(setadice("AKTLSISTEESANWLDUHSZEDFTAVROENFAELTOAAEFTEEGEATFFRCDLRNGNEBSYFRPLCURXLKRAQDGDQIGKEIIIMDLSEHESBSI"))
		env.population.append(setadice("ABTLEISTEEEAKWDLUSSZNSBSAVAEFLSKBCIOTZEASEAGAKYLERRASIPGDHCTIOQPHVFRXZNRDQTNSILFRPSCDLMADEGEJESI"))
		env.population.append(setadice("ACTLTFSBEERAYWLKUJSZNCZTAVRGRFSAEETAAAEFTEDGSHTFEREDRVPGLHCTIOQPNIYRXSNRDQTESIBFRESCDLMANEGEJASI"))
		env.population.append(setadice("ARTLSISTEEDAKWLDURSZNSFTAVAOKFSKSCBODYFYSEDGPENLERBVNCEGLHASPEQLHIFRXSNRFQTGSIBLEAECETMASEDGJIFI"))
		env.population.append(setadice("ABTLIESTEEEFKWDDUSSZDSASAVAEFLGKBCNTYGFIFEFZKETLERRASVPSLHCTIOQPHYLRXGQRNNODSIBFRASCDLMANEGEJESI"))
		env.population.append(setadice("AKTLDISTEEZAKWLKUJSZICFTAVROBFSAESTIAAEFTEBGEETLEREARVPGLHCTIOQPNIYRXSNRDQTESIBFRESCDLMANEGEJASI"))
		env.population.append(setadice("ABTLEISTEEEDKWALUSSZNSLSAVAEFLSKBCIOTZEPSEAGAKYLERRASIPGDHCTIOQPHVFRXZNRDQTNSIBFRASCDLMADEGEJESI"))
		env.population.append(setadice("ABTQEISTEEEAKWDRUSFZNSLSCVAEFLTSBANONYSYFEFGKFTLERRAGVSGLHCPIOQPHIERXZNRDLTDSIBFDASCDLMAKEGEJESI"))
		env.population.append(setadice("ABTLPISTEEEAKWDDUSSZNSLSFXAEFLSKBGHOGFAYFEFOKETLERSARVIGLHCTEGQPNIYRVZNRDQTDSIBFRASCDLMANECEJESI"))
		env.population.append(setadice("ABTLDISTEEEAKWLKUJSZICTTAVROKFSAESTIAAEFTEBGEEFLETZARVPGLHCRIOQPSIYRXZNRDQTDNIBFRASCDLMANEGEJASI"))
		env.population.append(setadice("LPRGZIFFDELSKTERWSSVNSETADAOKFSAELTOAAEFTLEGEATFERCDLRNGNEBSYFEDHISTXUNRDQTLEEBEFAECQGNASESDYIRI"))
		env.population.append(setadice("ARTLSISTEESAKWLDUHCZNDFTAVROKFSAEETOAAEFTEEGEATFEGSDLRNRNLBSYFEPLCURXLNRAQHGDQBGKEIIIMDLSEDESIFI"))
		env.population.append(setadice("LFZLDISTEEEAKWLKUJSAICFTAVROKFSAESTIAAEBTEBGEETLERZTLFNGNESSYOEPECUDXIBRAQHGKQBOKEIIEMDLSERISIFF"))
		env.population.append(setadice("AKTLEISTEEEAKWDDUSSZNSLSAVSEFLSBBPNTGYFYFEIGKETLIRRASVCGLHCTEOQPHLFRXZNRDQODSIBFRAACDFMANEGEJESI"))
		env.population.append(setadice("ABTLEISTEIERKWDLUSSZNSLSAVAEFLSKBCIOTZEPSEAGAKYLERRASIPGDHCNEOQPHVFRXZNADQTTSIBFRASCDLMADEGEJESI"))
		env.population.append(setadice("ARTLSISTEEDAKDLDURSONSFEAVAOKFSKFCBZDYFYSEWGPENLTRBVNAEGLHCSPEQLHIFRXZNRFQTGSIBLEAECETMASEDGJISI"))
		env.population.append(setadice("ABTLTISTEFEAKWDDUSSZGSLSAVAEFLSSBCNONYFYFEENKZTLERRAGVTGLHCPIOQPHIERXFNRDQEDSIBFRASCDLMAKEGEJESI"))
		env.population.append(setadice("ABTLEISTEEEAKWDDUSSZNSLSAVADFLSSBCNONYFYFEFGKZTLERRAGVTGLHCPIOQPHIERXBNRDQTDSIFFRASCELMAKEGEJESI"))
		env.population.append(setadice("ARSLSIETEEZAKWLDURSDNSFTAVJOKFSKSCBODYAYTEDGPENLERBVNAEGLHCSPEQLHIFRXZNRFQDGSIBLEAECKTMASEDEAIFI"))
		env.population.append(setadice("ABTLEIATEEEAKWDDUSSZNSLSAVADFLSKBCHOGFFYFEFGKETLERSARVPGTHCLIOQPNIYRXZEREQTDSIBFRASCDLMSNEGNJESI"))
		env.population.append(setadice("ABTLEISTEEEAKWDDUSSZNSLSAVSEFLSKBPNTGYFYFEIGKETLIRRASVCGLHCTEOQPHLFRXZNRDQODSIBFRAACDFMANEGEJESI"))
		env.population.append(setadice("AETEQISTEEEAKWDRUSSZNSLSAVABFLTSBCNONYFYFEFGKATLERRAGVSGLHCPIOQPHIERXZNLDRTDSIBFDFSCDLMAKEGEJESI"))
		env.population.append(setadice("ARTLSISTEESANWLDUHSZFDFTAVROENFAELTOAAAFTEEEEATGERCDLRNGNEBSYFKPLCURXLKRGQHGDQIFKEIIIMDLSEDESBSI"))
		env.population.append(setadice("EPRGZIFFDLLSKDELWSSVNSETADAOKFSAELTOAAEFTEEGEATFERCDLRNGNEBSYFEDHFSTXUNRDQTLEEBRIAECQGNASESTYIRI"))
		env.population.append(setadice("LBTLEISTEEEAKWDDUSSZNSLSAVAEFASSBCNONYFYFEFGKZTLERRAGVTGLHCPIOQPHIERXFNRDQTDSIBFRASCDLMAKEGEJESI"))
		env.population.append(setadice("ABTLDISTEEEAKWLKUJSZICFTAVROKFSAESTIAAEFTEBGEETLERZARVPGLHCTIOQPNIYRXSNRDQTESIBFRESCDLMANEGEJASI"))
		env.population.append(setadice("ABTLEISTEEEOKWDDUSSZNSLSFVAEFLSKBGHAGFAYFEFOKETCERSARVPGLHLTPGQINIYRXZNRDQTDSIBFRASCDLAMNECEJESI"))
		env.population.append(setadice("ABTLDISTEEEAKSLKEJWZICFTAVROKFSAUSTIAAEFTEBGEETLERZARVPGLHCTIOQPNIYRXSNRDQTESIBFRESCDLMANEGEJASI"))
		env.population.append(setadice("LPRGZIFFDELSITERWSSVNSETADAOKFSAEDTOAAEFTEEGEATFERCDLRLGNEBSYFEDHISTXUNRLQTLEEBNFAECQGNASESDYKRI"))
		env.population.append(setadice("ABTLEISTEEEAKWDDUSSZNSLSAVAEFLSSBCNONYFYFEFGKZTLERRAGVTGLHCPISQPHIERXFNRDQTDSIBFRAOCDLMAKEGEJESI"))
		env.population.append(setadice("ABTLEISTEEEAKWDLUSSZNSLSAVAEFLSKBCIOTEZPSEAGAKYLERRASIPGDHCTIOQPHVFRXZNRDQTNSIBFRASCDLMADEGEJESI"))
		env.population.append(setadice("LSTGFISAVESBOXTRRKSLNDREAVAFASSKWCIEFYOPKRFGZEALLATDNBYDQTCSEEQPHIIFEFNRDZLTEEBLUADCGMNSSJZGHEEI"))
		env.population.append(setadice("ABTLEIATEEEAKWDDUSSZSSLSAVAEFLNKBCHOGFFYTEFGKETLERSARVPGFHCLIOQPNIYXRSNRDQTESIBFRESCDMLSNEGEJESI"))
		env.population.append(setadice("ABTLDISTEEEACWLKUJSZIKFTAVROKFSAESTIAAEFTEBGEETLERZARVPGLHCCIOQPNIYRXSNRDQTESIBFRESTDLMANEGEJASI"))
		env.population.append(setadice("ASTLSISPESTFGWLDURRZNSBTAVAOKFSKSCBODYFYSEDGTENLERFVNAEGLHCSPEQLHIFRXZNRFQTGSIBLEAECETMASEDGJIFI"))
		env.population.append(setadice("ARTLSISTEESAKWLGUHCZNDFTAVROKFSAEETOAAEFTEEGEATFEDSDLRNRNLBSYFEPLCURXLNRAQHGDQBGKEIIIMDLSEDESIFI"))
		env.population.append(setadice("ABULEISTREEAKWDDTSSZNSLSFVAEFLSZHGHOGFAYFEFOKETLESSARVDGLBCTPGQINIYRXKNEDQTDSIBFRASCPLMANECEJERI"))
		env.population.append(setadice("ABIQESSTGEEAKWDRUSSZNSLSAVAEFLTSBCNONYFYFEFEKFTLERRAGVSGLHCPIOQPHIIRXZNRDLTDSIBFDASCDLMAKEGEJETE"))
		env.population.append(setadice("ABTDEISTREEAKWDDUSSZNSLSAVSEFLSKBPNTGYFYFEIGKETLIRRASVCGLHCFEOQPHLTRXZNELQODSIBFRAACDFMANEGEJESI"))

def main():
	print "Generating random set of dice. 100 generations."
	print "1 generation will take about 3-10 minutes, and a (wide) report will be printed after each generation"
	print "The current state is saved after each generation, so the process can be interrupted and restarted."
	load()
	for a in range(100):
		step()
		save()
	return 0

def clf():
		global letter_freq
		# esianrtolcdugpmhbyfkvwzxqj but may be different for different languages.
		# So I include the code used to count the letter freq in your dictionary.
		letter_freq="esianrtolcdugpmhbyfkvwzxqj"
		return
		letter_freq=""
		print "groveling through dictionary to count letters"
		f=open("/usr/share/dict/words","r")
		alphabet="abcdefghijklmnopqrstuvwxyz"
		freq = []
		for letter in alphabet:
				freq.append(0)
		for word in f:
				if len(word) == 0:
						continue
				#Ignore words that start with a capital letter.
				if not alphabet.count(word[0]):
						continue
				for letter in word:
						if alphabet.count(letter):
									freq[alphabet.index(letter)]+=1
		order=freq[:]
		order.sort()
		while len(order):
				letter_freq+=(alphabet[freq.index(order.pop())])
		print "frequency order=",letter_freq

if __name__ == "__main__":
	clf()
	print "starting evolution"
	main()
