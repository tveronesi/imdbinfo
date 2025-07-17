# imdbinfo
A Python package to fetch and manage IMDb movie information easily.

## Requirements

Python (3.7 or higher)

## Installation

`pip install imdbinfo`

## Usage

``` python
from imdbinfo.services import search_title, get_movie

# Search for a movie by title
results = search_title("The Matrix")
for movie in results.titles:
    print(f"{movie.title} ({movie.year}) - {movie.imdb_id}")
``` 
Will output:
``` 
Matrix (1999) - 0133093
Matrix Reloaded (2003) - 0234215
Matrix Resurrections (2021) - 10838180
Matrix Revolutions (2003) - 0242653
The Matrix Recalibrated (2004) - 0410519
``` 

The search results : 

``` python
print(results.model_dump_json())
```

The search results output will look like this:
``` json
{
  "titles": [
    {
      "imdbId": "tt0133093",
      "imdb_id": "0133093",
      "title": "Matrix",
      "cover_url": "https://m.media-amazon.com/images/M/MV5BOWVlOTU2MzktN2Q0Ny00Y2M5LTkzY2QtNjBjOWRhZTQwMmQxXkEyXkFqcGc@._V1_.jpg",
      "url": "https://www.imdb.com/title/tt0133093/",
      "year": 1999,
      "kind": "movie"
    },
    {
      "imdbId": "tt0234215",
      "imdb_id": "0234215",
      "title": "Matrix Reloaded",
      "cover_url": "https://m.media-amazon.com/images/M/MV5BMTMwNjM4NjAzOF5BMl5BanBnXkFtZTcwODI2MDEyMQ@@._V1_.jpg",
      "url": "https://www.imdb.com/title/tt0234215/",
      "year": 2003,
      "kind": "movie"
    },
    {
      "imdbId": "tt10838180",
      "imdb_id": "10838180",
      "title": "Matrix Resurrections",
      "cover_url": "https://m.media-amazon.com/images/M/MV5BMDMyNDIzYzMtZTMyMy00NjUyLWI3Y2MtYzYzOGE1NzQ1MTBiXkEyXkFqcGc@._V1_.jpg",
      "url": "https://www.imdb.com/title/tt10838180/",
      "year": 2021,
      "kind": "movie"
    },
    {
      "imdbId": "tt0242653",
      "imdb_id": "0242653",
      "title": "Matrix Revolutions",
      "cover_url": "https://m.media-amazon.com/images/M/MV5BZGFkNmFhMzUtZTQ4Yy00YjgxLWEwZjEtNjY3MjUwN2Y1ODk0XkEyXkFqcGc@._V1_.jpg",
      "url": "https://www.imdb.com/title/tt0242653/",
      "year": 2003,
      "kind": "movie"
    },
    {
      "imdbId": "tt0410519",
      "imdb_id": "0410519",
      "title": "The Matrix Recalibrated",
      "cover_url": "https://m.media-amazon.com/images/M/MV5BZjU2Y2FmNjEtYTc5Ni00MmMyLTljOTktODdkNmQ0YTk1NjYwXkEyXkFqcGc@._V1_.jpg",
      "url": "https://www.imdb.com/title/tt0410519/",
      "year": 2004,
      "kind": "video"
    }
  ],
  "names": [
    {
      "name": "The Matrix",
      "id": "nm4210667",
      "url": "https://www.imdb.com/name/nm4210667",
      "job": "Soundtrack"
    },
    {
      "name": "Vasyl Lomachenko",
      "id": "nm5263899",
      "url": "https://www.imdb.com/name/nm5263899",
      "job": "Actor"
    },
    {
      "name": "Rooney Mara",
      "id": "nm1913734",
      "url": "https://www.imdb.com/name/nm1913734",
      "job": "Actress"
    },
    {
      "name": "Ye",
      "id": "nm1577190",
      "url": "https://www.imdb.com/name/nm1577190",
      "job": "Soundtrack"
    },
    {
      "name": "Etta James",
      "id": "nm0416483",
      "url": "https://www.imdb.com/name/nm0416483",
      "job": "Actress"
    }
  ]
}

```

The full details of the search results are :
``` python
print(movie.model_dump_json())
```

And the json output will look like this:
``` json
{
  "imdbId": "tt0133093",
  "imdb_id": "0133093",
  "title": "The Matrix",
  "kind": "movie",
  "url": "https://www.imdb.com/title/tt0133093/",
  "cover_url": "https://m.media-amazon.com/images/M/MV5BOWVlOTU2MzktN2Q0Ny00Y2M5LTkzY2QtNjBjOWRhZTQwMmQxXkEyXkFqcGc@._V1_.jpg",
  "plot": "When a beautiful stranger leads computer hacker Neo to a forbidding underworld, he discovers the shocking truth--the life he knows is the elaborate deception of an evil cyber-intelligence.",
  "release_date": "1999-05-07",
  "languages": [
    "en"
  ],
  "certificates": {
    "AR": [
      "Argentina",
      "13"
    ],
    /* removed for brevity  53 certificate elements*/
  },
  "directors": [
    {
      "name": "Lana Wachowski",
      "id": "nm0905154",
      "url": "https://www.imdb.com/name/nm0905154",
      "job": "Director"
    },
    {
      "name": "Lilly Wachowski",
      "id": "nm0905152",
      "url": "https://www.imdb.com/name/nm0905152",
      "job": "Director"
    }
  ],
  "cast": [
    {
      "name": "Keanu Reeves",
      "id": "nm0000206",
      "url": "https://www.imdb.com/name/nm0000206",
      "job": "Cast"
    },
    {
      "name": "Laurence Fishburne",
      "id": "nm0000401",
      "url": "https://www.imdb.com/name/nm0000401",
      "job": "Cast"
    },
    {
      "name": "Carrie-Anne Moss",
      "id": "nm0005251",
      "url": "https://www.imdb.com/name/nm0005251",
      "job": "Cast"
    },
    {
      "name": "Hugo Weaving",
      "id": "nm0915989",
      "url": "https://www.imdb.com/name/nm0915989",
      "job": "Cast"
    }
  ],
  "year": 1999,
  "duration": 136,
  "country_codes": [
    "US",
    "AU"
  ],
  "rating": 8.7,
  "metacritic_rating": 73,
  "votes": 2170072,
  "trailers": [
    "https://www.imdb.com/video/vi1032782617",
    "https://www.imdb.com/video/vi3203793177"
  ],
  "genres": [
    "Action",
    "Sci-Fi"
  ],
  "interests": [
    "Action Epic",
    "Artificial Intelligence",
    "Cyberpunk",
    "Dystopian Sci-Fi",
    "Gun Fu",
    "Martial Arts",
    "Sci-Fi Epic",
    "Action",
    "Sci-Fi"
  ],
  "worldwide_gross": "467841735 USD",
  "production_budget": "63000000 USD",
  "storyline_keywords": [
    "artificial reality",
    "war with machines",
    "simulated reality",
    "dystopia",
    "questioning reality"
  ],
  "filming_locations": [
    "Nashville, Tennessee, USA"
  ],
  "sound_mixes": [
    "DTS",
    "Dolby Digital",
    "SDDS",
    "Dolby Atmos"
  ],
  "processes": [
    "Digital Intermediate",
    "Dolby Vision",
    "Super 35",
    "VistaVision"
  ],
  "printed_formats": [
    "16 mm",
    "70 mm",
    "35 mm"
  ],
  "negative_formats": [
    "16 mm",
    "35 mm"
  ],
  "laboratories": [
    "Technicolor, Hollywood (CA), USA",
    "Atlab Film Laboratory Service, Sydney, Australia"
  ],
  "colorations": [
    "Color"
  ],
  "cameras": [
    "Arriflex 435, Panavision Primo Lenses",
    "Panavision Panaflex Platinum, Panavision Primo Lenses",
    "Panavision Panastar, Panavision Primo Lenses",
    "Photosonics Camera"
  ],
  "aspect_ratios": [
    [
      "2.20 : 1",
      "70 mm prints"
    ],
    [
      "2.39 : 1",
      ""
    ]
  ],
  "summaries": [
    "Thomas A. Anderson is a man living two lives. By day he is an average computer programmer and by night a hacker known as Neo. Neo has always questioned his reality, but the truth is far beyond his imagination. Neo finds himself targeted by the police when he is contacted by Morpheus, a legendary computer hacker branded a terrorist by the government. As a rebel against the machines, Neo must confront the agents: super-powerful computer programs devoted to stopping Neo and the entire human rebellion."
  ],
  "synopses": [
    "In 1999, in an unnamed city, Computer programmer Thomas Anderson (Keanu Reeves) is secretly a hacker known as &quot;Neo&quot;. He is restless, eager and driven to learn the meaning of cryptic references to the &quot;Matrix&quot; appearing on his computer.\nA woman named Trinity is observing Neo, and she does so knowing that Morpheus believes that Neo is &quot;the One&quot;.<br/><br/>During one of her forays, Trinity is tracked down by the local police to her hotel room. Outside the hotel a car drives up and three agents appear in neatly pressed black suits. They are Agent Smith (Hugo Weaving), Agent Brown (Paul Goddard), and Agent Jones (Robert Taylor). Trinity calls Morpheus and says that her line was tracked and Morpheus orders her to find another exit.\nTrinity easily defeats the six policemen sent to apprehend her, using fighting and evasion techniques that seem to defy gravity.<br/><br/>A fierce rooftop chase ensues with Trinity and an Agent leaping impossibly from one building to the next, astonishing the policemen left behind. Trinity makes a daring leap across an alley and through a small window. Trinity makes it to a public phone booth on the street level. The phone begins to ring. As she approaches it a garbage truck, driven by Agent Smith, careens towards the phone booth. Trinity makes a desperate dash to the phone, picking it up just moments before the truck smashes the booth into a brick wall. The three Agents find no body in the wreckage. &quot;She got out,&quot; one says. The other says, &quot;The informant is real.&quot; &quot;We have the name of their next target,&quot; says the other, &quot;His name is Neo.&quot;<br/><br/>Notices about a manhunt for a man named Morpheus scroll across Neo&#39;s screen as he sleeps. Suddenly Neo&#39;s screen goes blank, and a series of text messages appear: &quot;Wake up, Neo.&quot; &quot;The Matrix has you.&quot; &quot;Follow the White Rabbit.&quot; A group of ravers comes to Neo and Neo gives them a contraband disc he has secreted in a copy of &quot;Simulacra and Simulation.&quot; The lead raver asks him to join them and Neo demurs until he sees the tattoo of a small white rabbit on the shoulder of a seductive girl in the group.<br/><br/>Trinity approaches Neo at the rave bar. Neo recognizes her name as she was a famous hacker and had cracked the IRS database.\nA female hacker named Trinity (Carrie-Anne Moss) confirms that a man named Morpheus (Laurence Fishburne) can help him.<br/><br/>Neo works at Metacortex, a leading software company housed in an ominous high rise. At his desk, Neo finds a package with a phone, which rings. On the other end is Morpheus, who informs Neo that they&#39;ve both run out of time and that &quot;they&quot; are coming for him. Morpheus tells him to slowly look up, toward the elevator. Agents Smith, Jones, and Brown are there, obviously looking for him, as a woman points towards Neo&#39;s cube.<br/><br/>Three sinister Agents, led by Agent Smith (Hugo Weaving), come to arrest Neo and attempt to prevent him from collaborating with Morpheus. Morpheus guides Neo&#39;s escape by phone, able to somehow remotely observe their movements. Morpheus tries to guide Neo out of the building but when he is instructed to get on a scaffolding and take it to the roof Neo rejects Morpheus&#39; advice, allowing himself to be taken by the Agents.<br/><br/>The Agents interrogate Neo about Morpheus, but he refuses to cooperate. Agent Smith asks him to help them capture Morpheus, considered a dangerous terrorist, in exchange for amnesty. Neo gives them the finger and asks for his phone call. In response, Neo&#39;s mouth suddenly seals shut, and the Agents implant a robotic device in his abdomen. Neo awakens at home, initially dismissing the encounter as a nightmare.<br/><br/>Neo awakens with a start in his own bed. Morpheus is on the other line. Morpheus tells Neo he is the One and to meet him at the Adams St. bridge. There he is picked up by Trinity and two others in a car. A woman in the front seat, Switch (Belinda McClory) uses a device to remove the probe that Neo believed had been part of a nightmare. Trinity drops the bug out into the road where it slowly goes dark in the rain.\nTrinity and her allies bring Neo to Morpheus, their leader.<br/><br/>Undeterred, Neo meets with Morpheus. Morpheus offers Neo a choice: a red pill to uncover the truth about the Matrix or a blue pill to forget everything and return to his normal life. Neo agrees to follow him by swallowing an offered red pill. As the rest of Morpheus&#39;s crew straps him into a chair, Neo is told that pill he took is part of a trace program, to &quot;disrupt his input/output carrier signal&quot; so that they can pinpoint him.\nOpting for the red pill, Neo&#39;s reality distorts, and he awakens submerged in a liquid-filled, mechanical pod with invasive cables running throughout his body. He is hairless and naked, with thick black tubes snaking down his throat, plugged into the back of his skull, his spine, and invading most of the rest of his body.<br/><br/>Neo is connected along with thousands of other people to an elaborate electrical structure. Suddenly a menacing, hovering nurse robot grabs him by the throat. The cable inserted into the base of his skull suddenly detaches. The rest of the tubes pop off his limbs and Neo is flushed down a tube into an underground pool of filthy water. Just as he&#39;s about to drown in the muck a hovercraft appears above him, snags him and hauls him into its cargo bay.<br/><br/>He is rescued by Morpheus and brought aboard a levitating ship called the Nebuchadnezzar. Morpheus&#39;s crew includes Trinity, Apoc (Julian Arahanga), a man with long, flowing black hair, Switch, Cypher (bald with a goatee), two brawny brothers, Tank (Marcus Chong) and Dozer (Anthony Ray Parker), and a young, thin man named Mouse (Matt Doran).<br/><br/>Morpheus gets to the point. &quot;You wanted to know about the Matrix,&quot; he says, ushering him to a chair. Neo sits down in it and Trinity straps him in. A long probe is inserted into the socket at the back of Neo&#39;s skull.<br/><br/>Neo wakes in a world of all white. He is in the Construct, a &quot;loading platform&quot; that Morpheus and his team use to prepare newly freed humans to deal with the Matrix world. Gone are the sockets in Neo&#39;s arms and neck and his hair is grown in. Morpheus tells him that what he is experiencing of himself is the &quot;residual self image, the mental projection of your digital self&quot; and bids him to sit while he explains the truth. &quot;This,&quot; he says, showing an image of a modern city, &quot;is the world that you know.&quot; A thing that really exists &quot;only as part of a neural, interactive simulation that we call the Matrix.&quot;\nMorpheus then shows Neo the world as it truly exists today, a scarred, desolate emptiness with charred, abandoned buildings, black earth, and a shrouded sky.<br/><br/>Morpheus tells Neo that the year is approximately 2199, and humans are fighting against intelligent machines that were created early in the 21st century and have since taken control of the Earth&#39;s surface. Humanity lost a war with their artificially intelligent creations, leaving the Earth a devastated ruin. As a last resort, humans blackened the sky to eliminate the machines&#39; access to solar power and, in response, the machines developed farms of artificially grown humans to harness their bio-electric energy.<br/><br/>A human&#39;s body provides &quot;more electricity than a 120 volt battery and over 25k BTUs in body heat.&quot; Morpheus shows Neo fields where machines grow human beings, connecting them to their outlets, ensconcing them in their pods, and feeding them with the liquefied remains of other human beings. &quot;The Matrix,&quot; says Morpheus, &quot;is a computer-generated dreamworld created to keep us under control, to turn us&quot; into a mere power source, into copper-top batteries.<br/><br/>The remaining free humans established an underground refuge known as Zion, living a harsh existence on scarce resources.\nThe humans are kept docile within the Matrix, a simulated reality of the world as it was in 1999. The Matrix is a simulated reality based on human civilization at its peak, designed to keep the subjugated humans oblivious and pacified. That simulation is the world Neo has been living in since birth.<br/><br/>Morpheus and his crew belong to a group of free humans who &quot;unplug&quot; others from the Matrix and recruit them to their rebellion against the Machines, and who are able to gain superhuman abilities within the Matrix by using their understanding of its true nature to manipulate its physical laws.<br/><br/>Even so, they are outmatched by the overwhelmingly powerful Agents-sentient programs protecting the Matrix-and dying in the Matrix causes death in the real world.<br/><br/>When the Matrix was created there was a man born inside it who could create his own reality inside it. It was this man who set Morpheus and the others free. When he died, the Oracle (Gloria Foster) prophesied that he would return in another form. And that the return of the One would mean the destruction of the Matrix.\nMorpheus liberated Neo because he believes him to be &quot;the One&quot;, a prophesied figure destined to dismantle the Matrix and liberate humanity by ending the war with the machines.<br/><br/>The next day Neo starts his training. Tank is his operator. Tank and his brother Dozer are &quot;100% pure old-fashioned, homegrown human. Born in the real world; a genuine child of Zion.&quot; Zion, Tank explains, is the last human city, buried deep in the earth, near the core, for warmth. Tank straps Neo back into the jack-in chair, by-passes some preliminary programs and loads him up with combat training, starting with Jiu Jitsu. Neo is fed a series of martial arts techniques including Kempo, Tae Kwon Do, Drunken Boxing and Kung Fu. Morpheus and Tank are amazed at Neo&#39;s ability to ingest information, but Morpheus wants to test Neo.<br/><br/>Morpheus and Neo stand in a sparring program. The program has rules, like gravity. But as in many computer programs, some rules can be bent while others can be broken. Morpheus bids Neo to hit him, if he can. They fight with Neo impressively attacking but Morpheus easily parrying and subduing him. Morpheus ends up kicking Neo into a beam, explaining to him that the reason he has beaten him has nothing to do with muscles or reality. Neo finally brings a punch near his teacher&#39;s face.<br/><br/>A &quot;jump&quot; program is loaded. Both men now stand on one of several tall buildings in a normal city skyline. Morpheus tells Neo he must free his mind and leaps easily but impossibly from one building to the next. Neo nervously tries to follow him and doesn&#39;t make the jump, falling to the pavement below.\nMorpheus and Neo are walking down a standard city street in what appears to be the Matrix. Morpheus explains that the Matrix is a system and that the system is their enemy. All the people that inhabit it, the people they are trying to free, are part of that system. Some are so inert, so dependent upon the Matrix that they can never be free.<br/><br/>Neo asks what the Agents are. &quot;Sentient programs,&quot; says Morpheus, that &quot;can move in and out of any software hard-wired into their system, meaning that they can take over anyone in the Matrix program. &quot;Inside the Matrix,&quot; Morpheus says, &quot;They are everyone and they are no one.&quot; Thus Morpheus and his crew survive the Agents by running from them and hiding from the Agents even though they &quot;are guarding all the doors. They are holding all the keys and sooner or later, someone is going to have to fight them.&quot; But no one who has ever stood up to an Agent has survived; all have died. Still, Morpheus is certain that because the Agents live in a world of rules that they can never be as strong, never be as fast as he can be. &quot;What are you trying to tell me,&quot; asks Neo, &quot;That I can dodge bullets?&quot; &quot;When you&#39;re ready,&quot; Morpheus says, &quot;You won&#39;t have to.&quot;<br/><br/>The Nebuchadnezzar is on alert. They see the holographic image of a Squiddy, a search and destroy sentinel, which is on their trail. They set the ship down in a huge sewer system and turn off the power. Tank stands at the ready switch of an EMP, Electro-magnetic pulse, the only weapon man has against the machines in the real world. Two Squiddies search for the ship -- the crew can see them -- but they move on.<br/><br/>Cypher meets with Agent Smith inside the Matrix. Smith says he wants access codes to the mainframe in Zion. Cypher says he can&#39;t do that, but that he can get him the man who does, meaning Morpheus. The deal is that the machines to reinsert his body into a power plant, reinsert him into the Matrix, and he&#39;ll help the Agents.<br/><br/>The group enters the Matrix to visit the Oracle, who predicted the emergence of the One. As they walk out of a warehouse Cypher secretly throws his cell phone into the garbage. The Oracle, Morpheus explains, has been with them since the beginning of the Resistance. She is the one who made the Prophecy of the One and that Morpheus would be the one to find him.\nThe Oracle implies that Neo is not the One but warns that Neo must soon choose between his life and that of Morpheus.<br/><br/>The group is ambushed by Agents and tactical police, leading to the death of the crew member Mouse (Matt Doran). Morpheus allows himself to be captured to let Neo and the crew escape. Their ally Cypher (Joe Pantoliano) had betrayed them.\nMeanwhile, Cypher exits the Matrix and begins forcefully disconnecting the others, killing them. Before Cypher can kill Neo and Trinity, Tank (Marcus Chong), a subdued crew member, regains consciousness, kills Cypher, and safely extracts the survivors.<br/><br/>The Agents drug and interrogate Morpheus in an attempt to learn his access codes to the mainframe computer in Zion, the humans&#39; subterranean refuge in the real world. He informs Morpheus, who is tied to a chair, that the first Matrix was designed as a utopia, engineered to make everyone happy. &quot;It was a disaster,&quot; says Agent Smith, people wouldn&#39;t accept the program and &quot;entire crops were lost.&quot; &quot;Some believed,&quot; continues Smith, &quot;that we lacked the programming language to describe your perfect world. But I believe that, as a species, human beings define their reality through misery and suffering. The perfect world was a dream that your primitive cerebrum kept trying to wake up from. Which is why the Matrix was redesigned.&quot;<br/><br/>Tank is performing what amounts to last rites for Morpheus, laying one hand on his head as his other moves to the back of his skull to remove the jack. Just as he&#39;s about to pull it out Neo stops him. He realizes that the Oracle was right. He now has to make the choice to save himself or to save Morpheus; his choice is to head back into the Matrix. Trinity rejects the idea. Morpheus gave himself up so that Neo could be saved since he is the One. &quot;I&#39;m not the One, Trinity,&quot; Neo says, relaying his understanding of the discussion with the Oracle: she did not enlighten him as to whether he was the promised messiah. And, since Morpheus was willing to sacrifice himself, Neo knows that he must do that same.<br/><br/>Neo and Trinity return to the Matrix and rescue their leader; in the process, Neo becomes more confident in his ability to manipulate the Matrix and is ultimately able to dodge bullets fired at him.<br/><br/>Morpheus and Trinity use a telephone to exit the Matrix, but Neo is ambushed by Agent Smith. He stands his ground and defeats Smith but flees when the Agent possesses another body. Meanwhile, in the real world &quot;sentinel&quot; machines converge on the Nebuchadnezzar.<br/><br/>Just before reaching another exit, Neo is shot and killed by Agent Smith. Trinity, who is standing over Neo in the real world, whispers that the Oracle told her she would fall in love with the One. She kisses Neo and restores his life. Neo revives with new power to perceive and control the Matrix, and effortlessly destroys Agent Smith, before returning to the real world in time for the ship&#39;s EMP weapon to destroy the attacking sentinels.<br/><br/>The film ends with Neo back in the Matrix, making a telephone call promising that he will demonstrate to the people imprisoned in the Matrix that &quot;anything is possible.&quot; He hangs up the phone and flies into the sky."
  ],
  "production": [
    "Warner Bros.",
    "Village Roadshow Pictures",
    "Groucho Film Partnership"
  ]
}
    
```




Get detailed information about a movie by IMDb ID

``` python
# Get detailed information about a movie by IMDb ID
movie = get_movie("0133093") 
print(f"Title: {movie.title}") # Title: The Matrix
print(f"Year: {movie.year}") # Year: 1999
print(f"Rating: {movie.rating}") # Rating: 8.7
print(f"Genres: {', '.join(movie.genres)}") # Genres: Action, Sci-Fi
print(f"Plot: {movie.plot}") # Plot: A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.
``` 

## Documentation
For detailed documentation, it is straightforward and self-explanatory.
## License
This project is licensed under GPL  v2.0 - see the [LICENSE](LICENSE) file for details.
## Contributing
Contributions are welcome! Please read the [CONTRIBUTING](CONTRIBUTING.md) file for details on how to contribute to this project.
## Issues
